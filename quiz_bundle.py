"""
把 quiz/*.json 打包成前端可直接引用的 quiz_data.js
缺失的题库用空结构补齐, 保证 quiz.html 不报错
"""
import json, os

APP = os.path.dirname(os.path.abspath(__file__))
QUIZ = os.path.join(APP, 'quiz')

MAP = {
    'cloze.json':  ('__QUIZ_CLOZE__',  {'version': 0, 'items': []}),
    'choice.json': ('__QUIZ_CHOICE__', {'version': 0, 'items': []}),
    'words.json':  ('__QUIZ_WORDS__',  {'version': 0, 'items': []}),
    'fill.json':   ('__QUIZ_FILL__',   {'version': 0, 'items': []}),
    'math.json':   ('__QUIZ_MATH__',   {'version': 0, 'tests': []}),
}

parts = []
for fname, (gvar, default) in MAP.items():
    path = os.path.join(QUIZ, fname)
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        n = len(obj.get('items', obj.get('tests', [])))
        print(f"  {gvar}: {n} 条")
    else:
        obj = default
        print(f"  {gvar}: 缺失 → 空")
    parts.append(f"window.{gvar} = " + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ";")

out = os.path.join(APP, 'quiz_data.js')
with open(out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(parts) + '\n')
print(f"✅ quiz_data.js 生成 ({os.path.getsize(out)} bytes)")
