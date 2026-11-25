#!/usr/bin/env python3
"""PDF の各ページを PNG にする。verify_pdf.py が見ないもの（段の割り当て・図の位置・列の潰れ・生の記法の残り）を目視するため。

  uv run --with pymupdf python3 pdf_to_png.py deck.pdf build/png/ [--dpi 100] [--pages 2,5-7]

出力は <outdir>/pNN.png。
"""
import argparse
import pathlib

import pymupdf


def parse_pages(spec: str, count: int) -> set[int]:
    if not spec:
        return set(range(1, count + 1))
    wanted = set()
    for part in spec.split(","):
        a, _, b = part.partition("-")
        wanted.update(range(int(a), int(b or a) + 1))
    return wanted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("outdir")
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--pages", default="", help="出すページ（例: 2,5-7）。省くと全ページ")
    opt = ap.parse_args()

    doc = pymupdf.open(opt.pdf)
    out = pathlib.Path(opt.outdir)
    out.mkdir(parents=True, exist_ok=True)
    wanted = parse_pages(opt.pages, doc.page_count)
    for no, page in enumerate(doc, 1):
        if no in wanted:
            path = out / f"p{no:02d}.png"
            page.get_pixmap(dpi=opt.dpi).save(path)
            print(path)


if __name__ == "__main__":
    main()
