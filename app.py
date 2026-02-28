import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# ページ構成
st.set_page_config(page_title="湾岸不動産マーケット・アナリティクス", layout="wide")

# Secretsから安全にキーを読み込む
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("設定画面の 'Secrets' に GEMINI_API_KEY を登録してください。")
    st.stop()

# 高級感を演出するカスタムデザイン
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Hiragino Sans', sans-serif; font-weight: 800; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 15px; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ 湾岸不動産マーケット・アナリティクス")
st.markdown("<p style='color: #888;'>AIアルゴリズムによる資産価値推移と特定物件のポテンシャル分析</p>", unsafe_allow_html=True)
st.divider()

# サイドバー設定
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>分析パラメータ</h2>", unsafe_allow_html=True)
    target_property = st.text_input("特定のマンション名（任意）", placeholder="例：パークホームズ豊洲")
    prop_type = st.radio("物件種別", ["標準（全体）", "ファミリー向け（3LDK〜）", "コンパクト（1LDK〜）"], index=1)
    interest_rate = st.slider("想定市場金利 (%)", 0.0, 3.0, 0.5, 0.1)
    areas = st.multiselect("対象エリア", ["勝どき・月島", "晴海", "豊洲", "有明", "芝浦・港南"], default=["豊洲", "晴海"])
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2026))

# API消費を抑えるためのキャッシュ関数
@st.cache_data(show_spinner=False)
def get_analysis_data(property_name, p_type, rate, selected_areas, y_range, _api_key):
    genai.configure(api_key=_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # 安定版を使用
    
    prop_info = f"特に「{property_name}」の資産性を考慮してください。" if property_name else ""
    prompt = f"{prop_info} 期間:{y_range[0]}-{y_range[1]}年, エリア:{','.join(selected_areas)}, タイプ:{p_type}, 金利:{rate}%. 最初はCSV(時期,エリア名...,要因)を出し、次に'---SUMMARY---'と書いてから日本語で解説して。"
    
    response = model.generate_content(prompt)
    return response.text

# メイン分析ロジック
if st.button("プロフェッショナル分析を実行"):
    with st.spinner("AIが市場データを照合中..."):
        try:
            full_text = get_analysis_data(target_property, prop_type, interest_rate, areas, years, API_KEY)
            parts = full_text.split("---SUMMARY---")
            
            # グラフ表示
            df = pd.read_csv(io.StringIO(parts[0].strip()))
            st.subheader("📊 市場強気スコア推移")
            fig = px.line(df, x="時期", y=[c for c in df.columns if c not in ["時期", "主な市場要因"]], markers=True, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            # 解説表示
            if len(parts) > 1:
                st.markdown(f"<div class='report-box'><h3>🖋️ エグゼクティブ・サマリー</h3><p>{parts[1].strip()}</p></div>", unsafe_allow_html=True)
            
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            st.download_button("📥 データをCSVで保存", data=csv_buffer.getvalue(), file_name="market_report.csv", mime="text/csv")

        except Exception as e:
            st.error(f"現在、APIの利用制限（429）がかかっています。数分〜1時間ほど待ってから再度お試しください。({e})")
