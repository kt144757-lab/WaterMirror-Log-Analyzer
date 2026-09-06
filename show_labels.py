# -*- coding: utf-8 -*-
import csv, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
rows = list(csv.DictReader(open(r'C:\Users\ZhuanZ\Desktop\网安报告\_work\log_analyzer\data\analysis.csv', encoding='utf-8')))
print('=== 恶意/可疑 IP 完整标注 ===')
for r in rows:
    if r['label'] != 'normal':
        print('  [%s] %-16s 事件%-5s | %s' % (r['label'], r['ip'], r['total_events'], r['reason']))
