import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
from googletrans import Translator
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="PDF編集アプリ", layout="wide")
st.title("📄 PDFを表示しながら直接編集")

translator = Translator()

uploaded_file = st.file_uploader("PDFファイルをアップロード", type="pdf")
if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    page_count = len(doc)
    page_num = st.sidebar.slider("📄 編集するページ", 0, page_count - 1, 0)
    page = doc[page_num]

    # PDFページを画像として表示
    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
    img_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

    # レイアウト：ツールバー + プレビュー
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### 🛠 ツールバー")

        st.markdown("#### ✍️ 文字挿入")
        text = st.text_input("挿入する文字", key="text_input")
        font_size = st.slider("フォントサイズ", 8, 48, 12, key="font_size")
        color = st.color_picker("文字色", "#000000", key="font_color")

        st.markdown("#### 🖼 画像挿入")
        image_file = st.file_uploader("画像ファイル", type=["png", "jpg", "jpeg"], key="image_upload")
        img_width = st.number_input("画像幅", value=100, key="img_width")
        img_height = st.number_input("画像高さ", value=100, key="img_height")

        st.markdown("#### 🌐 翻訳")
        tx1 = st.number_input("範囲X1", value=50, key="translate_x1")
        ty1 = st.number_input("範囲Y1", value=50, key="translate_y1")
        tx2 = st.number_input("範囲X2", value=300, key="translate_x2")
        ty2 = st.number_input("範囲Y2", value=150, key="translate_y2")
        lang = st.selectbox("翻訳先言語", ["ja", "en", "zh-cn", "fr", "de"], key="translate_lang")
        if st.button("範囲内のテキストを翻訳"):
            rect = fitz.Rect(tx1, ty1, tx2, ty2)
            selected_text = page.get_textbox(rect)
            translated = translator.translate(selected_text, dest=lang)
            st.info(f"翻訳結果（{lang}）: {translated.text}")

        st.markdown("#### 💾 保存")
        if st.button("PDFを保存してダウンロード"):
            output = io.BytesIO()
            doc.save(output)
            st.download_button("編集済みPDFをダウンロード", data=output.getvalue(), file_name="edited.pdf", mime="application/pdf")

    with col2:
        st.markdown("### 🖼 ページプレビュー（クリックで編集）")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=1,
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="point",
            key=f"canvas_{page_num}",
        )

        clicked = False
        if canvas_result.json_data and canvas_result.json_data["objects"]:
            obj = canvas_result.json_data["objects"][-1]
            x = obj["left"]
            y = obj["top"]
            clicked = True
            st.info(f"クリック座標: ({x:.1f}, {y:.1f})")

        if clicked and text and st.button("この位置に文字を挿入"):
            page.insert_text((x, y), text, fontsize=font_size, color=fitz.utils.getColor(color))
            st.success("文字を挿入しました")

        if clicked and image_file and st.button("この位置に画像を挿入"):
            img = Image.open(image_file)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            rect = fitz.Rect(x, y, x + img_width, y + img_height)
            page.insert_image(rect, stream=img_bytes.getvalue())
            st.success("画像を挿入しました")
