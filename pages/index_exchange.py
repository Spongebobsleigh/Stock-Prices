import yfinance as yf
import plotly.graph_objs as go
import streamlit as st

st.markdown("""
    <style>
    .title {
        color: #04B486;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title">指数・為替</h1>', unsafe_allow_html=True)


period = st.sidebar.radio("表示期間を選択", ('5d', '1mo', '6mo', '1y'), index=3)

nikkei = yf.Ticker("^N225")
usdjpy = yf.Ticker("JPY=X")

nikkei_hist = nikkei.history(period=period)
usdjpy_hist = usdjpy.history(period=period)

# 現在の値を取得
nikkei_current = nikkei_hist['Close'].iloc[-1]
usdjpy_current = usdjpy_hist['Close'].iloc[-1]

# 日経平均
st.markdown(f"## 日経平均株価　{nikkei_current:.2f}", unsafe_allow_html=True)

nikkei_fig = go.Figure()
nikkei_fig.add_trace(go.Scatter(x=nikkei_hist.index, y=nikkei_hist['Close'],
                                fill='tozeroy', 
                                line_color='#04B486'))
nikkei_fig.update_layout(title="", yaxis_range=[24000, max(nikkei_hist['Close'])])
st.plotly_chart(nikkei_fig)


# ドル/円
st.markdown(f"## USドル/円　{usdjpy_current:.2f}", unsafe_allow_html=True)

usdjpy_fig = go.Figure()
usdjpy_fig.add_trace(go.Scatter(x=usdjpy_hist.index, y=usdjpy_hist['Close'],
                                fill='tozeroy',
                                line_color='#04B486'))
usdjpy_fig.update_layout(title="", yaxis_range=[130, max(usdjpy_hist['Close'])])
st.plotly_chart(usdjpy_fig)
