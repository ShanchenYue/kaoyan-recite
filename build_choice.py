# -*- coding: utf-8 -*-
"""解析肖八选择题 (试题册OCR) + 匹配答案 (人工核对的答案表) -> quiz/choice.json"""
import re, json, os

OCR_S = r"d:\Desktop\背诵\ocr\xiaoba_shiti.txt"
OCR_J = r"d:\Desktop\背诵\ocr\xiaoba_jiexi.txt"
ANS = r"d:\Desktop\背诵\ocr\answers_xiaoba.json"
APP = os.path.dirname(os.path.abspath(__file__))

SET_CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8}


def norm(s):
    p = None
    while p != s:
        p = s
        s = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff，、；：（）《》“”])', '', s)
        s = re.sub(r'(?<=[，、；：（）《》“”])\s+(?=[\u4e00-\u9fff])', '', s)
    s = s.replace('\u3000', ' ')
    # OCR 常把相邻数字拆开: "1 1" -> "11"
    s = re.sub(r'(?<=\d)\s+(?=\d)', '', s)
    return s


def split_sets(text):
    """按 冲刺套卷X / 8套卷（X） 切分为 8 段"""
    text = norm(text)
    # 找所有 套卷（X）或 套卷X 的位置
    marks = []
    for m in re.finditer(r'套\s*卷\s*[（(]\s*([一二三四五六七八])\s*[)）]', text):
        marks.append((m.start(), SET_CN[m.group(1)]))
    if len(marks) < 8:
        for m in re.finditer(r'套\s*卷\s*([一二三四五六七八])', text):
            marks.append((m.start(), SET_CN[m.group(1)]))
    marks.sort()
    # 取每个套卷第一次出现的位置
    first = {}
    for pos, k in marks:
        if k not in first:
            first[k] = pos
    return first, text


def opt_letters(body):
    lets = []
    for m in re.finditer(r'(?<![A-Za-z0-9])([A-Da-d&])\s*[.．、,，]', body):
        let = 'B' if m.group(1) == '&' else m.group(1).upper()
        if let not in lets:
            lets.append(let)
    return lets


def parse_all(text):
    """状态机扫描: 只接受连续递增的题号, 并用「后面有4个选项」校验"""
    cands = []
    for m in re.finditer(r'(?<![\d.\-])(\d{1,2})\s*[．.、,，]', text):
        n = int(m.group(1))
        if 1 <= n <= 33:
            cands.append((m.start(), m.end(), n))
    cands.sort()

    accepted = []
    expect = 1
    i = 0
    while i < len(cands):
        pos, end, n = cands[i]
        if n != expect:
            i += 1
            continue
        # 找下一个「可能」的接受点做区间校验
        # 在 pos 之后找第一个 n+1 (或 1) 的候选
        nxt_pos = len(text)
        j = i + 1
        while j < len(cands):
            if cands[j][2] == (n + 1 if n < 33 else 1):
                nxt_pos = cands[j][0]
                break
            if cands[j][2] == expect:
                # 出现了重复的当前题号, 说明当前 pos 是假的
                nxt_pos = -1
                break
            j += 1
        body = text[end:nxt_pos] if nxt_pos > 0 else text[end:end + 600]
        letters = opt_letters(body)
        if nxt_pos > 0 and len(letters) >= 3:
            accepted.append((n, pos, end, nxt_pos))
            expect = n + 1 if n < 33 else 1
            i = j
        else:
            i += 1
    return accepted


def parse_questions(seg, expected_qnums):
    """兼容旧接口: 用状态机解析并组装"""
    accepted = parse_all(seg)
    results = []
    for n, pos, end, nxt in accepted:
        body = seg[end:nxt]
        body = re.split(r'<<<PAGE', body)[0]
        chosen = []
        seen = set()
        for m in re.finditer(r'(?<![A-Za-z0-9])([A-Da-d&])\s*[.．、,，]\s*', body):
            let = 'B' if m.group(1) == '&' else m.group(1).upper()
            if let in seen:
                continue
            seen.add(let)
            chosen.append((let, m))
            if len(chosen) == 4:
                break
        if len(chosen) < 4:
            results.append({'q': n, 'stem': body.strip(), 'options': {}, 'raw_opts': len(chosen)})
            continue
        stem = body[:chosen[0][1].start()].strip()
        opts_dict = {}
        for i2, (let, m) in enumerate(chosen):
            oe = chosen[i2 + 1][1].start() if i2 + 1 < len(chosen) else len(body)
            txt = re.sub(r'\s+', ' ', body[m.end():oe].strip())
            opts_dict[let] = txt
        results.append({'q': n, 'stem': stem, 'options': opts_dict, 'raw_opts': len(chosen)})
    return results


