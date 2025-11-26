#!/usr/bin/env python3
"""
Backend API - WAF Test için basit web sunucusu
ESP8266 WAF'ın arkasında çalışacak gerçek backend simülasyonu
"""
from flask import Flask, request, jsonify
import time
from datetime import datetime

app = Flask(__name__)

# Request log
request_log = []

@app.route('/')
def home():
    """Ana sayfa"""
    log_request()
    return jsonify({
        "status": "ok",
        "message": "Backend API is running",
        "timestamp": datetime.now().isoformat(),
        "total_requests": len(request_log)
    })

@app.route('/api/status')
def status():
    """API durumu"""
    log_request()
    return jsonify({
        "status": "healthy",
        "uptime": time.time(),
        "requests_received": len(request_log)
    })

@app.route('/api/data')
def get_data():
    """Örnek veri endpoint'i"""
    log_request()
    return jsonify({
        "data": [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
            {"id": 3, "name": "Item 3", "value": 300}
        ]
    })

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    """Kullanıcı bilgisi"""
    log_request()
    return jsonify({
        "user_id": user_id,
        "username": f"user{user_id}",
        "email": f"user{user_id}@example.com"
    })

@app.route('/api/search')
def search():
    """Arama endpoint'i"""
    log_request()
    query = request.args.get('q', '')
    return jsonify({
        "query": query,
        "results": [
            f"Result 1 for '{query}'",
            f"Result 2 for '{query}'",
            f"Result 3 for '{query}'"
        ]
    })

@app.route('/search')
def search_simple():
    """Basit arama endpoint'i"""
    log_request()
    query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    return jsonify({
        "query": query,
        "category": category,
        "results": ["Item 1", "Item 2", "Item 3"]
    })

@app.route('/product/<product_id>')
def get_product(product_id):
    """Ürün detayı"""
    log_request()
    return jsonify({
        "product_id": product_id,
        "name": f"Product {product_id}",
        "price": 99.99,
        "stock": 10
    })

@app.route('/api/v1/users')
def get_users_v1():
    """API v1 kullanıcılar"""
    log_request()
    return jsonify({
        "users": [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"}
        ]
    })

@app.route('/api/users')
def get_users():
    """API kullanıcılar"""
    log_request()
    return jsonify({
        "users": [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"}
        ]
    })

@app.route('/download')
def download():
    """Download endpoint"""
    log_request()
    filename = request.args.get('file', '')
    return jsonify({
        "file": filename,
        "message": "Download started"
    })

@app.route('/file')
def get_file():
    """File endpoint"""
    log_request()
    path = request.args.get('path', '')
    return jsonify({
        "path": path,
        "message": "File accessed"
    })

@app.route('/login')
def login():
    """Login endpoint"""
    log_request()
    return jsonify({
        "message": "Login page"
    })

@app.route('/profile')
def profile():
    """Profile endpoint"""
    log_request()
    return jsonify({
        "message": "User profile"
    })

@app.route('/redirect')
def redirect_page():
    """Redirect endpoint"""
    log_request()
    url = request.args.get('url', '')
    return jsonify({
        "redirect_to": url
    })

@app.route('/admin')
def admin():
    """Admin panel (WAF tarafından engellenecek)"""
    log_request()
    return jsonify({
        "error": "This endpoint should be blocked by WAF",
        "message": "If you see this, WAF is not working!"
    }), 403

@app.route('/api/logs')
def get_logs():
    """Son 50 request log'unu göster"""
    return jsonify({
        "total_requests": len(request_log),
        "recent_logs": request_log[-50:]
    })

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Log'ları temizle"""
    global request_log
    count = len(request_log)
    request_log = []
    return jsonify({
        "message": f"Cleared {count} logs"
    })

def log_request():
    """Request'i logla"""
    request_log.append({
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": request.path,
        "query": request.query_string.decode('utf-8'),
        "user_agent": request.headers.get('User-Agent', ''),
        "ip": request.remote_addr
    })
    
    # Console'a da yazdır
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {request.method} {request.path} - {request.remote_addr}")

if __name__ == '__main__':
    print("="*60)
    print("  Backend API Server")
    print("="*60)
    print("Starting server on http://0.0.0.0:8080")
    print("This will act as the backend behind ESP8266 WAF")
    print("="*60)
    print("\nEndpoints:")
    print("  GET  /                  - Home")
    print("  GET  /api/status        - Status")
    print("  GET  /api/data          - Sample data")
    print("  GET  /api/user/<id>     - User info")
    print("  GET  /api/search?q=...  - Search")
    print("  GET  /admin             - Admin (should be blocked)")
    print("  GET  /api/logs          - View request logs")
    print("  POST /api/logs/clear    - Clear logs")
    print("="*60)
    print()
    
    app.run(host='0.0.0.0', port=8080, debug=True)
