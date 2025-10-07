# Stock Analysis with Reddit Sentiment and ARIMA Model

This project is a web-based application that performs stock analysis by combining traditional time-series forecasting with modern sentiment analysis from social media.

## Features

*   **Interactive Charts:** Visualizes historical stock data, including Simple Moving Averages (SMAs), and an ARIMA-based price forecast.
*   **Reddit Sentiment Analysis:** Fetches recent posts from Reddit (r/wallstreetbets and r/stocks) to gauge market sentiment for a specific stock.
*   **Sentiment-Adjusted Forecast:** Adjusts the ARIMA forecast based on the calculated Reddit sentiment, providing a more holistic view.
*   **Web-Based UI:** A simple and intuitive Flask web interface for entering stock tickers and viewing the analysis.

## How It Works

1.  **Data Fetching:** The application uses the `yfinance` library to download historical stock data from Yahoo Finance.
2.  **Technical Analysis:** It calculates 50-day and 200-day Simple Moving Averages (SMAs) to identify trends.
3.  **ARIMA Forecasting:** A time-series ARIMA model is used to forecast future stock prices based on historical data.
4.  **Reddit Sentiment:** The `praw` library is used to connect to the Reddit API and fetch posts related to the stock ticker. The sentiment of these posts is analyzed using `TextBlob`.
5.  **Combined Analysis:** The ARIMA forecast is adjusted based on the sentiment score from Reddit.
6.  **Visualization:** The results are displayed in an interactive chart using `plotly` and a web page rendered by `Flask`.

## Getting Started

### Prerequisites

*   Python 3.x
*   A Reddit account and API credentials (client ID, client secret, user agent).

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Stock-Analysis-WITH-Reddit-SentimentAnalyzer-AND-ARIMA-model.git
    cd Stock-Analysis-WITH-Reddit-SentimentAnalyzer-AND-ARIMA-model
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**

    ```bash
    python app.py
    ```

4.  Open your web browser and navigate to `http://127.0.0.1:5000`.

## Important Security Note

This application currently requires you to enter your Reddit API credentials directly into the web form. This is **not a secure practice** for a production environment. For personal, local use, it is acceptable, but if you plan to deploy this application, you should implement a more secure way to handle these credentials, such as using environment variables or a dedicated secrets management service.

## Disclaimer

This is not financial advice. All data and analysis are for informational purposes only.