from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import requests
import threading
import time
import logging
import socket

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sudarshan-stock-tracker'
socketio = SocketIO(app, cors_allowed_origins="*")

STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
FINNHUB_KEY = 'd8sk6ihr01qh5reringgd8sk6ihr01qh5rerinh0'

# Get EC2 server's own public IP
def get_server_ip():
    try:
        public_ip = requests.get('https://api.ipify.org').text
        private_ip = socket.gethostbyname(socket.gethostname())
        return public_ip, private_ip
    except Exception as e:
        logging.error(f"Could not get server IP: {e}")
        return 'unknown', 'unknown'

PUBLIC_IP, PRIVATE_IP = get_server_ip()
logging.info(f"Server started | Public IP={PUBLIC_IP} | Private IP={PRIVATE_IP}")

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
        logging.info(f"STOCK FETCH | server={PUBLIC_IP} | {symbol} | price=${result['price']} | change={result['change']}% | status={result['status']}")
        return result
    except Exception as e:
        logging.error(f"STOCK ERROR | server={PUBLIC_IP} | {symbol} | {e}")
        return None

def fetch_all_stocks():
    logging.info(f"Fetching all stocks | server={PUBLIC_IP}")
    results = []
    for s in STOCKS:
        results.append(get_stock_price(s))
        time.sleep(1)
    logging.info(f"Fetch complete | server={PUBLIC_IP} | results={results}")
    return results

def stock_price_thread():
    while True:
        try:
            logging.info(f"Background thread | server={PUBLIC_IP} | fetching stock prices...")
            prices = fetch_all_stocks()
            socketio.emit('stock_update', {'stocks': prices})
            logging.info(f"Emitted stock_update | server={PUBLIC_IP}")
            time.sleep(30)
        except Exception as e:
            logging.error(f"Thread error | server={PUBLIC_IP} | {e}")
            time.sleep(30)

@app.route('/')
def index():
    client_ip = request.remote_addr
    logging.info(f"Home page requested | server={PUBLIC_IP} | client_ip={client_ip}")
    return render_template('index.html', stocks=STOCKS)

@app.route('/api/stocks')
def get_stocks():
    client_ip = request.remote_addr
    logging.info(f"API /api/stocks called | server={PUBLIC_IP} | client_ip={client_ip}")
    return jsonify(fetch_all_stocks())

@app.route('/health')
def health():
    logging.info(f"Health check | server={PUBLIC_IP}")
    return jsonify({
        'status': 'healthy',
        'server_public_ip': PUBLIC_IP,
        'server_private_ip': PRIVATE_IP
    })

@socketio.on('connect')
def on_connect():
    client_ip = request.remote_addr
    logging.info(f"Client connected | server={PUBLIC_IP} | client_ip={client_ip}")
    prices = fetch_all_stocks()
    emit('stock_update', {'stocks': prices})

@socketio.on('disconnect')
def on_disconnect():
    client_ip = request.remote_addr
    logging.info(f"Client disconnected | server={PUBLIC_IP} | client_ip={client_ip}")

if __name__ == '__main__':
    logging.info(f"Starting Stock Tracker | Public IP={PUBLIC_IP} | Private IP={PRIVATE_IP} | port=5002")
    thread = threading.Thread(target=stock_price_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)
