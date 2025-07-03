# pdf_add_jp_text_noarg.py
from pathlib import Path
from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ---------- ここだけ書き換えて使う ----------------------------------
SRC_PDF   = "PDF/input.pdf"                 # 元 PDF
DST_PDF   = "PDF/output.pdf"                # 出力 PDF
TEXT      = "機密資料 2025-07-03"       # 追記文字列
PAGE_NO   = 0                           # 0 始まりのページ番号
X_MM      = 30                          # 左端から [mm]
Y_MM      = 260                         # 下端から [mm]
FONT_FILE = "NotoSansJP-Regular.ttf"    # 日本語対応フォント
FONT_SIZE = 14                          # pt
# -------------------------------------------------------------------


def mm_to_pt(mm: float) -> float:
    return mm * 72.0 / 25.4


def register_font(font_path: Path) -> str:
    """ReportLab に TTF/OTF フォントを登録し、内部名を返す"""
    internal_name = font_path.stem
    if internal_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(internal_name, str(font_path)))
    return internal_name


def add_text_jp(
    src_pdf: str | Path,
    dst_pdf: str | Path,
    text: str,
    page_no: int,
    x_mm: float,
    y_mm: float,
    font_path: str | Path,
    font_size: int = 12,
) -> None:
    """既存 PDF に日本語テキストを追記して保存"""
    reader = PdfReader(str(src_pdf))
    page   = reader.pages[page_no]
    w_pt, h_pt = float(page.mediabox.width), float(page.mediabox.height)

    # オーバレイ PDF をメモリ上に生成
    buf = BytesIO()
    c   = canvas.Canvas(buf, pagesize=(w_pt, h_pt))
    font_name = register_font(Path(font_path))
    c.setFont(font_name, font_size)
    c.drawString(mm_to_pt(x_mm), mm_to_pt(y_mm), text)
    c.save()
    buf.seek(0)

    stamp_page = PdfReader(buf).pages[0]

    writer = PdfWriter()
    writer.append(reader)
    target = writer.pages[page_no]
    if "/Rotate" in target:
        target.transfer_rotation_to_content()
    target.merge_page(stamp_page, over=True)

    with open(dst_pdf, "wb") as f:
        writer.write(f)


if __name__ == "__main__":
    add_text_jp(
        SRC_PDF,
        DST_PDF,
        TEXT,
        PAGE_NO,
        X_MM,
        Y_MM,
        FONT_FILE,
        FONT_SIZE,
    )
    print(f"✅ 完了: {DST_PDF}")
