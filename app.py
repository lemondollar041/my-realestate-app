import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# ★あなたのGemini APIキーをここに貼り付けてください
MY_GEMINI_API_KEY = "AIzaSyCfABn17hK0bA7NMilKNcqbg_7XsqWtp-M"

# 1. ページ設定：汎用的なプロ仕様のタイトル
st.set_page_config(page_title="湾岸不動産マーケット・アナリティクス", layout="wide")

# カスタムCSS：シャンパンゴールドとダークネイビーの高級感
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Hiragino Sans', 'Meiryo', sans-serif; font-weight: 800; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 15px; font-size: 18px; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; line-height: 1.8; margin-top: 20px; }
    .stMetric { background-color: #1c212d; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# エリアごとの固定プレミアムカラー
AREA_COLORS = {
    "勝どき・月島": "#4A90E2", "晴海": "#F5A623", "豊洲": "#50E3C2", 
    "東雲": "#9B51E0", "有明": "#F2C94C", "芝浦・港南": "#EB5757", "日本橋・茅場町": "#6FCF97"
}

# タイトル
st.title("🏙️ 湾岸不動産マーケット・アナリティクス")
st.markdown("<p style='color: #888;'>AIアルゴリズムによる資産価値推移と市場センチメントの可視化</p>", unsafe_allow_html=True)
st.divider()

# --- サイドバー：詳細設定（日本語ベース・汎用版） ---
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>分析パラメータ</h2>", unsafe_allow_html=True)
    
    # 機能1: 物件タイプの指定
    prop_type = st.radio("対象アセットを選択", ["標準（全体平均）", "3LDK / ファミリー向け（70㎡〜）", "1LDK / コンパクト（〜40㎡）"], index=1)
    
    st.divider()
    st.markdown("<h3 style='color: #D4AF37;'>経済シミュレーション</h3>", unsafe_allow_html=True)
    # 機能2: 金利シミュレーター
    interest_rate = st.slider("想定市場金利 (%)", 0.3, 3.0, 0.5, 0.1)
    
    st.divider()
    # 機能4: 対象エリアの拡大
    areas = st.multiselect("分析対象エリア", 
                           ["勝どき・月島", "晴海", "豊洲", "東雲", "有明", "芝浦・港南", "日本橋・茅場町"], 
                           default=["豊洲", "晴海", "勝どき・月島"])
    
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2026))
    st.divider()
    st.caption("最新の不動産市況データに基づき実行")

# --- メインロジック ---
if st.button("プロフェッショナル分析を実行"):
    with st.spinner("AIが市場トレンドを抽出しています..."):
        try:
            genai.configure(api_key=MY_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f'''
            あなたは湾岸エリアの不動産市場を専門とするシニア・アナリストです。
            投資家および居住検討者向けに、以下の条件で客観的な市場分析を行ってください。

            【条件】
            ・期間: {years[0]}年〜{years[1]}年
            ・エリア: {", ".join(areas)}
            ・物件タイプ: {prop_type}
            ・想定市場金利: {interest_rate}%

            1. 最初にCSV形式で半年ごとの市場強気スコア（0-100）を出力してください。
            時期,{" ,".join(areas)},主な市場要因
            2. 次に「---SUMMARY---」と書き、その後に以下の2点について日本語で詳しく解説してください。
               A) 全体総括: {prop_type}における、金利{interest_rate}%が市場に与える影響と背景。
               B) 将来展望: 各エリアの中長期的な資産価値の安定性と、推奨されるマーケットアクション。
            '''
            
            response = model.generate_content(prompt)
            parts = response.text.split("---SUMMARY---")
            csv_part = parts[0].strip()
            summary_part = parts[1].strip() if len(parts) > 1 else "分析要約の生成に失敗しました。"

            # データの読み込み
            df = pd.read_csv(io.StringIO(csv_part))
            st.subheader("📊 市場強気スコア推移（Market Sentiment Index）")
            area_cols = [c for c in df.columns if c not in ["時期", "主な市場要因"]]
            df_melted = df.melt(id_vars=["時期", "主な市場要因"], value_vars=area_cols, var_name="エリア", value_name="スコア")
            
            fig = px.line(df_melted, x="時期", y="スコア", color="エリア", 
                          color_discrete_map=AREA_COLORS, markers=True, template="plotly_dark")
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#e0e0e0"),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#333")
            )
            st.plotly_chart(fig, use_container_width=True)

            # AIレポートセクション
            st.markdown(f"<div class='report-box'><h3>🖋️ エ
