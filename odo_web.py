import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json
import os
from datetime import datetime
import time
from io import BytesIO

# ==========================================
# 0. 系統設定與初始變數
# ==========================================
st.set_page_config(page_title="Odo 股市操盤戰情室", page_icon="📈", layout="wide")

# 預設清單 (當沒有設定檔時使用)
DEFAULT_WATCHLIST = [
    {"id": "2330.TW", "name": "台積電", "ma": 18},
    {"id": "2301.TW", "name": "光寶", "ma": 18},
    {"id": "2324.TW", "name": "仁寶", "ma": 19},
    {"id": "2006.TW", "name": "東和鋼鐵", "ma": 21},
    {"id": "2303.TW", "name": "聯電", "ma": 21},
    {"id": "2382.TW", "name": "廣達", "ma": 23},
    {"id": "3231.TW", "name": "緯創", "ma": 26},
    {"id": "2454.TW", "name": "聯發科", "ma": 29},
    {"id": "2317.TW", "name": "鴻海",   "ma": 18},
    {"id": "NVDA",    "name": "輝達",   "ma": 19},
    {"id": "TSLA",    "name": "特斯拉", "ma": 17},
    {"id": "MSFT", "name": "微軟", "ma": 21},
    {"id": "GOOGLE", "name": "GOOGLE", "ma": 26},
    {"id": "AMZN", "name": "亞馬遜", "ma": 19},
    {"id": "APPL", "name": "蘋果", "ma": 19},
    {"id": "AMD", "name": "AMD", "ma": 22},
    {"id": "ADBE", "name": "ADOBE", "ma": 25},
    {"id": "ASML", "name": "阿麥斯", "ma": 24},
    {"id": "NFLX", "name": "奈飛", "ma": 23},
    {"id": "COST", "name": "好市多", "ma": 18},
    {"id": "MA", "name": "萬事達卡", "ma": 33},
    {"id": "V", "name": "VISA卡", "ma": 22},
    {"id": "2603.TW", "name": "長榮",   "ma": 35},
]

# ==========================================
# 1. 功能函式區
# ==========================================

def send_telegram_message(token, chat_id, msg):
    if not token or not chat_id:
        return False, "未設定 Token 或 Chat ID"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True, "發送成功"
        else:
            return False, f"發送失敗: {response.text}"
    except Exception as e:
        return False, f"錯誤: {e}"

# 回測邏輯
def run_backtest_logic(df, ma_period):
    df = df.copy()
    df['MA_Custom'] = df['Close'].rolling(window=ma_period).mean()
    wins = 0; trades = 0
    
    if len(df) <= ma_period + 1:
        return 0

    for j in range(ma_period+1, len(df)):
        d_today = df.iloc[j]
        d_prev = df.iloc[j-1]
        
        if pd.isna(d_today['MA_Custom']) or pd.isna(d_prev['MA_Custom']):
            continue

        entry = float(d_today['MA_Custom']) * 1.01
        
        # 策略：昨收 < MA (線下) 且 今高 > MA*1.01 (突破)
        if float(d_prev['Close']) < float(d_prev['MA_Custom']): 
            if float(d_today['High']) >= entry:
                trades += 1
                if float(d_today['Close']) > entry: wins += 1
    
    win_rate = 0
    if trades > 0: win_rate = round((wins/trades)*100, 1)
    return win_rate

# ==========================================
# 2. 網頁介面佈局
# ==========================================

# --- 側邊欄 (設定區) ---
with st.sidebar:
    st.header("⚙️ 系統設定")
    
    # Telegram 設定 (預設值)
    default_token = "8413918726:AAHVSDexSP7kXpU62iLT5xcKUunfHXeL9QY"
    default_chat_id = "7362057006"
    
    tg_token = st.text_input("Telegram Token", value=default_token, type="password")
    tg_chat_id = st.text_input("Telegram Chat ID", value=default_chat_id)
    
    st.divider()
    
    st.header("📝 股票清單管理")
    
    # 初始化 Session State 中的清單
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = DEFAULT_WATCHLIST

    # 新增股票介面
    with st.expander("➕ 新增/修改股票"):
        new_id = st.text_input("代碼 (如 2330.TW / NVDA)")
        new_name = st.text_input("名稱 (如 台積電)")
        new_ma = st.number_input("MA 參數", value=18, min_value=5, max_value=200)
        
        if st.button("儲存設定"):
            if new_id and new_name:
                found = False
                for stock in st.session_state.watchlist:
                    if stock["id"] == new_id:
                        stock["name"] = new_name
                        stock["ma"] = int(new_ma)
                        found = True
                        break
                if not found:
                    st.session_state.watchlist.append({"id": new_id, "name": new_name, "ma": int(new_ma)})
                
                st.success(f"已儲存 {new_name}")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("代碼與名稱不可為空")

    # 顯示目前清單
    st.write("目前觀察清單：")
    for i, stock in enumerate(st.session_state.watchlist):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text(f"{stock['name']} ({stock['id']}) - {stock['ma']}MA")
        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.watchlist.pop(i)
                st.rerun()

    if st.button("🔄 重置為預設清單"):
        st.session_state.watchlist = DEFAULT_WATCHLIST
        st.rerun()

