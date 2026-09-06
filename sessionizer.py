# -*- coding: utf-8 -*-
"""④ 会话聚合 sessionizer.py
输入：parsed.csv（结构化日志）
输出：data/sessions.csv（成功登录会话，含时长）
机制：按 sshd-session 的 PID 串联事件链
  会话开始 = LOGIN_SUCCESS（Accepted）
  会话结束 = 同 PID 后续 SESSION_CLOSED / DISCONNECT / CONN_CLOSED
  无 LOGIN_SUCCESS 的 PID = 纯探测连接（归入扫描画像，不进会话表）
"""
import os
import csv
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
PARSED_CSV = os.path.join(BASE, 'data', 'parsed.csv')
SESSIONS_CSV = os.path.join(BASE, 'data', 'sessions.csv')

FIELDS = ['pid', 'user', 'ip', 'port', 'method', 'login_time', 'logout_time', 'duration_sec']


def parse_ts(s):
    """ISO 时间戳统一转 datetime，失败返回 None"""
    if not s:
        return None
    try:
        # '2026-09-04T10:54:16.879545+08:00' / '+0800' 均可
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return None


def build_sessions(rows):
    """rows: parsed.csv 行列表 → 会话列表 + 探测连接计数"""
    # 按 pid 聚合 auth 事件
    by_pid = {}
    for r in rows:
        if r['source'] != 'auth':
            continue
        by_pid.setdefault(r['pid'], []).append(r)

    sessions = []
    probe_count = 0  # 纯探测连接（无登录成功）
    for pid, evs in by_pid.items():
        if not pid:
            continue
        logins = [e for e in evs if e['event'] == 'LOGIN_SUCCESS']
        if not logins:
            # 无成功登录：按 IP 计数为探测
            probe_count += len([e for e in evs if e['event'] in ('CONN_CLOSED', 'CONN_RESET')])
            continue
        # 会话：每次 LOGIN_SUCCESS 开一个会话
        evs_sorted = sorted(evs, key=lambda e: parse_ts(e['ts']) or datetime.min)
        for li, le in enumerate(logins):
            t0 = parse_ts(le['ts'])
            # 会话结束 = 该登录事件之后最近的 SESSION_CLOSED/DISCONNECT/CONN_CLOSED
            end_ts = None
            for later in evs_sorted:
                lt = parse_ts(later['ts'])
                if lt and t0 and lt <= t0:
                    continue
                if later['event'] in ('SESSION_CLOSED', 'DISCONNECT', 'CONN_CLOSED'):
                    end_ts = lt
                    break
            dur = None
            if t0 and end_ts:
                dur = round((end_ts - t0).total_seconds(), 1)
            method = 'unknown'
            raw = le.get('raw') or ''
            if 'Accepted password' in raw:
                method = 'password'
            elif 'Accepted publickey' in raw:
                method = 'publickey'
            sessions.append({
                'pid': pid,
                'user': le.get('user'),
                'ip': le.get('ip'),
                'port': le.get('port'),
                'method': method,
                'login_time': le.get('ts'),
                'logout_time': end_ts.isoformat() if end_ts else None,
                'duration_sec': dur,
            })
    return sessions, probe_count


def run():
    if not os.path.exists(PARSED_CSV):
        print('parsed.csv 不存在，请先运行 main.py')
        return None, None
    rows = list(csv.DictReader(open(PARSED_CSV, encoding='utf-8')))
    sessions, probe = build_sessions(rows)

    with open(SESSIONS_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        w.writeheader()
        w.writerows(sessions)

    print('[sessionizer] 成功登录会话 %d 条，纯探测连接 %d 条（未登录）' % (len(sessions), probe))
    print('[sessionizer] 输出 -> %s' % SESSIONS_CSV)
    return sessions, probe


if __name__ == '__main__':
    run()
