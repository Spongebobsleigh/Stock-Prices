import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import datetime
import pandas as pd


st.title('株価・株式情報表示アプリ')

# ユーザーに証券コードの入力を求める
symbol = st.text_input('証券コードを入力してEnterを押してください（例: <9211.T> <GOOGL>）', '9211.T')
if not symbol.strip():
    st.error("証券コードを入力してください。")
else:

    # 株価データの取得
    data = yf.Ticker(symbol)

    # 会社名の取得と表示
    company_name = data.info['longName']
    st.write(f'## {company_name}')  

    # 現在の株価と時価総額の取得
    current_price = data.info['currentPrice']
    market_cap = data.info['marketCap']

    # 日本株の場合、百万単位
    if symbol.endswith('.T'):
        market_cap_million = "{:,}百万".format(market_cap // 1000000)
    else:
        market_cap_million = "{:,}".format(market_cap)

    # 現在の株価と時価総額の表示
    st.markdown(f'<h1 style="font-size:25px;">現在の株価: {current_price}</h1>', unsafe_allow_html=True)
    st.write(f'時価総額: {market_cap_million}')

    # 株価の履歴データを取得する
    hist = data.history(period="2d")

    # 前日比とそのパーセンテージの計算と表示
    previous_close = hist['Close'][-2]
    change = current_price - previous_close
    percent_change = (change / previous_close) * 100
    st.write(f'前日比: {change:.1f}　　　変化率: {percent_change:.2f}%')

    # 最新の株価データを取得
    latest_data = hist.iloc[-1]

    # 始値、高値、安値、前日の終値を取得して表示
    open_price = latest_data['Open']
    high_price = latest_data['High']
    low_price = latest_data['Low']
    previous_close_price = hist.iloc[-2]['Close']
    st.write(f"前日終値: {previous_close_price:.1f}　 始値: {open_price:.1f}　高値: {high_price:.1f}　安値: {low_price:.1f}")

    # ユーザーに日付の入力を求める
    #start_date = st.date_input("表示開始日を選択", datetime.date.today() - datetime.timedelta(days=365))

    # 選択された日付から現在までの株価データを取得
    #hist = data.history(start=start_date, end=datetime.date.today())

    # サイドバーに選択ボックスを作成
    timeframe = st.sidebar.selectbox(
        "日足・週足・月足",
        ["1d", "1wk", "1mo"]
    )

    # 選択された時間間隔に基づいて株価データを取得
    hist = data.history(period="1y", interval=timeframe)

    # サイドバーに表示範囲を選択するスライドバーを追加
    days = st.sidebar.slider("表示範囲を選択（日数）", min_value=30, max_value=730, value=365, step=5)

    # 選択された日数に基づいて株価データの開始日を計算
    start_date = datetime.date.today() - datetime.timedelta(days=days)

    # 選択された日付から現在までの株価データを取得
    hist = data.history(start=start_date, end=datetime.date.today(), interval=timeframe)


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

    fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_5d, 
                            mode='lines', name='移動平均 5', 
                            line=dict(width=1.5, color='lightgreen')))
    fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_25d, 
                            mode='lines', name='移動平均 25', 
                            line=dict(width=1.5, color='skyblue')))
    fig.add_trace(go.Scatter(x=hist.index, y=moving_avg_75d, 
                            mode='lines', name='移動平均 75', 
                            line=dict(width=1.5, color='mediumpurple')))

    # 出来高の棒グラフの追加
    fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='出来高'), row=2, col=1)

    # レイアウトの更新
    fig.update_layout(xaxis_rangeslider_visible=False, height=800)

    # チャート表示
    st.plotly_chart(fig)


# 日本株銘柄一覧の読み込み
df = pd.read_excel('./dataJP.xls')

# 企業名て証券コードを検索
company_name_input = st.sidebar.text_input("銘柄名を入力して証券コードを検索(日本株)　　　　例: <トヨタ> <愛知>")

if company_name_input:
    result = df[df['銘柄名'].str.contains(company_name_input, case=False, na=False)]
    # result = df[df['銘柄名'] == company_name_input]

    if not result.empty:
        # st.sidebar.write(f"証券コード: {result.iloc[0]['コード']}")
        for _, row in result.iterrows():
            st.sidebar.write(f"銘柄名: {row['銘柄名']} - 証券コード: {row['コード']}.T")
    else:
        st.sidebar.write("該当する企業は見つかりませんでした。")

# col1, col2 = st.columns([2, 1])

# 左側のカラム（col1）にはメインのコンテンツを配置
# with col1:
    # ここに既存の株価チャートなどのコードを配置
