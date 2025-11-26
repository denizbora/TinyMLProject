# ESP8266 Firmware

TinyML Mini-WAF firmware for ESP8266 microcontroller.

## Files

- `esp8266_waf.ino` - Main Arduino sketch (for Arduino IDE)
- `src/main.cpp` - Main source file (for PlatformIO)
- `include/*.h` - Header files (model weights, scaler params, feature extraction)
- `platformio.ini` - PlatformIO configuration

## Build & Upload

### Option 1: PlatformIO (Recommended)

```bash
# Build
pio run

# Upload
pio run --target upload

# Monitor serial
pio device monitor --baud 115200
```

### Option 2: Arduino IDE

1. Open `esp8266_waf.ino` in Arduino IDE
2. Install ESP8266 board package (if not installed)
3. Select board: NodeMCU 1.0 (ESP-12E Module)
4. Edit WiFi credentials in the code
5. Upload

## Configuration

Edit these values in `esp8266_waf.ino` or `src/main.cpp`:

```cpp
// WiFi credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";

// Backend server
const char* BACKEND_HOST = "192.168.1.100";  // Your backend IP
const int BACKEND_PORT = 8080;

// Detection threshold
const float MALICIOUS_THRESHOLD = 0.5f;  // 0.3-0.7 recommended
```

## Hardware Requirements

- ESP8266 board (NodeMCU, Wemos D1 Mini, etc.)
- USB cable for programming
- WiFi network (2.4 GHz)

## Memory Usage

- RAM: ~31KB / 81KB (38%)
- Flash: ~288KB / 1MB (27%)
- Model size: 772 bytes

## Serial Monitor Output

The WAF prints detailed logs at 115200 baud:

```
========================================
  ESP8266 TinyML Mini-WAF
========================================
Model: MLP(8) - F1: 99.99%
Features: 22 dimensions
Model size: 772 bytes
========================================

Connecting to WiFi: YOUR_SSID
.......
[+] WiFi connected!
    IP address: 192.168.1.50
    Listening on port: 80
    Backend: 192.168.1.100:8080

[*] WAF is ready. Waiting for requests...

========================================
[*] New request #1
========================================
Request: GET /admin HTTP/1.1
Probability: 1.0000 | Classification: MALICIOUS
[!] BLOCKED - Malicious request detected
Stats: Total=1 | Allowed=0 | Blocked=1
```

## Troubleshooting

**WiFi won't connect:**
- Check SSID and password
- Ensure 2.4 GHz network (ESP8266 doesn't support 5 GHz)
- Check serial monitor for error messages

**Backend connection fails:**
- Verify backend IP and port
- Check firewall settings
- Ensure backend is running

**Upload fails:**
- Check USB cable and port
- Try pressing FLASH button during upload
- Verify correct board selection
