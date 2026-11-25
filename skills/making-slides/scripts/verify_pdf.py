#!/usr/bin/env python3
"""スライドの PDF を検査する。文の中身・段の割り当て・図の位置は見ないので、0件でも PNG を目視する。

  uv run --with pymupdf python3 verify_pdf.py deck.pdf --expect-pages 12
  uv run --with pymupdf python3 verify_pdf.py deck.pdf --allow-fonts 'Hiragino|Menlo' --footer-top 0.92

検査するもの:
  - 書体: --allow-fonts の正規表現に合わない書体（和文の代替・Type3 化の検出）。省くと一覧だけ出す
  - はみ出し: 本文の領域（ページ上端から --footer-top の割合まで）の下端を越える文字
  - スライド外: ページの外にある文字
  - 重なり: 文字の見える範囲（em box）が縦横とも食い込む組
  - ページ数: --expect-pages と一致するか
exit: 0 = 問題なし / 1 = 問題あり
"""
import argparse
import re
import sys

import pymupdf

# 隣接するスパンが 1pt 未満で触れるのは組版として正常なので、重なりに数えない
OVERLAP_TOL = 1.0
# 箇条書きの記号は ::before の絶対配置で別のスパンになり、本文と重なって見える
BULLET = re.compile(r"^[●○■・•\-]+$")
# テンプレートの書体。fontsource の Noto Sans JP は名前表の都合で NotoSansJPThin-Regular / -Bold として埋め込まれる
DEFAULT_ALLOW = r"NotoSansJP|SFMono|Menlo|Consolas"


def spans(page):
    # 既定の get_text はページの範囲で切り抜き、ページの外の文字を返さない。スライド外を検査するため切り抜かない
    for block in page.get_text("dict", clip=pymupdf.INFINITE_RECT())["blocks"]:
        for line in block.get("lines", []):
            for sp in line["spans"]:
                if sp["text"].strip():
                    x0, y0, x1, y1 = sp["bbox"]
                    yield {"text": sp["text"], "font": sp["font"], "size": sp["size"],
                           "left": x0, "top": y0, "right": x1, "bottom": y1}


def ink_box(sp):
    # スパンの bbox は ascent/descent を含み、和文書体では 1.4em を超える。行送りを詰めた正常な行同士も
    # bbox では重なるので、中心から font size 分の em box を文字の見える範囲とみなす
    cy = (sp["top"] + sp["bottom"]) / 2
    half = sp["size"] / 2
    return sp["left"], cy - half, sp["right"], cy + half


def overlaps(items):
    hits = []
    boxes = [(sp, ink_box(sp)) for sp in items if not BULLET.match(sp["text"].strip())]
    for i, (a, (ax0, ay0, ax1, ay1)) in enumerate(boxes):
        for b, (bx0, by0, bx1, by1) in boxes[i + 1:]:
            dx = min(ax1, bx1) - max(ax0, bx0)
            dy = min(ay1, by1) - max(ay0, by0)
            if dx > OVERLAP_TOL and dy > OVERLAP_TOL:
                hits.append(f"{a['text'][:20]!r} と {b['text'][:20]!r}（{dx:.1f}x{dy:.1f}pt）")
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--expect-pages", type=int)
    ap.add_argument("--allow-fonts", default=DEFAULT_ALLOW,
                    help=f"許容する書体名の正規表現。空文字で書体の検査をしない（既定: {DEFAULT_ALLOW}）")
    ap.add_argument("--footer-top", type=float, default=0.92,
                    help="フッター（ページ番号・注記の帯）の上端をページの高さの割合で（既定 0.92）")
    opt = ap.parse_args()

    allow = re.compile(opt.allow_fonts) if opt.allow_fonts else None
    doc = pymupdf.open(opt.pdf)
    fonts: dict[str, int] = {}
    problems = {"書体": [], "はみ出し": [], "スライド外": [], "重なり": []}

    for no, page in enumerate(doc, 1):
        w, h = page.rect.width, page.rect.height
        footer_top = h * opt.footer_top
        items = list(spans(page))
        for sp in items:
            fonts[sp["font"]] = fonts.get(sp["font"], 0) + 1
            if allow and not allow.search(sp["font"]):
                problems["書体"].append(f"p{no} {sp['font']}: {sp['text'][:30]!r}")
            if sp["top"] < footer_top < sp["bottom"]:
                problems["はみ出し"].append(f"p{no} 下端 {sp['bottom']:.0f}pt: {sp['text'][:30]!r}")
            if sp["left"] < -0.5 or sp["right"] > w + 0.5 or sp["top"] < -0.5 or sp["bottom"] > h + 0.5:
                problems["スライド外"].append(f"p{no}: {sp['text'][:30]!r}")
        problems["重なり"] += [f"p{no} {hit}" for hit in overlaps(items)]

    print(f"ページ数: {doc.page_count}（{doc[0].rect.width:.0f}x{doc[0].rect.height:.0f}pt）")
    print("書体:")
    for name, count in sorted(fonts.items(), key=lambda kv: -kv[1]):
        print(f"  {name} {count}")

    failed = 0
    for name, items in problems.items():
        if name == "書体" and allow is None:
            continue
        print(f"{name}: {len(items)}件 [{'OK' if not items else 'NG'}]")
        for it in items[:20]:
            print(f"  {it}")
        failed += len(items)
    if opt.expect_pages is not None and doc.page_count != opt.expect_pages:
        print(f"ページ数: 期待 {opt.expect_pages} / 実際 {doc.page_count} [NG]")
        failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
