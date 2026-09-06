# -*- coding: utf-8 -*-
"""生成教学文档《日志智能分析流水线——设计思路与代码执行流程》
多彩排版规范（用户既定）：
  标题深蓝 #1A2E4B · 目的块 #EAF0F8 · 命令块 #F2F2F2 · 输出块 #F7F7F7
  要点块 #FFF6E5 · 警告块 #FDECEA · 成功块 #E8F5EC · 表头深蓝白字+斑马纹
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = r'C:\Users\ZhuanZ\Desktop\网安报告\项目三 资产梳理报告\日志智能分析流水线_设计思路与代码执行流程_教学文档.docx'

DARK = RGBColor(0x1A, 0x2E, 0x4B)      # 深蓝主色
BODY = RGBColor(0x33, 0x33, 0x33)
GRAY = RGBColor(0x55, 0x55, 0x55)

doc = Document()

# ---------- 页面 ----------
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.5)
sec.top_margin = sec.bottom_margin = Cm(2.5)

# ---------- 默认样式 ----------
style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
style.paragraph_format.line_spacing = 1.3


def _shade(paragraph, color):
    """段落底纹"""
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), color)
    pPr.append(shd)


def _cell_shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)


def set_font(run, size=11, bold=False, color=BODY, mono=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = 'Consolas' if mono else 'Arial'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')


def H1(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_font(r, 16, True, DARK)
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    # 下边框线
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single'); bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:color'), '1A2E4B')
    pbdr.append(bottom)
    pPr.append(pbdr)
    return p


def H2(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_font(r, 14, True, DARK)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    return p


def H3(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_font(r, 12, True, RGBColor(0x2D, 0x5F, 0x8A))
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    return p


def P(text, indent=True, size=11):
    p = doc.add_paragraph()
    r = p.add_run(text)
    set_font(r, size)
    p.paragraph_format.first_line_indent = Pt(22) if indent else Pt(0)
    p.paragraph_format.space_after = Pt(4)
    return p


def BLOCK(text, color, title=None, size=10.5):
    """色块段落：title 加粗置首"""
    p = doc.add_paragraph()
    if title:
        r1 = p.add_run(title + '　')
        set_font(r1, size, True, BODY)
    r = p.add_run(text)
    set_font(r, size)
    p.paragraph_format.left_indent = Pt(4)
    p.paragraph_format.right_indent = Pt(4)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    _shade(p, color)
    return p


def CODE(text):
    """命令/代码块：等宽字体+灰底，保留换行"""
    for i, line in enumerate(text.rstrip('\n').split('\n')):
        p = doc.add_paragraph()
        r = p.add_run(line if line else ' ')
        set_font(r, 10, mono=True, color=RGBColor(0x20, 0x20, 0x20))
        p.paragraph_format.left_indent = Pt(6)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        if line.strip().startswith('#'):
            set_font(r, 10, mono=True, color=RGBColor(0x2E, 0x7D, 0x32))
        _shade(p, '#F2F2F2')
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(2)


def OUT(text):
    """输出块：浅底+等宽，灰字"""
    for line in text.rstrip('\n').split('\n'):
        p = doc.add_paragraph()
        r = p.add_run(line if line else ' ')
        set_font(r, 9.5, mono=True, color=GRAY)
        p.paragraph_format.left_indent = Pt(6)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.1
        _shade(p, '#F7F7F7')
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(2)


def TABLE(headers, rows, widths=None, size=9.5):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.text = ''
        r = cell.paragraphs[0].add_run(h)
        set_font(r, size, True, RGBColor(0xFF, 0xFF, 0xFF))
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        _cell_shade(cell, '1A2E4B')
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            cell = t.rows[i + 1].cells[j]
            cell.text = ''
            r = cell.paragraphs[0].add_run(str(v))
            set_font(r, size, color=BODY)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER if len(str(v)) < 12 else WD_ALIGN_PARAGRAPH.LEFT
            if i % 2 == 1:
                _cell_shade(cell, 'F2F2F2')
    if widths:
        for j, w in enumerate(widths):
            for row in t.rows:
                row.cells[j].width = Cm(w)
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(2)
    return t


# ==================== 封面 ====================
for _ in range(3):
    doc.add_paragraph()
p = doc.add_paragraph(); r = p.add_run('日志智能分析流水线')
set_font(r, 26, True, DARK)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

p = doc.add_paragraph(); r = p.add_run('设计思路与代码执行流程')
set_font(r, 20, True, DARK)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

p = doc.add_paragraph()
r = p.add_run('—— 蜜罐服务器日志结构化解析 · 统计分析 · 机器学习异常检测 · 可视化 ——')
set_font(r, 11, False, GRAY)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

for _ in range(2):
    doc.add_paragraph()

TABLE(['项目', '内容'], [
    ['文档类型', '教学讲义（技术培训材料）'],
    ['配套项目', '项目三 · 公网蜜罐诱捕服务器日志分析工具'],
    ['数据源主机', '47.243.223.221（阿里云香港 ECS / Ubuntu 26.04）'],
    ['日志范围', '/var/log/auth.log（9321 行）+ /var/log/nginx/access.log（2416 行）'],
    ['解析结果', '11612 条结构化记录 · 200 个来源 IP · 30 条登录会话'],
    ['工具版本', 'v1.0（M1 增量解析 + M2 会话聚合与特征 + M3 ML 分析与报告）'],
    ['文档版本', 'v1.0'],
], widths=[4.5, 11.5])

doc.add_page_break()

# ==================== 第 1 章 ====================
H1('第 1 章　文档说明与阅读指南')

H2('1.1 文档目的')
P('本教学文档完整讲解一套"日志智能分析流水线"的设计思路与代码执行流程。该流水线服务于公网蜜罐服务器'
  '（47.243.223.221）的日志分析任务：将 sshd 认证日志与 nginx 访问日志从"大量重复、难以阅读的原始文本"'
  '转化为"结构化、可统计、可机器学习判定、可可视化呈现"的安全情报。')
BLOCK('读者定位：安全方向学生、安全运营入门人员，或希望用 Python 自建日志分析工具的安全工程师。'
      '文档不假设读者有安全分析经验，但需要具备 Python 基础语法、CSV/正则基本认知、以及 SSH 登录服务器的基本操作能力。',
      '#FFF6E5', '要点', 10.5)

H2('1.2 前置知识')
TABLE(['知识项', '要求', '用途'], [
    ['Python 基础', '函数、字典、列表、文件读写', '读懂全部代码'],
    ['正则表达式', '命名分组 (?P<name>...)', '理解日志模板解析'],
    ['CSV 概念', '表头 + 数据行', '理解各中间产物'],
    ['SSH/日志常识', 'auth.log 的认证事件、nginx access log 格式', '理解数据来源'],
    ['机器学习基础（可选）', '无监督异常检测概念', '理解第 5.6 节'],
], widths=[4.0, 6.5, 5.5])

H2('1.3 阅读路径建议')
P('本文档按"先思路、后代码、再实测"组织，建议顺序阅读：', indent=False)
P('① 第 2 章：理解要解决什么问题（原始日志为什么难读）')
P('② 第 3 章：理解六个核心设计决策（为什么这样设计，含时间戳方案的对比）')
P('③ 第 4 章：建立工程全貌（文件结构、数据流转）')
P('④ 第 5 章：逐模块精读代码（每节 = 设计思路 + 关键代码 + 逐行讲解 + 输出样例）')
P('⑤ 第 6 章：看真实运行结果与开发中踩过的三个坑')
P('⑥ 第 7 章：扩展方向与思考题')
BLOCK('本文档所有代码、数据、运行输出均来自真实执行，无虚构内容。代码文件位于配套工程目录'
      'log_analyzer\\，完整文件索引见附录 A。', '#EAF0F8', '目的', 10.5)

# ==================== 第 2 章 ====================
H1('第 2 章　项目背景与需求分析')

H2('2.1 痛点：原始日志为什么"看得难受"')
P('公网服务器每天被全球扫描器持续探测。仅 2026-09-04 至 09-05 两天，auth.log 就记录了 9321 行，'
  '其中绝大多数是同一类内容：')
CODE('2026-09-05T11:08:08.371158+08:00 mcstart sshd-session[46343]: Connection closed by 108.95.165.39 port 49228 [preauth]\n'
     '2026-09-05T11:00:17.149527+08:00 mcstart sshd-session[46070]: Connection closed by 190.46.212.56 port 54908')
P('这行日志的含义：某 IP 在未完成认证（preauth）阶段就断开了连接——这是端口扫描器的典型指纹。'
  '仅 108.95.165.39 一个 IP 就贡献了 8747 条此类记录，占全部日志的 75%。')
BLOCK('痛点本质：不是"日志太多"，而是"有效信息被淹没"。9321 行里真正有安全价值的行不到 5%，'
      '其余都是同一攻击模式的重复变体。人工翻看既无法统计全貌，也无法及时识别新增攻击源。',
      '#FDECEA', '痛点', 10.5)

H2('2.2 需求拆解')
P('用户最初提出五步设想，本流水线将其升级为七模块实现：', indent=False)
TABLE(['用户设想', '流水线实现', '升级点'], [
    ['清洗大量重复内容', '① 增量读取 + ② 模板解析 + ③ 标准化', '由"删除"升级为"归类"，信息不丢失'],
    ['清洗成功登录日志', '④ 会话聚合（PID 串联）', '成功登录不删除，还原为完整会话链'],
    ['杂乱进程分类统计', '② 动态提取进程类型', '进程名不写死，自动归纳'],
    ['格式化与分类统计', '③ 标准化 + ⑤ 特征工程', '16 维特征为 ML 提供输入'],
    ['机器学习分析出总表', '⑥ 规则引擎 + 无监督 ML 融合', '规则可解释打底，ML 补充离群'],
    ['网页呈现', '⑦ ECharts 静态报告', '浏览器直接打开，无需服务端'],
], widths=[4.5, 6.5, 5.0])

H2('2.3 设计目标：四原则')
BLOCK('① 增量可续：日志文件不断增长，每次运行只读新增部分，断点持久化，重启不丢不重。', '#EAF0F8', '原则一', 10.5)
BLOCK('② 规则可配：日志格式 → 字段映射全部写在 rules.yaml，新增日志源只改配置不改代码。', '#EAF0F8', '原则二', 10.5)
BLOCK('③ 可解释优先：规则引擎给出明确判定依据（如"SSH 端口扫描器，探测 8770 条"），ML 只做补充，不替代人工判断。', '#EAF0F8', '原则三', 10.5)
BLOCK('④ 数据不丢：任何解析不了的行进入"未知类"单独落盘，绝不静默丢弃。', '#EAF0F8', '原则四', 10.5)

# ==================== 第 3 章 ====================
H1('第 3 章　总体设计思路')

H2('3.1 七模块流水线总览')
TABLE(['模块', '文件名', '核心职责', '输入 → 输出'], [
    ['① 增量读取', 'log_reader.py', '按物理游标续读日志新增行', '日志文件 → 新增行流'],
    ['② 模板解析', 'parser.py', '正则模板拆字段，动态提取进程/事件', '行文本 → 结构化字段'],
    ['③ 标准化', 'parser.py', '时间归一、字段整理、未知类兜底', '字段 → parsed.csv'],
    ['④ 会话聚合', 'sessionizer.py', '按 PID 串联登录事件为会话', 'parsed.csv → sessions.csv'],
    ['⑤ 特征工程', 'features.py', '按 IP 聚合 16 维统计特征', 'parsed.csv → features.csv'],
    ['⑥ 规则+ML', 'analyzer.py', '规则打底 + 无监督异常检测融合', 'features.csv → analysis.csv'],
    ['⑦ 可视化', 'report.py', '聚合总表 + ECharts 图表', 'csv 数据 → report.html'],
], widths=[2.2, 3.2, 5.0, 5.6])

H2('3.2 设计决策①：结构化解析，而非删除式清洗')
P('用户最初的设想是"清洗掉大量重复内容"。本方案将其改为"结构化解析"：每条日志用正则模板拆成'
  '时间戳、主机、进程、PID、事件类型、来源 IP、端口、用户、标签等字段。')
BLOCK('为什么？清洗=删除，删除=丢失证据。扫描器的 8747 条 Connection closed 虽然重复，但它是攻击源画像'
      '的原材料——统计"谁在扫、扫了多久、频率多高"全靠它。归类到 CONN_CLOSED 事件后，它既能被压缩成'
      '一条统计（8770 条），又能随时按 IP 还原明细。', '#EAF0F8', '设计逻辑', 10.5)

H2('3.3 设计决策②：inode+偏移游标，而非时间戳')
P('用户提议"用时间戳作为读取边界，下次只读时间戳之后的新日志"。该方案看似简单，但有四个致命缺陷：')
TABLE(['时间戳方案的缺陷', '后果'], [
    ['时间戳是内容而非位置', '游标必须是文件中的物理位置，否则无法定位'],
    ['日志可能乱序到达', 'rsyslog 批量刷盘、远程日志延迟都会导致后写的时间戳更小，会漏读'],
    ['时间可能倒退', 'NTP 校时、时区切换、攻击者篡改，都会让时间戳回退'],
    ['多文件时间线不统一', 'auth.log 与 nginx 日志时间精度不同，无法共用单一游标'],
], widths=[7.0, 9.0])
P('正确方案是业界标准（filebeat / logstash sincedb 同款）：记录文件的 (设备号, inode) 与字节偏移量 offset。', indent=False)
BLOCK('① 正常追加：inode 不变，seek(offset) 从上次位置续读；\n'
      '② 文件被截断（size < offset）：日志被 copytruncate 轮转清空，回退从 0 重读；\n'
      '③ 文件被轮转（inode 改变）：logrotate 改名生成了新文件，从 0 读新文件。\n'
      '游标持久化到 data/.log_cursor.json，进程重启后依然有效。', '#EAF0F8', '三种场景', 10.5)

H2('3.4 设计决策③：进程/事件名动态提取，零硬编码')
P('日志中的进程形如 sshd-session[46343]，其中 46343 是 PID（进程号），每次连接都不同。'
  '若把进程名写死，每次连接都会生成新的"类型"，统计会彻底碎片化。')
CODE('提取逻辑：取方括号前的部分作为进程类型，方括号内为 PID\n'
     'sshd-session[46343]  →  进程类型: sshd-session，PID: 46343\n'
     'systemd-logind[1129]  →  进程类型: systemd-logind，PID: 1129')
BLOCK('同一思路用于事件类型：从消息正文中匹配 Accepted / Failed / Invalid / Connection closed 等关键词，'
      '映射为 LOGIN_SUCCESS / LOGIN_FAILED / CONN_CLOSED 等标准事件名。进程与事件都是动态归纳，'
      '新增日志格式不需要改代码。', '#EAF0F8', '设计逻辑', 10.5)

H2('3.5 设计决策④：未知类兜底，绝不静默丢弃')
P('实际日志中总有模板覆盖不到的行（服务启动日志、审计消息、异常格式）。这些行统一标记为 UNKNOWN 事件，'
  '单独落盘到 unknown.log。')
BLOCK('本次实测 11737 行中有 153 条未知类（占 1.3%），多为 sshd 启动、系统按钮事件、sudo 审计等。'
      '它们被完整保留，可随时人工复核或补充规则模板。', '#EAF0F8', '实测', 10.5)

H2('3.6 设计决策⑤：规则 + ML 双层判定')
P('单用机器学习有一个致命问题：模型给出"异常分数"却无法回答"为什么"。单用规则又无法覆盖未知攻击模式。'
  '本方案采用双层融合：')
BLOCK('第一层 规则引擎（强证据，可解释，秒级）：扫描器指纹（探测占比≥95% 且量≥500）、敏感文件扫描'
      '（HTTP 404 占比≥90%）、爆破（失败次数≥5）、攻击链组合。规则给出明确依据字符串。\n'
      '第二层 无监督 ML（Isolation Forest + DBSCAN）：在标准化特征上找统计离群点，补充规则未覆盖的异常。\n'
      '融合规则：规则强证据 > ML；规则判定正常但 ML 离群 → 升级为"可疑待复核"。白名单 IP 永久豁免。',
      '#EAF0F8', '融合逻辑', 10.5)

H2('3.7 设计决策⑥：规则配置化 rules.yaml')
P('所有日志源与正则模板集中在 rules.yaml。新增一个日志源只需：声明 source（名称+路径+类型），'
  '在 patterns 下添加正则与事件名。解析器代码零改动。')

doc.add_page_break()

# ==================== 第 4 章 ====================
H1('第 4 章　工程结构与数据流')

H2('4.1 目录结构')
CODE('log_analyzer/\n'
     '├── main.py              # M1 调度：增量读取 → 解析 → parsed.csv → 统计\n'
     '├── run_m2.py            # M2 调度：会话聚合 + 特征工程 + 画像展示\n'
     '├── rules.yaml           # 规则库：日志格式 → 字段映射模板\n'
     '├── log_reader.py        # ① 增量读取器（inode+偏移游标）\n'
     '├── parser.py            # ②③ 模板解析 + 标准化（动态提取 + 未知兜底）\n'
     '├── sessionizer.py       # ④ 会话聚合（PID 串联）\n'
     '├── features.py          # ⑤ 特征工程（16 维 IP 画像）\n'
     '├── analyzer.py          # ⑥ 规则引擎 + IsolationForest/DBSCAN\n'
     '├── report.py            # ⑦ ECharts 网页报告\n'
     '├── data/\n'
     '│   ├── logs/            # 原始日志（从服务器拉取）\n'
     '│   ├── parsed.csv       # 结构化事件表（11612 条）\n'
     '│   ├── sessions.csv     # 登录会话表（30 条）\n'
     '│   ├── features.csv     # IP 特征表（200 行 × 16 维）\n'
     '│   ├── analysis.csv     # 标注结果表（normal/suspect/malicious）\n'
     '│   ├── unknown.log      # 未知类兜底文件\n'
     '│   └── .log_cursor.json # 增量游标状态\n'
     '└── output/report.html   # 最终可视化报告')

H2('4.2 数据流转链')
BLOCK('原始日志(auth.log / nginx access.log)\n'
      '  → [① 增量读取] 新增行流\n'
      '  → [② 模板解析] 结构化字段\n'
      '  → [③ 标准化] parsed.csv（事件明细，无限追加）\n'
      '  → [④ 会话聚合] sessions.csv（登录行为链）\n'
      '  → [⑤ 特征工程] features.csv（IP 画像）\n'
      '  → [⑥ 规则+ML] analysis.csv（异常标注）\n'
      '  → [⑦ 可视化] report.html（最终交付）', '#FFF6E5', '数据流', 10.5)

H2('4.3 各产物职责')
TABLE(['产物', '粒度', '用途'], [
    ['parsed.csv', '一行一事件', '明细证据，可追溯任意一条原始日志'],
    ['sessions.csv', '一行一会话', '还原攻击者从登录到退出的行为链'],
    ['features.csv', '一行一 IP', 'ML 输入，攻击源画像'],
    ['analysis.csv', '一行一 IP', '判定结果 + 依据 + ML 分数'],
    ['report.html', '一页一报告', '面试/汇报展示，浏览器直接打开'],
], widths=[3.5, 3.5, 9.0])

# ==================== 第 5 章 ====================
H1('第 5 章　模块详解与代码执行流程')

# ----- 5.1 rules.yaml -----
H2('5.1 rules.yaml：规则库（模板化的核心）')
H3('5.1.1 设计思路')
P('规则库是解析器的"字典"。每条规则 = 正则模板 + 事件类型 + 字段映射。正则使用命名分组 '
  '(?P<ip>...) 直接声明字段名，解析器无需知道每条日志的具体格式。')
H3('5.1.2 关键片段讲解')
CODE('patterns:\n'
     '  auth:                    # auth.log 的事件规则组\n'
     '    - name: sshd_accepted_password\n'
     '      desc: SSH 密码认证登录成功\n'
     '      regex: \'Accepted password for (?P<user>\\S+) from (?P<ip>[0-9a-fA-F:.]+) port (?P<port>\\d+)\'\n'
     '      event: LOGIN_SUCCESS\n'
     '    - name: sshd_conn_closed\n'
     '      desc: SSH 连接关闭（扫描器 preauth 特征）\n'
     '      regex: \'Connection closed by (?P<ip>[0-9a-fA-F:.]+) port (?P<port>\\d+)(?P<tag>.*)\'\n'
     '      event: CONN_CLOSED')
BLOCK('正则用单引号包裹（YAML 规则），内部单引号用两个单引号转义。如果误用双引号包裹正则，'
      'YAML 会把 \\d 当作转义符报错——这是本次开发踩到的第一个坑，详见 6.4 节。', '#FDECEA', '易错点', 10.5)

# ----- 5.2 log_reader.py -----
H2('5.2 log_reader.py：增量读取器')
H3('5.2.1 设计思路')
P('增量读取的本质：记录"上次读到哪"，下次从那里继续。文件可能被追加、被截断、被轮转，'
  '三种情况对应三种游标策略（见 3.3 节）。状态以 JSON 持久化，异常时宁可重复也不漏报。')
H3('5.2.2 核心代码逐行讲解')
CODE('# 正常追加：inode 相同且 size >= offset → seek(offset) 续读\n'
     '# 截断重读：offset > size → 文件被清空过 → 回退从 0\n'
     '# 轮转重读：key(inode) 变了 → 新文件从 0 读\n'
     'st = os.stat(file_path)\n'
     "key = '%d:%d' % (st.st_dev, st.st_ino)     # 设备号+inode 唯一标识文件本体\n"
     "if last.get('key') != key:                  # 无记录(首次) 或 文件被轮转\n"
     "    offset = 0 if first_mode == 'full' else st.st_size\n"
     "elif last.get('offset', 0) > st.st_size:    # 文件被截断(copytruncate)\n"
     "    offset, full = 0, True\n"
     'else:                                       # 正常追加\n'
     "    offset = last.get('offset', 0)\n"
     'with open(file_path, "rb") as f:\n'
     '    f.seek(offset)                          # 跳到上次读到的字节位置\n'
     '    lines = [raw.decode("utf-8", "replace") for raw in f]  # 只读新增\n'
     'state[source_key] = {"key": key, "offset": st.st_size, ...}  # 更新游标')
BLOCK('游标记录的 offset 不是行号而是字节偏移（st.st_size），因为行号在截断/轮转后会错位，'
      '字节偏移是文件系统层面的物理事实，永远准确。', '#EAF0F8', '设计逻辑', 10.5)
H3('5.2.3 三连验证（实测记录）')
P('第一次（首次全量）：读取 9321 + 2416 = 11737 行。', indent=False)
OUT('[auth] data/logs/auth.log 新增 9321 行（全量首次读取）\n[nnginx] data/logs/nginx_access.log 新增 2416 行（全量首次读取）')
P('第二次（空跑，文件未变）：读取 0 行——游标生效。', indent=False)
OUT('[auth] data/logs/auth.log 新增 0 行（增量读取）\n[nginx] data/logs/nginx_access.log 新增 0 行（增量读取）')
P('第三次（从服务器重新拉取日志后）：只读新增的 30 行，历史零重复。', indent=False)
OUT('[auth] data/logs/auth.log 新增 30 行（增量读取）\n[nginx] data/logs/nginx_access.log 新增 0 行（增量读取）')
BLOCK('三次运行证明：首次全量建底、空跑零读、增量只读新增。游标机制完整可用。', '#E8F5EC', '验证通过', 10.5)

# ----- 5.3 parser.py -----
H2('5.3 parser.py：模板解析与标准化')
H3('5.3.1 设计思路')
P('解析器先统一提取行头（时间戳/主机/进程/PID），再用规则库逐条匹配消息正文。'
  '进程从行头动态拆解，事件从正文匹配，未命中归入 UNKNOWN。')
H3('5.3.2 核心代码讲解')
CODE('# 行头正则：时间 主机 进程[PID]: 消息\n'
     "_LINE_HEAD = re.compile(r'^(\\S+) (\\S+) (\\S+?)(?:\\[(\\d+)\\])?: (.*)$')\n"
     'm = _LINE_HEAD.match(line)\n'
     'ts, host, proc, pid, msg = m.groups()   # 进程/PID 自动拆解\n'
     '# 进程名动态提取：sshd-session[46343] → proc=sshd-session, pid=46343\n'
     '# 事件匹配：遍历该源的规则，命中即提取字段\n'
     'for pat in patterns:\n'
     '    m = pat["regex"].search(head["msg"])\n'
     '    if m:\n'
     '        rec["event"] = pat["event"]       # 事件类型\n'
     '        g = m.groupdict()\n'
     "        rec['ip'], rec['user'], rec['port'] = g.get('ip'), g.get('user'), g.get('port')\n"
     '        break\n'
     'if rec["event"] is None:                  # 兜底：未知类\n'
     '    rec["event"] = "UNKNOWN"\n'
     '    rec["detail"] = head["msg"][:80]')
P('解析结果示例（parsed.csv 中的一行）：', indent=False)
OUT('CONN_CLOSED → {ts: 2026-09-04T10:54:16+08:00, proc: sshd-session, pid: 1353,\n'
    '                ip: 108.95.165.39, port: 56260, tag: [preauth]}\n'
    'LOGIN_SUCCESS → {ts: 2026-09-04T11:03:07+08:00, proc: sshd-session, pid: 1851,\n'
    '                 user: root, ip: 106.61.42.246, port: 44746}')

# ----- 5.4 sessionizer.py -----
H2('5.4 sessionizer.py：会话聚合')
H3('5.4.1 设计思路')
P('单条"登录成功"只是瞬间事件，攻击者真正有价值的行为发生在登录之后。会话聚合把同一 PID 上的事件'
  '串联成完整会话：LOGIN_SUCCESS（开始）→ 后续的 SESSION_CLOSED / DISCONNECT / CONN_CLOSED（结束），'
  '算出会话时长。')
BLOCK('为什么按 PID？sshd 为每次 SSH 连接创建一个独立进程（sshd-session[PID]），PID 是天然的唯一键。'
      '同一个 PID 上不会出现第二个人的会话，按 PID 串联不会串线。', '#EAF0F8', '设计逻辑', 10.5)
H3('5.4.2 核心代码讲解')
CODE('# 按 PID 分组 auth 事件\n'
     'by_pid = {}\n'
     "for r in rows:\n"
     "    by_pid.setdefault(r['pid'], []).append(r)\n"
     '# 无 LOGIN_SUCCESS 的 PID = 纯探测连接（扫描器），只计数\n'
     '# 有 LOGIN_SUCCESS 的 PID：每次登录开一个会话\n'
     'evs_sorted = sorted(evs, key=lambda e: parse_ts(e[\'ts\']) or datetime.min)\n'
     'for le in logins:\n'
     "    t0 = parse_ts(le['ts'])                 # 会话开始\n"
     '    end_ts = None\n'
     '    for later in evs_sorted:\n'
     "        if later['event'] in ('SESSION_CLOSED', 'DISCONNECT', 'CONN_CLOSED'):\n"
     '            end_ts = parse_ts(later[\'ts\']); break   # 最近结束事件\n'
     "    dur = round((end_ts - t0).total_seconds(), 1)     # 会话时长\n"
     "    method = 'password' if 'Accepted password' in raw else 'publickey' ...")
H3('5.4.3 实测输出')
OUT('pid    user     ip               method  duration   login_time           logout_time\n'
    '1851   root     106.61.42.246    password 11.8s      2026-09-04T11:03:07  2026-09-04T11:03:19\n'
    '3080   root     106.61.42.246    password 8105.7s    2026-09-04T11:27:45  2026-09-04T13:42:51\n'
    '…共 30 条登录会话')
BLOCK('重要结论：30 条会话全部来自白名单 IP（本机运维），deploy 诱饵用户目前零真实攻击者成功登录——'
      '诱捕体系完整有效，未失守。', '#E8F5EC', '实测结论', 10.5)

# ----- 5.5 features.py -----
H2('5.5 features.py：特征工程')
H3('5.5.1 设计思路')
P('特征工程把"事件明细"压缩为"IP 画像"。每个来源 IP 一行，16 个特征分四组：')
TABLE(['特征组', '特征', '安全含义'], [
    ['总量类', 'total_events / probe_conn / login_failed / login_success / http_requests / http_404', '活动规模'],
    ['比例类', 'fail_rate（失败率）/ probe_ratio（探测占比）', '攻击模式：扫描器探测占比≈100%，爆破失败率高'],
    ['多样性', 'unique_users / unique_ports / unique_paths', '探测广度：爆破会尝试多用户名'],
    ['时间类', 'time_span_h / events_per_h / active_hours', '持续性与频率：扫描器 24h 在线'],
], widths=[2.0, 7.5, 6.5])
BLOCK('特征设计原则：为 ML 准备的每个特征都必须有安全语义，能从特征值直接反推攻击行为。'
      '例如 probe_ratio=1.00 且 probe_conn=8770 → 纯 SSH 端口扫描器。', '#EAF0F8', '设计逻辑', 10.5)
H3('5.5.2 核心代码讲解')
CODE('# 按 IP 分组后逐维度统计\n'
     "by_ip = {}\n"
     "for r in rows:\n"
     "    by_ip.setdefault(r['ip'] or '', []).append(r)\n"
     "probe   = sum(1 for e in evs if e['event'] == 'CONN_CLOSED')\n"
     "failed  = sum(1 for e in evs if e['event'] in ('LOGIN_FAILED', 'AUTH_FAILURE', ...))\n"
     "success = sum(1 for e in evs if e['event'] == 'LOGIN_SUCCESS')\n"
     "# 攻击链特征：探测+失败+成功同时出现 = 完整攻击流程\n"
     "attack_chain = 1 if (probe > 0 and failed > 0 and success > 0) else 0\n"
     "# 事件频率：总事件数 / 时间跨度（小时）\n"
     "events_per_h = round(total / span_h, 2) if span_h > 0 else total")

# ----- 5.6 analyzer.py -----
H2('5.6 analyzer.py：规则引擎 + 无监督 ML 融合')
H3('5.6.1 设计思路')
P('两层判定：规则引擎给出可解释的强证据判定，ML 在标准化特征上找统计离群点。融合时规则优先，'
  'ML 只负责"规则说正常但统计上很怪"的兜底。白名单 IP（运维本机）永久豁免。')
H3('5.6.2 规则引擎核心逻辑')
CODE('# 规则 1：纯 SSH 端口扫描器\n'
     "if probe >= 500 and probe_ratio >= 0.95:\n"
     "    return 'malicious', 'SSH 端口扫描器（探测 %d 条，占比 %.0f%%）'\n"
     "# 规则 2：Web 目录/敏感文件扫描\n"
     "if http >= 100 and http404 / http >= 0.9:\n"
     "    return 'malicious', 'Web 目录/敏感文件扫描（HTTP %d 条，404 占比 %.0f%%）'\n"
     "# 规则 3：SSH 爆破\n"
     "if failed >= 5 and success == 0:\n"
     "    return 'suspect', 'SSH 爆破尝试（失败 %d 次）'\n"
     "# 规则 4：完整攻击链\n"
     "if attack_chain and ip not in WHITELIST:\n"
     "    return 'suspect', '完整攻击链特征（探测+失败+成功）'")
H3('5.6.3 ML 融合逻辑')
CODE('# 标准化 + 两种无监督算法\n'
     'Xs = StandardScaler().fit_transform(X)          # 特征标准化（去量纲）\n'
     'iso_l = IsolationForest(contamination=0.08).fit_predict(Xs)  # 孤立森林\n'
     'db_l  = DBSCAN(eps=1.6, min_samples=3).fit_predict(Xs)       # 密度聚类\n'
     '# 任一算法判为离群 → ML 异常\n'
     "ml_abn = iso_l[i] == -1 or db_l[i] == -1\n"
     '# 融合：白名单豁免；规则 normal 但 ML 离群 → 升级 suspect 待复核\n'
     "if ip in WHITELIST: label = 'normal'\n"
     "elif label == 'normal' and ml_label == 'anomaly': label = 'suspect'")
BLOCK('为什么选无监督？真实攻击样本稀缺，无法标注训练集。Isolation Forest 随机切分找孤立点、'
      'DBSCAN 找密度离群，两者互补且无需标签。', '#EAF0F8', '设计逻辑', 10.5)
H3('5.6.4 实测标注结果')
OUT('[analyzer] 标注完成：{\'malicious\': 3, \'suspect\': 13, \'normal\': 184}\n'
    '[malicious] 108.95.165.39    事件8770  | SSH 端口扫描器（探测 8770 条，占比 100%）\n'
    '[malicious] 213.209.159.175  事件1294  | Web 目录/敏感文件扫描（HTTP 1294 条，404 占比 99%）\n'
    '[malicious] 34.96.49.66      事件778   | Web 目录/敏感文件扫描（HTTP 778 条，404 占比 98%）')
BLOCK('开发中发现的第三个坑：白名单 IP（106.61.42.246）因运维操作特征量大被 ML 误标为可疑。'
      '修复：白名单判定置于融合逻辑最前，权限最高。修复后标注变为恶意 3 / 可疑 11 / 正常 186。',
      '#FDECEA', '坑三', 10.5)

# ----- 5.7 report.py -----
H2('5.7 report.py：ECharts 网页报告')
H3('5.7.1 设计思路')
P('报告为单文件静态 HTML，内嵌 ECharts CDN，浏览器直接打开。五块内容：概览卡片（总事件/来源 IP/'
  '恶意/可疑/成功登录）、事件类型饼图、24 小时时间线折线图、Top IP 横向柱状图、异常 IP 标注总表。')
H3('5.7.2 关键实现')
CODE('# 数据注入：把统计结果 JSON 序列化嵌入 HTML\n'
     "html = TEMPLATE % (now, total, src, mal, susp, login, rows_tbl,\n"
     "                   json.dumps({'ev': ev_dist, 'tl': timeline, 'topIp': top_ip}))\n"
     '# ECharts 图表：饼图/折线/柱状各一个 option\n'
     "# series:[{type:'pie', radius:['30%%','62%%'], data:D.ev}]\n"
     "# series:[{type:'line', smooth:true, data:D.tl.probe}]\n"
     "# series:[{type:'bar', data:D.topIp}]")
BLOCK('开发中踩到的第二个坑：HTML 模板内 CSS 的 width:100% 与 Python % 格式化冲突，'
      '报 unsupported format character。修复：字面 % 全部转义为 %%。详见 6.4 节。', '#FDECEA', '坑二', 10.5)

doc.add_page_break()

# ==================== 第 6 章 ====================
H1('第 6 章　全流程执行与实测结果')

H2('6.1 运行命令序列')
CODE('# M1：增量读取 + 解析 + 标准化 + 统计\n'
     'python main.py\n'
     '# M2：会话聚合 + 特征工程 + 攻击源画像\n'
     'python run_m2.py\n'
     '# M3：规则+ML 标注 + 网页报告\n'
     'python analyzer.py\n'
     'python report.py\n'
     '# 浏览器打开最终报告\n'
     'output/report.html')

H2('6.2 增量读取三连验证')
TABLE(['轮次', '操作', '读取行数', '验证点'], [
    ['第 1 次', '首次运行（全量建底）', '11737（9321+2416）', '全量解析成功'],
    ['第 2 次', '立即空跑（文件未变）', '0', '游标生效，不重复读'],
    ['第 3 次', '重新拉取服务器日志', '30（仅 auth 新增）', '增量只读新增，历史零重复'],
], widths=[2.0, 5.5, 5.0, 3.5])

H2('6.3 实测攻击源画像')
P('基于 11612 条结构化记录，200 个来源 IP 被分为三类：', indent=False)
TABLE(['判定', '来源 IP', '画像', '关键证据'], [
    ['恶意', '108.95.165.39', 'SSH 端口扫描器', '8770 条 preauth 探测，占比 100%，持续 24.7h'],
    ['恶意', '213.209.159.175', '敏感文件扫描器', '1294 条 .env/.aws/config 枚举，404 占 99%'],
    ['恶意', '34.96.49.66', 'Web 目录爆破器', '778 条随机 hash 路径探测'],
    ['可疑', '11 个 IP', 'ML 离群', '低频异常行为，分数 0.44-0.68'],
    ['正常', '186 个 IP', '无异常行为', '白名单豁免 2 个运维本机'],
], widths=[2.0, 3.2, 3.5, 7.3])
BLOCK('安全结论：所有敏感文件探测（.env/.aws/config）均返回 404/403，官网诱饵无真实泄露；'
      'deploy 诱饵用户零成功登录，诱捕体系完整未失守。', '#E8F5EC', '结论', 10.5)

H2('6.4 开发中三个问题的定位与修复（教学价值）')
H3('问题 1：YAML 正则转义错误')
P('现象：解析 rules.yaml 报 yaml.scanner.ScannerError: found unknown escape character。', indent=False)
P('定位：YAML 中正则若用双引号包裹，\\d 会被当作转义符。')
P('修复：全部改为单引号包裹；正则内的单引号用双单引号转义（如 New session \'\'...\'\'）。')
H3('问题 2：HTML 模板 % 格式化冲突')
P('现象：生成报告报 ValueError: unsupported format character。', indent=False)
P('定位：CSS 的 width:100% 与 Python 字符串 % 格式化冲突。')
P('修复：模板中所有字面 % 写成 %%。')
H3('问题 3：白名单 IP 被 ML 误标')
P('现象：运维本机 106.61.42.246 因事件特征量大被判为可疑。', indent=False)
P('定位：ML 只看统计离群，不理解"这是运维人员"的语义。')
P('修复：白名单判定放在融合逻辑最前，权限最高，规则与 ML 均不能越权。')

# ==================== 第 7 章 ====================
H1('第 7 章　扩展方向与进阶练习')

H2('7.1 扩展方向')
BLOCK('① cron 定时自动化：cron 每小时跑 main.py + report.py，报告自动更新（增量游标天然支持，'
      '无需担心重复）。\n'
      '② 部署到服务器端：全部脚本纯标准库 + sklearn，可直接上传服务器运行，从本机拉日志改为服务器本地读。\n'
      '③ 敏感路径规则增强：在规则库中直接加入 /.env、/.git/config、/.aws 的命中即 malicious，'
      '比当前"404 占比间接判定"更精准。\n'
      '④ ttyrec 录像关联：sessions.csv 已保留 PID，可关联 /var/log/ttyrec/ 下的 script 录制文件，'
      '还原攻击者登录后的完整操作录屏。\n'
      '⑤ 实时告警：规则判定 malicious 时触发企业微信 webhook（服务器已具备告警通道）。',
      '#EAF0F8', '扩展', 10.5)

H2('7.2 进阶思考题')
TABLE(['#', '题目', '考察点'], [
    ['1', '为什么游标用字节偏移而不是行号？截断场景下两者有何区别？', '文件系统语义'],
    ['2', '若日志到达乱序，时间戳游标会漏读，inode 游标为什么不会？', '内容 vs 位置'],
    ['3', '为什么规则引擎的判定优先级高于 ML？什么场景下 ML 判定更可信？', '可解释性与误报'],
    ['4', 'DBSCAN 的 eps 参数过大/过小分别会导致什么后果？', '无监督超参'],
    ['5', '如何把会话聚合扩展到 HTTP 侧（用 IP+UA 作为会话键）？', '方案迁移能力'],
], widths=[1.0, 9.0, 6.0])

doc.add_page_break()

# ==================== 附录 A ====================
H1('附录 A　工程文件索引与数据口径')

H2('A.1 文件索引')
CODE('C:\\Users\\ZhuanZ\\Desktop\\网安报告\\_work\\log_analyzer\\\n'
     '  main.py / run_m2.py / rules.yaml / log_reader.py / parser.py\n'
     '  sessionizer.py / features.py / analyzer.py / report.py\n'
     '  data\\logs\\auth.log · nginx_access.log（原始日志）\n'
     '  data\\parsed.csv · sessions.csv · features.csv · analysis.csv · unknown.log\n'
     '  data\\.log_cursor.json（游标）\n'
     '  output\\report.html（报告）')

H2('A.2 数据口径说明')
TABLE(['项目', '口径'], [
    ['日志时间范围', '2026-09-04 至 2026-09-05（服务器时区 UTC+8）'],
    ['auth.log', '9321 行，其中 CONN_CLOSED 8864 行（扫描器指纹）'],
    ['nginx access.log', '2416 行，含 ::1 本机 curl 测试与公网爬虫/扫描'],
    ['结构化记录', '11612 条（9321+2416 中成功解析部分）'],
    ['未知类', '153 条（1.3%），单独落盘 unknown.log'],
    ['登录会话', '30 条，全部来自白名单 IP'],
    ['来源 IP', '200 个，恶意 3 / 可疑 11 / 正常 186'],
], widths=[4.0, 12.0])
BLOCK('本文档全部数据来源于上述真实日志的自动化解析，未做任何人工修饰。'
      '复现方式：下载服务器日志至 data\\logs\\ 后依次运行 main.py → run_m2.py → analyzer.py → report.py。',
      '#FFF6E5', '复现说明', 10.5)

# ==================== 保存 ====================
os.makedirs(os.path.dirname(DOC_PATH), exist_ok=True)
doc.save(DOC_PATH)
print('saved:', DOC_PATH)
