import streamlit as st

st.set_page_config(page_title="Word風文書編集", layout="wide")
st.title("📝 Microsoft Word風 文書編集アプリ")

# ツールバー風レイアウト
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("### 🛠 ツールバー")

    font_size = st.slider("フォントサイズ", 12, 48, 16, key="font_size")
    color = st.color_picker("文字色", "#000000", key="font_color")
    bold = st.checkbox("太字", key="bold")
    italic = st.checkbox("斜体", key="italic")
    underline = st.checkbox("下線", key="underline")

    st.markdown("### 💾 保存")
    file_name = st.text_input("ファイル名", value="document.txt", key="filename")

with col2:
    st.markdown("### ✍️ 編集エリア")
    content = st.text_area("ここに文章を入力", height=300, key="editor")

    # Markdown装飾の適用
    styled = content
    if bold:
        styled = f"**{styled}**"
    if italic:
        styled = f"*{styled}*"
    if underline:
        styled = f"<u>{styled}</u>"

    # HTMLスタイル適用
    styled = f"<div style='font-size:{font_size}px; color:{color}'>{styled}</div>"

    st.markdown("### 🔍 プレビュー")
    st.markdown(styled, unsafe_allow_html=True)

    st.download_button("文書を保存", data=content, file_name=file_name, mime="text/plain")
