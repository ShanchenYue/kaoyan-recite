# -*- coding: utf-8 -*-
"""
校对肖八选择题：清理题干噪声、修正错答、剔除错位解析
- 解析若与本題题干无关（字符重合度过低），改为「正确答案 + 正确选项」的准确简析
- 保留与題干匹配的原有解析
用法: python fix_choice.py [--dry]
"""
import json, os, re, sys

APP = os.path.dirname(os.path.abspath(__file__))
CHOICE = os.path.join(APP, 'quiz', 'choice.json')

NOISE = ['公众号', '不止考研', '考研政治冲刺', '回回关', '免费分享', '免囹料', '获史免', '扫码']


def grams(s):
    s = re.sub(r'[^\u4e00-\u9fff]', '', s or '')
    return {s[i:i + 2] for i in range(len(s) - 1)}


def clean_text(s):
    s = (s or '').replace('\u3000', ' ')
    for mk in NOISE:
        i = s.find(mk)
        if i > 10:
            s = s[:i]
    s = re.sub(r'[．.]\s*一\s*[．.](?:\s*[．.])*', ' ', s)
    s = re.sub(r'(?:\s*[．.·]\s*){3,}', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip(' 。.')
    return s


def strip_prefix(stem):
    s = clean_text(stem)
    # "16 小题，...。下列每小题...。1 ．" 这类大题说明
    s = re.sub(r'^\d{1,2}\s*小题[^。]*。\s*(?:[^。]*。\s*)?', '', s)
    s = re.sub(r'^\d{1,2}\s*[．.、,，]\s*', '', s)
    return s.strip()


def generic(it):
    good = [it['options'][k] for k in it['answer'] if k in it['options']]
    return '正确答案：%s。正确选项：%s。' % (it['answer'], '；'.join(good))


# 人工修正（有据可查的错答）
FIX_ANSWER = {
    'xb227': ('BCD', '正确答案：BCD。A项错误：反帝反封建的民主革命纲领是1922年党的二大提出的，'
                      '并非“成立之初”（中共一大）提出。B、C、D三项均符合史实。'),
}


def main():
    dry = '--dry' in sys.argv
    data = json.load(open(CHOICE, encoding='utf-8'))
    n_prefix = n_explain = n_answer = 0
    for it in data['items']:
        old_stem = it['stem']
        it['stem'] = strip_prefix(old_stem)
        if it['stem'] != old_stem:
            n_prefix += 1
        for k in list(it['options']):
            it['options'][k] = clean_text(it['options'][k])
        if it['id'] in FIX_ANSWER:
            it['answer'], it['explain'] = FIX_ANSWER[it['id']]
            n_answer += 1
            continue
        ex = clean_text(it['explain'])
        keep = ex.startswith('正确答案：') and it['answer'] in ex[:14]
        if not keep:
            # 与「题干 + 正确选项」比较：解析若在讲别的题，重合度会极低
            q = it['stem'] + ''.join(it['options'].get(k, '') for k in it['answer'])
            a, b = grams(q), grams(ex)
            r = len(a & b) / max(1, min(len(a), len(b))) if a and b else 0
            keep = r >= 0.18
        if not keep:
            ex = generic(it)
            n_explain += 1
        it['explain'] = ex

    print(f'共 {len(data["items"])} 题：清理题干 {n_prefix}，重写解析 {n_explain}，修正错答 {n_answer}')
    for it in data['items']:
        if it['id'] in ('xb201', 'xb227'):
            print(' ', it['id'], it['answer'], '|', it['stem'][:60], '|', it['explain'][:80])
    if dry:
        print('（dry-run，未写入）')
        return
    json.dump(data, open(CHOICE, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('✅ 已写入 quiz/choice.json')


if __name__ == '__main__':
    main()
