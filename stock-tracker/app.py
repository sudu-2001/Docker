from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sudarshan-stock-tracker'
socketio = SocketIO(app, cors_allowed_origins="*")

STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
FINNHUB_KEY = 'd8sk6ihr01qh5reringgd8sk6ihr01qh5rerinh0'

def get_stock_price(symbol):
    try:
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}'
        response = requests.get(url).json()
        price = float(response['c'])   # current price
        prev  = float(response['pc'])  # previous close
        change = ((price - prev) / prev) * 100
        return {
            'symbol': symbol,
            'price': round(price, 2),
            'change': round(change, 2),
            'status': 'up' if change >= 0 else 'down'
        }
    except Exception as e:
        print(f"{symbol} ERROR: {e}")
        return None

def fetch_all_stocks():
    results = []
    for s in STOCKS:
        results.append(get_stock_price(s))
        time.sleep(1)
    return results

def stock_price_thread():
    while True:
        try:
            prices = fetch_all_stocks()
            socketio.emit('stock_update', {'stocks': prices})
            time.sleep(30)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

@app.route('/')
def index():
    return render_template('index.html', stocks=STOCKS)

@app.route('/api/stocks')
def get_stocks():
    return jsonify(fetch_all_stocks())

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@socketio.on('connect')
def on_connect():
    print('Client connected')
    prices = fetch_all_stocks()
    emit('stock_update', {'stocks': prices})

if __name__ == '__main__':
    thread = threading.Thread(target=stock_price_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)
