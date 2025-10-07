
# Technical Documentation

This document provides a technical overview of the Stock Analysis application.

## System Architecture

The application is a monolithic web application built with Python and the Flask framework. It consists of two main components:

1.  **`app.py`:** The main Flask application file that handles routing, web requests, and renders the HTML templates.
2.  **`analysis_engine.py`:** A module that contains all the core logic for stock data analysis, including data fetching, technical indicator calculation, forecasting, and sentiment analysis.

## Key Libraries and Technologies

*   **Flask:** A lightweight web framework for Python used to build the user interface.
*   **yfinance:** A popular library for downloading historical market data from Yahoo Finance.
*   **pandas:** Used for data manipulation and analysis.
*   **statsmodels:** Provides the ARIMA model for time-series forecasting.
*   **plotly:** A graphing library used to create interactive charts.
*   **praw:** The Python Reddit API Wrapper, used to fetch data from Reddit.
*   **TextBlob:** A simple library for processing textual data and performing sentiment analysis.
*   **Tailwind CSS:** A utility-first CSS framework used for styling the web interface.

## Code Structure

### `app.py`

*   **Routes:** Defines the URL endpoints for the application:
    *   `/`: The home page where users can enter a stock ticker and their Reddit API credentials.
    *   `/analyze`: The endpoint that receives the form data, calls the `run_analysis` function, and displays the results.
    *   `/reddit/<ticker_symbol>`: A page to display the specific Reddit posts used for the sentiment analysis.
*   **Session Management:** Uses Flask's session object to store the Reddit API credentials securely across requests.

### `analysis_engine.py`

*   **`get_stock_data()`:** Fetches stock data from Yahoo Finance.
*   **`calculate_technical_indicators()`:** Calculates the 50-day and 200-day SMAs.
*   **`forecast_stock_price()`:** Implements the ARIMA model to forecast future stock prices.
*   **`get_reddit_sentiment()`:** Fetches and analyzes the sentiment of Reddit posts.
*   **`create_plot()`:** Generates the interactive Plotly chart.
*   **`run_analysis()`:** The main function that orchestrates the entire analysis workflow.

## Sentiment-Based Forecast Adjustment

The current implementation uses a simplified approach to adjust the ARIMA forecast based on Reddit sentiment. The adjustment is a linear scaling based on the sentiment score:

```python
if sentiment > 0.1:
    adjustment_factor = 1 + (sentiment * 0.5) # Max 50% boost
    forecast = forecast * adjustment_factor
elif sentiment < -0.1:
    adjustment_factor = 1 + (sentiment * 0.5) # Max 50% reduction
    forecast = forecast * adjustment_factor
```

This is a basic model and could be improved with more sophisticated techniques, such as:

*   **Non-linear adjustments:** Using a non-linear function to apply the sentiment score.
*   **Weighted sentiment:** Giving more weight to posts with more upvotes or comments.
*   **Time-decay model:** Giving more weight to more recent posts.

## Future Improvements

*   **Secure Credential Management:** Implement a more secure method for storing and accessing API keys, such as environment variables or a secrets management tool (e.g., HashiCorp Vault).
*   **Asynchronous Tasks:** Use a task queue (e.g., Celery) to run the analysis asynchronously, preventing the web server from being blocked during long-running analyses.
*   **More Advanced Models:** Incorporate more advanced forecasting models (e.g., LSTMs) and sentiment analysis techniques (e.g., using pre-trained language models like BERT).
*   **Database Integration:** Store the analysis results in a database to track historical performance and build more complex features.
