import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import datetime


st.title('日本株　株価情報')

# ユーザーに証券コードの入力を求める
symbol = st.text_input('証券コードを入力してください（例:9211.T）', '9211.T')

# 株価データの取得
data = yf.Ticker(symbol)

# 会社名の取得と表示
company_name = data.info['longName']
st.write(f'## {company_name}')  

# 現在の株価と時価総額の取得
current_price = data.info['currentPrice']
market_cap = data.info['marketCap']

# 時価総額を百万単位に変換
market_cap_million = "{:,}百万".format(market_cap // 1000000)

# 現在の株価と時価総額の表示
st.markdown(f'<h1 style="font-size:25px;">現在の株価: {current_price}</h1>', unsafe_allow_html=True)
st.write(f'時価総額: {market_cap_million}')

# 株価の履歴データを取得する
hist = data.history(period="2d")

# 前日比とそのパーセンテージの計算と表示
previous_close = hist['Close'][-2]
change = current_price - previous_close
percent_change = (change / previous_close) * 100
st.write(f'前日比: {change}　　　変化率: {percent_change:.2f}%')

# 最新の株価データを取得
latest_data = hist.iloc[-1]

# 始値、高値、安値、前日の終値を取得して表示
open_price = latest_data['Open']
high_price = latest_data['High']
low_price = latest_data['Low']
previous_close_price = hist.iloc[-2]['Close']
st.write(f"前日終値: {previous_close_price}　 始値: {open_price}　高値: {high_price}　安値: {low_price}")

# ユーザーに日付の入力を求める
start_date = st.date_input("開始日を選択", datetime.date.today() - datetime.timedelta(days=365))

# 選択された日付から現在までの株価データを取得
hist = data.history(start=start_date, end=datetime.date.today())

# サブプロットの作成（2行1列）
fig = make_subplots(rows=2, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.03,
                    subplot_titles=('株価', '出来高'), 
                    row_width=[0.2, 0.7])

# ローソク足チャートの追加
fig.add_trace(go.Candlestick(x=hist.index, 
                             open=hist['Open'],
                             high=hist['High'], 
                             low=hist['Low'], 
                             close=hist['Close'], 
                             name="OHLC", 
                             increasing_line_color='red',
                             decreasing_line_color='limegreen'),
                             row=1, col=1)

# 移動平均のラインを計算、追加
moving_avg_5d = hist['Close'].rolling(window=5).mean()
moving_avg_25d = hist['Close'].rolling(window=25).mean()
moving_avg_75d = hist['Close'].rolling(window=75).mean()
fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_5d, mode='lines', name='MA 5 days', line=dict(width=1.5, color='lightgreen')))
fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_25d, mode='lines', name='MA 25 days', line=dict(width=1.5, color='skyblue')))
fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_75d, mode='lines', name='MA 75 days', line=dict(width=1.5, color='mediumpurple')))

# 出来高の棒グラフの追加
fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume'), row=2, col=1)

# レイアウトの更新
fig.update_layout(xaxis_rangeslider_visible=False, height=800)

# チャート表示
st.plotly_chart(fig)