def set_segments(text):
    """按 8 个「单项选择」标题切分为 8 段"""
    starts = [m.start() for m in re.finditer(r'单\s*项\s*选\s*择', text)]
    segs = []
    for k, st in enumerate(starts[:8]):
        en = starts[k + 1] if k + 1 < len(starts) else len(text)
        segs.append(text[st:en])
    return segs


MARK = re.compile(r'(?<![\d.\-])(\d{1,2})\s*[．.、,，](?!\d)')


def parse_set(seg):
    """用题号定位, 每个题号一次, body 到下一个题号为止"""
    marks = []
    seen = set()
    for m in MARK.finditer(seg):
        n = int(m.group(1))
        if 1 <= n <= 33 and n not in seen:
            seen.add(n)
            marks.append((m.start(), m.end(), n))
    marks.sort()
    results = {}
    for i, (pos, end, n) in enumerate(marks):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(seg)
        body = seg[end:nxt]
        body = re.split(r'材料分析题|<<<PAGE', body)[0]
        # 去掉页眉页脚噪声
        body = re.sub(r'公众号[:：]?不止考研[，,]?\s*免?费?分享?', '', body)
        body = re.sub(r'\d{0,2}\s*考研政治冲刺\s*[O08]?\s*套卷[（(]?[一二三四五六七八]?[)）]?', '', body)
        chosen = []
        seenL = set()
        for m in re.finditer(r'(?<![A-Za-z0-9])([A-Da-d&])\s*[.．、,，]\s*', body):
            let = 'B' if m.group(1) == '&' else m.group(1).upper()
            if let in seenL:
                continue
            seenL.add(let)
            chosen.append((let, m))
            if len(chosen) == 4:
                break
        if len(chosen) < 4:
            continue
        stem = body[:chosen[0][1].start()].strip()
        stem = re.sub(r'\s+', ' ', stem)
        opts = {}
        for i2, (let, m) in enumerate(chosen):
            oe = chosen[i2 + 1][1].start() if i2 + 1 < len(chosen) else len(body)
            opts[let] = re.sub(r'\s+', ' ', body[m.end():oe].strip())
        if len(stem) < 6 or any(len(v) < 1 for v in opts.values()):
            continue
        results[n] = {'stem': stem, 'options': opts}
    return results


def main():
    raw = open(OCR_S, encoding='utf-8').read()
    text = norm(raw)
    answers = json.load(open(ANS, encoding='utf-8'))
    segs = set_segments(text)
    print(f"套卷段数: {len(segs)}")

    items = []
    jmap = parse_jiexi(answers)
    hit = 0
    for k, seg in enumerate(segs, 1):
        qmap = parse_set(seg)
        cnt = 0
        for q in range(1, 34):
            if q not in qmap:
                continue
            x = qmap[q]
            answer = answers[str(k)]['single'][q - 1] if q <= 16 else answers[str(k)]['multi'][q - 17]
            explain = jmap.get((k, q), '')
            if explain:
                hit += 1
            else:
                good = [x['options'].get(c, '') for c in answer if c in x['options']]
                explain = '正确答案：%s。正确选项：%s。' % (answer, '；'.join(good))
            items.append({
                'id': f'xb{k}{q:02d}',
                'set': f'肖八·套卷{k}',
                'no': q,
                'multi': q > 16,
                'stem': x['stem'],
                'options': x['options'],
                'answer': answer,
                'explain': explain,
            })
            cnt += 1
        missing = [q for q in range(1, 34) if q not in qmap]
        print(f"  套卷{k}: {cnt}/33  (缺 {missing})")
    print(f"  解析命中: {hit}/{len(items)}")

    os.makedirs(os.path.join(APP, 'quiz'), exist_ok=True)
    with open(os.path.join(APP, 'quiz', 'choice.json'), 'w', encoding='utf-8') as f:
        json.dump({'version': 1, 'items': items}, f, ensure_ascii=False, separators=(',', ':'))
    print(f"✅ 选择题 {len(items)} 道")
    for it in items[:2]:
        print('  sample', it['id'], it['answer'], '|', it['stem'][:34], '|', it['options'])


