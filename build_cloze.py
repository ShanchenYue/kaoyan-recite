"""
从 data.json 的背诵段落生成「政治挖空」题库
输出 quiz/cloze.json
"""
import json, os, re, random

APP = os.path.dirname(os.path.abspath(__file__))
random.seed(42)

# ── 关键词后接答案的模式 (捕获 2~14 个中文字符) ──
KW_PATTERNS = [
    r'[《]([^》]{2,30})[》]',
    r'[“"]([^”"]{2,20})[”"]',
    r'(\d{4})\s*年',
    r'(\d+(?:\.\d+)?\s*%)',
    r'(?:标志着|称之为|被称为|体现了|意味着|核心是|关键是|根本是|本质是|实质是|目的是|目标是|要求是|指的是|就是指|在于)'
    r'([^，。；、：！？\s的]{2,12})',
]
KW_RES = [re.compile(p) for p in KW_PATTERNS]

# 兜底: 取「的」之后的名词性短语
FALLBACK = re.compile(r'的([^，。；、：！？\s的]{3,9})')

# 干扰项必须像「完整术语」
CLEAN_RE = re.compile(r'^[\u4e00-\u9fa5A-Za-z0-9%＋+\-\.·]{2,16}$')
BAD_END = ('是', '的', '和', '与', '在', '把', '被', '了', '着', '为', '以', '对', '从')


def is_clean(a):
    if not a or not CLEAN_RE.match(a):
        return False
    if a.endswith(BAD_END):
        return False
    # 排除夹杂题号/选项的碎片
    if re.search(r'[A-DＡ-Ｄ][\.．、]', a):
        return False
    return True


def find_blanks(text):
    """返回 [(start,end,answer)] 不重叠, 最多 2 个"""
    spans = []
    used = [False] * len(text)
    for rx in KW_RES:
        for m in rx.finditer(text):
            g = 1 if rx.groups else 0
            s, e = m.span(g)
            ans = m.group(g)
            if not ans or len(ans) < 2:
                continue
            if any(used[s:e]):
                continue
            # 不要挖到句首
            if s == 0:
                continue
            spans.append((s, e, ans))
            for i in range(s, e):
                used[i] = True
            if len(spans) >= 2:
                return spans
    if spans:
        return spans
    # 兜底
    m = FALLBACK.search(text)
    if m:
        s, e = m.span(1)
        if 3 <= e - s <= 10:
            return [(s, e, m.group(1))]
    return []


def make_item(seg, sid, book_name, sub):
    text = (seg.get('text') or '').strip()
    if len(text) < 12:
        return None
    spans = find_blanks(text)
    if not spans:
        return None
    # 按位置从后往前替换, 保持索引
    spans.sort(key=lambda x: x[0])
    template = ''
    last = 0
    blanks = []
    for i, (s, e, ans) in enumerate(spans):
        template += text[last:s] + '〔{}〕'.format(i + 1)
        blanks.append(ans)
        last = e
    template += text[last:]
    if len(blanks) > 2:
        return None
    return {
        'id': f'c{sid}',
        'book': book_name,
        'sub': sub or '',
        'template': template,
        'blanks': blanks,
        'audio': seg.get('audio', ''),
        'full': text,
    }


def main():
    with open(os.path.join(APP, 'data.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = []
    sid = 0
    for book in data['books']:
        book_name = book.get('main_category', '')
        for seg in book.get('segments', []):
            sid += 1
            it = make_item(seg, sid, book_name, seg.get('sub'))
            if it:
                items.append(it)

    # 构建干扰项池: 按答案长度分组 (只保留像术语的)
    pool = {}
    for it in items:
        for b in it['blanks']:
            if is_clean(b):
                pool.setdefault(len(b), set()).add(b)
    all_answers = [b for it in items for b in it['blanks'] if is_clean(b)]

    # 给每个空配 3 个干扰项
    for it in items:
        opts_all = []
        for b in it['blanks']:
            cands = set()
            for d in (-1, 0, 1, 2, -2):
                k = len(b) + d
                cands |= pool.get(k, set())
            cands.discard(b)
            cands = [c for c in cands if c and c != b]
            random.shuffle(cands)
            opts = [b] + cands[:3]
            while len(opts) < 4:
                opts.append(random.choice(all_answers))
            # 去重保底
            seen = []
            for o in opts:
                if o not in seen:
                    seen.append(o)
            if len(seen) < 4:
                while len(seen) < 4:
                    x = random.choice(all_answers)
                    if x not in seen:
                        seen.append(x)
            random.shuffle(seen)
            opts_all.append(seen)
        it['options'] = opts_all

    out = {'version': 1, 'items': items}
    os.makedirs(os.path.join(APP, 'quiz'), exist_ok=True)
    with open(os.path.join(APP, 'quiz', 'cloze.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

    # 统计
    from collections import Counter
    bc = Counter(it['book'] for it in items)
    print(f"✅ 挖空题 {len(items)} 道")
    for k, v in bc.items():
        print(f"   {k}: {v}")


if __name__ == '__main__':
    main()
