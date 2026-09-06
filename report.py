# -*- coding: utf-8 -*-
"""⑦ 聚合总表 + 网页可视化报告 report.py
输入：data/parsed.csv + data/analysis.csv
输出：output/report.html（ECharts 静态报告，浏览器直接打开）
"""
import os
import csv
import json
import sys
import io
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
PARSED_CSV = os.path.join(BASE, 'data', 'parsed.csv')
ANALYSIS_CSV = os.path.join(BASE, 'data', 'analysis.csv')
OUT_HTML = os.path.join(BASE, 'output', 'report.html')

EVENT_CN = {
    'CONN_CLOSED': '连接关闭(preauth探测)', 'CONN_RESET': '连接重置',
    'LOGIN_SUCCESS': '登录成功', 'LOGIN_FAILED': '登录失败',
    'LOGIN_FAILED_MAX': '认证次数超限', 'LOGIN_FAILED_INVALID': '无效用户爆破',
    'LOGIN_INVALID_USER': '无效用户探测', 'AUTH_FAILURE': 'PAM认证失败',
    'SESSION_OPENED': '会话建立', 'SESSION_CLOSED': '会话关闭',
    'DISCONNECT': '连接断开', 'SERVICE_EVENT': '服务事件',
    'ACCOUNT_CHANGE': '账号变更', 'HTTP_REQUEST': 'HTTP请求', 'UNKNOWN': '未知类',
}
LABEL_CN = {'normal': '正常', 'suspect': '可疑', 'malicious': '恶意'}
LABEL_COLOR = {'normal': '#52C41A', 'suspect': '#FAAD14', 'malicious': '#EA6668'}


def _hour_key(ts):
    """ISO ts -> 'YYYY-MM-DD HH' 小时键"""
    try:
        return ts[:13].replace('T', ' ')
    except Exception:
        return 'unknown'


def collect():
    rows = list(csv.DictReader(open(PARSED_CSV, encoding='utf-8')))
    analysis = []
    if os.path.exists(ANALYSIS_CSV):
        analysis = list(csv.DictReader(open(ANALYSIS_CSV, encoding='utf-8')))

    # 事件分布
    ev_cnt = Counter(r['event'] for r in rows)
    ev_dist = [{'name': EVENT_CN.get(e, e), 'value': n} for e, n in ev_cnt.most_common(12)]

    # 小时时间线（三类主力事件）
    hourly = defaultdict(Counter)
    for r in rows:
        h = _hour_key(r['ts'])
        if r['event'] == 'CONN_CLOSED':
            hourly[h]['probe'] += 1
        elif r['event'] == 'HTTP_REQUEST':
            hourly[h]['http'] += 1
        elif r['event'] in ('LOGIN_FAILED', 'LOGIN_FAILED_MAX', 'AUTH_FAILURE'):
            hourly[h]['failed'] += 1
    hours = sorted(hourly.keys())
    tl = {
        'hours': hours,
        'probe': [hourly[h]['probe'] for h in hours],
        'http': [hourly[h]['http'] for h in hours],
        'failed': [hourly[h]['failed'] for h in hours],
    }

    # Top IP（按事件量）
    ip_cnt = Counter(r['ip'] for r in rows if r['ip'])
    top_ip = [{'name': ip, 'value': n} for ip, n in ip_cnt.most_common(12)]

    # 恶意/可疑标注表
    label_map = {}
    for a in analysis:
        label_map[a['ip']] = a
    abnormal = [a for a in analysis if a['label'] != 'normal']
    abnormal.sort(key=lambda x: (x['label'] != 'malicious', -int(x['total_events'])))

    # 概览
    n_src = len(ip_cnt)
    n_mal = sum(1 for a in analysis if a['label'] == 'malicious')
    n_susp = sum(1 for a in analysis if a['label'] == 'suspect')
    n_login = sum(1 for r in rows if r['event'] == 'LOGIN_SUCCESS')

    return {
        'total': len(rows), 'src': n_src, 'mal': n_mal, 'susp': n_susp,
        'login': n_login, 'ev_dist': ev_dist, 'tl': tl, 'top_ip': top_ip,
        'abnormal': abnormal, 'label_cn': LABEL_CN, 'label_color': LABEL_COLOR,
    }


def render(d):
    rows_tbl = ''
    for a in d['abnormal']:
        color = d['label_color'][a['label']]
        rows_tbl += (
            '<tr><td style="padding:8px 10px;border-bottom:1px solid #EEE;font-family:Consolas,monospace;font-size:12.5px;">%s</td>'
            '<td style="padding:8px 10px;border-bottom:1px solid #EEE;font-size:12.5px;"><span style="background:%s;color:#fff;border-radius:4px;padding:2px 8px;font-size:11.5px;">%s</span></td>'
            '<td style="padding:8px 10px;border-bottom:1px solid #EEE;font-size:12.5px;color:#555;">%s</td>'
            '<td style="padding:8px 10px;border-bottom:1px solid #EEE;font-size:12.5px;">%s</td>'
            '<td style="padding:8px 10px;border-bottom:1px solid #EEE;font-size:12px;color:#888;">%.3f</td></tr>'
        ) % (a['ip'], color, d['label_cn'][a['label']], a['reason'], a['total_events'], float(a['ml_score']))

    html = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>蜜罐日志智能分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<style>
