import io
import re
from typing import Optional

import streamlit as st
from pypdf import PdfReader, PdfWriter


def extract_trailing_number(filename: str) -> Optional[int]:
    """
    Extract a trailing number used for ordering from a filename.

    Rules (best-effort):
    - Prefer last number inside parentheses: `name (8).pdf` -> 8
    - Else, prefer a number immediately before the extension: `name 8.pdf` -> 8
    - Else, return None.
    """
    # Try last number inside parentheses
    paren_matches = re.findall(r"\((\d+)\)", filename)
    if paren_matches:
        try:
            return int(paren_matches[-1])
        except ValueError:
            pass

    # Try number just before extension
    m = re.search(r"(\d+)(?=\.[^.]+$)", filename)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    # No number found
    return None


def merge_pdfs_in_order(uploaded_files):
    """Return merged PDF bytes for uploaded files sorted by extracted trailing number.

    Tie-breaking: files with equal or missing numbers preserve the original upload order.
    """
    # Prepare list with extracted numbers and original index
    prepared = []
    for idx, f in enumerate(uploaded_files):
        num = extract_trailing_number(f.name)
        prepared.append((f, num, idx))

    # Sort rule change: files WITHOUT a trailing number should come first (preserve upload order among them),
    # then files with numbers sorted by that number, tie-broken by upload order.
    def sort_key(item):
        _num = item[1]
        # For None (no number), use a key that places them before numbered files while preserving upload order
        if _num is None:
            return (0, item[2])
        # Numbered files come after, sorted by number then upload index
        return (1, _num, item[2])

    prepared.sort(key=sort_key)

    writer = PdfWriter()

    for f, num, idx in prepared:
        try:
            # f is an UploadedFile (file-like). We must ensure it's at start
            f.seek(0)
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            st.error(f"Error reading {f.name}: {e}")
            return None

    out = io.BytesIO()
    writer.write(out)
    out.seek(0)
    return out.getvalue(), prepared


# ---- Streamlit UI ----
st.set_page_config(page_title="PDF Binder", layout="centered")
st.title("PDF Binder — filename-number orderで結合")

st.markdown(
    """
    アップロードした複数のPDFを、ファイル名の末尾にある数字（例: `document (8).pdf` の `8`）の順番で結合してダウンロードできます。

    ルール:
    - 最後の括弧の中の数字を優先して使います: `name (8).pdf` → 8
    - それが無ければ拡張子直前の数字を使います: `name 8.pdf` → 8
    - 数字が見つからないファイルは末尾に回されます（アップロード順を維持）
    """
)

uploaded = st.file_uploader("PDFファイルをまとめてアップロードしてください", accept_multiple_files=True, type=["pdf"])

if uploaded:
    st.subheader("アップロードされたファイルと抽出した順序")
    # Build a table-like display
    display_rows = []
    for idx, f in enumerate(uploaded):
        num = extract_trailing_number(f.name)
        display_rows.append((idx + 1, f.name, num if num is not None else "(なし)"))

    for row in display_rows:
        st.write(f"{row[0]}. `{row[1]}` → {row[2]}")

    if st.button("結合してダウンロード" ):
        result = merge_pdfs_in_order(uploaded)
        if result is None:
            st.error("PDFの読み込みに失敗しました。ファイルが壊れていないか確認してください。")
        else:
            merged_bytes, prepared = result

            # Show final merge order
            st.subheader("結合順（先頭が最初のページになります）")
            for i, (f, num, idx) in enumerate(prepared, start=1):
                st.write(f"{i}. `{f.name}` — {num if num is not None else '(なし)'}")

            st.success("結合が完了しました。下のボタンからダウンロードしてください。")
            st.download_button(
                label="マージ済みPDFをダウンロード",
                data=merged_bytes,
                file_name="merged.pdf",
                mime="application/pdf",
            )

else:
    st.info("まずは上のアップローダーから複数のPDFを選択してください（Ctrl/Shiftで複数選択可）。")

st.markdown("---")
st.markdown("小さな注意: 大きなPDFを多数アップロードするとメモリを多く使います。必要ならファイルサイズのチェックやストリーム処理を追加してください。")
