# -*- coding: utf-8 -*-
"""
把《重点时政总结-国内部分.docx》《重点时政总结-国际部分.docx》
解析为背诵书籍，追加到 data.json（保留原有书籍与音频路径）
- 每个“编号条目”与其 ①②③ 选项、续写行合并为同一段，避免问答被拆开
- 输出 audio 路径: audios/<book>/<seg>.mp3（随后用 gen-audio.mjs 生成）
用法: python build_shizheng.py [--dry]
"""
import docx, json, os, re, sys

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, 'data.json')
SRC = r'd:\Desktop\背诵\资源'
CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
ITEM_RE = re.compile(r'^(\d{1,3})\s*[.．、]\s*')
HEAD_RE = re.compile(r'^[一二三四五六七八九十]+\s*[、.]')
TITLE_RE = re.compile(r'^20\d{2}\s*重点时政总结')

BOOKS = [
    ('重点时政·国内', '国内部分', 'zh-CN-XiaoxiaoNeural', '2027重点时政总结（国内）'),
    ('重点时政·国际', '国际部分', 'zh-CN-YunxiNeural', '2027重点时政总结（国际）'),
]


def cjk(ch):
    if not ch:
        return False
    o = ord(ch)
    return (0x4e00 <= o <= 0x9fff) or ch in '，。；：、（）《》“”‘’—…·！？【】'


def clean(s):
    s = (s or '').replace('\u3000', ' ').replace('\xa0', ' ').replace('\t', ' ')
    s = s.replace('\n', '').replace('\r', '')
    s = re.sub(r' {2,}', ' ', s).strip()
    # 编号统一为 "N. "
    s = re.sub(r'^(\d{1,3})\s*[.．、]\s*', r'\1. ', s)
    # 去掉中文字符之间的排版空格（①-⑳ 前保留一个空格）
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch != ' ':
            out.append(ch)
            i += 1
            continue
        j = i
        while j < n and s[j] == ' ':
            j += 1
        prev = out[-1] if out else ''
        nxt = s[j] if j < n else ''
        if nxt in CIRCLED:
            out.append(' ')
        elif cjk(prev) and cjk(nxt):
            pass
        elif (cjk(prev) and nxt.isdigit()) or (prev.isdigit() and cjk(nxt)):
            pass
        elif prev in '，。；：、（）《》“”' or nxt in '，。；：、（）《》“”':
            pass
        else:
            out.append(' ')
        i = j
    s = ''.join(out)
    # ②-⑳ 前补一个空格，便于阅读与断句
    s = re.sub(r'(?<=\S)(?=[\u2461-\u2473])', ' ', s)
    return re.sub(r' {2,}', ' ', s).strip()


def parse_docx(path):
    d = docx.Document(path)
    sub = '前言'
    items = []
    cur = None
    for para in d.paragraphs:
        t = clean(para.text)
        if not t:
            continue
        if TITLE_RE.match(t):
            continue
        if HEAD_RE.match(t) and len(t) <= 60 and not ITEM_RE.match(t):
            sub = t
            continue
        if ITEM_RE.match(t):
            cur = {'sub': sub, 'text': t}
            items.append(cur)
        elif cur is None:
            cur = {'sub': sub, 'text': t}
            items.append(cur)
        else:
            cur['text'] += t
    return items


def main():
    dry = '--dry' in sys.argv
    with open(DATA, encoding='utf-8') as f:
        data = json.load(f)
    max_cid = 0
    for b in data['books']:
        for s in b.get('segments', []):
            max_cid = max(max_cid, s.get('cid', 0))
    next_cid = max_cid + 1

    # 先移除同名旧书，保证重复执行时书籍索引不漂移
    new_names = {m for m, *_ in BOOKS}
    data['books'] = [b for b in data['books'] if b.get('main_category') not in new_names]
    added = []
    for main, part, voice, note in BOOKS:
        items = parse_docx(os.path.join(SRC, '重点时政总结-%s.docx' % part))
        bi = len(data['books']) + len(added)
        segs = []
        for i, it in enumerate(items):
            seg = {
                'sub': it['sub'],
                'text': it['text'],
                'audio': 'audios/%02d/%04d.mp3' % (bi, i),
                'cid': next_cid,
            }
            next_cid += 1
            segs.append(seg)
        order, groups = [], {}
        for i, s in enumerate(segs):
            sn = s['sub']
            if sn not in groups:
                groups[sn] = {'name': sn, 'count': 0, 'indices': []}
                order.append(sn)
            groups[sn]['count'] += 1
            groups[sn]['indices'].append(i)
        book = {
            'file': '重点时政总结-%s.docx' % part,
            'main_category': main,
            'note': note,
            'total_segments': len(segs),
            'segments': segs,
            'sub_categories': [groups[k] for k in order],
            'audio_voice': voice,
        }
        print('%s: %d 段 / %d 字, %d 个子类' % (
            main, len(segs), sum(len(s['text']) for s in segs), len(order)))
        for i, s in enumerate(segs[:3]):
            print('   [%d] %s | %s' % (i, s['sub'], s['text'][:70]))
        added.append(book)

    if dry:
        print('（dry-run，未写入）')
        return
    data['books'].extend(added)
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print('✅ 已追加到 data.json，共 %d 本书' % len(data['books']))


if __name__ == '__main__':
    main()