body{margin:0;background:#F4F3EE;font-family:'PingFang SC','Microsoft YaHei',sans-serif;color:#1A1B1C;}
.wrap{max-width:1080px;margin:0 auto;padding:24px 16px 48px;}
h1{font-size:22px;color:#1A2E4B;margin:4px 0 2px;}
.sub{font-size:13px;color:#6B7280;margin-bottom:20px;}
.cards{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px;}
.card{flex:1 1 150px;background:#fff;border-radius:12px;padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,.06);}
.card .v{font-size:26px;font-weight:600;}
.card .k{font-size:12px;color:#6B7280;margin-top:4px;}
.panel{background:#fff;border-radius:12px;padding:16px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.06);}
.panel h2{font-size:15px;margin:0 0 12px;color:#1A2E4B;}
.chart{width:100%%;height:280px;}
table{width:100%%;border-collapse:collapse;}
th{background:#1A2E4B;color:#fff;text-align:left;padding:8px 10px;font-size:12.5px;font-weight:500;}
tr:nth-child(even) td{background:#FAFAF7;}
.legend{font-size:12px;color:#6B7280;margin-top:8px;}
</style></head><body><div class="wrap">
<h1>蜜罐服务器日志智能分析报告</h1>
<div class="sub">数据源：47.243.223.221 /var/log/auth.log + nginx access.log · 流水线 M1-M3 全自动解析 · 生成时间 %s</div>
<div class="cards">
<div class="card"><div class="v" style="color:#1A2E4B;">%d</div><div class="k">解析事件总数</div></div>
<div class="card"><div class="v">%d</div><div class="k">来源 IP 数</div></div>
<div class="card"><div class="v" style="color:#EA6668;">%d</div><div class="k">恶意 IP</div></div>
<div class="card"><div class="v" style="color:#FAAD14;">%d</div><div class="k">可疑 IP</div></div>
<div class="card"><div class="v" style="color:#52C41A;">%d</div><div class="k">成功登录</div></div>
</div>
<div class="panel"><h2>事件类型分布</h2><div id="ev" class="chart"></div></div>
<div class="panel"><h2>24 小时事件时间线</h2><div id="tl" class="chart"></div>
<div class="legend">探测=SSH preauth 连接关闭（扫描器指纹）· HTTP=Web 请求 · 失败=认证失败</div></div>
<div class="panel"><h2>Top 12 来源 IP（按事件量）</h2><div id="ip" class="chart"></div></div>
<div class="panel"><h2>异常 IP 标注总表</h2><div style="overflow-x:auto;">
<table><tr><th>来源 IP</th><th>判定</th><th>判定依据</th><th>事件量</th><th>ML 异常分</th></tr>%s</table></div>
<div class="legend">判定融合：规则引擎强证据优先（扫描器/爆破/敏感文件探测），ML（Isolation Forest + DBSCAN）补充统计离群点；白名单为运维本机。</div></div>
</div>
<script>
(function(){
try{
var D = %s;
function mk(id,opt){var c=document.getElementById(id);if(!c||typeof echarts==='undefined'){c.innerHTML='<div style="padding:12px;color:#6B7280;font-size:13px;">图表库加载失败</div>';return;}var m=echarts.init(c);m.setOption(opt);window.addEventListener('resize',function(){m.resize();});}
var AX={axisLabel:{color:'#555',fontSize:11},splitLine:{lineStyle:{color:'#EEE'}}};
mk('ev',{backgroundColor:'transparent',tooltip:{trigger:'item',confine:true},legend:{bottom:0,textStyle:{fontSize:11}},series:[{type:'pie',radius:['30%%','62%%'],center:['50%%','42%%'],data:D.ev,label:{fontSize:11,color:'#555'},itemStyle:{borderColor:'#fff',borderWidth:1}}]});
mk('tl',{backgroundColor:'transparent',tooltip:{trigger:'axis',confine:true},legend:{top:0,textStyle:{fontSize:11}},grid:{left:42,right:16,top:30,bottom:34,containLabel:true},xAxis:Object.assign({type:'category',data:D.tl.hours},AX),yAxis:Object.assign({type:'value',name:'条/小时'},AX),series:[
{name:'探测',type:'line',smooth:true,data:D.tl.probe,itemStyle:{color:'#EA6668'},lineStyle:{width:2},symbolSize:3},
{name:'HTTP',type:'line',smooth:true,data:D.tl.http,itemStyle:{color:'#8BC8EA'},lineStyle:{width:2},symbolSize:3},
{name:'失败',type:'line',smooth:true,data:D.tl.failed,itemStyle:{color:'#FAAD14'},lineStyle:{width:2},symbolSize:3}]});
mk('ip',{backgroundColor:'transparent',tooltip:{trigger:'axis',confine:true,axisPointer:{type:'shadow'}},grid:{left:130,right:40,top:10,bottom:24},xAxis:Object.assign({type:'value'},AX),yAxis:Object.assign({type:'category',data:D.topIp.map(function(x){return x.name;}),axisLabel:{color:'#444',fontSize:11}},AX),series:[{type:'bar',data:D.topIp.map(function(x){return x.value;}),itemStyle:{color:'#1A2E4B',borderRadius:[0,4,4,0]},barWidth:14,label:{show:true,position:'right',fontSize:10,color:'#666'}}]});
}catch(e){console.error(e);}
})();
</script>
</body></html>""" % (
        __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'),
        d['total'], d['src'], d['mal'], d['susp'], d['login'],
        rows_tbl,
        json.dumps({
            'ev': d['ev_dist'],
            'tl': d['tl'],
            'topIp': d['top_ip'],
        }, ensure_ascii=False),
    )

    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    print('[report] 报告已生成 -> %s' % OUT_HTML)


if __name__ == '__main__':
    d = collect()
    render(d)
