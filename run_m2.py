# -*- coding: utf-8 -*-
"""M2 运行入口：会话聚合 + 特征工程 + 画像展示
用法: python run_m2.py
"""
import os
import sys
import io
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sessionizer
import features

BASE = os.path.dirname(os.path.abspath(__file__))
SESSIONS_CSV = os.path.join(BASE, 'data', 'sessions.csv')
FEATURES_CSV = os.path.join(BASE, 'data', 'features.csv')

print('=' * 68)
print('日志智能分析流水线 · M2 会话聚合 + 特征工程')
print('=' * 68)

sessions, probe = sessionizer.run()
feats = features.run()

# ---------- 会话展示 ----------
if sessions and os.path.exists(SESSIONS_CSV):
    print('\n--- 登录会话明细（%d 条）---' % len(sessions))
    print('%-6s %-8s %-16s %-7s %-10s %-20s %-20s %-8s' % ('pid', 'user', 'ip', 'method', 'duration', 'login_time', 'logout_time', 'dur_sec'))
    for s in sessions[:15]:
        print('%-6s %-8s %-16s %-7s %-10s %-20s %-20s %-8s' % (
            s['pid'], s['user'], s['ip'], s['method'],
            '%ss' % s['duration_sec'] if s['duration_sec'] is not None else '进行中',
            (s['login_time'] or '')[:19], (s['logout_time'] or '')[:19],
            s['duration_sec']))
    if len(sessions) > 15:
        print('  …共 %d 条' % len(sessions))

# ---------- 攻击源画像展示 ----------
if feats:
    print('\n--- 攻击源画像 Top 15（按事件量）---')
    print('%-16s %6s %6s %6s %6s %6s %6s %6s %6s %6s' % (
        'IP', '总量', '探测', '失败', '成功', 'HTTP', '失败率', '探测占比', 'IP跨度h', '攻击链'))
    for f in feats[:15]:
        print('%-16s %6d %6d %6d %6d %6d %6.2f %6.2f %6.1f %6d' % (
            f['ip'], f['total_events'], f['probe_conn'], f['login_failed'],
            f['login_success'], f['http_requests'], f['fail_rate'],
            f['probe_ratio'], f['time_span_h'], f['attack_chain']))
    print('  …共 %d 个来源 IP' % len(feats))

print('\n完成。输出：sessions.csv / features.csv')
