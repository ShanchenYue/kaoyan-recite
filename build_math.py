# -*- coding: utf-8 -*-
"""把「数学核心公式测试」学生版 + 解析版渲染成图片题，生成 quiz/math.json"""
import os, re, json, io, glob
import pypdfium2 as pdfium
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
STU = r"d:\Desktop\背诵\数学资源\考研数学核心公式（学生版）.pdf"
ANS_DIR = r"d:\Desktop\背诵\数学资源\解析版(1)"
OUT_IMG = os.path.join(BASE, "math")
OUT_JSON = os.path.join(BASE, "quiz", "math.json")

CAT_KEY = {"高数": "gaoshu", "线代": "xiandai", "概率": "gailv"}
CAT_CN = {"gaoshu": "高数", "xiandai": "线代", "gailv": "概率"}


def render(pdf, page_idx, width, dst):
    pg = pdf[page_idx]
    w, h = pg.get_size()
    img = pg.render(scale=width / w).to_pil().convert("RGB")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img.save(dst, "WEBP", quality=80, method=6)
    return os.path.getsize(dst)


def main():
    stu = pdfium.PdfDocument(STU)
    total = len(stu)
    # 目录
    import pdfplumber
    with pdfplumber.open(STU) as p:
        toc_txt = (p.pages[0].extract_text() or "") + "\n" + (p.pages[1].extract_text() or "")
    tests = []
    for line in toc_txt.splitlines():
        m = re.search(r"数学核心公式测试\s*(\S+?)第\s*(\d+)\s*次(.*?)\.{2,}\s*(\d+)", line)
        if not m:
            continue
        cat, no, note, page = m.group(1), int(m.group(2)), m.group(3).strip(), int(m.group(4))
        if cat not in CAT_KEY:
            continue
        tests.append({"cat": cat, "no": no, "note": note, "start": page})
    tests.sort(key=lambda x: (["高数", "线代", "概率"].index(x["cat"]), x["no"]))

    # 解析版文件
    ans_files = {}
    for f in glob.glob(os.path.join(ANS_DIR, "*.pdf")):
        name = os.path.basename(f)
        m = re.search(r"(高数|线代|概率)\s*(\d+)", name)
        if m:
            cat, fno = m.group(1), int(m.group(2))
            no = fno if cat == "高数" else fno - (13 if cat == "线代" else 20)
            ans_files[(cat, no)] = f

    out = []
    for i, t in enumerate(tests):
        start = t["start"]
        end = tests[i + 1]["start"] - 1 if i + 1 < len(tests) else total
        catk = CAT_KEY[t["cat"]]
        tid = "%s%d" % (catk, t["no"])
        pages, answers = [], []
        # 学生版（题目）
        for n, pi in enumerate(range(start - 1, end)):
            rel = "math/%s/%d/q%02d.webp" % (catk, t["no"], n + 1)
            render(stu, pi, 1200, os.path.join(BASE, rel))
            pages.append(rel)
        # 解析版（答案）
        af = ans_files.get((t["cat"], t["no"]))
        if af:
            ap = pdfium.PdfDocument(af)
            for n in range(len(ap)):
                rel = "math/%s/%d/a%02d.webp" % (catk, t["no"], n + 1)
                render(ap, n, 1200, os.path.join(BASE, rel))
                answers.append(rel)
        out.append({
            "id": tid,
            "cat": catk,
            "catName": t["cat"],
            "no": t["no"],
            "title": "%s第%d次%s" % (t["cat"], t["no"], t["note"]),
            "pages": pages,
            "answers": answers,
        })
        print("  %s: %d 题页 / %d 解析页" % (tid, len(pages), len(answers)))

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "tests": out}, f, ensure_ascii=False, separators=(",", ":"))

    n_img = sum(1 for _ in glob.glob(os.path.join(OUT_IMG, "*", "*", "*.webp")))
    size = sum(os.path.getsize(p) for p in glob.glob(os.path.join(OUT_IMG, "*", "*", "*.webp")))
    print("✅ %d 套测试, %d 张图片, %.1f MB" % (len(out), n_img, size / 1024 / 1024))


if __name__ == "__main__":
    main()
