"""
同步前端资源到 Android assets 目录
- 把 data.json 内联到 index.html (绕过 WebView file:// fetch 限制)
- 同步 audios 目录
- 复制 sw.js / manifest.json
"""
import json, os, shutil, re

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS  = os.path.join(APP_DIR, 'android', 'app', 'src', 'main', 'assets')

print("📦 同步前端资源到 Android assets...")

# 1. 读 data.json
with open(os.path.join(APP_DIR, 'data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
data_json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# 2. 读原始 index.html
with open(os.path.join(APP_DIR, 'index.html'), 'r', encoding='utf-8') as f:
    html = f.read()

# 3. 把 fetch 那段替换成直接用内联数据
old_fetch = """  // 加载数据
  try {
    const r = await fetch('data.json', { cache: 'no-store' });
    state.data = await r.json();
  } catch(e) {
    // 直接打开HTML时fetch会被CORS阻止，回退到相对路径
    alert('无法加载 data.json，请使用本地服务器启动。\\n\\nWindows: 在本文件夹执行:\\npython -m http.server 8000\\n然后浏览器打开 http://localhost:8000/');
    document.getElementById('loading').remove();
    return;
  }"""

new_fetch = """  // 加载数据 (Android WebView file:// 协议直接读 window.__APP_DATA__)
  state.data = window.__APP_DATA__;
  if (!state.data || !state.data.books) {
    alert('数据加载失败');
    document.getElementById('loading').remove();
    return;
  }"""

if old_fetch in html:
    html = html.replace(old_fetch, new_fetch)
    print("  ✅ fetch 替换为内联数据加载")
else:
    # 可能上次已经替换过了, 或略有不同
    html = re.sub(
        r"try\s*\{\s*const r = await fetch\('data\.json'[^}]+state\.data = await r\.json\(\)[^}]+catch\(e\)\s*\{[^}]+\}",
        new_fetch, html, flags=re.DOTALL
    )
    print("  ✅ fetch 正则替换完成")

# 4. 在 </head> 前插入内联 JSON
inline_tag = f'<script>window.__APP_DATA__ = {data_json_str};</script>'
html = html.replace('</head>', inline_tag + '\n</head>', 1)

# 5. 写 APK 专用 index.html
os.makedirs(ASSETS, exist_ok=True)
out_html = os.path.join(ASSETS, 'index.html')
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"  ✅ index.html (内联版) → {out_html}  ({len(html)} bytes)")

# 6. 同步 audios
src_audios = os.path.join(APP_DIR, 'audios')
dst_audios = os.path.join(ASSETS, 'audios')
if os.path.isdir(src_audios):
    if os.path.exists(dst_audios):
        shutil.rmtree(dst_audios)
    shutil.copytree(src_audios, dst_audios)
    count = sum(1 for _ in os.walk(dst_audios) for f in _[2] if f.endswith('.mp3'))
    print(f"  ✅ audios 目录同步 ({count} 个 MP3)")
else:
    print("  ⚠️  没有 audios 目录, 跳过")

# 7. 复制其他静态文件
for fname in ['sw.js', 'manifest.json', 'icon.svg', 'quiz.html', 'quiz_data.js', 'plan.html', 'plan_data.js', 'auth.js']:
    src = os.path.join(APP_DIR, fname)
    if os.path.isfile(src):
        shutil.copy2(src, os.path.join(ASSETS, fname))
        print(f"  ✅ {fname}")

# 7.1 复制 KaTeX (公式离线渲染)
src_katex = os.path.join(APP_DIR, 'vendor', 'katex')
dst_katex = os.path.join(ASSETS, 'vendor', 'katex')
if os.path.isdir(src_katex):
    if os.path.exists(dst_katex):
        shutil.rmtree(dst_katex)
    shutil.copytree(src_katex, dst_katex)
    print("  ✅ vendor/katex 同步")

# 7.2 复制数学公式题图片
src_math = os.path.join(APP_DIR, 'math')
dst_math = os.path.join(ASSETS, 'math')
if os.path.isdir(src_math):
    if os.path.exists(dst_math):
        shutil.rmtree(dst_math)
    shutil.copytree(src_math, dst_math)
    n = sum(1 for _ in os.walk(dst_math) for f in _[2] if f.endswith('.webp'))
    print(f"  ✅ math 公式题图片同步 ({n} 张)")

# 8. 同步 data.json 到 assets (备份, 以防万一)
shutil.copy2(os.path.join(APP_DIR, 'data.json'), os.path.join(ASSETS, 'data.json'))
print("  ✅ data.json (独立备份)")

print("\n✅ 全部同步完成!")
