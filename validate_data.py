# -*- coding: utf-8 -*-
"""
题库 / 音频 / 计划数据完整性校验（CI 与本地发布前运行）
用法: python validate_data.py
退出码 1 表示存在阻断性问题
"""
import json, os, re, sys

APP = os.path.dirname(os.path.abspath(__file__))
errors, warns = [], []


def load(rel):
    with open(os.path.join(APP, rel), encoding='utf-8') as f:
        return json.load(f)


def audio_ok(rel):
    if not rel:
        return False
    p = os.path.join(APP, rel)
    return os.path.isfile(p) and os.path.getsize(p) > 500


# ── 1. 背诵数据 ──
data = load('data.json')
nseg = 0
for bi, b in enumerate(data.get('books', [])):
    if b.get('total_segments') != len(b.get('segments', [])):
        errors.append('book %s total_segments 不一致' % b.get('main_category'))
    for si, s in enumerate(b.get('segments', [])):
        nseg += 1
        if not (s.get('text') or '').strip():
            errors.append('空段落 book%d seg%d' % (bi, si))
        if not audio_ok(s.get('audio')):
            errors.append('音频缺失/过小 book%d seg%d %s' % (bi, si, s.get('audio')))

# ── 2. 挖空 ──
clz = load('quiz/cloze.json')['items']
ids = set()
for x in clz:
    if x['id'] in ids:
        errors.append('cloze id 重复 %s' % x['id'])
    ids.add(x['id'])
    if not x.get('blanks') or not all(str(b).strip() for b in x['blanks']):
        errors.append('cloze 空答案 %s' % x['id'])
    if not audio_ok(x.get('audio')):
        errors.append('cloze 音频缺失 %s' % x['id'])

# ── 3. 选择题 ──
for fn in ('quiz/choice.json', 'quiz/exam_choice.json'):
    for x in load(fn)['items']:
        opts = x.get('options') or {}
        if len(opts) < 4:
            errors.append('%s 选项不足 %s' % (fn, x.get('id')))
        if not (x.get('stem') or '').strip():
            errors.append('%s 空题干 %s' % (fn, x.get('id')))
        for k in x.get('answer', ''):
            if k not in opts:
                errors.append('%s 答案 %s 不在选项 %s' % (fn, k, x.get('id')))

# ── 4. 单词 ──
for x in load('quiz/words.json')['items']:
    if len(x.get('options') or []) != 4 or x.get('meaning') not in (x.get('options') or []):
        errors.append('word 选项异常 %s' % x.get('word'))
    if not (x.get('meaning') or '').strip():
        errors.append('word 空释义 %s' % x.get('word'))

# ── 5. 填空 ──
fl = load('quiz/fill.json')['items']
for x in fl:
    if not (x.get('q') or '').strip():
        errors.append('fill 空题干 %s' % x.get('id'))
    if not (x.get('a') or '').strip():
        warns.append('fill 空答案 %s' % x.get('id'))

# ── 6. 数学公式 ──
for t in load('quiz/math.json')['tests']:
    for p in t.get('pages', []):
        if not os.path.isfile(os.path.join(APP, p)):
            errors.append('math 页面缺失 %s %s' % (t.get('id'), p))

# ── 7. 30天计划 ──
plan_js = open(os.path.join(APP, 'plan_data.js'), encoding='utf-8').read()
m = re.search(r'window\.__PLAN__\s*=\s*(\{.*\});', plan_js, re.S)
if not m:
    errors.append('plan_data.js 解析失败')
else:
    plan = json.loads(m.group(1))
    if len(plan.get('days', [])) != 30:
        errors.append('计划天数不是 30')
    for d in plan['days']:
        for g in d['groups']:
            for it in g['items']:
                b = it.get('b')
                i = it.get('i')
                if not (0 <= b < len(data['books']) and 0 <= i < len(data['books'][b]['segments'])):
                    errors.append('计划 Day%d 段落越界 b%d i%d' % (d['day'], b, i))

# ── 输出 ──
print('校验：%d 本书 / %d 段 / %d 挖空 / %d 填空' % (len(data['books']), nseg, len(clz), len(fl)))
if warns:
    print('⚠️ 警告 %d 条（不阻断）:' % len(warns))
    for w in warns[:10]:
        print('  -', w)
if errors:
    print('❌ 错误 %d 条:' % len(errors))
    for e in errors[:20]:
        print('  -', e)
    sys.exit(1)
print('✅ 全部通过')
