import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import io

# ★あなたのGemini APIキーをここに貼り付けてください
MY_GEMINI_API_KEY = "AIzaSyCfABn17hK0bA7NMilKNcqbg_7XsqWtp-M"

# 1. ページ設定
st.set_page_config(page_title="湾岸プレミア・アセット分析", layout="wide")

# カスタムCSS：日本語フォントの読みやすさと高級感の両立
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; font-family: 'Hiragino Sans', 'Meiryo', sans-serif; font-weight: 800; }
    .stButton>button { background-color: #D4AF37; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; padding: 15px; font-size: 18px; }
    .report-box { background-color: #1c212d; padding: 25px; border-radius: 15px; border-left: 5px solid #D4AF37; color: #e0e0e0; line-height: 1.8; }
    .sidebar .sidebar-content { background-color: #11151c; }
    </style>
    """, unsafe_allow_html=True)

# エリアカラーの設定
AREA_COLORS = {
    "勝どき・月島": "#4A90E2", "晴海": "#F5A623", "豊洲": "#50E3C2", 
    "東雲": "#9B51E0", "有明": "#F2C94C", "芝浦・港南": "#EB5757", "日本橋・茅場町": "#6FCF97"
}

# メインタイトル
st.title("🏙️ 湾岸プレミア・アセット分析")
st.markdown("<p style='color: #888;'>2027年6月の帰国を見据えた、エグゼクティブ専用の資産管理ダッシュボード</p>", unsafe_allow_html=True)
st.divider()

# --- サイドバー：設定 ---
with st.sidebar:
    st.markdown("<h2 style='color: #D4AF37;'>ポートフォリオ設定</h2>", unsafe_allow_html=True)
    
    # 機能1: 物件タイプの指定（パークホームズ豊洲などの3LDKを想定）
    prop_type = st.radio("物件タイプを選択", ["一般（平均）", "3LDK / ファミリー（70㎡〜）", "1LDK / コンパクト（〜40㎡）"], index=1)
    
    st.divider()
    st.markdown("<h3 style='color: #D4AF37;'>マクロ経済シミュレーション</h3>", unsafe_allow_html=True)
    # 機能2: 金利シミュレーター
    interest_rate = st.slider("想定ローン金利 (%)", 0.3, 3.0, 0.5, 0.1)
    
    st.divider()
    # 機能4: 対象エリアの選択（港区・中央区を含む）
    areas = st.multiselect("分析対象エリア（複数選択可）", 
                           ["勝どき・月島", "晴海", "豊洲", "東雲", "有明", "芝浦・港南", "日本橋・茅場町"], 
                           default=["豊洲", "晴海", "芝浦・港南"])
    
    years = st.select_slider("分析期間", options=list(range(2015, 2028)), value=(2018, 2027))
    st.divider()
    st.caption("2027年6月 帰国戦略モデル実行中")

# --- メインロジック ---