def extract_explain(jseg, q):
    if not jseg:
        return ''
    # 找 "q." 后跟 答案 的区域
    m = re.search(r'(?<![\d.])' + str(q) + r'\s*[．.、,，]\s*[^。]{0,10}?答\s*案\s*[ABCDabcd]{1,4}', jseg)
    if not m:
        return ''
    start = m.end()
    nxt = re.search(r'(?<![\d.])' + str(q + 1) + r'\s*[．.、,，]', jseg[start:])
    end = start + (nxt.start() if nxt else min(400, len(jseg) - start))
    txt = jseg[start:end]
    txt = re.sub(r'【\s*简\s*析\s*】|\[\s*简\s*析\s*\]', '', txt)
    txt = re.sub(r'\s+', '', txt)
    return txt[:300]


# ══════════════════════════════════════════════════════
#  解析册 OCR -> 每题解析
# ══════════════════════════════════════════════════════
# 解析册中 8 套「单项选择题」正文起始位置(规范化后, 见 ocr/xiaoba_jiexi.txt)
JIE_STARTS = [193, 12721, 24498, 37443, 49400, 59747, 71132, 82893]


def jiexi_text():
    t = open(OCR_J, encoding='utf-8', errors='ignore').read()
    t = re.sub(r'\s+', '', t)
    t = re.sub(r'<<<PAGEp\d{3}>>>', '', t)
    t = re.sub(r'公众号[:：]?不止考研[，,]?免?费?分享?', '', t)
    return t


def _jie_clean(txt):
    txt = re.sub(r'^[^。]{0,16}?[A-Da-d]{1,4}', '', txt)
    for _ in range(4):
        txt = re.sub(r'^[〔\[（(【][^〕\]）)】]{0,8}[〕\]）)】]', '', txt)
        txt = re.sub(r'^[，、。；：|丨丨〕\]）】\|]', '', txt)
    txt = re.sub(r'[〔\[（(【][^〕\]）)】]{0,6}[〕\]）)】]', '', txt)
    txt = re.sub(r'(答案速[查跹]?|多项选择题|单项选择题)', '', txt)
    m = re.match(r'^[^\u4e00-\u9fff]+', txt)
    if m:
        txt = txt[m.end():]
    txt = re.sub(r'^[桐徇陌狁酮厑衢額悭峥卓丨|、，。；：\s]{1,4}', '', txt)
    txt = txt.strip()
    if len(re.findall(r'[\u4e00-\u9fff]', txt)) < 24:
        return ''
    if len(txt) > 460:
        cut = txt[:460]
        p = max(cut.rfind('。'), cut.rfind('；'))
        txt = cut[:p + 1] if p > 120 else cut
    return txt


def parse_jiexi(answers):
    """返回 {(套卷, 题号): 解析文本}"""
    t = jiexi_text()
    out = {}
    for k in range(1, 9):
        st = JIE_STARTS[k - 1]
        en = JIE_STARTS[k] if k < 8 else len(t)
        seg = t[st:en]
        seg = re.sub(r'[0-9Oo]{0,4}[烤考]研政[治洽氵台]冲刺[0-9Ooß]?套卷[（(〈]?[一二三四五六七八直t丿l]*[)）]?[答嗒]案[及发]解[析霎霁帝麂]?', '', seg)
        if '答案速' in seg[:320]:
            p = seg.find('。')
            if 0 < p < 500:
                seg = seg[p + 1:]
        cands = []
        for m in re.finditer(r'(?<!\d)(\d{1,2})(?!\d)', seg):
            n = int(m.group(1))
            if not (1 <= n <= 33):
                continue
            head = seg[m.end():m.end() + 12]
            lets = set(re.findall(r'[A-Da-d]', head.upper()))
            if not lets:
                continue
            exp = set(answers[str(k)]['single'][n - 1] if n <= 16 else answers[str(k)]['multi'][n - 17])
            if len(lets & exp) >= max(1, len(exp) - 1) and len(lets - exp) <= 1:
                cands.append((m.start(), m.end(), n))
        cands.sort()
        for i, (pos, end, n) in enumerate(cands):
            if (k, n) in out:
                continue
            nxt = len(seg)
            for c in cands[i + 1:]:
                if c[0] > end + 20:
                    nxt = c[0]
                    break
            txt = _jie_clean(seg[end:min(nxt, end + 900)])
            if txt:
                out[(k, n)] = txt
    return out


if __name__ == '__main__':
    main()
