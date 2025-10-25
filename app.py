import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
from googletrans import Translator
from PIL import Image
import io

st.set_page_config(page_title="PDF編集アプリ", layout="wide")
st.title("📄 PDF編集Webアプリ")

translator = Translator()

uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf")
if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.sidebar.write(f"ページ数: {len(doc)}")
    page_num = st.sidebar.number_input("編集するページ番号", min_value=0, max_value=len(doc)-1, value=0)
    page = doc[page_num]

    # 文字数カウント
    text = page.get_text()
    st.sidebar.write(f"このページの文字数: {len(text)}")

    # 文字の書き込み
    st.subheader("✍️ 文字の書き込み")
    input_text = st.text_area("追加する文字")
    x = st.number_input("X座標", value=50)
    y = st.number_input("Y座標", value=50)
    font_size = st.slider("フォントサイズ", 8, 48, 12)
    color = st.color_picker("文字色", "#000000")
    bold = st.checkbox("太字")
    italic = st.checkbox("イタリック")

    if st.button("文字を挿入"):
        font_flags = 0
        if bold: font_flags += 2
        if italic: font_flags += 1
        page.insert_text((x, y), input_text, fontsize=font_size, color=fitz.utils.getColor(color), fontfile=None, render_mode=0, fontname="helv", rotate=0, morph=None, stroke_color=None, fill_opacity=1.0, stroke_opacity=1.0, overlay=True, flags=font_flags)
        st.success("文字を挿入しました")

    # 文字の削除（簡易：矩形で塗りつぶし）
    st.subheader("🧹 文字の削除（矩形指定）")
    rx1 = st.number_input("削除範囲X1", value=100)
    ry1 = st.number_input("削除範囲Y1", value=100)
    rx2 = st.number_input("削除範囲X2", value=300)
    ry2 = st.number_input("削除範囲Y2", value=150)
    if st.button("範囲を塗りつぶして削除"):
        rect = fitz.Rect(rx1, ry1, rx2, ry2)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
        st.success("範囲を塗りつぶしました")

    # 画像の挿入
    st.subheader("🖼 画像の挿入")
    image_file = st.file_uploader("画像ファイルを選択", type=["png", "jpg", "jpeg"])
    img_x = st.number_input("画像X座標", value=50)
    img_y = st.number_input("画像Y座標", value=150)
    img_width = st.number_input("画像幅", value=100)
    img_height = st.number_input("画像高さ", value=100)
    if image_file and st.button("画像を挿入"):
        image = Image.open(image_file)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        rect = fitz.Rect(img_x, img_y, img_x + img_width, img_y + img_height)
        page.insert_image(rect, stream=img_bytes.getvalue())
        st.success("画像を挿入しました")

    # 選択範囲の翻訳
    st.subheader("🌐 選択範囲の翻訳")
    tx1 = st.number_input("翻訳範囲X1", value=50)
    ty1 = st.number_input("翻訳範囲Y1", value=50)
    tx2 = st.number_input("翻訳範囲X2", value=300)
    ty2 = st.number_input("翻訳範囲Y2", value=150)
    target_lang = st.selectbox("翻訳先言語", ["ja", "en", "zh-cn", "fr", "de"])
    if st.button("範囲内のテキストを翻訳"):
        rect = fitz.Rect(tx1, ty1, tx2, ty2)
        selected_text = page.get_textbox(rect)
        translated = translator.translate(selected_text, dest=target_lang)
        st.info(f"翻訳結果（{target_lang}）: {translated.text}")

    # PDF保存とダウンロード
    st.subheader("💾 編集済みPDFの保存")
    output = io.BytesIO()
    doc.save(output)
    st.download_button("編集済みPDFをダウンロード", data=output.getvalue(), file_name="edited.pdf", mime="application/pdf")