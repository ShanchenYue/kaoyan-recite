# -*- coding: utf-8 -*-
"""
扫描 audios 目录，更新 data.json 给每个 segment 加上 audio 字段
在 gen-audio.mjs 跑完后执行，或者每次启动前执行一次
"""
import os, json, glob

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE, 'audios')
DATA_PATH = os.path.join(BASE, 'data.json')

data = json.loads(open(DATA_PATH, encoding='utf-8').read())

total_audio = 0
for bi, book in enumerate(data['books']):
    if book.get('is_scanned'): continue
    book_dir = os.path.join(AUDIO_DIR, f"{bi:02d}")
    has_audio = os.path.isdir(book_dir)
    book['audio_voice'] = None
    if has_audio:
        mp3s = set(os.listdir(book_dir))
        voice_map = {0: 'zh-CN-XiaoyiNeural', 1: 'zh-CN-YunxiNeural',
                     2: 'zh-CN-XiaohanNeural', 3: 'zh-CN-XiaoxiaoNeural'}
        book['audio_voice'] = voice_map.get(bi, 'zh-CN-XiaoyiNeural')
        found = 0
        for si, seg in enumerate(book['segments']):
            fname = f"{si:04d}.mp3"
            if fname in mp3s:
                seg['audio'] = f"audios/{bi:02d}/{fname}"
                found += 1
            else:
                seg.pop('audio', None)
        total_audio += found
        print(f"  {book['main_category']}: {found}/{len(book['segments'])} 条有音频")
    else:
        for seg in book['segments']:
            seg.pop('audio', None)

with open(DATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n共 {total_audio} 个音频片段已索引")
