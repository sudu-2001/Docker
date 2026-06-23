from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sudarshan-stock-tracker'
socketio = SocketIO(app, cors_allowed_origins="*")

STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
FINNHUB_KEY = 'd8sk6ihr01qh5reringgd8sk6ihr01qh5rerinh0'

def get_stock_price(symbol):
    try:
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}'
        response = requests.get(url).json()
        price = float(response['c'])
        prev  = float(response['pc'])
        change = ((price - prev) / prev) * 100
        result = {
            'symbol': symbol,
            'price': round(price, 2),
            'change': round(change, 2),
            'status': 'up' if change >= 0 else 'down'
        }
        logging.info(f"STOCK FETCH | {symbol} | price=${result['price']} | change={result['change']}% | status={result['status']}")
        return result
    except Exception as e:
        logging.error(f"STOCK ERROR | {symbol} | {e}")
        return None

def fetch_all_stocks():
    logging.info("Fetching all stocks...")
    results = []
    for s in STOCKS:
        results.append(get_stock_price(s))
        time.sleep(1)
    logging.info(f"Fetch complete | results={results}")
    return results

def stock_price_thread():
    while True:
        try:
            logging.info("Background thread | fetching stock prices...")
            prices = fetch_all_stocks()
            socketio.emit('stock_update', {'stocks': prices})
            logging.info("Emitted stock_update to all clients")
            time.sleep(30)
        except Exception as e:
            logging.error(f"Thread error: {e}")
            time.sleep(30)

@app.route('/')
def index():
    logging.info("Home page requested")
    return render_template('index.html', stocks=STOCKS)

@app.route('/api/stocks')
def get_stocks():
    logging.info("API /api/stocks called")
    return jsonify(fetch_all_stocks())

@app.route('/health')
def health():
    logging.info("Health check called")
    return jsonify({'status': 'healthy'})

@socketio.on('connect')
def on_connect():
    logging.info("Client connected via WebSocket")
    prices = fetch_all_stocks()
    emit('stock_update', {'stocks': prices})

@socketio.on('disconnect')
def on_disconnect():
    logging.info("Client disconnected")

if __name__ == '__main__':
    logging.info("Starting Stock Tracker app on port 5002...")
    thread = threading.Thread(target=stock_price_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)
