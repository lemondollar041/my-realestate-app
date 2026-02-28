import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# 1. ページ設定とデザイン
st.set_page_config(page_title="不動産マーケット・アナリティクス", layout="wide")

# StreamlitのSecretsからAPIキーを安全に取得
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("設定画面の 'Secrets' に GEMINI_API_KEY が登録されていません。")
    st.stop()

# 高級感のあるカスタムCSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Hiragino Sans', sans-serif; font-weight: 800; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 15px; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; line-height: 1.8; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ 不動産マーケット・アナリティクス")
st.markdown("<p style='color: #888;'>AIアルゴリズムによる資産価値推移と特定物件のポテンシャル分析</p>", unsafe_allow_html=True)
st.divider()

# サイドバー設定
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>分析パラメータ</h2>", unsafe_allow_html=True)
    target_property = st.text_input("マンション名（任意）", placeholder="例：パークホームズ豊洲")
    prop_type = st.radio("物件種別", ["標準（全体）", "ファミリー向け", "コンパクト"], index=1)
    interest_rate = st.slider("想定市場金利 (%)", 0.0, 3.0, 0.5, 0.1)
    areas = st.multiselect("対象エリア", ["勝どき・月島", "晴海", "豊洲", "有明", "芝浦・港南"], default=["豊洲", "晴海"])
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2026))

# API消費を抑えるためのキャッシュ機能
@st.cache_data(show_spinner=False)
def fetch_analysis(prop, p_type, rate, selected_areas, y_range, _key):
    genai.configure(api_key=_key)
    # 404エラーを回避するため、2026年時点で確実に存在する最新のモデルを指定
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    p_info = f"特に「{prop}」の物件力を考慮してください。" if prop else ""
    prompt = f"{p_info} 期間:{y_range[0]}-{y_range[1]}年, エリア:{','.join(selected_areas)}, タイプ:{p_type}, 金利:{rate}%. 最初はCSV(時期,エリア名...,要因)を出し、次に'---SUMMARY---'と書いてから日本語で解説して。"
    
    response = model.generate_content(prompt)
    return response.text

if st.button("プロフェッショナル分析を実行"):
    with st.spinner("AIが最新の市場データを解析中..."):
        try:
            full_text = fetch_analysis(target_property, prop_type, interest_rate, areas, years, API_KEY)
            
            if "---SUMMARY---" in full_text:
                parts = full_text.split("---SUMMARY---")
                # グラフ表示
                df = pd.read_csv(io.StringIO(parts[0].strip()))
                st.subheader("📊 市場強気スコア推移")
                area_cols = [c for c in df.columns if c not in ["時期", "主な市場要因"]]
                fig = px.line(df, x="時期", y=area_cols, markers=True, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                # レポート表示
                st.markdown(f"<div class='report-box'><h3>🖋️ エグゼクティブ・サマリー</h3><p>{parts[1].strip()}</p></div>", unsafe_allow_html=True)
            else:
                st.warning("分析データの生成に失敗しました。もう一度実行してください。")

        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                st.error("現在、APIの利用制限がかかっています。数分〜1時間ほど待ってから再度お試しください。")
            else:
                st.error(f"システムエラーが発生しました。時間を置いて再試行してください。({error_str})")
