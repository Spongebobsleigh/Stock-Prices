import streamlit as st
import yfinance as yf
import plotly.graph_objs as go


st.title('日本株  株価表示')

# ユーザーに証券コードの入力を求める
symbol = st.text_input('証券コードを入力してください（例:7203.T）', '7203.T')

# 株価データの取得
data = yf.Ticker(symbol)

# 会社名の取得と表示
company_name = data.info['longName']
st.write(f'## {company_name}')  

# 現在の株価と時価総額の取得
current_price = data.info['currentPrice']
market_cap = data.info['marketCap']

# 時価総額を百万単位に変換し、フォーマットを適用
market_cap_million = "{:,}百万".format(market_cap // 1000000)

# 現在の株価と時価総額の表示
st.write(f'現在の株価: {current_price}')
st.write(f'時価総額: {market_cap_million}')

# 株価の履歴データを取得する
hist = data.history(period="2d")

# 前日比とそのパーセンテージの計算
previous_close = hist['Close'][-2]
change = current_price - previous_close
percent_change = (change / previous_close) * 100

# 前日比とそのパーセンテージの表示
st.write(f'前日比: {change}')
st.write(f'変化率: {percent_change:.2f}%')

# ユーザーに期間の選択を求める
timeframe = st.selectbox(
    '表示する期間を選択してください',
    ('1d', '1wk', '1h')
)

# 選択された期間に基づいて株価の履歴データを取得
hist = data.history(period="1y", interval=timeframe)

# ローソク足チャートの作成
fig = go.Figure(data=[go.Candlestick(x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                increasing_line_color='orangered',
                decreasing_line_color='lawngreen'
)])

# チャートのタイトル
fig.update_layout(title=f'過去1年間のチャート', xaxis_rangeslider_visible=True)

# チャートの表示
st.plotly_chart(fig)
