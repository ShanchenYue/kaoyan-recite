# -*- coding: utf-8 -*-
"""把 2016-2025 政治真题整理成选择题 + 大题题库"""
import glob
import json
import os
import re
import sys
import docx

BASE = r'd:\Desktop\背诵\资源'
QBASE = os.path.join(BASE, '02. 2009-2025年真题及答案解析', '2009-2025年真题')
ABASE = os.path.join(BASE, '2009-2025年真题答案解析')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quiz')
YEARS = range(2016, 2026)

NUM_RE = re.compile(r'^(\d{1,2})\s*[.．、]\s*')
OPT_RE = re.compile(r'^([A-D])\s*[.．、]?\s*(.*)$')
TAG = {34: '马原', 35: '毛中特', 36: '史纲', 37: '思修', 38: '当代'}


def norm(t):
    t = t.replace('\u3000', ' ').replace('\xa0', ' ')
    t = t.replace('家庭关德', '家庭美德')
    return re.sub(r'\s+', ' ', t).strip()


def paras(path):
    out = []
    for p in docx.Document(path).paragraphs:
        t = norm(p.text)
        if not t:
            continue
        if re.search(r'微信公众号|微信扫码|考研政治真题第\s*\d+\s*页|自助打印|顺丰|淘宝|叮当助考|政治真题答案解析第'
                     r'|考研政治讲真题|^\d{4}\s*年全国硕士研究生招生考试', t):
            continue
        if re.match(r'^[\u4e00-\u9fa5](\s+[\u4e00-\u9fa5]){1,8}$', t):
            continue
        out.append(t)
    return out


def find_sec(ps, kind):
    for i, t in enumerate(ps):
        tt = t.replace(' ', '')
        if kind == 'single' and re.match(r'^一[、.]', tt):
            return i
        if kind == 'multi' and re.match(r'^二[、.]', tt):
            return i
        if kind == 'essay' and re.match(r'^三[、.]', tt):
            return i
    return -1


def split_blocks_seq(lines, lo, hi):
    blocks, cur = [], None
    nxt = lo
    for t in lines:
        num, rest = None, ''
        m = re.match(r'^[*＊]?\s*(\d{1,2})\s*[.．、]\s*(.*)$', t)
        if m:
            num, rest = int(m.group(1)), m.group(2)
        else:
            m2 = re.match(r'^[*＊]?\s*(\d{1,2})\s*(?=[\u4e00-\u9fa5A-Za-z“《(（])(.*)$', t)
            if m2 and int(m2.group(1)) == nxt:
                num, rest = int(m2.group(1)), m2.group(2)
        if num is not None and lo <= num <= hi and num >= nxt:
            if cur:
                blocks.append(cur)
            cur = {'no': num, 'lines': [rest.strip()]}
            nxt = num + 1
            continue
        if cur:
            cur['lines'].append(t)
    if cur:
        blocks.append(cur)
    return blocks


def split_blocks(lines, lo, hi):
    return split_blocks_seq(lines, lo, hi)


def _cand(letter, text, loose):
    """收集某个选项字母的候选位置 (start, end)"""
    out = []
    for m in re.finditer(letter, text):
        i = m.start()
        if i > 0 and text[i - 1].isascii() and (text[i - 1].isalpha() or text[i - 1].isdigit()):
            continue
        prev = text[i - 1] if i > 0 else '\n'
        strict = (prev == '\n' or prev in ' \t\u3000、，,；;()（）?？:：。.！!“”"\'')
        if not strict:
            if not loose:
                continue
            if not ('\u4e00' <= prev <= '\u9fff' or prev in '”』）'):
                continue
        j = m.end()
        while j < len(text) and text[j] in ' \t':
            j += 1
        if j < len(text) and text[j] in '.．、':
            j += 1
            while j < len(text) and text[j] in ' \t':
                j += 1
        if j >= len(text):
            continue
        ch = text[j]
        if not (ch.isalnum() or ch in '《“"（(【'):
            continue
        out.append((i, j))
    return out


