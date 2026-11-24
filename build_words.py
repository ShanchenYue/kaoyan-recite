# -*- coding: utf-8 -*-
"""从英语词汇书 OCR 文本解析单词-词义, 生成四选一题库 quiz/words.json"""
import re, json, os, random
from collections import Counter

random.seed(7)
OCR = r"d:\Desktop\背诵\ocr\english_vocab.txt"
APP = os.path.dirname(os.path.abspath(__file__))

CJK = r'\u4e00-\u9fff'
POS = r'(?:n|v|vt|vi|adj|adv|prep|conj|pron|num|art|aux)'

def norm_cjk_spaces(s):
    # 去掉中文字符之间/中文与中文标点之间的空格
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'(?<=[' + CJK + r'])\s+(?=[' + CJK + r'，、；：（）])', '', s)
        s = re.sub(r'(?<=[，、；：（）])\s+(?=[' + CJK + r'])', '', s)
    return s

def split_pages(text):
    parts = re.split(r'<<<PAGE (p\d+)>>>', text)
    pages = []
    for i in range(1, len(parts), 2):
        pages.append((parts[i], parts[i + 1]))
    return pages

def extract_pairs(page_text):
    t = norm_cjk_spaces(page_text)
    # 统一 pos 标记前的分隔
    chunks = re.split(r'\s*(' + POS + r')\s*[·．.。]\s*', t)
    out = []
    i = 0
    # chunks: [pre, pos, meaning, pre, pos, meaning, ...]
    while i + 2 < len(chunks) + 1 and i + 1 < len(chunks):
        pre = chunks[i] if i < len(chunks) else ''
        if i + 2 >= len(chunks):
            break
        pos = chunks[i + 1]
        meaning = chunks[i + 2]
        # 从 pre 末尾取英文单词
        mwords = re.findall(r"[A-Za-z][A-Za-z'\-]{1,}", pre)
        if mwords:
            word = mwords[-1]
            # 考虑两词短语 (末两个都是字母且前一个很短)
            if len(mwords) >= 2 and len(word) <= 4:
                word = mwords[-2] + ' ' + word
        else:
            word = ''
        # 取 meaning 起始的中文串
        mm = re.match(r'([' + CJK + r'][^A-Za-z]{0,24})', meaning)
        mean = mm.group(1).strip() if mm else ''
        mean = mean.strip('，、；： ')
        if word and mean and len(mean) <= 20:
            # 过滤乱码
            cjk = len(re.findall('[' + CJK + ']', mean))
            if cjk >= 1 and cjk / max(1, len(mean)) >= 0.6 and not re.search(r'[丿丨刁氵礻胤洱]', mean):
                out.append((word.lower(), mean))
        i += 3
    return out

def main():
    text = open(OCR, encoding='utf-8').read()
    pages = split_pages(text)

    pairs = []
    for name, body in pages:
        for w, m in extract_pairs(body):
            pairs.append((w, m))

    # 去重 (按单词)
    seen = {}
    for w, m in pairs:
        if w not in seen:
            seen[w] = m
    items_raw = list(seen.items())
    print(f"解析出单词: {len(items_raw)}")

    # 频率: 统计单词列表页 (p004~p039) 中每个词出现次数
    freq = Counter()
    ascii_word = re.compile(r"[A-Za-z][A-Za-z'\-]{2,}")
    for name, body in pages:
        num = int(name[1:])
        if 4 <= num <= 42:
            for w in ascii_word.findall(body):
                freq[w.lower()] += 1

    # 构建选项: 干扰项从其它词义中取
    meanings = [m for _, m in items_raw]
    items = []
    for idx, (w, m) in enumerate(items_raw):
        cands = [x for x in meanings if x != m and abs(len(x) - len(m)) <= 6]
        random.shuffle(cands)
        opts = [m] + cands[:3]
        # 去重补足
        if len(set(opts)) < 4:
            for x in random.sample(meanings, min(20, len(meanings))):
                if x not in opts:
                    opts.append(x)
                if len(set(opts)) >= 4:
                    break
        opts = list(dict.fromkeys(opts))[:4]
        if len(opts) < 4:
            continue
        random.shuffle(opts)
        items.append({
            'id': f'w{idx+1}',
            'word': w,
            'meaning': m,
            'options': opts,
            'freq': freq.get(w, 0),
        })

    os.makedirs(os.path.join(APP, 'quiz'), exist_ok=True)
    out = {'version': 1, 'items': items}
    with open(os.path.join(APP, 'quiz', 'words.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f"✅ 单词题 {len(items)} 道 -> quiz/words.json")
    for it in items[:6]:
        print('  ', it['word'], '|', it['meaning'], '| freq', it['freq'], '|', it['options'])

if __name__ == '__main__':
    main()
