# -*- coding: utf-8 -*-
"""把扫描版 PDF 逐页渲染成 PNG, 供 Windows OCR 使用"""
import os, sys, pdfplumber

OUT_ROOT = r"d:\Desktop\背诵\ocr"

JOBS = [
    (r"d:\Desktop\背诵\资源\27肖秀荣《八套卷》【试题册】【公众号：不止考研】免费分享.pdf", "xiaoba_shiti"),
    (r"d:\Desktop\背诵\资源\27肖秀荣《八套卷》【解析册】【公众号：不止考研】免费分享.pdf", "xiaoba_jiexi"),
    (r"d:\Desktop\背诵\英语资源\考研英语真题词汇汇编 V20260702(1).pdf", "english_vocab"),
]


def run(pdf_path, tag, dpi=180):
    out_dir = os.path.join(OUT_ROOT, tag)
    os.makedirs(out_dir, exist_ok=True)
    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages)
        print(f"[{tag}] {n} pages -> {out_dir}")
        for i, page in enumerate(pdf.pages):
            png = os.path.join(out_dir, f"p{i+1:03d}.png")
            if os.path.isfile(png) and os.path.getsize(png) > 5000:
                continue
            im = page.to_image(resolution=dpi)
            im.save(png)
            if (i + 1) % 10 == 0:
                print(f"   {i+1}/{n}")
    print(f"[{tag}] done")


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    for path, tag in JOBS:
        if which == 'all' or which == tag:
            run(path, tag)
