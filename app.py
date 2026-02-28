import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# 1. ページ設定：高級感のあるデザインを維持
st.set_page_config(page_title="湾岸不動産マーケット・アナリティクス", layout="wide")

# 保管庫（Secrets）から安全にAPIキーを読み込む
try:
    MY_GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("StreamlitのSettings > Secrets で GEMINI_API_KEY を設定してください。")
    st.stop()

# カスタムCSS：シャンパンゴールドとダークネイビー
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Hiragino Sans', 'Meiryo', sans-serif; font-weight: 800; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 15px; font-size: 18px; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; line-height: 1.8; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

AREA_COLORS = {"勝どき・月島": "#4A90E2", "晴海": "#F5A623", "豊洲": "#50E3C2", "芝浦・港南": "#EB5757"}

st.title("🏙️ 湾岸不動産マーケット・アナリティクス")
st.markdown("<p style='color: #888;'>AIアルゴリズムによる資産価値推移と特定物件のポテンシャル分析</p>", unsafe_allow_html=True)
st.divider()

# --- サイドバー：詳細設定 ---
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>分析パラメータ</h2>", unsafe_allow_html=True)
    target_property = st.text_input("特定のマンション名（任意）", placeholder="例：パークホームズ豊洲")
    prop_type = st.radio("アセット種別", ["標準", "3LDK / ファミリー", "1LDK / コンパクト"], index=1)
    interest_rate = st.slider("想定市場金利 (%)", 0.0, 3.0, 0.5, 0.1)
    areas = st.multiselect("対象エリア", ["勝どき・月島", "晴海", "豊洲", "有明", "芝浦・港南"], default=["豊洲", "晴海"])
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2026))

# --- メインロジック ---
if st.button("プロフェッショナル分析を実行"):
    with st.spinner("AIが最新の市場トレンドを抽出しています..."):
        try:
            genai.configure(api_key=MY_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prop_info = f"特に「{target_property}」という物件の資産性を重点的に考慮してください。" if target_property else ""
            prompt = f"{prop_info} 期間:{years[0]}-{years[1]}年, エリア:{','.join(areas)}, タイプ:{prop_type}, 金利:{interest_rate}%. CSV(時期,エリア名...,要因)と、その後に'---SUMMARY---'を挟んで日本語で解説を出力して。"
            
            response = model.generate_content(prompt)
            parts = response.text.split("---SUMMARY---")
            csv_part = parts[0].strip()
            summary_part = parts[1].strip() if len(parts) > 1 else "要約の生成に失敗しました。"

            # グラフとレポート
            df = pd.read_csv(io.StringIO(csv_part))
            st.subheader("📊 市場強気スコア推移")
            area_cols = [c for c in df.columns if c not in ["時期", "主な市場要因"]]
            fig = px.line(df, x="時期", y=area_cols, color_discrete_map=AREA_COLORS, markers=True, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"<div class='report-box'><h3>🖋️ エグゼクティブ・サマリー</h3><p>{summary_part}</p></div>", unsafe_allow_html=True)
            
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            st.download_button("📥 データをCSVで保存", data=csv_buffer.getvalue(), file_name="wangan_report.csv", mime="text/csv")

        except Exception as e:
            st.error(f"分析エンジンでエラーが発生しました。({e})")
