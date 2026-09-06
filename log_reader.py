# -*- coding: utf-8 -*-
"""① 增量读取器 log_reader.py
机制：文件物理位置游标（inode + 字节偏移），业界标准（filebeat sincedb 同款）
- inode 相同 + size >= offset → 正常追加，seek(offset) 续读
- inode 相同 + size <  offset → 文件被截断，回退从 0 重读
- inode 不同（轮转/新建）        → 从 0 读新文件
- 无状态（首次）                → 按配置从 0 全量 或 从当前 size 跳过
状态持久化：data/.log_cursor.json
"""
import os
import json
import time

def _read_cursor(path):
    if os.path.exists(path):
        try:
            with open(path,encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _write_cursor(path, state):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=1)

def read_new(file_path, cursor_path, source_key, first_mode='full'):
    """返回 (新增行列表, 是否全量读取)
    first_mode: 'full' 首次全量读 | 'tail' 首次跳过历史只读新增
    """
    state = _read_cursor(cursor_path)
    last = state.get(source_key, {})

    if not os.path.exists(file_path):
        return [], False

    #获取file_path的设备号和inode
    st = os.stat(file_path)
    key = f"{st.st_dev}:{st.st_ino}"

    if last.get('key') != key:
        # 无记录（首次）或文件被轮转替换
        offset = 0 if first_mode == 'full' else st.st_size
        full = last.get('key') is None and first_mode == 'full'
    elif last.get('offset', 0) > st.st_size:
        # 文件被截断（copytruncate 轮转）→ 回退重读
        offset = 0
        full = True
    else:
        offset = last.get('offset', 0)
        full = False

    lines = []
    with open(file_path, 'rb') as f:
        f.seek(offset)
        for raw in f:
            lines.append(raw.decode('utf-8', 'replace').rstrip('\n'))

    state[source_key] = {
        'key': key,
        'offset': st.st_size,
        'size': st.st_size,
        'mtime': st.st_mtime,
        'read_at': time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    _write_cursor(cursor_path, state)
    return lines, full
