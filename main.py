# -*- coding: utf-8 -*-
"""M1 主流程 main.py
增量读取 → 模板解析 → 标准化落盘 parsed.csv → 统计摘要
用法: python main.py
"""
import os
import csv
import sys
import io
import time
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import log_reader
import parser as logparser

#本文件所在绝对路径
BASE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(BASE, 'rules.yaml')
CURSOR = os.path.join(BASE, 'data', '.log_cursor.json')
PARSED_CSV = os.path.join(BASE, 'data', 'parsed.csv')
UNKNOWN_LOG = os.path.join(BASE, 'data', 'unknown.log')

FIELDS = ['source', 'ts', 'host', 'proc', 'pid', 'event',
          'user', 'ip', 'port', 'tag', 'detail', 'raw']

def main():
    sources, patterns = logparser.load_rules(RULES)
    print('=' * 66)
    print('日志智能分析流水线 · M1 增量解析运行')
    print('=' * 66)

    # 追加模式写 parsed.csv（首次运行时创建表头）
    new_file = not os.path.exists(PARSED_CSV)
    fout = open(PARSED_CSV, 'a', newline='', encoding='utf-8')
    writer = csv.DictWriter(fout, fieldnames=FIELDS, extrasaction='ignore')
    if new_file:
        writer.writeheader()

    stats = Counter()
    unknown_buf = []
    total_new = 0

    for src in sources:
        name = src['name']
        path = os.path.join(BASE, src['path'])
        lines, is_full = log_reader.read_new(path, CURSOR, name)
        pats = patterns[name]
        print('\n[%s] %s 新增 %d 行%s' % (name, src['path'], len(lines),
                                         '（全量首次读取）' if is_full else '（增量读取）'))
        for line in lines:
            rec = logparser.parse_line(name, line, pats)
            stats[(name, rec['event'])] += 1
            total_new += 1
            if rec['event'] == 'UNKNOWN':
                unknown_buf.append(rec['raw'])
            else:
                writer.writerow(rec)
        # 未知类单独落盘（含未匹配行）
        if unknown_buf:
            with open(UNKNOWN_LOG, 'a', encoding='utf-8') as uf:
                uf.write('\n'.join(unknown_buf) + '\n')
            unknown_buf = []

    fout.close()

    print('\n' + '=' * 66)
    print('本次解析 %d 行 → 事件分布：' % total_new)
    print('=' * 66)
    for (src, ev), n in sorted(stats.items(), key=lambda x: -x[1]):
        print('  %-6s %-22s %6d' % (src, ev, n))

    # 总库统计（parsed.csv 全量）
    print('\n' + '=' * 66)
    print('parsed.csv 累计统计：')
    print('=' * 66)
    if os.path.exists(PARSED_CSV):
        rows = list(csv.DictReader(open(PARSED_CSV, encoding='utf-8')))
        ev_total = Counter(r['event'] for r in rows)
        for ev, n in sorted(ev_total.items(), key=lambda x: -x[1]):
            print('  %-22s %6d' % (ev, n))
        print('  共 %d 条结构化记录' % len(rows))

        # 扫描/爆破 Top IP
        ip_cnt = Counter(r['ip'] for r in rows if r['ip'])
        print('\nTop 10 来源 IP：')
        for ip, n in ip_cnt.most_common(10):
            print('  %-20s %6d' % (ip, n))

    print('\n完成。输出：parsed.csv / unknown.log / .log_cursor.json')

if __name__ == '__main__':
    main()
