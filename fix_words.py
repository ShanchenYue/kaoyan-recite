# -*- coding: utf-8 -*-
"""
校对并修复单词库（只改词条内容，保留 id / freq，学习进度不丢）
- 用 ECDICT 校正 OCR 错词与错误释义
- 清理乱码释义
- 用干净释义重建四选一干扰项
用法: python fix_words.py [--dry]
"""
import csv, json, io, os, re, sys, random

APP = os.path.dirname(os.path.abspath(__file__))
WORDS = os.path.join(APP, 'quiz', 'words.json')
DICT_CSV = os.path.join(os.environ.get('TEMP', '.'), 'ecdict.csv')
random.seed(42)

# OCR 错词 → 正确词（括号内为必要时的人工释义）
FIX = {
    'ln ry': 'inquiry', 'pr macy': 'primacy', 'the cuff': 'off the cuff',
    'excesslve': 'excessive', 'margln': 'margin', 'promlslng': 'promising',
    'collrlsel': 'counsel', 'spec es': 'species', 'gnevance': 'grievance',
    'refa': 'refine', 'sery': 'misery', 'imply rl': 'marine',
    'envls on': 'envision', 'lnlqlle': 'unique', 'rev se': 'revise',
    'compromlse': 'compromise', 'coioniai': 'colonial', 'preclslon': 'precision',
    'at deem': 'deem', 'eat very': 'verify', 'lmpalr': 'impair',
    'persuaslve': 'persuasive', 'glve away': 'give away', 'subsidize zeal': 'zeal',
    'top-tier': 'top-tier', 'consplre': 'conspire', 'cunmng': 'cunning',
    'campalgn': 'campaign', 'en ia': 'millennial', 'pern ous': 'pernicious',
    'progress ve': 'progressive', 'across pool': 'cohort', 'prommence': 'prominence',
    'open feve': 'fever', 'to bar': 'bar', 'success ve': 'successive',
    'rnpalr': 'impair', 'dismissai': 'dismissal', 'compmse': 'comprise',
    'the wa': 'millennium', 'born-digital': 'born-digital', 'expanslve': 'expansive',
    'genulne': 'genuine', 'reclpe': 'recipe', 'back wary': 'wary',
    'ffo rd': 'afford', 'comprom se': 'compromise', 'survlve': 'survive',
    'necessity ru': 'ruin', 'verslon': 'version', 'prudent poll': 'poll',
    'marrlage': 'marriage', 'reql llre': 'require', 'expenslve': 'expensive',
    'buy int': 'buy into', 'grleve': 'grieve', 'wln-wln': 'win-win',
    'superv se': 'supervise', 'masslve': 'massive', 'wonders fo': 'rigid',
    'preclse': 'precise', 'careg ver': 'caregiver', 'painstakingly ad': 'articulate',
    'mgorous': 'rigorous', 'supemse': 'supervise', 'anonymlze': 'anonymize',
    'cot-nbine': 'combine', 'sb roam': 'superb', 'lrnpalr': 'impair',
    'scenar': 'scenario', 'emeryng': 'emerging', 've rsi': 'version',
    'prernlum': 'premium', 'energze': 'energize', 'fact hook': 'hook',
    'ad norm': 'norm',
}

# 人工释义（优先于词典，用于语境义/词典缺失）
MANUAL = {
    'off the cuff': '即兴的', 'refine': '提炼；改进', 'cohort': '一拨人',
    'rigid': '死板的', 'articulate': '用语言表达', 'verify': '证实',
    'millennium': '一千年；千禧年', 'misery': '苦难', 'impair': '损害；妨碍',
    'born-digital': '数字原生的', 'top-tier': '顶级的', 'hook': '吸引人的事物',
    'co': '共同（前缀）', 'marine': '海洋的；航海的', 'buy into': '相信；买入',
    'bar': '禁止；酒吧', 'premium': '高级的；保险费', 'articulate': '清楚表达',
    'verify': '证实', 'impair': '损害；削弱', 'refine': '提炼；改进',
    'executive': '行政的；主管', 'admin': '行政管理', 'implementation': '实施；执行',
    'deliberation': '深思熟虑；商议', 'dictate': '决定；口述',
}