# --- 主畫面 (戰情室) ---
st.title("📈 Odo 股市操盤戰情室")
st.markdown(f"📅 **日期：** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    start_btn = st.button("🚀 開始智能分析", type="primary", use_container_width=True)

if start_btn:
    st.divider()
    progress_text = "數據連線中，正在下載資料..."
    my_bar = st.progress(0, text=progress_text)
    
    results = []
    telegram_report = f"📊 【Odo 網頁版日報】\n📅 {datetime.now().strftime('%Y-%m-%d')}\n" + "-"*20 + "\n"
    
    total_stocks = len(st.session_state.watchlist)
    
    for idx, stock in enumerate(st.session_state.watchlist):
        ticker = stock["id"]
        name = stock["name"]
        ma_val = stock["ma"]
        
        percent = int(((idx) / total_stocks) * 100)
        my_bar.progress(percent, text=f"正在分析：{name} ({ticker})...")
        
        try:
            df = yf.download(ticker, period="1y", progress=False)
            if len(df) < 60: continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            win_rate = run_backtest_logic(df, ma_val)
            
            df['MA_Custom'] = df['Close'].rolling(window=ma_val).mean()
            today = df.iloc[-1]
            close = float(today['Close'])
            ma_curr = float(today['MA_Custom'])
            
            entry_price = ma_curr * 1.01
            stop_price = ma_curr * 0.99
            
            status = "⚪ 觀望"
            if close < entry_price and close > stop_price:
                status = "🟡 準備 (掛單)"
            elif close > entry_price:
                status = "🔴 強勢 (持股)"
            elif close < stop_price:
                status = "🟢 弱勢 (空手)"
                
            res = {
                "代碼": ticker.replace(".TW", ""),
                "名稱": name,
                "MA參數": f"{ma_val}MA",
                "收盤價": round(close, 2),
                "🎯買入觸發": round(entry_price, 2),
                "🛡️停損觸發": round(stop_price, 2),
                "歷史勝率": f"{win_rate}%",
                "狀態": status
            }
            results.append(res)
            
            if "準備" in status or "強勢" in status:
                telegram_report += f"{status.split(' ')[0]} {name} ({ma_val}MA)\n"
                telegram_report += f"觸發: {res['🎯買入觸發']} | 停損: {res['🛡️停損觸發']}\n"
                telegram_report += "-"*15 + "\n"
                
        except Exception as e:
            st.error(f"{name} 分析錯誤: {e}")

    my_bar.progress(100, text="分析完成！")
    time.sleep(0.5)
    my_bar.empty()

    if results:
        df_res = pd.DataFrame(results)
        
        st.subheader("📋 分析結果總表")
        
        def highlight_status(val):
            if '強勢' in str(val): return 'background-color: #ffcccc'
            elif '準備' in str(val): return 'background-color: #ffffcc'
            elif '弱勢' in str(val): return 'background-color: #ccffcc'
            return ''

        st.dataframe(
            df_res.style.map(highlight_status, subset=['狀態']),
            use_container_width=True,
            height=400
        )
        
        file_name = f'Odo_Report_{datetime.now().strftime("%Y%m%d")}.xlsx'
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_res.to_excel(writer, index=False)
            excel_data = output.getvalue()

            st.download_button(
                label="📥 下載 Excel 報表",
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        except Exception as e:
            st.error(f"Excel 生成失敗: {e}")

        st.subheader("📡 Telegram 通知狀態")
        telegram_report += "✅ 詳細報表請見網頁或 Excel。"
        
        col_tg1, col_tg2 = st.columns([1, 4])
        with col_tg1:
            if st.button("手動發送 Telegram 通知"):
                success, msg = send_telegram_message(tg_token, tg_chat_id, telegram_report)
                if success:
                    st.success("訊息發送成功！")
                else:
                    st.error(msg)
        
        with st.expander("預覽 Telegram 訊息內容"):
            st.text(telegram_report)
    else:
        st.warning("無資料或所有股票下載失敗")

st.markdown("---")

st.markdown("Designed by **Odo AI Assistant** | Powered by Streamlit")
