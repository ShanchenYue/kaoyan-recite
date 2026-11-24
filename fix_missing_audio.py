# -*- coding: utf-8 -*-
"""把 data.json 中「MP3 实际不存在或过小」的段落 audio 置空，避免播放卡死。"""
import json, os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(APP_DIR, 'data.json')

with open(DATA, 'r', encoding='utf-8') as f:
    data = json.load(f)

cleared = 0
ok = 0
for book in data.get('books', []):
    for seg in book.get('segments', []):
        a = seg.get('audio') or ''
        if not a:
            continue
        p = os.path.join(APP_DIR, a.replace('/', os.sep))
        if os.path.isfile(p) and os.path.getsize(p) > 500:
            ok += 1
        else:
            seg['audio'] = ''
            cleared += 1

if cleared:
    with open(DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print(f"有音频: {ok}, 置空: {cleared}")
