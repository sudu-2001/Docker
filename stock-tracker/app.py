from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import yfinance as yf
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sudarshan-stock-tracker'
socketio = SocketIO(app, cors_allowed_origins="*")

# Stock symbols to track
STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

def get_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d', interval='1m')
        if not data.empty:
            latest = data['Close'].iloc[-1]
            prev = data['Close'].iloc[-2] if len(data) > 1 else latest
            change = ((latest - prev) / prev) * 100
            return {
                'symbol': symbol,
                'price': round(float(latest), 2),
                'change': round(float(change), 2),
                'status': 'up' if change >= 0 else 'down'
            }
    except Exception as e:
        return {
            'symbol': symbol,
            'price': 0.0,
            'change': 0.0,
            'status': 'error'
        }

def fetch_all_stocks():
    return [get_stock_price(s) for s in STOCKS]

# Background thread — pushes prices every 5 seconds
def stock_price_thread():
    while True:
        try:
            prices = fetch_all_stocks()
            socketio.emit('stock_update', {'stocks': prices})
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

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
    # Start background thread
    thread = threading.Thread(target=stock_price_thread)
    thread.daemon = True
    thread.start()

    socketio.run(app, host='0.0.0.0', port=5002, debug=True)
