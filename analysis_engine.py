

# --- IMPORTS ---


import yfinance as yf


import pandas as pd


import plotly.graph_objects as go


from statsmodels.tsa.arima.model import ARIMA


import praw


from textblob import TextBlob


import itertools





# --- STOCK DATA ---


def get_stock_data(ticker_symbol):


    """


    Fetches historical stock data and company information from Yahoo Finance.


    


    Args:


        ticker_symbol (str): The stock ticker symbol.


        


    Returns:


        tuple: A tuple containing the company information (dict) and historical data (DataFrame).


               Returns (None, None) if the ticker is invalid or data cannot be fetched.


    """


    try:


        # Create a Ticker object for the given symbol


        ticker = yf.Ticker(ticker_symbol)


        # Fetch company information


        info = ticker.info


        # Fetch 5 years of historical data


        hist = ticker.history(period="5y")


        # Check if historical data is empty


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


    


    Args:


        df (DataFrame): The stock's historical data.


        


    Returns:


        DataFrame: The DataFrame with added SMA50 and SMA200 columns.


    """


    # Calculate 50-day Simple Moving Average


    df['SMA50'] = df['Close'].rolling(window=50).mean()


    # Calculate 200-day Simple Moving Average


    df['SMA200'] = df['Close'].rolling(window=200).mean()


    return df





# --- FORECASTING ---


def find_best_arima_order(data):


    """


    Iterates through combinations of p, d, and q to find the best ARIMA model order based on AIC.


    


    Args:


        data (Series): The time series data (e.g., closing prices).


        


    Returns:


        tuple: The best (p, d, q) order for the ARIMA model.


    """


    # Define the range of p, d, and q values to test


    p = d = q = range(0, 3)


    # Generate all possible combinations of (p, d, q)


    pdq = list(itertools.product(p, d, q))


    


    best_aic = float("inf")


    best_order = None


    


    # Iterate through all combinations and find the one with the lowest AIC


    for order in pdq:


        try:


            model = ARIMA(data, order=order)


            model_fit = model.fit()


            # If the current model's AIC is better than the best one found so far, update it


            if model_fit.aic < best_aic:


                best_aic = model_fit.aic


                best_order = order


        except:


            # If a model fails to fit, skip it


            continue


            


    return best_order





def forecast_stock_price(df, days_to_predict=30):


    """


    Forecasts the stock price using the best ARIMA model found.


    


    Args:


        df (DataFrame): The stock's historical data.


        days_to_predict (int): The number of days to forecast into the future.


        


    Returns:


        tuple: A tuple containing the forecast (Series) and the corresponding dates (DatetimeIndex).


    """


    try:


        # Find the best ARIMA order for the closing prices


        best_order = find_best_arima_order(df['Close'])


        if best_order is None:


            # Fallback to a default order if no suitable model is found


            print("Could not find a suitable ARIMA model. Falling back to default order (5,1,0).")


            best_order = (5, 1, 0)





        # Create and fit the ARIMA model with the best order


        model = ARIMA(df['Close'], order=best_order)


        model_fit = model.fit()


        


        # Generate the forecast


        forecast = model_fit.forecast(steps=days_to_predict)


        


        # Create the date range for the forecast


        forecast_dates = pd.to_datetime(df.index[-1]) + pd.to_timedelta(range(1, days_to_predict + 1), unit='D')


        


        return forecast, forecast_dates


    except Exception as e:


        print(f"Error during ARIMA forecasting: {e}")


        return pd.Series(), pd.Index([])





# --- SENTIMENT ANALYSIS ---


from prawcore import exceptions as prawcore_exceptions





# ... (keep other imports)





def get_reddit_sentiment(ticker_symbol, reddit_credentials, submission_limit=15, comment_limit=10):


    """


    Fetches and analyzes Reddit sentiment for a given stock ticker using a weighted average.


    """


    try:


        reddit = praw.Reddit(**reddit_credentials)


        subreddit = reddit.subreddit("wallstreetbets+stocks")


        search_query = f'"{ticker_symbol}"'


        submissions = subreddit.search(search_query, limit=submission_limit)





        posts = []


        weighted_sentiments = []





        for submission in submissions:


            if ticker_symbol.lower() in submission.title.lower() or ticker_symbol.lower() in submission.selftext.lower():


                posts.append(submission)


                


                # Calculate the sentiment of the post title and comments


                title_sentiment = TextBlob(submission.title).sentiment.polarity


                


                comment_sentiments = []


                submission.comments.replace_more(limit=0)


                for comment in submission.comments[:comment_limit]:


                    comment_sentiments.append(TextBlob(comment.body).sentiment.polarity)


                


                # Average the sentiment of the comments


                avg_comment_sentiment = sum(comment_sentiments) / len(comment_sentiments) if comment_sentiments else 0


                


                # Combine title and comment sentiment


                post_sentiment = (title_sentiment + avg_comment_sentiment) / 2





                # Calculate a weight based on upvotes and comments


                weight = 1 + (submission.score / 100) + (submission.num_comments / 50)


                


                weighted_sentiments.append((post_sentiment, weight))





        if not weighted_sentiments:


            return 0, [], None





        # Calculate the weighted average sentiment


        total_sentiment = sum(score * weight for score, weight in weighted_sentiments)


        total_weight = sum(weight for _, weight in weighted_sentiments)


        sentiment = total_sentiment / total_weight if total_weight > 0 else 0


        


        return sentiment, posts, None





    except prawcore_exceptions.ResponseException as e:


        if e.response.status_code == 401:


            return 0, [], "Reddit API credentials are not valid. Please check your Client ID, Client Secret, and User Agent."


        else:


            print(f"Error fetching Reddit sentiment for {ticker_symbol}: {e}")


            return 0, [], f"An error occurred while fetching data from Reddit: {e}"


    except Exception as e:


        print(f"An unexpected error occurred in get_reddit_sentiment: {e}")


        return 0, [], f"An unexpected error occurred: {e}"





# --- PLOTTING ---


def create_plot(df, forecast, forecast_dates, ticker_symbol):


    """


    Creates an interactive Plotly chart of the stock data and forecast.


    


    Args:


        df (DataFrame): The stock's historical data.


        forecast (Series): The forecasted stock prices.


        forecast_dates (DatetimeIndex): The dates for the forecast.


        ticker_symbol (str): The stock ticker symbol.


        


    Returns:


        str: The HTML representation of the plot.


    """


    # Create a new Plotly figure


    fig = go.Figure()





    # Add traces for the historical data


    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='blue')))


    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], name='50-Day SMA', line=dict(color='yellow', dash='dash')))


    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], name='200-Day SMA', line=dict(color='red', dash='dash')))


    


    # Add a trace for the forecast


    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, name='Sentiment-Adjusted Forecast', line=dict(color='green', dash='dot')))





    # Update the layout of the plot


    fig.update_layout(


        title=f'{ticker_symbol.upper()} Stock Price Analysis & Forecast',


        xaxis_title='Date',


        yaxis_title='Price (USD)',


        template='plotly_dark',


        xaxis_rangeslider_visible=True


    )





    # Return the plot as an HTML string


    return fig.to_html(full_html=False)





# --- ANALYSIS ORCHESTRATION ---


def run_analysis(ticker_symbol, reddit_credentials, sentiment_adjustment_factor=0.5):


    """


    Orchestrates the entire stock analysis process.


    


    Args:


        ticker_symbol (str): The stock ticker symbol.


        reddit_credentials (dict): Reddit API credentials.


        sentiment_adjustment_factor (float): The factor by which to adjust the forecast based on sentiment.


        


    Returns:


        dict: A dictionary containing the analysis results or an error message.


    """


    # 1. Fetch stock data


    info, hist = get_stock_data(ticker_symbol)


    if info is None or hist is None:


        return {'error': f"Could not fetch data for {ticker_symbol.upper()}. It may be an invalid ticker."}





    # 2. Calculate technical indicators


    hist = calculate_technical_indicators(hist)





    # 3. Generate a stock price forecast


    forecast, forecast_dates = forecast_stock_price(hist)


    if forecast.empty:


        return {'error': f"Could not generate a forecast for {ticker_symbol.upper()}."}





        # 4. Get Reddit sentiment





        sentiment, posts, reddit_error = get_reddit_sentiment(ticker_symbol, reddit_credentials)





        if reddit_error:





            return {'error': reddit_error}





    # 5. Adjust the forecast based on the sentiment


    # This is a basic adjustment. A more complex model could be used here. See TECHDOC.md.


    if sentiment > 0.1:


        adjustment = 1 + (sentiment * sentiment_adjustment_factor)


        forecast = forecast * adjustment


    elif sentiment < -0.1:


        adjustment = 1 + (sentiment * sentiment_adjustment_factor)


        forecast = forecast * adjustment





    # 6. Create the plot


    plot_html = create_plot(hist, forecast, forecast_dates, ticker_symbol)





    # 7. Prepare the company information for display, handling missing values


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





    # Return all the analysis results


    return {


        'info': display_info,


        'plot_html': plot_html,


        'sentiment': sentiment,


        'posts': posts,


        'error': None


    }



