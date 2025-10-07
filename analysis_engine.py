

# --- IMPORTS ---
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pmdarima as pm
from statsmodels.tsa.arima.model import ARIMA
import praw
from textblob import TextBlob

# --- STOCK DATA ---
def get_stock_data(ticker_symbol):
    """
    Fetches historical stock data and company information from Yahoo Finance.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period="5y")
        if hist.empty:
            print(f"No historical data found for {ticker_symbol}")
            return None, None
        # Check for essential data points
        if 'longName' not in info or 'symbol' not in info:
            return None, None
        return info, hist
    except Exception as e:
        print(f"Error fetching stock data for {ticker_symbol}: {e}")
        return None, None

# --- TECHNICAL ANALYSIS ---
def calculate_technical_indicators(df):
    """
    Calculates Simple Moving Averages (SMA) for the stock data.
    """
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    return df

# --- FORECASTING ---
def forecast_stock_price(df, days_to_predict=30):
    """
    Forecasts the stock price using an auto-selected ARIMA model.
    """
    try:
        model = pm.auto_arima(df['Close'], start_p=1, start_q=1,
                             test='adf',       # use adftest to find optimal 'd'
                             max_p=3, max_q=3, # maximum p and q
                             m=1,              # frequency of series
                             d=None,           # let model determine 'd'
                             seasonal=False,   # No seasonality
                             start_P=0, 
                             D=0, 
                             trace=False,
                             error_action='ignore',  
                             suppress_warnings=True, 
                             stepwise=True)

        model_fit = model.fit(df['Close'])
        forecast = model_fit.predict(n_periods=days_to_predict)
        forecast_dates = pd.to_datetime(df.index[-1]) + pd.to_timedelta(range(1, days_to_predict + 1), unit='D')
        return forecast, forecast_dates
    except Exception as e:
        print(f"Error during ARIMA forecasting: {e}")
        return pd.Series(), pd.Index([])

# --- SENTIMENT ANALYSIS ---
def get_reddit_sentiment(ticker_symbol, reddit_credentials, submission_limit=15, comment_limit=10):
    """
    Fetches and analyzes Reddit sentiment for a given stock ticker.
    NOTE: This is a simplified sentiment analysis and may not capture the full nuance of financial discussions.
    """
    try:
        reddit = praw.Reddit(**reddit_credentials)
        subreddit = reddit.subreddit("wallstreetbets+stocks")
        # More specific search query
        search_query = f'"{ticker_symbol}"'
        submissions = subreddit.search(search_query, limit=submission_limit)

        posts = []
        sentiment_scores = []
        for submission in submissions:
            # Basic filtering to improve relevance
            if ticker_symbol.lower() in submission.title.lower() or ticker_symbol.lower() in submission.selftext.lower():
                posts.append(submission)
                sentiment_scores.append(TextBlob(submission.title).sentiment.polarity)
                submission.comments.replace_more(limit=0)
                for comment in submission.comments[:comment_limit]:
                    sentiment_scores.append(TextBlob(comment.body).sentiment.polarity)

        if not sentiment_scores:
            return 0, [], []

        sentiment = sum(sentiment_scores) / len(sentiment_scores)
        return sentiment, posts, []
    except Exception as e:
        print(f"Error fetching Reddit sentiment for {ticker_symbol}: {e}")
        return 0, [], []

# --- PLOTTING ---
def create_plot(df, forecast, forecast_dates, ticker_symbol):
    """
    Creates an interactive Plotly chart of the stock data and forecast.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='50-Day SMA', line=dict(color='yellow', dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], name='200-Day SMA', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, name='Sentiment-Adjusted Forecast', line=dict(color='green', dash='dot')))

    fig.update_layout(
        title=f'{ticker_symbol.upper()} Stock Price Analysis & Forecast',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        xaxis_rangeslider_visible=True
    )

    return fig.to_html(full_html=False)

# --- ANALYSIS ORCHESTRATION ---
def run_analysis(ticker_symbol, reddit_credentials, sentiment_adjustment_factor=0.5):
    """
    Orchestrates the entire stock analysis process.
    """
    # 1. Fetch Data
    info, hist = get_stock_data(ticker_symbol)
    if info is None or hist is None:
        return {'error': f"Could not fetch data for {ticker_symbol.upper()}. It may be an invalid ticker."}

    # 2. Technical Analysis
    hist = calculate_technical_indicators(hist)

    # 3. Forecasting
    forecast, forecast_dates = forecast_stock_price(hist)
    if forecast.empty:
        return {'error': f"Could not generate a forecast for {ticker_symbol.upper()}."}

    # 4. Sentiment Analysis
    sentiment, posts, _ = get_reddit_sentiment(ticker_symbol, reddit_credentials)

    # 5. Sentiment-based Forecast Adjustment
    # This is a basic adjustment. A more complex model could be used here. See TECHDOC.md.
    if sentiment > 0.1:
        adjustment = 1 + (sentiment * sentiment_adjustment_factor)
        forecast = forecast * adjustment
    elif sentiment < -0.1:
        adjustment = 1 + (sentiment * sentiment_adjustment_factor)
        forecast = forecast * adjustment

    # 6. Create Plot
    plot_html = create_plot(hist, forecast, forecast_dates, ticker_symbol)

    # 7. Prepare data for display, handling missing values
    display_info = {
        'longName': info.get('longName', 'N/A'),
        'symbol': info.get('symbol', 'N/A'),
        'longBusinessSummary': info.get('longBusinessSummary', 'N/A'),
        'marketCap': info.get('marketCap', 'N/A'),
        'dayHigh': info.get('dayHigh', 'N/A'),
        'dayLow': info.get('dayLow', 'N/A'),
        'trailingPE': info.get('trailingPE', 'N/A'),
        'dividendYield': info.get('dividendYield', 'N/A'),
        'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 'N/A'),
    }

    return {
        'info': display_info,
        'plot_html': plot_html,
        'sentiment': sentiment,
        'posts': posts,
        'error': None
    }
