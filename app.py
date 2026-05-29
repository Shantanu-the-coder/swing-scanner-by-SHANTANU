import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# Page configurations & Dark Theme
st.set_page_config(page_title="Ultimate Swing Scanner", layout="wide")

# ADVANCED UI CUSTOMIZATION: Thicker sliders with proper dynamic directional gradients
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { background-color: #2ea043; color: white; border-radius: 5px; width: 100%; }
    
    /* Global Thicker Slider Style */
    div[data-baseweb="slider"] div[role="slider"] {
        height: 22px !important;
        width: 22px !important;
        background-color: #ffffff !important;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.5) !important;
    }
    
    /* Specific Slider Track Overrides using unique keys */
    /* 1. Volume Slider Track: INVERTED (Red to Yellow to Green) - Higher is Safer */
    div[data-testid="stSidebar"] div.stSlider:nth-of-type(2) > div > div > div {
        height: 12px !important;
        background: linear-gradient(to right, #ea4335 0%, #ffeb3b 50%, #2ea043 100%) !important;
        border-radius: 6px !important;
    }
    
    /* 2. Distance From High Track: STANDARD (Green to Yellow to Red) - Lower is Safer */
    div[data-testid="stSidebar"] div.stSlider:nth-of-type(3) > div > div > div {
        height: 12px !important;
        background: linear-gradient(to right, #2ea043 0%, #ffeb3b 50%, #ea4335 100%) !important;
        border-radius: 6px !important;
    }
    
    /* 3. Distance From 20 SMA Track: STANDARD (Green to Yellow to Red) - Lower is Safer */
    div[data-testid="stSidebar"] div.stSlider:nth-of-type(4) > div > div > div {
        height: 12px !important;
        background: linear-gradient(to right, #2ea043 0%, #ffeb3b 50%, #ea4335 100%) !important;
        border-radius: 6px !important;
    }
    
    /* Badges & Recommendation Styles */
    .safe-badge { color: #2ea043; font-size: 13px; font-weight: bold; margin-top: -12px; margin-bottom: 2px; display: block; }
    .unsafe-badge { color: #ea4335; font-size: 13px; font-weight: bold; margin-top: -12px; margin-bottom: 2px; display: block; }
    .rec-text { color: #8892b0; font-size: 12px; font-style: italic; margin-bottom: 15px; display: block; }
    </style>
""", unsafe_allow_html=True)

BENCHMARK = "^NSEI"

UNIVERSE_STOCKS = {
    "NIFTY 50": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", "SBI.NS", "BAJAJFINSV.NS", "M&M.NS", "MARUTI.NS", "TATAMOTORS.NS", "SUNPHARMA.NS", "AXISBANK.NS", "ADANIENT.NS", "NTPC.NS", "KOTAKBANK.NS", "TITAN.NS"],
    "NIFTY 100": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", "SBI.NS", "M&M.NS", "MARUTI.NS", "TATAMOTORS.NS", "SUNPHARMA.NS", "AXISBANK.NS", "KOTAKBANK.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS", "VBL.NS", "COLPAL.NS", "PNB.NS"],
    "NIFTY 200": ["TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS", "PERSISTENT.NS", "LTIM.NS", "COFORGE.NS", "MPHASIS.NS", "KPITTECH.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "AUBANK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "INDUSINDBK.NS", "PNB.NS", "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "BALKRISIND.NS", "TIINDIA.NS", "MRF.NS", "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS", "BIOCON.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NATIONALUM.NS", "SAIL.NS", "JINDALSTEL.NS", "NMDC.NS", "ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS", "VBL.NS", "COLPAL.NS"],
    "NIFTY 500": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", "SBI.NS", "M&M.NS", "MARUTI.NS", "TATAMOTORS.NS", "SUNPHARMA.NS", "AXISBANK.NS", "KOTAKBANK.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS", "CIPLA.NS", "DRREDDY.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS", "VBL.NS", "COLPAL.NS", "PNB.NS", "BHEL.NS", "PFC.NS", "RECLTD.NS", "IRFC.NS", "GAIL.NS", "IOC.NS", "BPCL.NS"]
}

st.title("🚀 Ultimate Multi-Universe Swing Scanner")
st.subheader("Top-Down Strategy Dashboard (After-Market & Pre-Market Fixed Engine)")

# Sidebar Controls
st.sidebar.header("⚙️ Dynamic Configuration")
selected_universe = st.sidebar.selectbox("Select Stock Bunch (Universe)", ["NIFTY 50", "NIFTY 100", "NIFTY 200", "NIFTY 500"], index=2)
st.sidebar.markdown(f'<span class="safe-badge">🟢 Scanning {len(UNIVERSE_STOCKS[selected_universe])} Tickers</span>', unsafe_allow_html=True)

short_term_lookback = st.sidebar.slider("Sector Rotation Lookback (Days)", 3, 30, 10, 1, key="lookback_slider")
st.sidebar.markdown('<span class="safe-badge">🟢 Current Mode: Active</span>', unsafe_allow_html=True)
st.sidebar.markdown('<span class="rec-text">💡 Recommendation: 5 to 12 Days (Captures fresh institutional rotation)</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("🛡️ Strategy Safety Guards")

# 1. Volume Surge Slider (Inverted Logic Fixed: Higher is Safer)
vol_multiplier = st.sidebar.slider("Min Volume Surge (x)", 1.0, 3.0, 1.5, 0.1, key="volume_slider")
if vol_multiplier >= 1.5:
    st.sidebar.markdown(f'<span class="safe-badge">🟢 Status: Safe ({vol_multiplier}x Surge)</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<span class="unsafe-badge">🔴 Status: Unsafe Risk (Low Volume)</span>', unsafe_allow_html=True)
st.sidebar.markdown('<span class="rec-text">💡 Recommendation: 1.5x to 3.0x (Ensures institutional buying/heavy delivery)</span>', unsafe_allow_html=True)

# 2. Distance from High Slider (Lower is Safer)
max_dist_from_high = st.sidebar.slider("Max Distance from Day's High (%)", 0.5, 10.0, 2.0, 0.1, key="high_slider")
if max_dist_from_high <= 2.0:
    st.sidebar.markdown(f'<span class="safe-badge">🟢 Status: Safe ({max_dist_from_high}% Close)</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<span class="unsafe-badge">🔴 Status: Unsafe Risk (High Upper Wick)</span>', unsafe_allow_html=True)
st.sidebar.markdown('<span class="rec-text">💡 Recommendation: 0.5% to 2.0% (Traders are holding positions overnight near highs)</span>', unsafe_allow_html=True)

# 3. Distance from 20 SMA Slider (Lower is Safer)
max_20sma_dist = st.sidebar.slider("Max Distance from 20 SMA (%)", 1.0, 15.0, 5.0, 0.5, key="sma_slider")
if max_20sma_dist <= 5.0:
    st.sidebar.markdown(f'<span class="safe-badge">🟢 Status: Safe ({max_20sma_dist}% Near SMA)</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<span class="unsafe-badge">🔴 Status: Unsafe Risk (Overextended)</span>', unsafe_allow_html=True)
st.sidebar.markdown('<span class="rec-text">💡 Recommendation: 1.0% to 5.0% (Fresh breakouts prevent chasing overbought levels)</span>', unsafe_allow_html=True)

# 4. Liquidity Input Block
min_liquidity = st.sidebar.number_input("Min Historical Volume Filter (Shares)", min_value=0, max_value=1000000, value=50000, step=10000)
if min_liquidity >= 50000:
    st.sidebar.markdown('<span class="safe-badge">🟢 Status: Safe Liquidity</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="unsafe-badge">🔴 Status: Low Volume Risk</span>', unsafe_allow_html=True)
st.sidebar.markdown('<span class="rec-text">💡 Recommendation: >= 50,000 Shares (Avoids illiquid operators circuits stocks)</span>', unsafe_allow_html=True)

refresh_btn = st.sidebar.button("🔄 Refresh Scanner Data")

end_date = datetime.now() + timedelta(days=1)
start_date = end_date - timedelta(days=180)

@st.cache_data(ttl=300)
def load_market_data():
    nifty_data = yf.download(BENCHMARK, start=start_date, end=end_date, progress=False)
    return nifty_data

nifty = load_market_data()

if not nifty.empty:
    nifty_close_series = nifty['Close'].squeeze()
    
    nifty_idx = -1
    if pd.isna(nifty_close_series.values[-1]) or nifty['Volume'].squeeze().values[-1] == 0:
        nifty_idx = -2

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Selected Universe", selected_universe)
    with col2:
        st.metric("Sector Lookback Set", f"{short_term_lookback} Days")
    with col3:
        st.metric("Engine Status", "OFF-MARKET (HISTORICAL)")
        
    st.markdown("---")
    st.subheader(f"📋 Breakout Candidates Based on Last Trading Session")
    
    final_candidates = []
    tv_copy_list = []
    
    for ticker in UNIVERSE_STOCKS[selected_universe]:
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if len(df) < 50:
                continue
            
            close_array = df['Close'].squeeze().values
            high_array = df['High'].squeeze().values
            low_array = df['Low'].squeeze().values
            vol_array = df['Volume'].squeeze().values
            
            idx_pos = -1
            if pd.isna(close_array[-1]) or vol_array[-1] == 0:
                idx_pos = -2 if len(close_array) > 1 else -1
            
            close_today = float(close_array[idx_pos])
            high_today = float(high_array[idx_pos])
            low_today = float(low_array[idx_pos])
            volume_today = float(vol_array[idx_pos])
            
            if volume_today < min_liquidity:
                continue
            
            valid_len = len(close_array) + idx_pos + 1 if idx_pos == -2 else len(close_array)
            close_series = pd.Series(close_array[:valid_len])
            vol_series = pd.Series(vol_array[:valid_len])
            
            sma_20 = float(close_series.rolling(window=20).mean().iloc[-1])
            sma_50 = float(close_series.rolling(window=50).mean().iloc[-1])
            avg_vol_20 = float(vol_series.rolling(window=20).mean().iloc[-2])
            
            dist_from_sma20 = ((close_today - sma_20) / sma_20) * 100
            if dist_from_sma20 > max_20sma_dist or dist_from_sma20 < 0:
                continue 
            
            stock_lookback = min(short_term_lookback + 1, len(close_series))
            stock_short_perf = close_today / float(close_series.iloc[-stock_lookback])
            
            nifty_lookback = min(short_term_lookback + 1, len(nifty_close_series))
            nifty_short_perf = float(nifty_close_series.values[nifty_idx]) / float(nifty_close_series.values[-nifty_lookback])
            stock_rs = stock_short_perf - nifty_short_perf
            
            is_rs_positive = stock_rs > 0
            is_trend_bullish = close_today > sma_20 and sma_20 > sma_50
            is_vol_surge = volume_today >= (avg_vol_20 * vol_multiplier)
            dist_pct = ((high_today - close_today) / high_today) * 100
            is_strong_close = dist_pct <= max_dist_from_high
            
            if is_rs_positive and is_trend_bullish and is_vol_surge and is_strong_close:
                entry_level = high_today + (high_today * 0.002) 
                stop_loss = low_today - (low_today * 0.002)     
                risk = entry_level - stop_loss
                target_level = entry_level + (2 * risk)         
                
                clean_symbol = ticker.replace(".NS", "")
                tv_copy_list.append(f"NSE:{clean_symbol}")
                
                final_candidates.append({
                    "Stock Symbol": clean_symbol,
                    "Last Close": round(close_today, 2),
                    "Volume Surge": f"{round(volume_today / avg_vol_20, 2)}x",
                    "Dist from 20 SMA": f"{round(dist_from_sma20, 2)}%",
                    "Trigger Entry (Buy)": round(entry_level, 2),
                    "Price Action SL": round(stop_loss, 2),
                    "Target (1:2 RR)": round(target_level, 2)
                })
        except:
            continue
            
    final_candidates = final_candidates[:10]
    tv_copy_list = tv_copy_list[:10]
    
    if final_candidates:
        res_df = pd.DataFrame(final_candidates)
        st.dataframe(res_df, use_container_width=True, hide_index=True)
        
        tv_string = ", ".join(tv_copy_list)
        st.markdown("---")
        st.markdown("### 🛠️ TradingView Watchlist Copier")
        st.text_input("Copy the watchlist text inside the box below:", value=tv_string, key="tv_input")
        if st.button("📋 Click to Copy List"):
            st.success(f"Copied: {tv_string}")
    else:
        st.info("No breakouts found with current criteria. Loosen your sliders (e.g., higher Max Distance from 20 SMA) to scan deeper.")
else:
    st.error("Failed to connect with market data systems.")