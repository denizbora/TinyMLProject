# Backend API - WAF Test Server

ESP8266 WAF'ın arkasında çalışacak basit backend API.

## Kurulum

```bash
cd backend_api
pip install -r requirements.txt
```

## Çalıştırma

```bash
python3 app.py
```

Server `http://0.0.0.0:8080` adresinde başlayacak.

## Endpoints

### Benign (Normal) Endpoints
- `GET /` - Ana sayfa
- `GET /api/status` - API durumu
- `GET /api/data` - Örnek veri
- `GET /api/user/<id>` - Kullanıcı bilgisi
- `GET /api/search?q=...` - Arama

### Malicious (Engellenecek) Endpoints
- `GET /admin` - Admin panel (WAF tarafından engellenecek)
- `GET /wp-admin` - WordPress admin (WAF tarafından engellenecek)
- `GET /api/search?q=<script>alert(1)</script>` - XSS (engellenecek)

## Test

### Direkt Backend'e (WAF olmadan)
```bash
# Normal request
curl http://localhost:8080/

# Admin request (backend izin verir ama 403 döner)
curl http://localhost:8080/admin
```

### ESP8266 WAF üzerinden
```bash
# ESP8266 IP'si: 192.168.1.50 (örnek)
# Normal request (geçmeli)
curl http://192.168.1.50/

# Admin request (WAF engellemeli)
curl http://192.168.1.50/admin
```

## Log'ları Görüntüleme

```bash
# Son request'leri göster
curl http://localhost:8080/api/logs

# Log'ları temizle
curl -X POST http://localhost:8080/api/logs/clear
```

## ESP8266 Konfigürasyonu

ESP8266 WAF kodunda backend ayarları:
```cpp
const char* BACKEND_HOST = "192.168.1.XXX";  // Bu bilgisayarın IP'si
const int BACKEND_PORT = 8080;
```

IP adresini öğrenmek için:
```bash
# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1

# Linux
ip addr show | grep "inet " | grep -v 127.0.0.1
```
