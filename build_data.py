# -*- coding: utf-8 -*-
"""
PDF → 结构化知识点 JSON 构建脚本 v2
- 更精准的目录过滤
- 章节/月份自动识别为子分类
- 扫描版PDF自动跳过并标记
"""
import os, re, json, glob
import pdfplumber

BASE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE, "..", "资源")
OUT = os.path.join(BASE, "data.json")

PDF_CATEGORIES = {
    "27 肖《背诵手册》190 题背诵版(1).pdf": {"main": "肖190题客观题", "note": "单选/多选190题"},
    "1-10月的时政热点精选.pdf": {"main": "1-10月时政热点", "note": "按月份分类"},
    "27考研政治周年事件讲义.pdf": {"main": "周年事件", "note": "扫描版，需OCR"},
    "客观题和主观题背诵包.pdf": {"main": "主观题背诵包", "note": "马原/毛中特/史纲/思修"},
}

# ────────────────────────────────────────
# 目录/噪声行判断
# ────────────────────────────────────────
def is_toc_noise(para: str) -> bool:
    """判断是否为目录/页码/跳转错误等噪声行"""
    if not para or len(para) < 4:
        return True
    # 含大量点号(≥6个) → 目录行
    if para.count(".") >= 6:
        return True
    # 含连续中文省略号
    if "……" in para and len(para) < 80:
        return True
    # 目录标题
    if para.strip() in ("目 录", "目录", "CONTENTS", "目  录"):
        return True
    # 含"错误！未定义书签。"这类PDF跳转错误
    if "错误！" in para or "未定义书签" in para:
        return True
    # 页码行(独立数字 或 数字两侧有短横线)
    if re.match(r"^[-—–]\s*\d+\s*[-—–]?$", para):
        return True
    if re.match(r"^\d{1,3}$", para):
        return True
    # 行尾就是孤立数字(目录里"xxxx.......... 23")
    if re.search(r"\s\d{1,3}$", para) and ("." in para or "……" in para):
        return True
    # 纯空格+页码
    if re.match(r"^\s+\d+\s*$", para):
        return True
    return False

def is_heading(para: str) -> bool:
    """判断是否为章节/小标题(短、名词性、无句号)"""
    if len(para) > 45:
        return False
    if re.search(r"[。！？；，,]", para):
        return False
    # 典型标题开头
    if re.match(r"^[一二三四五六七八九十]+[、.]", para):
        return True
    if re.match(r"^(\d{1,2})月", para):
        return True
    if re.match(r"^第[一二三四五六七八九十\d]+[部分章节篇]", para):
        return True
    if re.match(r"^[【\[].+[】\]]", para):
        return True
    if "重要考点" in para or "重点考点" in para or "重要预测" in para:
        return True
    if para.endswith("部分") or para.endswith("篇"):
        return True
    return False

# ────────────────────────────────────────
# PDF 文本提取
# ────────────────────────────────────────
def extract_paragraphs(pdf_path: str) -> tuple[list[dict], bool]:
    """返回 (段落列表, 是否为扫描版)"""
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            pages_text.append(t)

    total_chars = sum(len(t) for t in pages_text)
    if total_chars < 100:
        return [], True  # 扫描版

    full = "\n".join(pages_text)

    # 步骤1：合并"PDF断行"——把同一语义单元的折行拼回
    lines = full.split("\n")
    merged = []
    buf = ""

    def fix(line: str) -> str:
        line = line.replace("  ", " ").replace("　", " ")
        return line.strip()

    for raw in lines:
        line = fix(raw)
        if not line:
            if buf:
                merged.append(buf)
                buf = ""
            merged.append("")
            continue

        # 新条目起点判断
        new_entry = bool(
            re.match(r"^\d{1,3}[.、)\)]", line) or
            re.match(r"^[一二三四五六七八九十]+[、.]", line) or
            re.match(r"^[（(]\d+[)）]", line) or
            re.match(r"^[【\[].+[】\]]", line) or
            (line.startswith("第") and ("部分" in line[:10] or "章" in line[:6])) or
            (len(line) < 25 and re.match(r"^[一二三四五六七八九十]+[、.]", line)) or
            re.match(r"^\d{1,2}月", line)
        )

        if buf:
            if re.search(r"[。！？…]$", buf):
                merged.append(buf)
                buf = line
            elif new_entry:
                merged.append(buf)
                buf = line
            else:
                # 同一自然段里的PDF折行 → 直接拼
                buf += line
        else:
            buf = line

    if buf:
        merged.append(buf)

    # 步骤2：过滤噪声 + 标记heading
    segments = []
    for para in merged:
        para = para.strip()
        if not para:
            continue
        if is_toc_noise(para):
            continue

        if is_heading(para):
            segments.append({"type": "heading", "text": para})
        elif len(para) >= 4:
            segments.append({"type": "content", "text": para})

    return segments, False


# ────────────────────────────────────────
# 主构建
# ────────────────────────────────────────
def build():
    all_data = {
        "version": "2.1",
        "books": []
    }

    pdf_files = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    print(f"发现 {len(pdf_files)} 个PDF文件\n")

    for pdf_path in pdf_files:
        fname = os.path.basename(pdf_path)
        meta = PDF_CATEGORIES.get(fname, {"main": fname.replace(".pdf", ""), "note": ""})
        print(f"解析: {fname}")

        segs, is_scanned = extract_paragraphs(pdf_path)

        if is_scanned:
            print(f"  ⚠️  扫描版PDF，跳过（需OCR）")
            all_data["books"].append({
                "file": fname,
                "main_category": meta["main"],
                "note": meta["note"] + "（扫描版暂未处理）",
                "total_segments": 0,
                "is_scanned": True,
                "sub_categories": [],
                "segments": []
            })
            continue

        content_segs = [s for s in segs if s["type"] == "content"]
        print(f"  → 段落 {len(segs)} / 有效内容 {len(content_segs)}")

        book = {
            "file": fname,
            "main_category": meta["main"],
            "note": meta["note"],
            "total_segments": len(content_segs),
            "segments": []
        }

        # 遍历，把heading作为当前子分类
        sub_idx = {}
        cur_sub = ""
        for seg in segs:
            if seg["type"] == "heading":
                cur_sub = seg["text"]
                sub_idx.setdefault(cur_sub, [])
            else:
                sub_idx.setdefault(cur_sub, []).append(len(book["segments"]))
                book["segments"].append({"sub": cur_sub, "text": seg["text"]})

        book["sub_categories"] = [
            {"name": k, "count": len(v), "indices": v}
            for k, v in sub_idx.items()
            if len(v) > 0
        ]
        book["sub_categories"].sort(key=lambda x: x["count"], reverse=True)

        all_data["books"].append(book)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    total_segs = sum(b["total_segments"] for b in all_data["books"])
    print(f"\n✅ 完成!  {len(all_data['books'])} 本书 / {total_segs} 个知识点")
    print(f"   → {OUT}")


if __name__ == "__main__":
    build()
