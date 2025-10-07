
# ARIMA & Reddit Stock Forecast 📈

A Python repo for **hybrid stock prediction**. It combines **ARIMA** (time series analysis) with **Reddit Sentiment Analysis** (NLP on market subreddits) to generate enhanced, dual-factor forecasts. Leverages both price history and public sentiment for smarter investment insights.

## Technologies Used

*   **Backend:** Python
*   **Web Framework:** Flask
*   **Data Fetching:** yfinance, PRAW
*   **Data Manipulation:** pandas
*   **Time-Series Forecasting:** statsmodels
*   **Sentiment Analysis:** TextBlob
*   **Data Visualization:** plotly
*   **Frontend Styling:** Tailwind CSS

## How to Install and Run the Application

1.  **Clone the repository:**

```bash
git clone https://github.com/your-username/stock-analysis-app.git
```

2.  **Install the required libraries:**

```bash
pip install -r requirements.txt
```

3.  **Get your Reddit API credentials:**

    *   Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
    *   Click "are you a developer? create an app..."
    *   Fill out the form:
        *   **name:** anything you want
        *   **type:** script
        *   **description:** anything you want
        *   **about url:** http://localhost:5000
        *   **redirect uri:** http://localhost:5000
    *   Click "create app"
    *   You will now have a `client_id` and a `client_secret`.

4.  **Run the application:**

```bash
python app.py
```

5.  **Open your web browser and go to:**

```
http://127.0.0.1:5000
```

## How to Use the Application

1.  Enter a stock ticker symbol in the input field.
2.  Enter your Reddit API credentials.
3.  Click the "Analyze" button.
4.  The application will display a detailed analysis page with company information, key financial metrics, an interactive chart showing historical prices, moving averages, a 30-day price forecast, and the Reddit sentiment score.

## Disclaimer

This is not financial advice. All data is for informational purposes only.
