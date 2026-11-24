"""
给 data.json 里每个 segment 补上 audio 路径
规则: book_index/seq_index.mp3
"""
import json, os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, 'data.json')

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 书的索引 → 音频目录前缀
# book[0] = audios/00/, book[1] = audios/01/, book[3] = audios/03/
BOOK_IDX_MAP = {
    0: '00',   # 1-10月时政热点
    1: '01',   # 肖190题
    2: '02',   # 周年事件 (扫描版, 暂时没 segments)
    3: '03',   # 主观题背诵包
}

fixed = 0
skipped = 0
for bi, book in enumerate(data['books']):
    prefix = BOOK_IDX_MAP.get(str(bi), f'{bi:02d}')
    for si, seg in enumerate(book.get('segments', [])):
        expected = f'audios/{prefix}/{si:04d}.mp3'
        existing = seg.get('audio', '')
        if existing != expected:
            seg['audio'] = expected
            fixed += 1
        else:
            skipped += 1

# 加版本号
data['version'] = '3.0'

with open(DATA, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 补完: fixed={fixed}, skipped={skipped}")
print(f"data.json 版本 → {data['version']}")

# 统计 audios 目录已生成多少
AUDIOS = os.path.join(APP_DIR, 'audios')
total = 0
existing = 0
for bi, book in enumerate(data['books']):
    prefix = BOOK_IDX_MAP.get(str(bi), f'{bi:02d}')
    bookDir = os.path.join(AUDIOS, prefix)
    if os.path.isdir(bookDir):
        for si in range(len(book.get('segments', []))):
            total += 1
            mp3 = os.path.join(bookDir, f'{si:04d}.mp3')
            if os.path.isfile(mp3) and os.path.getsize(mp3) > 500:
                existing += 1
print(f"🎵 MP3: {existing}/{total} 已生成 ({total-existing} 待生成)")
