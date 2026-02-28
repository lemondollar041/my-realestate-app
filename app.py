
import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# あなたのAPIキーを埋め込んでおきます（これでユーザーは入力不要）
MY_GEMINI_API_KEY = "AIzaSyCfABn17hK0bA7NMilKNcqbg_7XsqWtp-M"

st.set_page_config(page_title="湾岸エリア AIアナリスト", layout="wide")
st.title("🏙️ 湾岸エリア AIアナリスト")

# サイドバーでユーザーが地域と期間を選べるようにします
with st.sidebar:
    st.header("条件設定")
    areas = st.multiselect("分析対象エリア", 
                           ["勝どき・月島", "晴海", "豊洲", "東雲", "有明"], 
                           default=["豊洲"])
    years = st.select_slider("分析期間", 
                             options=list(range(2015, 2027)), 
                             value=(2020, 2026))

if st.button("🚀 AI分析を実行", type="primary", use_container_width=True):
    with st.spinner("AIがデータを抽出中..."):
        try:
            genai.configure(api_key=MY_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"{years[0]}年から{years[1]}年までの {', '.join(areas)} の不動産市況をCSV形式で分析して"
            response = model.generate_content(prompt)
            df = pd.read_csv(io.StringIO(response.text.strip()))
            area_cols = [c for c in df.columns if c not in ["時期", "主な市場要因"]]
            fig = px.line(df, x="時期", y=area_cols, markers=True)
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("エラーが発生しました。しばらく待ってから再度お試しください。")
