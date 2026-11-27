# -*- coding: utf-8 -*-
"""
修复 data.json 背诵切分问题（一次性、幂等）
- 把「答案/续写」段落合并回所属问题段落，避免问答被拆到两个板块
- 删除答案速查行（如 1.ABCD 2.D 3.ACD32 月）与页码残留
- 保留每段原有 audio 路径；被合并段落的音频按顺序拼接到首段 MP3
- 为每段写入稳定 cid（原全局序号），保证挖空题 id 与历史进度不漂移
用法: python repair_data.py [--dry]
"""
import json, os, re, sys

APP = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP, 'data.json')
TARGETS = {'1-10月时政热点', '肖190题客观题'}

ITEM_RE = re.compile(r'^\d{1,3}\s*[.．、]')
HEAD_RE = re.compile(r'^[一二三四五六七八九十]+\s*[、.]')
ANSKEY_RE = re.compile(r'^[\dA-Da-d\.．、,，\s年月日\-—]+$')
TAIL_NUM_RE = re.compile(r'(?<=[\u4e00-\u9fff）)」】。；！？])\d{1,2}$')


def is_anskey(t):
    if len(t) > 45:
        return False
    if not ANSKEY_RE.match(t):
        return False
    return len(re.findall(r'[A-Da-d]', t)) >= 2


def clean_sub(name):
    name = (name or '').strip()
    name = re.sub(r'\d+$', '', name).strip()
    return name or '未分类'


def concat_audio(paths, out_abs):
    if len(paths) < 2:
        return False
    buf = b''
    for p in paths:
        ap = os.path.join(APP, p)
        if os.path.isfile(ap) and os.path.getsize(ap) > 500:
            with open(ap, 'rb') as f:
                buf += f.read()
    if not buf:
        return False
    with open(out_abs, 'wb') as f:
        f.write(buf)
    return True


def main():
    dry = '--dry' in sys.argv
    with open(DATA, encoding='utf-8') as f:
        data = json.load(f)

    # 1) 写入稳定 cid（按原全局顺序，与 build_cloze 旧 sid 一致）
    gid = 0
    for book in data['books']:
        for seg in book.get('segments', []):
            gid += 1
            if 'cid' not in seg:
                seg['cid'] = gid
    max_cid = gid
    print(f'全局段落 {gid}，cid 已补齐')

    # 2) 修复目标书籍
    for book in data['books']:
        if book.get('main_category') not in TARGETS:
            continue
        name = book['main_category']
        segs = book.get('segments', [])
        before = len(segs)
        kept = []
        merged_groups = 0
        dropped = 0
        for seg in segs:
            t = (seg.get('text') or '').strip()
            if not t:
                dropped += 1
                continue
            if is_anskey(t):
                dropped += 1
                continue
            t = TAIL_NUM_RE.sub('', t).strip()
            if len(t) < 2:
                dropped += 1
                continue
            new_item = bool(ITEM_RE.match(t) or HEAD_RE.match(t))
            if not new_item and not kept:
                dropped += 1   # 书籍标题等首段噪声
                continue
            if not new_item and kept:
                prev = kept[-1]
                a, b = prev['text'], t
                sep = ' ' if (re.search(r'[A-Za-z0-9]$', a) and re.match(r'[A-Za-z0-9]', b)) else ''
                prev['text'] = a + sep + b
                prev['_audios'].append(seg.get('audio', ''))
                merged_groups += 1
            else:
                s = dict(seg)
                s['text'] = t
                s['_audios'] = [s.get('audio', '')]
                kept.append(s)

        # 合并音频
        for s in kept:
            auds = [x for x in s.get('_audios', []) if x]
            if len(auds) > 1:
                out_abs = os.path.join(APP, auds[0])
                if not dry:
                    concat_audio(auds, out_abs)
            s.pop('_audios', None)

        book['segments'] = kept
        book['total_segments'] = len(kept)
        # 重算子分类
        order, groups = [], {}
        for i, s in enumerate(kept):
            sn = clean_sub(s.get('sub'))
            s['sub'] = sn
            if sn not in groups:
                groups[sn] = {'name': sn, 'count': 0, 'indices': []}
                order.append(sn)
            groups[sn]['count'] += 1
            groups[sn]['indices'].append(i)
        book['sub_categories'] = [groups[k] for k in order]
        print(f'{name}: {before} → {len(kept)} 段（合并 {merged_groups}，删除 {dropped}）')
        if dry:
            for i, s in enumerate(kept):
                if i % max(1, len(kept) // 12) == 0:
                    print(f'   [{i}] {s["sub"]} | {s["text"][:70]}... ({len(s["text"])}字)')

    # 3) 其它书籍也清理一下子分类名（不改文本）
    for book in data['books']:
        if book.get('main_category') in TARGETS:
            continue
        for s in book.get('segments', []):
            s['sub'] = clean_sub(s.get('sub'))
        book['total_segments'] = len(book.get('segments', []))
        order, groups = [], {}
        for i, s in enumerate(book.get('segments', [])):
            sn = s['sub']
            if sn not in groups:
                groups[sn] = {'name': sn, 'count': 0, 'indices': []}
                order.append(sn)
            groups[sn]['count'] += 1
            groups[sn]['indices'].append(i)
        book['sub_categories'] = [groups[k] for k in order]

    if dry:
        print('（dry-run，未写入）')
        return
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f'✅ 已写入 data.json，最大 cid={max_cid}')


if __name__ == '__main__':
    main()