def option_markers(text):
    loose = {L: _cand(L, text, True) for L in 'BCD'}
    for a in _cand('A', text, False):
        pos = {'A': a}
        end = a[1]
        used = {'A'}
        ok = True
        for _ in range(3):
            best = None
            for L in 'BCD':
                if L in used:
                    continue
                nxt = next(((x, y) for x, y in loose[L] if x >= end and x not in (v[0] for v in pos.values())), None)
                if nxt and (best is None or nxt[0] < best[1][0]):
                    best = (L, nxt)
            if not best:
                ok = False
                break
            pos[best[0]] = best[1]
            used.add(best[0])
            end = best[1][1]
        if ok and len(pos) == 4:
            return pos
    return None


def option_markers_partial(text):
    a_list = _cand('A', text, False)
    if not a_list:
        return None
    chosen = {'A': a_list[0]}
    end = a_list[0][1]
    for L in 'BCD':
        cands = [c for c in _cand(L, text, True) if c[0] >= end]
        if cands:
            chosen[L] = cands[0]
            end = cands[0][1]
    return chosen if len(chosen) >= 3 else None


def parse_choice_lines(lines):
    text = '\n'.join(lines)
    pos = option_markers(text) or option_markers_partial(text)
    if not pos:
        return norm(text), {}
    stem = norm(text[:pos['A'][0]])
    opts = {}
    present = sorted(pos.items(), key=lambda kv: kv[1][0])
    for k, (L, (_, s)) in enumerate(present):
        e = present[k + 1][1][0] if k + 1 < len(present) else len(text)
        opts[L] = norm(text[s:e])
    return stem, opts


def parse_choice_questions(ps, year):
    si = find_sec(ps, 'single')
    ei = find_sec(ps, 'essay')
    if si < 0:
        return []
    lines = ps[si + 1:ei] if ei > si else ps[si + 1:]
    lines = [t for t in lines if not re.match(r'^[一二三]\s*[、.]\s*', t)]
    fixed = []
    for t in lines:
        if '社会主义法治道路' in t and '首先要' in t:
            t = ('14. 党的二十大报告指出：“我们要坚持走中国特色社会主义法治道路，建设中国特色社会主义法治体系，'
                 '建设社会主义法治国家，围绕保障和促进社会公平正义，坚持依法治国、依法执政、依法行政共同推进，'
                 '坚持法治国家、法治政府、法治社会一体建设，全面推进科学立法、严格执法、公正司法、全民守法，'
                 '全面推进国家各方面工作法治化。”坚持全面依法治国首先要( )')
        fixed.append(t)
    lines = fixed
    out = []
    for b in split_blocks_seq(lines, 1, 33):
        stem, opts = parse_choice_lines(b['lines'])
        if b['no'] == 13 and set(opts) >= {'A', 'B', 'C'} and 'D' not in opts:
            opts['D'] = '传承孝老爱亲、扶危济困、见义勇为等中华美德'
        if len(opts) < 4:
            print('  [!] %d 题选项不足: %s' % (b['no'], stem[:50]))
            continue
        out.append({'no': b['no'], 'stem': stem, 'options': opts})
    return out


def parse_choice_answers(ps):
    ans = {}
    cur = None
    for raw in ps:
        t = re.sub(r'^(\d)\s+(\d)(\s*[.．、])', r'\1\2\3', raw)
        tt = re.sub(r'^[一二三]\s*[、.]\s*', '', t)
        m = re.match(r'^[*＊]?\s*(\d{1,2})\s*[.．、]?\s*(.*)$', tt)
        if m and 1 <= int(m.group(1)) <= 33 and re.search(r'【\s*答案', m.group(2)):
            n = int(m.group(1))
            rest = m.group(2)
            letters = None
            mm = re.search(r'【\s*答\s*案\s*】\s*([A-D](?:\s*[A-D]){0,3})', rest)
            if not mm:
                mm = re.search(r'正确选项(?:为|是)?\s*([A-D](?:\s*[A-D]){0,3})', rest)
            if mm:
                letters = re.sub(r'\s+', '', mm.group(1))
            cur = {'answer': letters, 'explain': []}
            ans[n] = cur
            body = re.sub(r'^【[^】]*】\s*', '', rest).strip()
            if body:
                cur['explain'].append(body)
            continue
        if re.match(r'^[一二三]\s*[、.]', t):
            cur = None
            continue
        if cur is not None:
            cur['explain'].append(raw)
    for n, v in ans.items():
        v['explain'] = '\n'.join(v['explain']).strip()
    return ans


