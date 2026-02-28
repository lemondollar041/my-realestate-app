import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# ★あなたのGemini APIキーをここに貼り付けてください
MY_GEMINI_API_KEY = "AIzaSyCfABn17hK0bA7NMilKNcqbg_7XsqWtp-M"

# 1. ページ全体のラグジュアリー設定
st.set_page_config(page_title="WANGAN PREMIER ANALYTICS", layout="wide")

# カスタムCSSによるデザインの微調整（ゴールドのテーマカラー）
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Playfair Display', serif; font-weight: 700; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 5px; font-weight: bold; width: 100%; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# エリアごとのプレミアムカラー
AREA_COLORS = {
    "勝どき・月島": "#4A90E2", "晴海": "#F5A623", "豊洲": "#50E3C2", 
    "東雲": "#9B51E0", "有明": "#F2C94C", "芝浦・港南": "#EB5757", "日本橋・茅場町": "#6FCF97"
}

# タイトルセクション
st.title("🏙️ WANGAN PREMIER ASSET ANALYTICS")
st.markdown("<p style='color: #888;'>Exclusive Real Estate Intelligence for Private Clients</p>", unsafe_allow_html=True)
st.divider()

# --- サイドバー ---
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>Portfolio Setting</h2>", unsafe_allow_html=True)
    prop_type = st.radio("Asset Class", ["Standard", "Family (3LDK / 70㎡+)", "Compact (1LDK / ~40㎡)"], index=1)
    
    st.divider()
    st.markdown("<h3 style='color: #D4AF37;'>Macro Simulation</h3>", unsafe_allow_html=True)
    interest_rate = st.slider("Market Interest Rate (%)", 0.3, 3.0, 0.5, 0.1)
    
    st.divider()
    areas = st.multiselect("Selected Areas", 
                           ["勝どき・月島", "晴海", "豊洲", "東雲", "有明", "芝浦・港南", "日本橋・茅場町"], 
                           default=["豊洲", "晴海", "芝浦・港南"])
    
    years = st.select_slider("Timeline", options=list(range(2015, 2028)), value=(2018, 2027))
    st.divider()
    st.caption("2027 June Return Strategy Model")

# --- メイン画面 ---
if st.button("EXECUTE PREMIER ANALYSIS", type="primary"):
    with st.spinner("AIがプレミアム・レポートを作成中です..."):
        try:
            genai.configure(api_key=MY_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f'''
            あなたは超富裕層向けの不動産コンサルタントです。
            2027年6月に日本へ帰国するオーナー向けに、以下の条件で市場分析を行ってください。
            【期間】{years[0]}-{years[1]}年 【エリア】{", ".join(areas)} 【タイプ】{prop_type} 【金利】{interest_rate}%
            1. 最初にCSV形式で半年ごとの市場指標（時期,エリア名...,主な市場要因）を出力してください。
            2. その後「---SUMMARY---」と書き、2027年6月の帰国時に向けた資産価値予測とアクションを日本語で詳しく解説してください。
            '''
            
            response = model.generate_content(prompt)
            parts = response.text.split("---SUMMARY---")
            csv_part = parts[0].strip()
            summary_part = parts[1].strip() if len(parts) > 1 else "解説の生成に失敗しました。"

            # データの可視化
            df = pd.read_csv(io.StringIO(csv_part))
            st.subheader("Market Sentiment Index")
            area_cols = [c for c in df.columns if c not in ["時期", "主な市場要因"]]
            df_melted = df.melt(id_vars=["時期", "主な市場要因"], value_vars=area_cols, var_name="エリア", value_name="スコア")
            
            # --- 修正したグラフ描画コード ---
            fig = px.line(df_melted, x="時期", y="スコア", color="エリア", 
                          color_discrete_map=AREA_COLORS, markers=True, template="plotly_dark")
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#e0e0e0"),
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#333")
            )
            st.plotly_chart(fig, use_container_width=True)

            # エグゼクティブ・サマリー
            st.markdown(f"<div class='report-box'><h3>🖋️ Executive Summary</h3><p>{summary_part}</p></div>", unsafe_allow_html=True)

            # 指標表示
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="Target Return Date", value="2027.06", delta="Return to Japan")
            with c2:
                st.metric(label="Primary Asset Focus", value=prop_type)

            # ダウンロードボタン
            csv_buffer = io.StringIO()
            df.to_
