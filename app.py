
from flask import Flask, render_template, request, session, redirect, url_for
from analysis_engine import run_analysis, get_reddit_sentiment

app = Flask(__name__)
import os

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_development')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form.get('ticker')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    user_agent = request.form.get('user_agent')

    if not ticker or not ticker.isalnum() or not 2 <= len(ticker) <= 5:
        return render_template('results.html', error="Invalid ticker symbol. Please enter a valid symbol (e.g., AAPL).")

    reddit_credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }

    # The analysis can be slow, which is a poor user experience.
    # See TECHDOC.md for suggestions on asynchronous task handling.
    analysis_result = run_analysis(ticker, reddit_credentials)

    if analysis_result.get('error'):
        return render_template('results.html', error=analysis_result['error'])

    # Store credentials in session ONLY for the purpose of the reddit details page
    session['client_id'] = client_id
    session['client_secret'] = client_secret
    session['user_agent'] = user_agent

    return render_template('results.html', **analysis_result)

@app.route('/reddit/<ticker_symbol>')
def reddit_sentiment_page(ticker_symbol):
    client_id = session.get('client_id')
    client_secret = session.get('client_secret')
    user_agent = session.get('user_agent')

    if not all([client_id, client_secret, user_agent]):
        return redirect(url_for('index'))

    reddit_credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }

    sentiment, posts, _ = get_reddit_sentiment(ticker_symbol, reddit_credentials)

    return render_template('reddit.html', ticker_symbol=ticker_symbol, sentiment=sentiment, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)