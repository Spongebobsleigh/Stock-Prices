import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import datetime
import pandas as pd


st.markdown("""
    <style>
    .title {
        color: #04B486;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="title">株価・株式情報表示アプリ</h1>', unsafe_allow_html=True)

symbol = st.text_input('証券コードを入力してEnterを押してください（例: <9211.T> <GOOGL>）', '9211.T')
if not symbol.strip():
    st.error("証券コードを入力してください。")
else:

    data = yf.Ticker(symbol)

    if "longName" not in data.info:
        st.error("該当する銘柄が見つかりません。")
    else:
        company_name = data.info['longName']
        st.write(f'## {company_name}')  

        current_price = data.info['currentPrice']
        market_cap = data.info['marketCap']

        # 日本株の場合、百万単位
        if symbol.endswith('.T'):
            market_cap_million = "{:,}百万".format(market_cap // 1000000)
        else:
            market_cap_million = "{:,}".format(market_cap)

        st.markdown(f'<h1 style="font-size:25px;">現在の株価: {current_price}</h1>', unsafe_allow_html=True)
        st.write(f'時価総額: {market_cap_million}')

        # 株価の履歴データを取得する
        hist = data.history(period="2d")

        previous_close = hist['Close'][-2]
        change = current_price - previous_close
        percent_change = (change / previous_close) * 100
        st.write(f'前日比: {change:.1f}　　　変化率: {percent_change:.2f}%')


        latest_data = hist.iloc[-1]
        open_price = latest_data['Open']
        high_price = latest_data['High']
        low_price = latest_data['Low']
        previous_close_price = hist.iloc[-2]['Close']
        st.write(f"前日終値: {previous_close_price:.1f}　 始値: {open_price:.1f}　高値: {high_price:.1f}　安値: {low_price:.1f}")


        timeframe = st.sidebar.selectbox(
            "日足・週足・月足",
            ["1d", "1wk", "1mo"]
        )

        hist = data.history(period="1y", interval=timeframe)

        days = st.sidebar.slider("表示範囲を選択（日数）", min_value=30, max_value=730, value=365, step=5)

        start_date = datetime.date.today() - datetime.timedelta(days=days)

        hist = data.history(start=start_date, end=datetime.date.today(), interval=timeframe)


        fig = make_subplots(rows=2, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.03,
                            subplot_titles=('株価', '出来高'), 
                            row_width=[0.2, 0.7])

        # ローソク足チャート
        fig.add_trace(go.Candlestick(x=hist.index, 
                                    open=hist['Open'],
                                    high=hist['High'], 
                                    low=hist['Low'], 
                                    close=hist['Close'], 
                                    name="赤増：緑減", 
                                    increasing_line_color='red',
                                    decreasing_line_color='limegreen'),
                                    row=1, col=1)

        # 移動平均
        moving_avg_5d = hist['Close'].rolling(window=5).mean()
        moving_avg_25d = hist['Close'].rolling(window=25).mean()
        moving_avg_75d = hist['Close'].rolling(window=75).mean()

        fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_5d, 
                                mode='lines', name='移動平均 5', 
                                line=dict(width=1.5, color='lightgreen')))
        fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_25d, 
                                mode='lines', name='移動平均 25', 
                                line=dict(width=1.5, color='skyblue')))
        fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_75d, 
                                mode='lines', name='移動平均 75', 
                                line=dict(width=1.5, color='mediumpurple')))

        # 出来高
        fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='出来高'), row=2, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False, height=800)
        st.plotly_chart(fig)


# 証券コード検索機能
df = pd.read_excel('./dataJP2.xls')

company_name_input = st.sidebar.text_input("銘柄名を入力して証券コードを検索(日本株)　例: <トヨタ> <愛知>")

if company_name_input:
    result = df[df['銘柄名'].str.contains(company_name_input, case=False, na=False)]

    if not result.empty:
        for _, row in result.iterrows():
            st.sidebar.write(f"銘柄名: {row['銘柄名']} - 証券コード: {row['コード']:.0f}.T")
    else:
        st.sidebar.write("該当する銘柄は見つかりませんでした。")
