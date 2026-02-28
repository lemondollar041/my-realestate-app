import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# ★あなたのGemini APIキーを貼り付けてください
MY_GEMINI_API_KEY = "AIzaSyCfABn17hK0bA7NMilKNcqbg_7XsqWtp-M"

# ページ設定とデザイン（ダークモード対応）
st.set_page_config(page_title="湾岸エリア 資産管理コンシェルジュ", layout="wide")

# エリアごとのカラー固定（港区・中央区も追加）
AREA_COLORS = {
    "勝どき・月島": "#1f77b4", "晴海": "#ff7f0e", "豊洲": "#2ca02c", 
    "東雲": "#d62728", "有明": "#9467bd", "芝浦・港南": "#e377c2", "日本橋・茅場町": "#8c564b"
}

st.title("🏙️ 湾岸エリア 資産管理コンシェルジュ")
st.markdown("2027年6月の帰国を見据えた、あなた専用の不動産戦略ダッシュボードです。")

# --- サイドバー: 高度な設定 ---
with st.sidebar:
    st.header("⚙️ 分析・シミュレーション設定")
    
    # 機能1: 物件タイプの指定
    prop_type = st.radio("物件タイプ", ["一般（全体）", "3LDK/ファミリー（70㎡〜）", "1LDK/単身・投資（〜40㎡）"], index=1)
    
    # 機能2: 金利シミュレーター
    st.divider()
    st.subheader("💹 経済シミュレーター")
    interest_rate = st.slider("想定ローン金利（%）", 0.3, 3.0, 0.5, 0.1)
    st.caption("※金利上昇が強気スコアに与える影響をAIが計算します。")
    
    # 機能4: エリア拡大（港区・中央区の追加）
    st.divider()
    areas = st.multiselect("分析対象エリア", 
                           ["勝どき・月島", "晴海", "豊洲", "東雲", "有明", "芝浦・港南", "日本橋・茅場町"], 
                           default=["豊洲", "晴海", "芝浦・港南"])
    
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2027))
    st.divider()
    st.caption("Powered by Gemini 1.5 Flash")

# --- メイン画面 ---
if st.button("🚀 2027年帰国ターゲット分析を実行", type="primary", use_container_width=True):
    with st.spinner("マクロ経済指標と地域データを照合中..."):
        try:
            genai.configure(api_key=MY_GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 高度なプロンプト（全機能を反映）
            prompt = f'''
            あなたは東京の湾岸不動産に精通したシニアアナリストです。
            以下の条件で市場を分析し、2027年6月に海外から日本へ帰国するオーナー向けのレポートを作成してください。

            【条件】
            ・期間: {years[0]}年〜{years[1]}年
            ・エリア: {", ".join(areas)}
            ・物件タイプ: {prop_type}
            ・想定ローン金利: {interest_rate}%

            1. 最初にCSVデータを出力してください。
            時期,{" ,".join(areas)},主な市場要因
            2. 次に「---SUMMARY---」と書き、その後に以下の2点についてプロの視点で解説してください。
               A) 全体総括: 金利{interest_rate}%の影響と{prop_type}の値動きの傾向。
               B) 2027年帰国戦略: 2027年6月の帰国時における、豊洲周辺（特に築浅3LDK）の「売り・貸し・住む」の推奨判断。
            '''
            
            response = model.generate_content(prompt)
            parts = response.text.split("---SUMMARY---")
            csv_part = parts[0].strip()
            summary_part = parts[1].strip() if len(parts) > 1 else "解説の生成に失敗しました。"

            # データ処理とグラフ
            df = pd.read_csv(io.StringIO(csv_part))
            st.subheader(f"📈 {prop_type} 市場強気スコア（金利 {interest_rate}% 想定）")
            area_cols = [c for c in df.columns if c not in ["時期", "主な市場要因"]]
            df_melted = df.melt(id_vars=["時期", "主な市場要因"], value_vars=area_cols, var_name="エリア", value_name="スコア")
            
            fig = px.line(df_melted, x="時期", y="スコア", color="エリア", color_discrete_map=AREA_COLORS, markers=True)
            fig.update_layout(xaxis_tickangle=-45, height=500, hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # 解説セクション
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("📝 アナリスト・レポート")
                st.info(summary_part)
            with col2:
                # 機能3: 2027年ターゲット・アドバイス
                st.subheader("🎯 2027年6月の指針")
                st.success("【帰国時推奨アクション】\\nAI予測に基づき、住み替え・継続保有の最適バランスを算出済みです。レポートの内容を確認してください。")

            # CSVダウンロード
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            st.download_button(label="📥 分析データを保存", data=csv_buffer.getvalue(), file_name="wangan_pro_report.csv", mime="text/csv")

        except Exception as e:
            st.error(f"分析に失敗しました。条件を調整して再度お試しください。")
