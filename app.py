import streamlit as st
import pandas as pd
import anthropic

st.title("📊 社内データ分析ツール")

uploaded_file = st.file_uploader("CSVファイルを選択", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='cp932')
    st.success("ファイルを読み込みました！")
    st.write(f"行数: {len(df)}行 / 列数: {len(df.columns)}列")
    st.dataframe(df)

    question = st.text_input("データについて質問してください")

    if question:
        with st.spinner("考え中..."):
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
            st.write("### 回答")
            st.write(message.content[0].text)