JUNK_CHARS = set('彳亍阝刂扌讠彡卩纟疒')
FIXES = {
    '难心壮志': '雄心壮志', '无阝且碍的': '无阻碍的', '景彡卩向': '影响',
    '纟吉果': '结果', '纟只斗勿': '织物', '彳昱了于': '受益于',
    '彳走劳无益': '徒劳无益', '扌丸亍': '集中', '痂诱人的事物': '吸引人的事物',
    '实刂佥': '实验', '建笳物': '建筑物', '一干年': '一千年', '侵虫': '侵蚀',
    '无证明的的': '无证据的', '休目民的': '积极的', '．': '…',
}


def clean_trans(t):
    lines = [l.strip() for l in (t or '').replace('\\n', '\n').split('\n') if l.strip()]
    lines = [l for l in lines if not l.startswith('[网络]')]
    if not lines:
        return ''
    s = lines[0]
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = re.sub(r'^[A-Za-z]{1,6}\.\s*', '', s)
    s = re.sub(r'（[^）]*）|\([^)]*\)', '', s)
    s = re.sub(r'\s+', '', s)
    parts = [p.strip('，,。. ') for p in re.split(r'[；;，,]', s) if p.strip('，,。. ')]
    s = '；'.join(parts[:2])
    return s[:20]


def fix_meaning(m):
    m = (m or '').strip()
    for a, b in FIXES.items():
        m = m.replace(a, b)
    m = re.sub(r'\s*[0０]\s*$', '', m)
    m = m.replace(' ．', '…').replace('．', '…')
    m = re.sub(r'[《》]', '', m)
    m = re.sub(r'^[/、，；：\s]+|[/、，；：\s]+$', '', m)
    return m.strip()


def main():
    dry = '--dry' in sys.argv
    dic = {}
    with open(DICT_CSV, encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            w = (row['word'] or '').strip().lower()
            if w and w not in dic:
                dic[w] = row

    data = json.load(open(WORDS, encoding='utf-8'))
    items = data['items']
    changed_word = changed_meaning = 0
    problems, diffs = [], []
    for it in items:
        oldw = it['word'].strip()
        w = FIX.get(oldw.lower(), oldw)
        lw = w.lower()
        row = dic.get(lw)
        trans = clean_trans(row['translation']) if row else ''
        oldm = fix_meaning(it.get('meaning'))
        newm = oldm
        junk = bool(set(oldm) & JUNK_CHARS) or not oldm
        if lw in MANUAL:
            newm = MANUAL[lw]
        elif trans and (junk or (oldw.lower() in FIX and not (set(oldm) & set(trans)))):
            newm = trans
        if not newm:
            newm = trans or oldm or '（待补）'
            problems.append((oldw, newm))
        if w != oldw:
            it['word'] = w
            changed_word += 1
        if newm != it.get('meaning'):
            it['meaning'] = newm
            changed_meaning += 1
            diffs.append((w, oldm, newm))
        it['meaning'] = newm

    # 重建干扰项
    pool = sorted({it['meaning'] for it in items if it['meaning'] and not (set(it['meaning']) & JUNK_CHARS)})
    for it in items:
        m = it['meaning']
        cands = [x for x in pool if x != m]
        random.shuffle(cands)
        opts = [m] + cands[:3]
        seen, out = set(), []
        for o in opts:
            if o not in seen:
                seen.add(o); out.append(o)
        while len(out) < 4:
            x = random.choice(pool)
            if x not in seen:
                seen.add(x); out.append(x)
        random.shuffle(out)
        it['options'] = out

    print(f'词数 {len(items)}，修正单词 {changed_word}，修正释义 {changed_meaning}，仍缺释义 {len(problems)}')
    for p in problems[:10]:
        print('  待补:', p)
    random.shuffle(diffs)
    for w, a, b in diffs[:35]:
        print('  改:', w, '|', a, '→', b)
    if dry:
        print('（dry-run，未写入）')
        return
    json.dump(data, open(WORDS, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('✅ 已写入 quiz/words.json')


if __name__ == '__main__':
    main()
