# -*- coding: utf-8 -*-
"""收网篇素材文档：《收网：多漏洞组合扫描器捕获实录》
专栏第 6 篇素材 · 多彩排版（同教学文档规范）
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOC_PATH = r'C:\Users\ZhuanZ\Desktop\网安报告\项目三 资产梳理报告\收网篇_多漏洞组合扫描器捕获实录_136.107.98.147.docx'

DARK = RGBColor(0x1A, 0x2E, 0x4B)
BODY = RGBColor(0x33, 0x33, 0x33)
GRAY = RGBColor(0x55, 0x55, 0x55)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.5)
sec.top_margin = sec.bottom_margin = Cm(2.5)

style = doc.styles['Normal']
style.font.name = 'Arial'
style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
style.paragraph_format.line_spacing = 1.3


def _shade(paragraph, color):
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
    for i, line in enumerate(text.rstrip('\n').split('\n')):
        p = doc.add_paragraph()
        r = p.add_run(line if line else ' ')
        set_font(r, 9.5, mono=True, color=RGBColor(0x20, 0x20, 0x20))
        p.paragraph_format.left_indent = Pt(6)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        if line.strip().startswith('#'):
            set_font(r, 9.5, mono=True, color=RGBColor(0x2E, 0x7D, 0x32))
        _shade(p, '#F2F2F2')
    sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(2)


def OUT(text):
    for line in text.rstrip('\n').split('\n'):
        p = doc.add_paragraph()
        r = p.add_run(line if line else ' ')
        set_font(r, 9, mono=True, color=GRAY)
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
p = doc.add_paragraph(); r = p.add_run('收网：多漏洞组合扫描器捕获实录')
set_font(r, 24, True, DARK)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

p = doc.add_paragraph()
r = p.add_run('专栏第 6 篇素材 · 公网真实攻击数据分析')
set_font(r, 13, False, GRAY)
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

for _ in range(2):
    doc.add_paragraph()

TABLE(['项目', '内容'], [
    ['攻击源 IP', '136.107.98.147'],
    ['攻击时间', '2026-09-05 12:16:17 ~ 12:16:34（共 17 秒）'],
    ['请求总量', '644 条（GET 632 / POST 12）'],
    ['覆盖攻击面', 'SSRF/GraphQL 探测、.env 读取、Vite 路径穿越、AWS 泄露探测、Spring Actuator'],
    ['伪装手段', 'AI 爬虫 UA + 手机 UA 混淆日志分析'],
    ['攻击结果', '全部失败（404/400/301），官网零失守'],
    ['发现途径', '日志智能分析流水线 ⑤特征工程 → ⑥规则+ML 自动标注恶意'],
    ['素材定位', '专栏《公网捕猎》第 6 篇 · 可独立作为面试项目素材'],
], widths=[4.0, 12.0])

doc.add_page_break()

# ==================== 第 1 章 ====================
H1('1　素材概述：为什么要单独成篇')
P('专栏前五篇完成了从资产梳理到诱捕体系搭建，再到日志分析流水线的全部建设。本篇是"收网"：'
  '流水线在 2026-09-05 12:16 捕获到一个此前从未出现的高水平攻击者 136.107.98.147。'
  '它与前两篇记录的普通扫描器有本质区别——携带多个已知漏洞（CVE）的 POC 模板批量打站，'
  '并使用 AI 爬虫 UA 进行反检测伪装。')
BLOCK('本篇价值：①展示日志分析流水线的实际产出（自动从 13219 条日志中捞出恶意 IP）；'
      '②还原一个"专业级"攻击者的完整攻击手法（可面试讲解）；'
      '③用真实数据说明防御方的正确解读方式（200 状态码 ≠ 利用成功）。',
      '#EAF0F8', '本篇价值', 10.5)

# ==================== 第 2 章 ====================
H1('2　攻击者档案')
TABLE(['维度', '数据', '解读'], [
    ['来源 IP', '136.107.98.147', '美国 AS396982（非云厂商常见段）'],
    ['攻击时长', '17 秒（12:16:17→12:16:34）', '爆发式扫描，平均每秒 38 条请求'],
    ['请求总量', '644 条', 'GET 632 / POST 12'],
    ['状态码', '404 ×634 / 200 ×5 / 400 ×4 / 301 ×1', '404 占 98.4%，未命中任何真实漏洞'],
    ['User-Agent', 'ChatGPT-User / GrokBot / Perplexity-User / Claude-User / 手机 UA', 'AI 爬虫 UA 伪装'],
    ['攻击面数量', '≥5 类', 'SSRF、GraphQL、路径穿越、Actuator、AWS 泄露'],
], widths=[2.8, 6.2, 7.0])
BLOCK('自动判定：流水线规则引擎命中"Web 目录/敏感文件扫描（HTTP 644 条，404 占比 98%）"，'
      '自动标注 malicious，无人工干预。', '#E8F5EC', '判定', 10.5)

# ==================== 第 3 章 ====================
H1('3　攻击行为全景拆解')

H2('3.1 时间线：17 秒爆发式探测')
P('644 条请求集中在 17 秒内完成，这是典型的自动化漏洞扫描器行为——不等待响应、不分析结果，'
  '按预设字典高速轰炸。对比 213.209.159.175（1294 条分布在 7 小时），136.107.98.147 的节奏'
  '是"打完就走"，说明它有大量目标要扫，本服务器只是其中一个站点。')
OUT('05/Sep/2026:12:16:17 +0800  开始（GET / 探测站点存活）\n'
    '05/Sep/2026:12:16:19 +0800  GET /?file=../../../../etc/passwd   # 路径穿越尝试\n'
    '05/Sep/2026:12:16:20 +0800  GET /assets../../../.env           # 穿越读 .env\n'
    '05/Sep/2026:12:16:21 +0800  GET /?file=../../.env              # 参数注入变体\n'
    '05/Sep/2026:12:16:28 +0800  GET /%2e%2e/%2e%2e/.env            # URL 编码变体\n'
    '05/Sep/2026:12:16:28 +0800  GET /admin                         # 探测后台\n'
    '05/Sep/2026:12:16:29 +0800  GET /admin/                        # 后台目录确认\n'
    '05/Sep/2026:12:16:34 +0800  结束')

H2('3.2 攻击向量分类统计')
TABLE(['攻击向量', '请求数', '目标/漏洞'], [
    ['读取 .env 配置', '117', 'Laravel/Django/Node 项目的环境变量泄露'],
    ['SSRF / 代理探测', '54', 'POST /fetch、/proxy、/api/fetch、/api/preview'],
    ['AWS 泄露探测', '54', '/__aws_leak_probe_91cbc8c7__ 专用标记'],
    ['Vite 路径穿越', '29', '/@fs/etc/passwd?raw??（CVE-2023-34092）'],
    ['Spring Actuator', '8', '/actuator 端点信息泄露'],
    ['读取 /etc/passwd', '6', '穿越读取系统账号文件'],
    ['后台/应用识别', '8', '/admin、/wp- 等'],
    ['GraphQL 探测', '5', '/graphql、/graphql/console、/api/graphql、/v1/graphql'],
    ['其他变体路径', '366', '随机路径/字典变体（去重后的大类）'],
], widths=[4.5, 2.5, 9.0])

H2('3.3 User-Agent 伪装分析（本篇核心亮点）')
P('该攻击者的 UA 使用策略极具迷惑性，这是它与普通扫描器最本质的区别：', indent=False)
TABLE(['UA 类型', '伪装身份', '目的'], [
    ['ChatGPT-User/1.0', 'OpenAI 官方爬虫', '让日志分析师误判为"AI 搜索爬虫"而忽略'],
    ['GrokBot/1.0', 'xAI 官方爬虫', '同上'],
    ['Perplexity-User/1.0', 'Perplexity 官方爬虫', '同上'],
    ['Claude-User/1.0', 'Anthropic 官方爬虫', '同上'],
    ['Android 手机 UA', 'Pixel 8 / SM-G935R6', '伪装成移动端真实用户访问'],
], widths=[4.5, 5.0, 6.5])
BLOCK('攻击逻辑：搜索引擎爬虫（如 AI 爬虫）访问大量随机路径是"正常"现象，安全人员通常不告警。'
      '攻击者借用这些 UA，让防火墙/日志告警系统把攻击流量当成爬虫放行。'
      '识别突破点：①请求内容完全不符合爬虫行为（爬虫不 POST /fetch、不探测 /@fs/../etc/passwd）；'
      '②同一 IP 在 17 秒内轮换 4+ 种官方爬虫 UA，真实爬虫不会如此高频换身份。',
      '#FDECEA', '伪装逻辑', 10.5)

# ==================== 第 4 章 ====================
H1('4　攻击手法深度还原')

H2('4.1 路径穿越家族（读取敏感文件）')
P('攻击者围绕"路径穿越读取文件"展开多轮变体轰炸，覆盖四种编码形态：', indent=False)
CODE('① 参数注入：   GET /?file=../../../../etc/passwd\n'
     '② 目录拼接：   GET /assets../../../etc/passwd\n'
     '③ 编码绕过：   GET /%2e%2e/%2e%2e/.env        （URL 编码 ..）\n'
     '④ 归一化绕过： GET ////../.env                （nginx 归一化前探测）\n'
     '⑤ 开发框架：   GET /@fs/etc/passwd?raw??      （Vite dev server 特征）')
BLOCK('① 针对存在文件读取参数的 Web 应用；②③④ 针对未正确归一化 ../ 的中间件/框架；'
      '⑤ 是 Vite 开发服务器已知漏洞（CVE-2023-34092）的利用探测，?raw?? 为 Vite 4.2.0 以下的'
      '路径参数触发点。攻击者把"常见漏洞 + 编码变体 + 框架专属漏洞"打包成一套组合拳。',
      '#EAF0F8', '手法讲解', 10.5)

H2('4.2 SSRF / GraphQL 探测')
CODE('POST /fetch          # 通用 SSRF 探测\n'
     'POST /proxy          # 开放代理探测\n'
     'POST /api/fetch      # API 层 SSRF\n'
     'POST /api/preview    # 预览功能 SSRF（Gatsby/Nuxt 特征）\n'
     'POST /graphql        # GraphQL 端点探测\n'
     'POST /graphql/console # GraphQL 交互控制台')
BLOCK('SSRF 探测目的：如果目标应用存在"拉取远程 URL"功能（图片代理、预览、Webhook），攻击者可'
      '借助它访问内网资源（云元数据 169.254.169.254、内网服务）。GraphQL console 探测目的：'
      '发现暴露的 GraphQL 接口后尝试 introspection 查询拿全量 Schema。',
      '#EAF0F8', '手法讲解', 10.5)

H2('4.3 Spring Actuator 与 AWS 泄露探测')
CODE('GET /actuator                       # Spring Boot 监控端点\n'
     'GET /__aws_leak_probe_91cbc8c7__    # AWS 凭据泄露专用探测标记')
BLOCK('/__aws_leak_probe_<随机串>__ 是商业化漏洞扫描框架（如 Nuclei 的 aws-leak 模板）的固定探测'
      '路径——扫描器会先写入一个随机 token，再请求常见泄露路径（/aws/credentials、/.aws/config），'
      '通过回显 token 验证是否存在任意文件读取/SSRF。该随机串是判断"扫描器类型"的关键指纹。',
      '#EAF0F8', '手法讲解', 10.5)

# ==================== 第 5 章 ====================
H1('5　防御验证：为什么攻击全部失败')
H2('5.1 攻击面不存在的根因')
TABLE(['攻击向量', '失败原因'], [
    ['路径穿越读文件', '目标为纯静态官网（HTML/CSS），无文件读取参数、无动态框架，../ 归一化后全部 404'],
    ['SSRF/GraphQL', '无后端 API 服务，POST 端点不存在'],
    ['Vite @fs 穿越', '生产环境为 Nginx + 静态文件，非 Vite dev server'],
    ['Actuator', '无 Spring Boot 应用'],
    ['AWS 泄露', '服务器为阿里云 ECS，无 AWS 凭据文件'],
], widths=[5.0, 11.0])
H2('5.2 200 状态码的正确解读（专业性关键点）')
P('攻击者请求中有 5 条返回 200，极易被误读为"利用成功"：', indent=False)
OUT('GET /                            → 200（首页正常响应）\n'
    'GET /?file=../../../../etc/passwd → 200（参数被忽略，仍返回首页）\n'
    'GET /?file=../../.env             → 200（同上）\n'
    'GET /admin/                       → 200（诱饵后台登录页）')
BLOCK('正确解读：静态站点对未知查询参数直接忽略并返回首页，200 只代表"首页被返回"，'
      '不代表 /etc/passwd 内容被泄露。验证方法：检查响应体长度——正常首页 2017 字节，'
      '若攻击成功响应应包含 "root:x:0:0" 或 env 内容且体积显著变化。'
      '所有 passwd/.env 请求的实际响应均为首页或 404，无任何敏感内容回显。',
      '#FDECEA', '防误判', 10.5)

# ==================== 第 6 章 ====================
H1('6　攻击者对比：三个恶意源的画像差异')
TABLE(['维度', '108.95.165.39', '213.209.159.175', '136.107.98.147'], [
    ['画像', 'SSH 端口扫描器', '敏感文件扫描器', '多漏洞组合扫描器'],
    ['协议', 'SSH(22)', 'HTTP', 'HTTP'],
    ['量级', '9547 条 / 29.5h', '1294 条 / 7.1h', '644 条 / 17s'],
    ['节奏', '持续缓慢', '匀速遍历', '爆发式轰炸'],
    ['UA 伪装', '无', '无', 'AI 爬虫 UA + 手机 UA'],
    ['攻击面', '端口探测', '.env/.aws 枚举', 'SSRF+GraphQL+穿越+Actuator+AWS'],
    ['专业化', '低（脚本小子）', '中（字典枚举）', '高（带 CVE POC 模板）'],
], widths=[2.2, 4.6, 4.6, 4.6])
BLOCK('三个恶意源恰好代表攻击者的三个层次：无脑扫描 → 定向枚举 → 漏洞利用。'
      '136.107.98.147 是三者中唯一具备"利用意识"的攻击者——它不是为了发现开放端口，'
      '而是直接尝试利用已知漏洞拿文件、探内网。', '#FFF6E5', '小结', 10.5)

# ==================== 第 7 章 ====================
H1('7　专栏叙事线建议（可直接采用）')
BLOCK('本篇建议叙事：从流水线自动告警开场（"第 6.2 节部署的 Python 流水线在 12:16 弹出一条'
      '从未见过的告警"）→ 拉取攻击者全量请求 → 逐类拆解攻击手法（读者代入防御视角）→ '
      'UA 伪装反转（"他以为自己是爬虫，日志知道他是谁"）→ 200 状态码陷阱（"差点误判为失守"）→ '
      '三个攻击者分层收尾。', '#EAF0F8', '叙事', 10.5)

# ==================== 附录 ====================
doc.add_page_break()
H1('附录　真实日志样例与数据口径')
H2('A.1 原始日志样例（nginx access.log 原文）')
CODE('136.107.98.147 - - [05/Sep/2026:12:16:19 +0800] "GET /?file=../../../../etc/passwd HTTP/1.1" 200 2017 "-" "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user"\n'
     '136.107.98.147 - - [05/Sep/2026:12:16:20 +0800] "GET /assets../../../.env HTTP/1.1" 400 157 "-" "-"\n'
     '136.107.98.147 - - [05/Sep/2026:12:16:21 +0800] "POST /fetch HTTP/1.1" 404 564 "-" "Mozilla/5.0 (compatible; ChatGPT-User/1.0; +https://openai.com/bot)"\n'
     '136.107.98.147 - - [05/Sep/2026:12:16:28 +0800] "GET /@fs/etc/passwd?raw?? HTTP/1.1" 404 564 "-" "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36"')
H2('A.2 数据口径')
TABLE(['项目', '口径'], [
    ['数据来源', '47.243.223.221 /var/log/nginx/access.log（真实公网日志）'],
    ['提取方式', '按来源 IP 过滤全部请求，Python 正则解析原始格式'],
    ['时间范围', '2026-09-05 12:16:17 ~ 12:16:34（UTC+8）'],
    ['统计总量', '644 条（与流水线 parsed.csv 一致）'],
    ['分类口径', '按 URL 路径模式人工归类；“其他变体”为未命中已知模式的路径'],
    ['状态码解读', '200×5 中 4 条为首页正常响应，1 条为诱饵后台页，无敏感内容回显'],
], widths=[3.5, 12.5])
BLOCK('本文档所有数据可直接追溯至原始日志与流水线产物（parsed.csv / analysis.csv），'
      '无任何虚构或修饰。', '#FFF6E5', '真实性声明', 10.5)

os.makedirs(os.path.dirname(DOC_PATH), exist_ok=True)
doc.save(DOC_PATH)
print('saved:', DOC_PATH)
