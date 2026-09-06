# -*- coding: utf-8 -*-
"""②③ 解析器 + 标准化 parser.py
- 按 rules.yaml 正则模板解析每行 → 结构化字段
- 进程名/事件名动态提取：sshd-session[46343] → proc=sshd-session, pid=46343
- 匹配不到 → 未知类兜底（unknown），绝不静默丢弃
"""
import re
import yaml

# auth.log 行头：时间戳 主机 进程[pid]: 消息
# 2026-09-05T16:23:04.137375+08:00 mcstart sshd-session[50042]: Accepted password for root from 106.61.37.103 port 24256 ssh2
_LINE_HEAD = re.compile(r'^(\S+) (\S+) (\S+?)(?:\[(\d+)\])?: (.*)$')
# nginx 行头：IP - - [date] "..." status ...
_NGINX_HEAD = re.compile(r'^(?P<ip>\S+) - - \[(?P<date>[^\]]+)\]')


def load_rules(rules_path):
    with open(rules_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)
    compiled = {}
    for src in data['sources']:
        name, typ = src['name'], src['type']
        compiled[name] = []
        for pat in data['patterns'].get(typ, []):
            compiled[name].append({
                'name': pat['name'],
                'event': pat['event'],
                'desc': pat.get('desc', ''),
                'regex': re.compile(pat['regex']),
            })
    return data['sources'], compiled


def _extract_head(line):
    """统一提取行头（时间戳/主机/进程），auth 与 nginx 分格式"""
    m = _LINE_HEAD.match(line)
    if m:
        ts, host, proc, pid, msg = m.groups()
        return {'ts': ts, 'host': host, 'proc': proc, 'pid': pid, 'msg': msg}
    # nginx 格式
    m2 = _NGINX_HEAD.match(line)
    if m2:
        date = m2.group('date')
        # [04/Sep/2026:16:08:02 +0800] -> ISO
        try:
            t = re.match(r'(\d{2})/(\w{3})/(\d{4}):(\d{2}:\d{2}:\d{2}) ([+-]\d{4})', date)
            mon = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                   'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}[t.group(2)]
            iso = '%s-%02d-%sT%s%s' % (t.group(3), mon, t.group(1), t.group(4), t.group(5))
        except Exception:
            iso = date
        return {'ts': iso, 'host': '-', 'proc': 'nginx', 'pid': None, 'msg': line}
    return None


def parse_line(source, line, patterns):
    """解析单行 → dict；未知返回 None"""
    head = _extract_head(line)
    if head is None:
        return None
    rec = {
        'source': source,
        'ts': head['ts'],
        'host': head['host'],
        'proc': head['proc'],
        'pid': head['pid'],
        'event': None,
        'user': None,
        'ip': None,
        'port': None,
        'tag': None,
        'detail': '',
        'raw': line,
    }
    for pat in patterns:
        m = pat['regex'].search(head['msg'])
        if m:
            rec['event'] = pat['event']
            g = m.groupdict()
            rec['user'] = g.get('user')
            rec['ip'] = g.get('ip')
            rec['port'] = g.get('port')
            rec['tag'] = (g.get('tag') or '').strip() or None
            # detail: 命中的事件描述 + 命中原句
            rec['detail'] = pat['desc']
            if g.get('reason'):
                rec['detail'] = g['reason']
            elif g.get('path'):
                rec['detail'] = '%s %s -> %s' % (g.get('method', ''), g.get('path', ''), g.get('status', ''))
            rec['detail_raw'] = m.group(0)
            break
    if rec['event'] is None:
        # 未匹配：保留 msg 前 60 字做未知类线索
        rec['event'] = 'UNKNOWN'
        rec['detail'] = head['msg'][:80]
    return rec
