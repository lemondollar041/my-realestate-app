import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# 1. ページ設定：ラグジュアリーなデザイン
st.set_page_config(page_title="不動産マーケット・アナリティクス", layout="wide")

# Secretsから安全にAPIキーを読み込む
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("設定の 'Secrets' に GEMINI_API_KEY を登録してください。")
    st.stop()

# カスタムCSS：シャンパンゴールドとダークネイビー
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Hiragino Sans', sans-serif; font-weight: 800; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 15px; font-size: 18px; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; line-height: 1.8; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ 不動産マーケット・アナリティクス")
st.markdown("<p style='color: #888;'>AIによる資産価値推移と特定物件のポテンシャル分析</p>", unsafe_allow_html=True)
st.divider()

# サイドバー設定
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>分析設定</h2>", unsafe_allow_html=True)
    target_property = st.text_input("マンション名（任意）", placeholder="例：パークホームズ豊洲")
    prop_type = st.radio("物件種別", ["標準", "ファミリー向け", "コンパクト"], index=1)
    interest_rate = st.slider("想定市場金利 (%)", 0.0, 3.0, 0.5, 0.1)
    areas = st.multiselect("対象エリア", ["勝どき・月島", "晴海", "豊洲", "有明", "芝浦・港南"], default=["豊洲", "晴海"])
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2026))

# API消費を抑えるキャッシュ機能
@st.cache_data(show_spinner=False)
def get_ai_response(prop, p_type, rate, selected_areas, y_range, _key):
    genai.configure(api_key=_key)
    # 404エラーを防ぐため、最も標準的なモデル名を使用
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prop_info = f"特に「{prop}」の資産価値を重点的に考慮してください。" if prop else ""
    prompt = f"{prop_info} 期間:{y_range[0]}-{y_range[1]}年, エリア:{','.join(selected_areas)}, タイプ:{p_type}, 金利:{rate}%. 最初はCSV(時期,エリア名...,要因)を出し、次に'---SUMMARY---'と書いてから日本語で解説して。"
    
    response = model.generate_content(prompt)
    return response.text

# メイン処理
if st.button("プロフェッショナル分析を実行"):
    with st.spinner("AIがデータを解析中..."):
        try:
            full_text = get_ai_response(target_property, prop_type, interest_rate, areas, years, API_KEY)
            
            if "---SUMMARY---" in full_text:
                parts = full_text.split("---SUMMARY---")
                csv_data = parts[0].strip()
                summary_data = parts[1].strip()
                
                # グラフ表示
                df = pd.read_csv(io.StringIO(csv_data))
                st.subheader("📊 市場強気スコア推移")
                fig = px.line(df, x="時期", y=[c for c in df.columns if c not in ["時期", "主な市場要因"]], markers=True, template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

                # レポート表示
                st.markdown(f"<div class='report-box'><h3>🖋️ エグゼクティブ・サマリー</h3><p>{summary_data}</p></div>", unsafe_allow_html=True)
            else:
                st.warning("データの形式が正しく生成されませんでした。もう一度実行してください。")

        except Exception as e:
            # エラーの種類を正確に判定して表示
            error_msg = str(e)
            if "429" in error_msg:
                st.error(f"利用制限（Quota Exceeded）がかかっています。数分待ってから再度お試しください。")
            elif "404" in error_msg:
                st.error(f"モデルが見つかりません。APIのバージョンやライブラリの設定を確認してください。({error_msg})")
            else:
                st.error(f"予期せぬエラーが発生しました: {error_msg}")
