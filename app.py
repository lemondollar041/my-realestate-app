import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# ★あなたのGemini APIキーを貼り付けてください
MY_GEMINI_API_KEY = "AIzaSyCfABn17hK0bA7NMilKNcqbg_7XsqWtp-M"

# 1. デザインの洗練（ページ設定とカラー固定）
st.set_page_config(page_title="湾岸エリア AIアナリスト Pro", layout="wide")

# エリアごとのイメージカラーを固定（豊洲は高級感のあるブルー、晴海は活気のあるオレンジなど）
AREA_COLORS = {
    "勝どき・月島": "#1f77b4", 
    "晴海": "#ff7f0e", 
    "豊洲": "#2ca02c", 
    "東雲": "#d62728", 
    "有明": "#9467bd"
}

st.title("🏙️ 湾岸エリア AI不動産アナリスト Pro")
st.markdown("最新のAI分析により、マーケットの「現在地」と「背景」を可視化します。")

with st.sidebar:
    st.header("📊 条件設定")
    areas = st.multiselect("分析対象エリア", 
                           ["勝どき・月島", "晴海", "豊洲", "東雲", "有明"], 
                           default=["豊洲", "晴海"])
    years = st.select_slider("分析期間", 
                             options=list(range(2015, 2027)), 
                             value=(2018, 2026))
    st.divider()
    st.caption("Produced by Gemini 3 Flash")

if st.button("🚀 プロフェッショナル分析を実行", type="primary", use_container_width=True):
    with st.spinner("AIが膨大な市場データを解析して要約を作成中..."):
        try:
            genai.configure(api_key=MY_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 要約とCSVを同時に出させる高度なプロンプト
            prompt = f'''
            あなたは東京の湾岸エリアに精通したシニア不動産アナリストです。
            {years[0]}年から{years[1]}年までの {", ".join(areas)} の不動産市況を分析してください。

            1. 最初に、以下のCSV形式で半年ごとの強気スコア（0-100）を出力してください。
            時期,{" ,".join(areas)},主な市場要因
            2. CSVの後に、必ず「---SUMMARY---」という区切り線を入れ、その後にプロの視点による全体的な市場総括と、今後の見通しを日本語で詳しく解説してください。
            '''
            
            response = model.generate_content(prompt)
            full_text = response.text
            
            # データと要約を分離
            parts = full_text.split("---SUMMARY---")
            csv_part = parts[0].strip()
            summary_part = parts[1].strip() if len(parts) > 1 else "要約の生成に失敗しました。"

            # CSV読み込み
            df = pd.read_csv(io.StringIO(csv_part))
            
            # --- デザイン: グラフセクション ---
            st.subheader("📈 市場強気スコアの推移")
            area_cols = [c for c in df.columns if c not in ["時期", "主な市場要因"]]
            df_melted = df.melt(id_vars=["時期", "主な市場要因"], value_vars=area_cols, var_name="エリア", value_name="スコア")
            
            fig = px.line(df_melted, x="時期", y="スコア", color="エリア", 
                          color_discrete_map=AREA_COLORS, # カラー固定
                          hover_data={"主な市場要因": True}, markers=True)
            
            fig.update_layout(
                xaxis_tickangle=-45, 
                height=500, 
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- 機能: AI要約セクション ---
            st.subheader("📝 アナリスト・レポート")
            st.info(summary_part)

            # --- 機能: CSVダウンロードボタン ---
            st.divider()
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig') # Excelで開けるように sig を付与
            st.download_button(
                label="📥 分析データをCSV(Excel)でダウンロード",
                data=csv_buffer.getvalue(),
                file_name=f"wangan_analysis_{years[0]}_{years[1]}.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"分析エラー: {e}")
