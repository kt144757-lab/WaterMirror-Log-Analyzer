# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
html = open(r'C:\Users\ZhuanZ\Desktop\网安报告\_work\log_analyzer\output\report.html', encoding='utf-8').read()
print('HTML 大小:', len(html), '字节')
m = re.search(r'var D = (\{.*?\});', html, re.S)
if m:
    d = json.loads(m.group(1))
    print('JSON 注入解析 OK')
    print('  事件分布:', len(d['ev']), '类, 总数', sum(x['value'] for x in d['ev']))
    print('  时间线:', len(d['tl']['hours']), '小时, 探测峰值', max(d['tl']['probe']))
    print('  Top IP:', [x['name'] for x in d['topIp'][:5]])
else:
    print('JSON 提取失败！')
marker = '<tr><td style="padding:8px 10px'
print('  异常表行数:', html.count(marker))
print('  ECharts CDN:', 'echarts@5.4.3' in html)
