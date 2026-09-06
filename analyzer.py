# -*- coding: utf-8 -*-
"""⑥ 规则统计 + ML 异常检测 analyzer.py
输入：data/features.csv（IP 特征）
输出：data/analysis.csv（特征 + 标注 label + 依据 reason + ML 分数）

双层判定（可解释优先）：
  第一层 规则引擎（强证据，秒级，可解释）：
    - 白名单（运维本机）→ normal
    - 纯 SSH 扫描（探测占比高且量大）→ malicious
    - 高失败爆破 / 大流量 HTTP 探测 → suspect / malicious
  第二层 无监督 ML（Isolation Forest + DBSCAN）：
    - 在标准化特征上找统计离群点，补充规则未覆盖的异常
  融合：规则强证据 > ML；ML 命中且规则未覆盖 → suspect 待复核
"""
import os
import sys
import io
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
FEATURES_CSV = os.path.join(BASE, 'data', 'features.csv')
ANALYSIS_CSV = os.path.join(BASE, 'data', 'analysis.csv')

# 我们自己的运维/测试 IP（白名单）
WHITELIST = {'106.61.42.246', '106.61.37.103', '::1', '127.0.0.1'}

# 数值特征列（ML 输入）
NUM_COLS = ['total_events', 'probe_conn', 'login_failed', 'login_success',
            'http_requests', 'http_404', 'fail_rate', 'probe_ratio',
            'unique_users', 'unique_ports', 'unique_paths',
            'time_span_h', 'events_per_h', 'active_hours']


def _rule_label(f):
    """规则引擎：返回 (label, reason)"""
    ip = f['ip']
    probe, failed, success = f['probe_conn'], f['login_failed'], f['login_success']
    http, http404 = f['http_requests'], f['http_404']
    total = f['total_events']
    probe_ratio = f['probe_ratio']

    if ip in WHITELIST:
        return 'normal', '白名单（运维本机）'

    # 纯 SSH 端口扫描：探测占比高且量级大
    if probe >= 500 and probe_ratio >= 0.95:
        return 'malicious', 'SSH 端口扫描器（探测 %d 条，占比 %.0f%%）' % (probe, probe_ratio * 100)
    if probe >= 20 and probe_ratio >= 0.8:
        return 'suspect', '疑似 SSH 探测（探测 %d 条）' % probe

    # 敏感文件扫描（.env/.aws 等）在 report 阶段用 parsed 补充，这里用 HTTP 404 占比
    if http >= 100 and http404 / http >= 0.9:
        return 'malicious', 'Web 目录/敏感文件扫描（HTTP %d 条，404 占比 %.0f%%）' % (http, http404 / http * 100)

    # 爆破特征：失败次数多
    if failed >= 5 and success == 0:
        return 'suspect', 'SSH 爆破尝试（失败 %d 次）' % failed
    if failed + success >= 3 and f['fail_rate'] > 0.5:
        return 'suspect', '登录失败率偏高（%.0f%%）' % (f['fail_rate'] * 100)

    # 攻击链：探测+失败+成功组合
    if f['attack_chain'] and ip not in WHITELIST:
        return 'suspect', '完整攻击链特征（探测+失败+成功）'

    return 'normal', '未见明显异常行为'


def _ml_score(feats):
    """无监督异常检测：Isolation Forest + DBSCAN 融合
    返回 {ip: (ml_label, score)}，score 越大越异常
    """
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return {}

    X = np.array([[f[c] for c in NUM_COLS] for f in feats], dtype=float)
    Xs = StandardScaler().fit_transform(X)

    iso = IsolationForest(n_estimators=120, contamination=0.08, random_state=42)
    iso_l = iso.fit_predict(Xs)  # -1 异常
    iso_s = -iso.score_samples(Xs)  # 越大越异常

    db = DBSCAN(eps=1.6, min_samples=3)
    db_l = db.fit_predict(Xs)  # -1 噪声点

    out = {}
    for i, f in enumerate(feats):
        ml_abn = iso_l[i] == -1 or db_l[i] == -1
        out[f['ip']] = ('anomaly' if ml_abn else 'normal', round(float(iso_s[i]), 4))
    return out


def run():
    if not os.path.exists(FEATURES_CSV):
        print('features.csv 不存在，请先运行 run_m2.py')
        return None
    feats = list(csv.DictReader(open(FEATURES_CSV, encoding='utf-8')))
    for f in feats:
        for c in NUM_COLS:
            f[c] = float(f[c] or 0)
        f['total_events'] = int(f['total_events'])
        f['probe_conn'] = int(f['probe_conn'])
        f['login_failed'] = int(f['login_failed'])
        f['login_success'] = int(f['login_success'])
        f['http_requests'] = int(f['http_requests'])
        f['http_404'] = int(f['http_404'])
        f['unique_users'] = int(f['unique_users'])
        f['unique_ports'] = int(f['unique_ports'])
        f['unique_paths'] = int(f['unique_paths'])
        f['active_hours'] = int(f['active_hours'])
        f['attack_chain'] = int(f['attack_chain'])

    ml = _ml_score(feats)

    results = []
    for f in feats:
        label, reason = _rule_label(f)
        ml_label, ml_score = ml.get(f['ip'], ('normal', 0.0))
        # 白名单 IP：规则与 ML 均不越权（运维本机行为波动属正常）
        if f['ip'] in WHITELIST:
            label, reason = 'normal', '白名单（运维本机）'
        # 融合：规则 malicious 优先；规则 normal 但 ML anomaly → 待复核
        elif label == 'normal' and ml_label == 'anomaly':
            label = 'suspect'
            reason = 'ML 离群（规则未覆盖，分数 %.3f）' % ml_score
        elif label == 'suspect' and ml_label == 'anomaly':
            reason += '；ML 确认为离群'
        results.append({**f, 'label': label, 'reason': reason, 'ml_score': ml_score})

    results.sort(key=lambda x: (x['label'] != 'malicious', x['label'] != 'suspect', -x['total_events']))
    with open(ANALYSIS_CSV, 'w', newline='', encoding='utf-8') as fo:
        w = csv.DictWriter(fo, fieldnames=list(results[0].keys()) if results else [])
        w.writeheader()
        w.writerows(results)

    from collections import Counter
    cnt = Counter(r['label'] for r in results)
    print('[analyzer] 标注完成：%s' % dict(cnt))
    print('[analyzer] 输出 -> %s' % ANALYSIS_CSV)
    return results


if __name__ == '__main__':
    run()
