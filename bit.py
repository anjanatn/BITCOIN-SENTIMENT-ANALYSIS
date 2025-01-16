from flask import Flask, request, jsonify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import requests
import tweepy
import praw

app = Flask(_name_)

# Initialize VADER sentiment analyzer
vader_analyzer = SentimentIntensityAnalyzer()


# Twitter and Reddit API Setup (Replace with your actual API keys)
def setup_twitter_api():
    consumer_key = 'Uyg3Bn896WyUvjGlyLzOEfIi9'
    consumer_secret = '6EXFwqOAOtvkVzM1rww41xgeiARgFei3WZ7KDKzfcXLF82qSYL'
    access_token = '1848220537304289280-8DH1IErEduLU5mRZZUwhiWnjQ10SLf'
    access_token_secret = '3pQXCXC2od1fsq9h0N8WFKMjIPYQeIFW1fpkU1TahOR7ks'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def setup_reddit_api():
    return praw.Reddit(client_id='nEFvrxX26haCIj6bA34r9Q',
                       client_secret='buY2ZgaVcE8vCWTaUL1X7CgWc9RbsQ',
                       user_agent='myApp/0.1u/Icy_Philosopher_1183')


# Sentiment analysis
def vader_sentiment(text):
    score = vader_analyzer.polarity_scores(text)
    return score['compound']


def textblob_sentiment(text):
    return TextBlob(text).sentiment.polarity


# Bitcoin Price Data Collection
def get_current_bitcoin_price():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {'ids': 'bitcoin', 'vs_currencies': 'usd'}
    response = requests.get(url, params=params).json()
    return response['bitcoin']['usd']


# Fetch Twitter Data
def fetch_twitter_data(api, keyword):
    query = f'{keyword}'
    tweets = tweepy.Cursor(api.search_tweets, q=query, lang='en').items(100)
    return [{'text': tweet.text, 'created_at': tweet.created_at} for tweet in tweets]


# Fetch Reddit Data
def fetch_reddit_data(api, keyword):
    subreddit = api.subreddit('cryptocurrency')
    posts = subreddit.search(keyword, limit=100)
    return [{'text': post.title + " " + post.selftext, 'created_at': post.created_utc} for post in posts]


# API to handle sentiment analysis and Bitcoin price fetching
@app.route('/api/analyze', methods=['POST'])
def analyze_sentiment():
    data = request.get_json()
    source = data.get('source', '')
    keyword = data.get('keyword', '')

    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400

    # Setup APIs
    twitter_api = setup_twitter_api()
    reddit_api = setup_reddit_api()

    # Fetch data based on source
    if source == 'twitter':
        comments = fetch_twitter_data(twitter_api, keyword)
    else:
        comments = fetch_reddit_data(reddit_api, keyword)

    # Concatenate all text for sentiment analysis
    all_text = " ".join([comment['text'] for comment in comments])

    # Perform sentiment analysis
    vader_sentiment_score = vader_sentiment(all_text)
    textblob_sentiment_score = textblob_sentiment(all_text)

    # Fetch current Bitcoin price
    bitcoin_price = get_current_bitcoin_price()

    # Return results as JSON
    response = {
        'vader_sentiment': vader_sentiment_score,
        'textblob_sentiment': textblob_sentiment_score,
        'bitcoin_price': bitcoin_price
    }

    return jsonify(response)
from flask_cors import CORS
app = Flask(_name_)
CORS(app)  # This will allow cross-origin requests


if _name_ == '_main_':
    app.run(debug=True)