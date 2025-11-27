#!/usr/bin/env python3
"""
ESP8266 TinyML WAF Dashboard Backend
Real-time monitoring API for WAF events
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from collections import deque
import threading

app = Flask(__name__)
CORS(app)  # React frontend için CORS enable

# In-memory storage (son 1000 event)
events = deque(maxlen=1000)
stats = {
    'total_requests': 0,
    'blocked_requests': 0,
    'allowed_requests': 0,
    'last_updated': None,
    'block_rate': 0.0
}

# Thread-safe lock
lock = threading.Lock()


@app.route('/api/report', methods=['POST'])
def report_event():
    """ESP8266'dan event al"""
    try:
        data = request.get_json()
        
        # Event bilgilerini parse et
        event = {
            'id': stats['total_requests'] + 1,
            'timestamp': datetime.now().isoformat(),
            'esp_ip': request.remote_addr,
            'method': data.get('method', 'UNKNOWN'),
            'path': data.get('path', '/'),
            'query': data.get('query', ''),
            'user_agent': data.get('user_agent', ''),
            'probability': float(data.get('probability', 0)),
            'classification': data.get('classification', 'UNKNOWN'),
            'action': data.get('action', 'UNKNOWN'),  # ALLOWED or BLOCKED
            'client_ip': data.get('client_ip', 'unknown')
        }
        
        with lock:
            events.appendleft(event)
            stats['total_requests'] += 1
            
            if event['action'] == 'BLOCKED':
                stats['blocked_requests'] += 1
            elif event['action'] == 'ALLOWED':
                stats['allowed_requests'] += 1
            
            # Block rate hesapla
            if stats['total_requests'] > 0:
                stats['block_rate'] = (stats['blocked_requests'] / stats['total_requests']) * 100
            
            stats['last_updated'] = datetime.now().isoformat()
        
        print(f"[EVENT] {event['action']} - {event['method']} {event['path']} (prob={event['probability']:.4f})")
        
        return jsonify({'status': 'success', 'event_id': event['id']}), 200
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/events', methods=['GET'])
def get_events():
    """Son event'leri getir"""
    limit = request.args.get('limit', 100, type=int)
    with lock:
        return jsonify({
            'events': list(events)[:limit],
            'count': len(events)
        })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """İstatistikleri getir"""
    with lock:
        return jsonify(stats)


@app.route('/api/clear', methods=['POST'])
def clear_events():
    """Tüm event'leri temizle"""
    with lock:
        events.clear()
        stats['total_requests'] = 0
        stats['blocked_requests'] = 0
        stats['allowed_requests'] = 0
        stats['block_rate'] = 0.0
        stats['last_updated'] = datetime.now().isoformat()
    
    print("[INFO] Events cleared")
    return jsonify({'status': 'cleared'})


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    print("=" * 70)
    print("  ESP8266 TinyML WAF Dashboard Backend")
    print("=" * 70)
    print("  API Endpoint: http://0.0.0.0:5000/api/report")
    print("  Stats:        http://0.0.0.0:5000/api/stats")
    print("  Events:       http://0.0.0.0:5000/api/events")
    print("=" * 70)
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
