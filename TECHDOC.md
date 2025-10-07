# Technical Documentation

## Project Overview

This project is a web-based stock analysis and forecasting tool. It allows users to input a stock ticker symbol and view a comprehensive analysis, including company information, financial metrics, a price forecast, and Reddit sentiment analysis.

## Architecture

The application is built using a simple two-tier architecture:

*   **Frontend:** The frontend is a simple HTML interface styled with Tailwind CSS. It consists of two pages: an index page with a form to enter a stock ticker and Reddit API credentials, and a results page that displays the analysis.
*   **Backend:** The backend is a Flask web application that handles user requests, fetches and analyzes stock data, and renders the HTML templates.

## File Structure

```
.
├── analysis_engine.py
├── app.py
├── templates
│   ├── index.html
│   └── results.html
└── README.md
```

*   `analysis_engine.py`: This module contains all the logic for data fetching, analysis, forecasting, and plotting.
*   `app.py`: This is the main Flask application that handles web requests and renders the HTML templates.
*   `templates/`: This directory contains the HTML templates for the application.
*   `README.md`: This file contains a general overview of the project.

## `analysis_engine.py`

This module is responsible for the core logic of the application. It contains the following functions:

*   `get_stock_data(ticker_symbol)`: Fetches stock data from Yahoo Finance.
*   `calculate_technical_indicators(df)`: Calculates technical indicators for the stock data.
*   `forecast_stock_price(df, days_to_predict=30)`: Forecasts the stock price using an ARIMA model.
*   `get_reddit_sentiment(ticker_symbol, reddit_credentials)`: Fetches Reddit sentiment for a given stock ticker.
*   `create_plot(df, forecast, forecast_dates, ticker_symbol)`: Creates an interactive plot of the stock data and forecast.
*   `run_analysis(ticker_symbol, reddit_credentials)`: Runs the full stock analysis.

## `app.py`

This is the main entry point of the application. It creates a Flask app instance and defines the routes for the application.

*   `/`: Renders the `index.html` template.
*   `/analyze`: This route is called when the user submits the form on the index page. It retrieves the ticker symbol and Reddit API credentials from the form data, calls the `run_analysis()` function from the `analysis_engine` module, and renders the `results.html` template with the analysis data.

## Data Source

The application uses the `yfinance` library to fetch stock data from Yahoo Finance and the `praw` library to fetch data from Reddit.

## Time-Series Forecasting

The application uses the `statsmodels` library to perform time-series forecasting. Specifically, it uses the ARIMA model to forecast the stock price for the next 30 days.

## Sentiment Analysis

The application uses the `TextBlob` library to perform sentiment analysis on the Reddit data.

## Data Visualization

The application uses the `plotly` library to create an interactive chart of the stock data and forecast.