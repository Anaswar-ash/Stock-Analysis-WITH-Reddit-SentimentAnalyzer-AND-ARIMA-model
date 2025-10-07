import os
from flask import Flask, render_template, render_template_string, request
from analysis_engine import run_analysis

app = Flask(__name__)

# --- Template Generation ---
# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# index.html template
index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis & Forecast</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center mb-8">ARIMA & Reddit Stock Forecast 📈</h1>
        <form action="/analyze" method="post" class="max-w-md mx-auto">
            <div class="flex items-center border-b-2 border-teal-500 py-2">
                <input class="appearance-none bg-transparent border-none w-full text-white mr-3 py-1 px-2 leading-tight focus:outline-none" type="text" name="ticker" placeholder="Enter Stock Ticker (e.g., AAPL)">
            </div>
            <div class="flex items-center border-b-2 border-teal-500 py-2">
                <input class="appearance-none bg-transparent border-none w-full text-white mr-3 py-1 px-2 leading-tight focus:outline-none" type="text" name="client_id" placeholder="Enter Your Reddit Client ID">
            </div>
            <div class="flex items-center border-b-2 border-teal-500 py-2">
                <input class="appearance-none bg-transparent border-none w-full text-white mr-3 py-1 px-2 leading-tight focus:outline-none" type="text" name="client_secret" placeholder="Enter Your Reddit Client Secret">
            </div>
            <div class="flex items-center border-b-2 border-teal-500 py-2">
                <input class="appearance-none bg-transparent border-none w-full text-white mr-3 py-1 px-2 leading-tight focus:outline-none" type="text" name="user_agent" placeholder="Enter Your Reddit User Agent">
            </div>
            <div class="flex items-center py-2">
                <button class="flex-shrink-0 bg-teal-500 hover:bg-teal-700 border-teal-500 hover:border-teal-700 text-sm border-4 text-white py-1 px-2 rounded" type="submit">
                    Analyze
                </button>
            </div>
        </form>
    </div>
</body>
</html>
"""
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

# results.html template
results_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Results</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto px-4 py-8">
        <a href="/" class="text-teal-500 hover:text-teal-300">&larr; Back to Home</a>
        {% if error %}
            <div class="bg-red-500 text-white p-4 rounded-lg mt-8">
                <p class="font-bold">Error:</p>
                <p>{{ error }}</p>
            </div>
        {% else %}
            <h1 class="text-4xl font-bold text-center my-8">{{ info.longName }} ({{ info.symbol }})</h1>
            <div class="bg-gray-800 p-6 rounded-lg shadow-lg">
                <p class="text-lg">{{ info.longBusinessSummary }}</p>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-6 gap-4 my-8 text-center">
                <div class="bg-gray-800 p-4 rounded-lg shadow-lg">
                    <p class="font-bold text-teal-400">Market Cap</p>
                    <p>{{ "${:,.0f}".format(info.marketCap) }}</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg shadow-lg">
                    <p class="font-bold text-teal-400">Day High / Low</p>
                    <p>{{ "${:.2f} / ${:.2f}".format(info.dayHigh, info.dayLow) }}</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg shadow-lg">
                    <p class="font-bold text-teal-400">P/E Ratio</p>
                    <p>{{ "{:.2f}".format(info.trailingPE) if info.trailingPE else 'N/A' }}</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg shadow-lg">
                    <p class="font-bold text-teal-400">Dividend Yield</p>
                    <p>{{ "{:.2%}".format(info.dividendYield) if info.dividendYield else 'N/A' }}</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg shadow-lg">
                    <p class="font-bold text-teal-400">52 Week High</p>
                    <p>{{ "${:.2f}".format(info.fiftyTwoWeekHigh) }}</p>
                </div>
                <div class="bg-gray-800 p-4 rounded-lg shadow-lg">
                    <p class="font-bold text-teal-400">Reddit Sentiment</p>
                    <a href="/reddit/{{ info.symbol }}" class="text-teal-500 hover:text-teal-300">{{ "{:.2f}".format(sentiment) }}</a>
                </div>
            </div>

            <div class="my-8">
                {{ plot_html|safe }}
            </div>

            <p class="text-sm text-gray-500 text-center mt-8">Disclaimer: This is not financial advice. All data is for informational purposes only.</p>
        {% endif %}
    </div>
</body>
</html>
"""
with open('templates/results.html', 'w', encoding='utf-8') as f:
    f.write(results_html)

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form.get('ticker')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    user_agent = request.form.get('user_agent')

    if not ticker or not client_id or not client_secret or not user_agent:
        return render_template('results.html', error="Please fill out all fields.")

    reddit_credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }

    analysis_result = run_analysis(ticker, reddit_credentials)

    if analysis_result.get('error'):
        return render_template('results.html', error=analysis_result['error'])

    return render_template('results.html', **analysis_result)

@app.route('/reddit/<ticker_symbol>')
def reddit_sentiment(ticker_symbol):
    client_id = request.args.get('client_id')
    client_secret = request.args.get('client_secret')
    user_agent = request.args.get('user_agent')

    if not client_id or not client_secret or not user_agent:
        return render_template('results.html', error="Could not retrieve Reddit credentials.")

    reddit_credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }

    from analysis_engine import get_reddit_sentiment
    sentiment, posts, _ = get_reddit_sentiment(ticker_symbol, reddit_credentials)

    return render_template('reddit.html', ticker_symbol=ticker_symbol, sentiment=sentiment, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)