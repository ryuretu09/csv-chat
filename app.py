import streamlit as st
import pandas as pd
import anthropic
from streamlit_google_auth import Authenticate

st.set_page_config(
    page_title="DataChat AI",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stFileUploader { background-color: #1c1f26; border-radius: 10px; padding: 10px; }
    .stTextInput input { background-color: #1c1f26; color: #ffffff; border: 1px solid #333; border-radius: 8px; }
    .answer-box { background-color: #1c1f26; border-left: 4px solid #4f8ef7; border-radius: 8px; padding: 20px; margin-top: 20px; }
    h1 { color: #4f8ef7; font-size: 2rem; }
    .sub-text { color: #888; font-size: 0.9rem; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

# Google認証
authenticator = Authenticate(
    secret_credentials_path=None,
    cookie_name="datachat_cookie",
    cookie_key=st.secrets["COOKIE_KEY"],
    redirect_uri=st.secrets["REDIRECT_URI"],
    client_id=st.secrets["GOOGLE_CLIENT_ID"],
    client_secret=st.secrets["GOOGLE_CLIENT_SECRET"],
)

authenticator.check_authentification()

if not st.session_state.get("connected"):
    st.markdown("# 📊 DataChat AI")
    st.markdown('<p class="sub-text">CSVデータをアップロードして、自然言語で質問するだけ。</p>', unsafe_allow_html=True)
    authenticator.login()
    st.stop()

# ログイン済み
user_email = st.session_state["user_info"]["email"]

st.markdown("# 📊 DataChat AI")
st.markdown(f'<p class="sub-text">ようこそ、{user_email} さん</p>', unsafe_allow_html=True)

if st.button("ログアウト"):
    authenticator.logout()

# 利用回数チェック
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

FREE_LIMIT = 10
remaining = FREE_LIMIT - st.session_state.usage_count
st.sidebar.markdown(f"### 残り無料回数：{remaining}回")

col1, col2 = st.columns([1, 2])

with col1:
    uploaded_file = st.file_uploader("CSVファイルを選択", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='cp932')
        st.success(f"✅ 読み込み完了：{len(df)}行 / {len(df.columns)}列")
        st.dataframe(df, height=300)

with col2:
    if uploaded_file is not None:
        st.markdown("### 💬 データに質問する")

        if remaining <= 0:
            st.warning("無料回数を使い切りました。続けるには有料プランにアップグレードしてください。")
        else:
            question = st.text_input("例：売上が一番高い月は？")

            if question:
                with st.spinner("AI が分析中..."):
                    data_summary = df.to_string(max_rows=50)
                    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                    message = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=1024,
                        messages=[
                            {
                                "role": "user",
                                "content": f"以下のCSVデータについて質問に答えてください。\n\nデータ:\n{data_summary}\n\n質問: {question}"
                            }
                        ]
                    )
                    st.session_state.usage_count += 1
                    st.markdown(f'<div class="answer-box">🤖 {message.content[0].text}</div>', unsafe_allow_html=True)
    else:
        st.markdown("### 👈 まずCSVをアップロードしてください")
