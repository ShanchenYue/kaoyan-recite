# -*- coding: utf-8 -*-
"""
生成 30 天背诵计划数据 plan_data.js
- 解析《30天背诵计划.docx》的每日内容
- 把“题号 / 热点链接”映射到《主观题背诵包》的真实段落
- 附带对应挖空题 id（用于一键练习）
用法: python build_plan.py
"""
import json, os, re, sys, io
import docx

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, 'data.json')
DOCX = r'd:\Desktop\背诵\资源\30天背诵计划.docx'
OUT = os.path.join(APP, 'plan_data.js')
START = '2026-11-16'   # 用户当前进度：2026-11-27 = 第12天

data = json.load(open(DATA, encoding='utf-8'))
book = data['books'][3]            # 主观题背诵包
segs = book['segments']
clz = json.load(open(os.path.join(APP, 'quiz', 'cloze.json'), encoding='utf-8'))['items']
cid_by_audio = {}
for c in clz:
    a = c.get('audio')
    if a and a not in cid_by_audio:
        cid_by_audio[a] = c['id']

# ── 客观题：题号 → 段落索引 ──
PARTS = {
    '马原': (0, 99),
    '毛中特': (99, 131),
    '史纲': (131, 233),
    '德法': (233, 271),
    '时政': (271, 305),
}
NUM2IDX = {}
for name, (s, e) in PARTS.items():
    m = {}
    for i in range(s, e):
        mm = re.match(r'^\s*(\d{1,3})\s*[.．、]', segs[i]['text'])
        if mm:
            m[int(mm.group(1))] = i
    NUM2IDX[name] = m

# ── 主观题：热点链接区间 ──
def ranges_from_markers(markers, end):
    out = {}
    for k, start in enumerate(markers):
        stop = markers[k + 1] - 1 if k + 1 < len(markers) else end
        out[k + 1] = (start, stop)
    return out

HOT = {
    '马原': ranges_from_markers([305, 307, 309, 311, 313, 315, 317, 319, 321, 323, 325, 329, 332, 335, 337], 338),
    '史纲': ranges_from_markers([364, 372, 384, 399], 404),
    '德法': ranges_from_markers([405, 414, 426], 428),
    '当代': ranges_from_markers([429, 434, 438, 442, 446, 451, 454, 457], 464),
}
SPECIAL = {
    '生态法典': (339, 344),
    '十五五+五中全会': (345, 363),
}


def item(i):
    s = segs[i]
    d = {'b': 3, 'i': i, 't': s['text'], 'sub': s.get('sub', '')}
    cid = cid_by_audio.get(s.get('audio', ''))
    if cid:
        d['cid'] = cid
    return d


def obj_group(part, nums, name):
    its = []
    for n in nums:
        if n in NUM2IDX[part]:
            it = item(NUM2IDX[part][n])
            it['n'] = n
            its.append(it)
    return {'name': name, 'items': its}


def hot_group(part, nums, name):
    its = []
    for n in nums:
        if n in HOT[part]:
            s, e = HOT[part][n]
            for i in range(s, e + 1):
                its.append(item(i))
    return {'name': name, 'items': its}


def range_group(key, name):
    s, e = SPECIAL[key]
    return {'name': name, 'items': [item(i) for i in range(s, e + 1)]}


R = lambda a, b: list(range(a, b + 1))

