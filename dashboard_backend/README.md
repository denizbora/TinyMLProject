# WAF Dashboard Backend

Flask-based backend API for ESP8266 TinyML WAF real-time monitoring.

## Features

- 📊 Real-time event collection from ESP8266
- 📈 Statistics tracking (total, blocked, allowed)
- 🔄 Auto-updating dashboard data
- 💾 In-memory storage (last 1000 events)
- 🌐 CORS enabled for React frontend

## Installation

```bash
cd dashboard_backend
pip3 install -r requirements.txt
```

## Usage

```bash
python3 app.py
```

Server will start on `http://0.0.0.0:5000`

## API Endpoints

### POST /api/report
ESP8266'dan event raporu al.

**Request Body:**
```json
{
  "method": "GET",
  "path": "/admin",
  "query": "",
  "user_agent": "Mozilla/5.0",
  "probability": 0.9999,
  "classification": "MALICIOUS",
  "action": "BLOCKED",
  "client_ip": "192.168.1.100"
}
```

**Response:**
```json
{
  "status": "success",
  "event_id": 123
}
```

### GET /api/events?limit=100
Son N event'i getir.

**Response:**
```json
{
  "events": [
    {
      "id": 123,
      "timestamp": "2025-11-27T10:50:00",
      "method": "GET",
      "path": "/admin",
      "probability": 0.9999,
      "action": "BLOCKED",
      ...
    }
  ],
  "count": 100
}
```

### GET /api/stats
İstatistikleri getir.

**Response:**
```json
{
  "total_requests": 1000,
  "blocked_requests": 150,
  "allowed_requests": 850,
  "block_rate": 15.0,
  "last_updated": "2025-11-27T10:50:00"
}
```

### POST /api/clear
Tüm event'leri temizle.

### GET /api/health
Health check.

## ESP8266 Integration

ESP8266 firmware'inde dashboard'a rapor göndermek için:

```cpp
// Dashboard config
const char* DASHBOARD_HOST = "192.168.1.100";  // Backend IP
const int DASHBOARD_PORT = 5000;

void reportToDashboard(String method, String path, String query, 
                       String userAgent, float probability, 
                       String classification, String action, 
                       String clientIP) {
    WiFiClient dashboardClient;
    
    if (dashboardClient.connect(DASHBOARD_HOST, DASHBOARD_PORT)) {
        // JSON payload oluştur
        String payload = "{";
        payload += "\"method\":\"" + method + "\",";
        payload += "\"path\":\"" + path + "\",";
        payload += "\"query\":\"" + query + "\",";
        payload += "\"user_agent\":\"" + userAgent + "\",";
        payload += "\"probability\":" + String(probability, 4) + ",";
        payload += "\"classification\":\"" + classification + "\",";
        payload += "\"action\":\"" + action + "\",";
        payload += "\"client_ip\":\"" + clientIP + "\"";
        payload += "}";
        
        // HTTP POST request
        dashboardClient.println("POST /api/report HTTP/1.1");
        dashboardClient.println("Host: " + String(DASHBOARD_HOST));
        dashboardClient.println("Content-Type: application/json");
        dashboardClient.println("Content-Length: " + String(payload.length()));
        dashboardClient.println();
        dashboardClient.println(payload);
        
        dashboardClient.stop();
    }
}
```

## Development

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run in debug mode
python3 app.py
```

## Production

```bash
# Use gunicorn for production
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```
