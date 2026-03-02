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
    {"id": "^DJI", "name": "道瓊指數", "ma": 20},
{"id": "^GSPC", "name": "標普500", "ma": 19},
{"id": "^RUT", "name": "羅素2000", "ma": 22},
{"id": "^IXIC", "name": "那斯達克", "ma": 20},
{"id": "^SOX", "name": "費城半導體", "ma": 20},
{"id": "NVDA", "name": "輝達", "ma": 19},
{"id": "MSFT", "name": "微軟", "ma": 21},
{"id": "TSLA", "name": "特斯拉", "ma": 17},
{"id": "GOOGL", "name": "google", "ma": 26},
{"id": "AMZN", "name": "亞馬遜", "ma": 19},
{"id": "META", "name": "臉書", "ma": 24},
{"id": "AAPL", "name": "蘋果", "ma": 19},
{"id": "TSM", "name": "台積電", "ma": 19},
{"id": "INTC", "name": "英特爾", "ma": 27},
{"id": "AMD", "name": "AMD", "ma": 22},
{"id": "ADBE", "name": "Adobe", "ma": 25},
{"id": "ASML", "name": "阿麥斯", "ma": 24},
{"id": "QCOM", "name": "高通", "ma": 25},
{"id": "NFLX", "name": "奈飛", "ma": 23},
{"id": "COST", "name": "好市多", "ma": 18},
{"id": "MA", "name": "萬事達卡", "ma": 33},
{"id": "V", "name": "VISA卡", "ma": 22},
{"id": "HD", "name": "家得寶", "ma": 17},
{"id": "ZTS", "name": "碩騰動物疫苗寵愛疫苗", "ma": 28},
{"id": "TTD", "name": "THE TRADE", "ma": 23},
{"id": "JNJ", "name": "嬌生", "ma": 26},
{"id": "IBM", "name": "IBM", "ma": 19},
{"id": "AVGO", "name": "博通", "ma": 24},
{"id": "UNH", "name": "聯合健康", "ma": 26},
{"id": "ULTA", "name": "ULTA美容", "ma": 26},
{"id": "AMG", "name": "聯邦農業抵押貸款", "ma": 22},
{"id": "AJG", "name": "亞瑟保險經紀人", "ma": 23},
{"id": "BKNG", "name": "BOOKING訂房網", "ma": 23},
{"id": "NVO", "name": "諾和諾德", "ma": 26},
{"id": "IBP", "name": "IBP建築施工", "ma": 20},
{"id": "PAYC", "name": "PAYCOM人資管理系統", "ma": 20},
{"id": "URI", "name": "聯合工業設備租賃", "ma": 22},
{"id": "GIB", "name": "GIB綜合資訊服務", "ma": 21},
{"id": "CTAS", "name": "信達斯", "ma": 19},
{"id": "CHE", "name": "CHEMED臨終照護", "ma": 24},
{"id": "1210.TW", "name": "大成", "ma": 26},
{"id": "1216.TW", "name": "統一", "ma": 26},
{"id": "1477.TW", "name": "聚陽", "ma": 25},
{"id": "1514.TW", "name": "亞力", "ma": 51},
{"id": "2006.TW", "name": "東和鋼鐵", "ma": 21},
{"id": "2303.TW", "name": "聯電", "ma": 21},
{"id": "2301.TW", "name": "光寶", "ma": 18},
{"id": "2308.TW", "name": "台達電", "ma": 19},
{"id": "2313.TW", "name": "華通", "ma": 20},
{"id": "2317.TW", "name": "鴻海", "ma": 19},
{"id": "2324.TW", "name": "仁寶", "ma": 19},
{"id": "2327.TW", "name": "國巨", "ma": 20},
{"id": "2330.TW", "name": "台積電", "ma": 17},
{"id": "2337.TW", "name": "旺宏", "ma": 28},
{"id": "2344.TW", "name": "華邦電", "ma": 31},
{"id": "2345.TW", "name": "智邦", "ma": 28},
{"id": "2352.TW", "name": "佳士達", "ma": 19},
{"id": "2353.TW", "name": "宏碁", "ma": 20},
{"id": "2354.TW", "name": "鴻準", "ma": 34},
{"id": "2356.TW", "name": "英業達", "ma": 23},
{"id": "2357.TW", "name": "華碩", "ma": 21},
{"id": "2360.TW", "name": "致茂", "ma": 21},
{"id": "2362.TW", "name": "藍天", "ma": 23},
{"id": "2368.TW", "name": "金像電", "ma": 22},
{"id": "2376.TW", "name": "技嘉", "ma": 29},
{"id": "2377.TW", "name": "微星", "ma": 18},
{"id": "2379.TW", "name": "瑞昱", "ma": 26},
{"id": "2382.TW", "name": "廣達", "ma": 23},
{"id": "2383.TW", "name": "台光電", "ma": 18},
{"id": "2385.TW", "name": "群光", "ma": 20},
{"id": "2393.TW", "name": "億光", "ma": 20},
{"id": "2395.TW", "name": "研華", "ma": 22},
{"id": "2404.TW", "name": "漢唐", "ma": 29},
{"id": "2408.TW", "name": "南亞科", "ma": 13},
{"id": "2409.TW", "name": "友達", "ma": 18},
{"id": "2428.TW", "name": "興勤", "ma": 24},
{"id": "2439.TW", "name": "美律", "ma": 18},
{"id": "2454.TW", "name": "聯發科", "ma": 29},
{"id": "2472.TW", "name": "立隆電", "ma": 24},
{"id": "2496.TW", "name": "卓越", "ma": 29},
{"id": "2603.TW", "name": "長榮", "ma": 35},
{"id": "2727.TW", "name": "王品", "ma": 28},
{"id": "2753.TW", "name": "八方雲集", "ma": 29},
{"id": "2755.TW", "name": "揚秦", "ma": 22},
{"id": "2891.TW", "name": "中信金", "ma": 18},
{"id": "3005.TW", "name": "神基", "ma": 21},
{"id": "3017.TW", "name": "奇鋐", "ma": 19},
{"id": "3029.TW", "name": "零壹", "ma": 20},
{"id": "3036.TW", "name": "文曄", "ma": 18},
{"id": "3130.TW", "name": "104", "ma": 22},
{"id": "3231.TW", "name": "緯創", "ma": 26},
{"id": "3443.TW", "name": "創意", "ma": 18},
{"id": "3583.TW", "name": "辛耘", "ma": 21},
{"id": "3706.TW", "name": "神達", "ma": 23},
{"id": "4987.TW", "name": "科誠", "ma": 25},
{"id": "5904.TW", "name": "寶雅", "ma": 21},
{"id": "6138.TW", "name": "茂達", "ma": 21},
{"id": "6146.TW", "name": "耕興", "ma": 25},
{"id": "6176.TW", "name": "瑞儀", "ma": 22},
{"id": "6191.TW", "name": "精誠科", "ma": 25},
{"id": "6192.TW", "name": "巨路", "ma": 29},
{"id": "6197.TW", "name": "佳必琪", "ma": 23},
{"id": "6201.TW", "name": "亞弘電", "ma": 34},
{"id": "6239.TW", "name": "力成", "ma": 23},
{"id": "6279.TW", "name": "胡連", "ma": 19},
{"id": "6284.TW", "name": "佳邦", "ma": 24},
{"id": "6409.TW", "name": "旭準", "ma": 23},
{"id": "6285.TW", "name": "啟碁", "ma": 21},
{"id": "6667.TW", "name": "信紘科", "ma": 26},
{"id": "6669.TW", "name": "緯穎", "ma": 28},
{"id": "6706.TW", "name": "惠特", "ma": 19},
{"id": "6721.TW", "name": "信實", "ma": 17},
{"id": "6728.TW", "name": "上洋", "ma": 19},
{"id": "6805.TW", "name": "富世達", "ma": 18},
{"id": "8210.TW", "name": "勤誠", "ma": 25},
{"id": "8367.TW", "name": "建新國際", "ma": 22},
{"id": "9939.TW", "name": "宏全", "ma": 17},
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