def parse_essay_answers(ps):
    si = find_sec(ps, 'essay')
    seg = ps[si:] if si >= 0 else ps
    text = '\n'.join(seg)
    marks = list(re.finditer(r'(?<!\d)(3[4-8])\s*[.．、]', text))
    out = {}
    for i, m in enumerate(marks):
        n = int(m.group(1))
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[start:end].strip()
        body = re.sub(r'^【[^】]*】\s*', '', body).strip()
        out[n] = body
    return out


def parse_essay_questions(ps):
    ei = find_sec(ps, 'essay')
    if ei < 0:
        return []
    out = []
    for b in split_blocks(ps[ei + 1:], 34, 38):
        text = '\n'.join(b['lines'])
        m = re.search(r'[（(]\s*1\s*[）)]', text)
        if m:
            material, questions = text[:m.start()].strip(), text[m.start():].strip()
        else:
            material, questions = text.strip(), ''
        out.append({'no': b['no'], 'material': material, 'questions': questions})
    return out


def find_doc(pattern):
    fs = glob.glob(pattern)
    return fs[0] if fs else None


def main():
    os.makedirs(OUT, exist_ok=True)
    choices, essays = [], []
    for y in YEARS:
        qf = os.path.join(QBASE, '%d年考研政治真题.docx' % y)
        af = find_doc(os.path.join(ABASE, '%d*.docx' % y))
        if not os.path.isfile(qf) or not af:
            print('跳过', y, '缺文件', qf, af)
            continue
        qp, ap = paras(qf), paras(af)
        qs = parse_choice_questions(qp, y)
        aa = parse_choice_answers(ap)
        eq = parse_essay_questions(qp)
        ea = parse_essay_answers(ap)

        ok = 0
        missing = []
        for q in qs:
            a = aa.get(q['no'])
            if not a or not a['answer']:
                missing.append(q['no'])
                continue
            letters = ''.join(sorted(set(re.findall(r'[A-D]', a['answer']))))
            if not letters:
                missing.append(q['no'])
                continue
            item = {
                'id': 'zt%d_%d' % (y, q['no']),
                'set': '%d真题' % y,
                'no': q['no'],
                'multi': q['no'] >= 17,
                'stem': q['stem'],
                'options': {k: q['options'][k] for k in 'ABCD'},
                'answer': letters,
                'explain': a['explain'] or '暂无解析',
            }
            choices.append(item)
            ok += 1

        eok = 0
        for e in eq:
            ans = ea.get(e['no'], '').strip()
            essays.append({
                'id': 'zt%d_%d' % (y, e['no']),
                'year': y,
                'no': e['no'],
                'tag': TAG.get(e['no'], ''),
                'material': e['material'],
                'questions': e['questions'],
                'answer': ans or '参考答案暂未收录',
            })
            eok += 1
        print('%d: 选择 %d/%d  大题 %d/5  缺答案 %s' % (y, ok, len(qs), eok, missing))

    with open(os.path.join(OUT, 'exam_choice.json'), 'w', encoding='utf-8') as f:
        json.dump({'version': 1, 'items': choices}, f, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, 'essay.json'), 'w', encoding='utf-8') as f:
        json.dump({'version': 1, 'items': essays}, f, ensure_ascii=False, separators=(',', ':'))
    print('总计：选择 %d 题，大题 %d 题' % (len(choices), len(essays)))


if __name__ == '__main__':
    main()
