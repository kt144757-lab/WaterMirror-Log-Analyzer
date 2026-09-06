# -*- coding: utf-8 -*-
"""⑤ 特征工程 features.py
输入：parsed.csv + sessions.csv
输出：data/features.csv（每来源 IP 一行聚合特征，供 M3 ML 异常检测）
特征维度：
  总量类：总事件数、探测连接数、失败数、成功数、HTTP 请求数
  比例类：失败率、探测占比
  多样性：唯一用户数、唯一端口数、唯一路径数（Web）
  时间类：时间跨度(小时)、事件频率(条/小时)、活跃小时数
  攻击链：是否同时具备 探测+失败+成功（完整攻击链特征）
"""
import os
import csv
from collections import Counter
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PARSED_CSV = os.path.join(BASE, 'data', 'parsed.csv')
FEATURES_CSV = os.path.join(BASE, 'data', 'features.csv')

FIELDS = ['ip', 'total_events', 'probe_conn', 'login_failed', 'login_success',
          'http_requests', 'http_404', 'fail_rate', 'probe_ratio',
          'unique_users', 'unique_ports', 'unique_paths',
          'time_span_h', 'events_per_h', 'active_hours',
          'attack_chain']


def _parse(s):
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return None


def run():
    if not os.path.exists(PARSED_CSV):
        print('parsed.csv 不存在')
        return None

    rows = list(csv.DictReader(open(PARSED_CSV, encoding='utf-8')))
    # 按 IP 分组
    by_ip = {}
    for r in rows:
        ip = r.get('ip') or ''
        if not ip:
            continue
        by_ip.setdefault(ip, []).append(r)

    feats = []
    for ip, evs in by_ip.items():
        times = [t for t in (_parse(e['ts']) for e in evs) if t]
        total = len(evs)
        probe = sum(1 for e in evs if e['event'] == 'CONN_CLOSED')
        failed = sum(1 for e in evs if e['event'] in ('LOGIN_FAILED', 'LOGIN_FAILED_MAX', 'AUTH_FAILURE', 'LOGIN_INVALID_USER'))
        success = sum(1 for e in evs if e['event'] == 'LOGIN_SUCCESS')
        http = sum(1 for e in evs if e['source'] == 'nginx')
        http404 = sum(1 for e in evs if e['source'] == 'nginx' and e['detail'] and '404' in e['detail'])
        users = {e['user'] for e in evs if e['user']}
        ports = {e['port'] for e in evs if e['port']}
        paths = set()
        for e in evs:
            d = e['detail'] or ''
            if e['source'] == 'nginx' and ' ' in d:
                paths.add(d.split()[1] if len(d.split()) > 1 else '')
        paths.discard('')

        span_h = 0.0
        if len(times) >= 2:
            span_h = round((max(times) - min(times)).total_seconds() / 3600, 2)
        elif len(times) == 1:
            span_h = 0.0
        events_per_h = round(total / span_h, 2) if span_h > 0 else (total if total else 0)
        active_hours = len({t.strftime('%Y%m%d%H') for t in times})

        fail_rate = round(failed / (failed + success), 3) if (failed + success) else 0.0
        probe_ratio = round(probe / total, 3) if total else 0.0
        attack_chain = 1 if (probe > 0 and failed > 0 and success > 0) else 0

        feats.append({
            'ip': ip, 'total_events': total, 'probe_conn': probe,
            'login_failed': failed, 'login_success': success,
            'http_requests': http, 'http_404': http404,
            'fail_rate': fail_rate, 'probe_ratio': probe_ratio,
            'unique_users': len(users), 'unique_ports': len(ports),
            'unique_paths': len(paths), 'time_span_h': span_h,
            'events_per_h': events_per_h, 'active_hours': active_hours,
            'attack_chain': attack_chain,
        })

    feats.sort(key=lambda x: -x['total_events'])
    with open(FEATURES_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(feats)

    print('[features] 特征表 %d 个来源 IP -> %s' % (len(feats), FEATURES_CSV))
    return feats


if __name__ == '__main__':
    run()
