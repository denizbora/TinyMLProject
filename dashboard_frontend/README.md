# WAF Dashboard Frontend

React-based real-time monitoring dashboard for ESP8266 TinyML WAF.

## Features

- 📊 Real-time statistics (total, blocked, allowed, block rate)
- 📋 Live event feed with auto-refresh
- 🎨 Beautiful, modern UI with gradient design
- 🔄 Auto-refresh every 2 seconds
- 🗑️ Clear all events functionality
- 📱 Responsive design

## Installation

```bash
cd dashboard_frontend
npm install
```

## Usage

### Development Mode

```bash
npm start
```

Dashboard will open at `http://localhost:3000`

### Production Build

```bash
npm run build
```

Static files will be in `build/` directory.

## Configuration

Edit `src/App.js` to change backend API URL:

```javascript
const API_URL = 'http://localhost:5000/api';  // Backend URL
```

## Features Overview

### Statistics Cards
- **Total Requests**: Toplam istek sayısı
- **Allowed**: İzin verilen istekler (yeşil)
- **Blocked**: Engellenen istekler (kırmızı)
- **Block Rate**: Engelleme oranı (%)

### Event Feed
Her event için gösterilen bilgiler:
- Event ID
- Timestamp
- HTTP Method & Path
- Client IP & ESP IP
- User-Agent
- Probability (malicious olma olasılığı)
- Classification (BENIGN/MALICIOUS)
- Action (ALLOWED/BLOCKED)

### Controls
- **Pause/Resume**: Auto-refresh'i durdur/başlat
- **Refresh Now**: Manuel güncelleme
- **Clear All**: Tüm event'leri temizle

## Screenshots

### Dashboard Overview
```
┌─────────────────────────────────────────────────────┐
│  🛡️ ESP8266 TinyML WAF Dashboard                   │
│  Real-time Web Application Firewall Monitoring      │
└─────────────────────────────────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│📊 Total  │ │✅ Allowed│ │🚫 Blocked│ │📈 Rate   │
│   1,234  │ │   1,050  │ │    184   │ │  14.9%   │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

┌─────────────────────────────────────────────────────┐
│ 📋 Recent Events                                     │
├─────────────────────────────────────────────────────┤
│ #123 🚫 BLOCKED                        10:50:23 AM  │
│ GET /admin                                           │
│ Client: 192.168.1.100  ESP: 192.168.1.50            │
│ Probability: 99.99% | Classification: MALICIOUS     │
└─────────────────────────────────────────────────────┘
```

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Backend Integration

Dashboard expects backend API at `http://localhost:5000/api` with endpoints:

- `GET /api/stats` - Statistics
- `GET /api/events?limit=N` - Recent events
- `POST /api/clear` - Clear all events

## Deployment

### Option 1: Static Hosting (Netlify, Vercel)

```bash
npm run build
# Upload build/ directory
```

### Option 2: Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
RUN npm install -g serve
CMD ["serve", "-s", "build", "-l", "3000"]
EXPOSE 3000
```

### Option 3: Nginx

```bash
npm run build
cp -r build/* /var/www/html/
```

## Troubleshooting

**CORS Error:**
- Backend'de CORS enabled olmalı
- `flask-cors` paketi yüklü olmalı

**Connection Refused:**
- Backend çalışıyor mu kontrol et
- API_URL doğru mu kontrol et

**Events Not Updating:**
- Auto-refresh aktif mi kontrol et
- Backend'e event geliyor mu kontrol et
- Browser console'da hata var mı bak

## License

MIT
