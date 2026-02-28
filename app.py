import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# ★あなたのGemini APIキーをここに貼り付けてください
MY_GEMINI_API_KEY = "AIzaSyCfABn17hK0bA7NMilKNcqbg_7XsqWtp-M"

# 1. ページ全体のラグジュアリー設定
st.set_page_config(page_title="湾岸不動産マーケット・アナリティクス", layout="wide")

# カスタムCSS：高級感のあるデザイン設定
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Hiragino Sans', 'Meiryo', sans-serif; font-weight: 800; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 15px; font-size: 18px; cursor: pointer; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; line-height: 1.8; margin-top: 20px; }
    .stMetric { background-color: #1c212d; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    /* テキスト入力欄のスタイル */
    .stTextInput>div>div>input { background-color: #1c212d; color: white; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# エリアごとの固定プレミアムカラー
AREA_COLORS = {
    "勝どき・月島": "#4A90E2", "晴海": "#F5A623", "豊洲": "#50E3C2", 
    "東雲": "#9B51E0", "有明": "#F2C94C", "芝浦・港南": "#EB5757", "日本橋・茅場町": "#6FCF97"
}

# タイトル
st.title("🏙️ 湾岸不動産マーケット・アナリティクス")
st.markdown("<p style='color: #888;'>AIアルゴリズムによる資産価値推移と特定物件のポテンシャル分析</p>", unsafe_allow_html=True)
st.divider()

# --- サイドバー：詳細設定 ---
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>分析パラメータ</h2>", unsafe_allow_html=True)
    
    # 新機能: 特定マンション名の入力
    target_property = st.text_input("特定のマンション名（任意）", placeholder="例：パークホームズ豊洲")
    st.caption("※入力すると、その物件の特性を考慮した分析を行います。")
    
    st.divider()
    # 物件タイプの指定
    prop_type = st.radio("対象アセットを選択", ["標準（全体平均）", "3LDK / ファミリー向け（70㎡〜）", "1LDK / コンパクト（〜40㎡）"], index=1)
    
    st.divider()
    # 金利シミュレーター
    interest_rate = st.slider("想定市場金利 (%)", 0.3, 3.0, 0.5, 0.1)
    
    st.divider()
    # 対象エリアの選択
    areas = st.multiselect("分析対象エリア", 
                           ["勝どき・月島", "晴海", "豊洲", "東雲", "有明", "芝浦・港南", "日本橋・茅場町"], 
                           default=["豊洲", "晴海", "勝どき・月島"])
    
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2026))
    st.divider()
    st.caption("最新の不動産市況データに基づき実行")

# --- メインロジック ---
if st.button("プロフェッショナル分析を実行"):
    with st.spinner("AIが市場トレンドと物件データを照合しています..."):
        try:
            genai.configure(api_key=MY_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 物件名がある場合のプロンプト調整
            property_info = f"特に「{target_property}」という物件の資産価値や特徴を重点的に考慮してください。" if target_property else ""
            
            prompt = f'''
            あなたは湾岸エリアの不動産市場を専門とするシニア・アナリストです。
            投資家および居住検討者向けに、以下の条件で客観的な市場分析を行ってください。
            {property_info}

            【条件】
            ・期間: {years[0]}年〜{years[1]}年
            ・エリア: {", ".join(areas)}
            ・物件タイプ: {prop_type}
            ・想定市場金利: {interest_rate}%

            1. 最初にCSV形式（時期,エリア名...,主な市場要因）を出力してください。
            2. その後「---SUMMARY---」と書き、以下の内容を日本語で詳しく解説してください。
               A) 全体総括: {prop_type}における、金利{interest_rate}%の影響。
               B) 物件・エリア分析: 指定エリアの推移と、特定物件（指定があれば）のポテンシャル。
               C) 将来展望: 推奨されるマーケットアクション。
            '''
            
            response = model.generate_content(prompt)
            parts = response.text.split("---SUMMARY---")
            csv_part = parts[0].strip()
            summary_part = parts[1].strip() if len(parts) > 1 else "分析要約の生成に失敗しました。"

            # データの可視化
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
            display_name = target_property if target_property else "エリア全体"
            st.markdown(f"<div class='report-box'><h3>🖋️ エグゼクティブ・サマリー（対象: {display_name}）</h3><p>{summary_part}</p></div>", unsafe_allow_html=True)

            # ステータス指標
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label="分析対象物件", value=display_name)
            with c2:
                st.metric(label="想定金利", value=f"{interest_rate}%")

            # CSVダウンロード
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            st.download_button(label="📥 分析データをCSV形式でダウンロード", data=csv_buffer.getvalue(), 
                               file_name="wangan_market_report.csv", mime="text/csv")

        except Exception as e:
            st.error(f"分析中にエラーが発生しました。({e})")