SPEC = {
    1: [hot_group('马原', [1, 2, 3, 4, 5, 10], '马原 · 主观题热点链接 1-5、10')],
    2: [obj_group('马原', R(1, 8), '马原 · 导论客观题 1-8'),
        obj_group('马原', R(11, 19) + [30] + R(40, 46), '马原 · 马哲客观题'),
        obj_group('马原', R(60, 62) + [65] + R(68, 71) + [82], '马原 · 政经客观题'),
        obj_group('马原', R(84, 86), '马原 · 科社客观题')],
    3: [obj_group('毛中特', R(1, 7), '毛中特 · 客观题 1-7')],
    4: [obj_group('毛中特', R(8, 15), '毛中特 · 客观题 8-15')],
    5: [range_group('生态法典', '毛中特 · 生态环境法典（设问一、二）')],
    6: [obj_group('史纲', R(1, 30), '史纲 · 客观题 1-30')],
    7: [obj_group('史纲', R(31, 60), '史纲 · 客观题 31-60')],
    8: [obj_group('德法', R(1, 33), '德法 · 客观题 1-33')],
    9: [hot_group('德法', [1, 2], '德法 · 主观题热点链接 1、2')],
    10: [hot_group('当代', [1, 2, 3], '当代 · 主观题热点链接 1、2、3'),
         obj_group('时政', R(1, 10), '时政 · 客观题 1-10')],
    11: [hot_group('马原', [6, 7, 8, 9, 12], '马原 · 主观题热点链接 6-9、12')],
    12: [obj_group('马原', [9, 10] + R(20, 23) + R(31, 39) + [52, 53], '马原 · 马哲客观题 9-10、20-23、31-39、52-53')],
    13: [obj_group('马原', [59, 63, 64] + R(73, 75) + [78, 79], '马原 · 政经客观题'),
         obj_group('马原', [87, 88], '马原 · 科社客观题 87-88')],
    14: [obj_group('毛中特', R(16, 26), '毛中特 · 客观题 16-26')],
    15: [range_group('十五五+五中全会', '毛中特 · 十五五规划纲要 + 二十届五中全会')],
    16: [obj_group('史纲', R(61, 89), '史纲 · 客观题 61-89')],
    17: [hot_group('史纲', [1], '史纲 · 主观题热点链接 1')],
    18: [obj_group('德法', R(1, 33), '德法 · 客观题 1-33')],
    19: [hot_group('德法', [1, 2, 3], '德法 · 主观题热点链接 1、2、3')],
    20: [hot_group('当代', [4, 5, 7], '当代 · 主观题热点链接 4、5、7'),
         obj_group('时政', R(11, 20), '时政 · 客观题 11-20')],
    21: [hot_group('马原', [10, 11, 13, 14, 15], '马原 · 主观题热点链接 10-11、13-15')],
    22: [obj_group('马原', R(24, 29) + R(47, 51) + R(54, 58), '马原 · 马哲客观题'),
         obj_group('马原', [66, 67, 72, 76, 77, 80, 81, 83], '马原 · 政经客观题'),
         obj_group('马原', R(89, 92), '马原 · 科社客观题 89-92')],
    23: [hot_group('史纲', [2], '史纲 · 主观题热点链接 2')],
    24: [hot_group('史纲', [3, 4], '史纲 · 主观题热点链接 3、4')],
    25: [obj_group('德法', R(1, 34), '德法 · 选择题全部考点 1-34')],
    26: [hot_group('德法', [3], '德法 · 主观题热点链接 3')],
    27: [hot_group('当代', [6, 8], '当代 · 主观题热点链接 6、8'),
         obj_group('时政', R(21, 29), '时政 · 客观题 21-29')],
}

# ── 解析计划表 ──
doc = docx.Document(DOCX)
raw_days = {}
for table in doc.tables:
    for row in table.rows:
        vals, seen = [], set()
        for c in row.cells:
            if id(c._tc) in seen:
                continue
            seen.add(id(c._tc))
            vals.append(c.text.strip())
        if len(vals) < 5 or not vals[0].isdigit():
            continue
        day = int(vals[0])
        raw_days[day] = {
            'subject': vals[2],
            'content': re.sub(r'\s*/\s*', '\n', vals[3]).strip(),
            'check': re.sub(r'\s*/\s*', '\n', vals[4]).strip(),
        }

GEN = {
    28: ('二轮复习', '马原 + 毛中特：错题与高频客观题\n二刷对应挖空', '错题重做；填空二刷'),
    29: ('二轮复习', '史纲 + 德法 + 时政：客观题高频与易错点', '错题重做；时政填空'),
    30: ('全真模拟', '限时完成一套选择题 + 主观题框架默写\n回看 30 天错题本', '限时模拟；主观题框架默写'),
}

days = []
for d in range(1, 31):
    if d in raw_days:
        info = raw_days[d]
        groups = SPEC.get(d, [])
        generated = False
    else:
        subj, content, check = GEN[d]
        info = {'subject': subj, 'content': content, 'check': check}
        groups = []
        generated = True
    count = sum(len(g['items']) for g in groups)
    days.append({
        'day': d,
        'subject': info['subject'],
        'content': info['content'],
        'check': info['check'],
        'generated': generated,
        'groups': groups,
        'count': count,
        'review': [x for x in (d - 1, d - 2, d - 4, d - 7, d - 15) if x >= 1],
    })

out = {'version': 1, 'start': START, 'days': days}
with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write('window.__PLAN__ = ')
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')

print('✅ plan_data.js 生成')
print('  天数', len(days), '总条目', sum(x['count'] for x in days))
for d in (1, 5, 12, 15, 27):
    x = next(v for v in days if v['day'] == d)
    print('  Day %-2d %-16s %2d 条 | %s' % (d, x['subject'], x['count'], x['content'].replace('\n', ' / ')[:50]))
