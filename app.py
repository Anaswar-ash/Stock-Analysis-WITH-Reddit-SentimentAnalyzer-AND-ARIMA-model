
# --- IMPORTS ---
from flask import Flask, render_template, request, session, redirect, url_for
from analysis_engine import run_analysis, get_reddit_sentiment
import os

# --- APP SETUP ---
app = Flask(__name__)
# Set a secret key for session management. 
# It's important to use an environment variable for this in production.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_development')

# --- ROUTES ---
@app.route('/')
def index():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles the form submission and displays the analysis results."""
    # Get form data
    ticker = request.form.get('ticker')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    user_agent = request.form.get('user_agent')

    # --- Input Validation ---
    # Check if the ticker symbol is valid
    if not ticker or not ticker.isalnum() or not 2 <= len(ticker) <= 5:
        return render_template('results.html', error="Invalid ticker symbol. Please enter a valid symbol (e.g., AAPL).")
    # Check if all Reddit API credentials are provided
    if not all([client_id, client_secret, user_agent]):
        return render_template('results.html', error="Please provide all Reddit API credentials.")

    # Store credentials in a dictionary
    reddit_credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }

    # --- Run Analysis ---
    # The analysis can be slow, which is a poor user experience.
    # See TECHDOC.md for suggestions on asynchronous task handling.
    analysis_result = run_analysis(ticker, reddit_credentials)

    # If there was an error during the analysis, display it
    if analysis_result.get('error'):
        return render_template('results.html', error=analysis_result['error'])

    # Store credentials in session ONLY for the purpose of the reddit details page
    session['client_id'] = client_id
    session['client_secret'] = client_secret
    session['user_agent'] = user_agent

    # Render the results page with the analysis data
    return render_template('results.html', **analysis_result)

@app.route('/reddit/<ticker_symbol>')
def reddit_sentiment_page(ticker_symbol):
    """Displays the Reddit posts used for the sentiment analysis."""
    # Get Reddit credentials from the session
    client_id = session.get('client_id')
    client_secret = session.get('client_secret')
    user_agent = session.get('user_agent')

    # If the credentials are not in the session, redirect to the home page
    if not all([client_id, client_secret, user_agent]):
        return redirect(url_for('index'))

    # Store credentials in a dictionary
    reddit_credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'user_agent': user_agent
    }

    # Get the Reddit sentiment and posts
    sentiment, posts, reddit_error = get_reddit_sentiment(ticker_symbol, reddit_credentials)

    # Render the Reddit posts page
    return render_template('reddit.html', ticker_symbol=ticker_symbol, sentiment=sentiment, posts=posts, error=reddit_error)

# --- MAIN ---
if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True)