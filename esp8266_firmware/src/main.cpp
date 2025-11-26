/*
 * ESP8266 TinyML Mini-WAF
 * 
 * HTTP isteklerini analiz ederek benign/malicious sınıflandırması yapar.
 * Benign istekleri backend sunucuya iletir, malicious olanları engeller.
 * 
 * Hardware: ESP8266 (NodeMCU, Wemos D1 Mini, vb.)
 * Model: MLP(8) - 22 features -> 8 hidden -> 1 output
 * Accuracy: 99.99% F1 score
 */

#include <ESP8266WiFi.h>
#include <WiFiClient.h>

// Model ve feature extraction header'ları
#include "scaler_params.h"
#include "model_weights.h"
#include "esp8266_features.h"

// ===== CONFIGURATION =====
// WiFi ayarları
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// WAF ayarları
const int WAF_PORT = 80;                    // ESP8266'nın dinleyeceği port
const char* BACKEND_HOST = "192.168.1.100"; // Gerçek web sunucusu IP
const int BACKEND_PORT = 8080;              // Gerçek web sunucusu port

// Model threshold
const float MALICIOUS_THRESHOLD = 0.5f;     // >0.5 = malicious

// Debug mode
const bool DEBUG_MODE = true;

// ===== FUNCTION DECLARATIONS =====
void parseRequestLine(const String& requestLine, String& method, String& path, String& query);
void extractFeaturesFromRequest(const char* method, const char* path, const char* query, 
                                const char* userAgent, String headers[], int headerCount, 
                                int contentLength, float features[N_FEATURES]);
void forwardToBackend(WiFiClient& client, const String& method, const String& path, 
                     const String& query, String headers[], int headerCount);
void blockRequest(WiFiClient& client, float probability);

// ===== GLOBAL VARIABLES =====
WiFiServer wafServer(WAF_PORT);
unsigned long requestCount = 0;
unsigned long blockedCount = 0;
unsigned long allowedCount = 0;

// ===== SETUP =====
void setup() {
    Serial.begin(115200);
    delay(100);
    
    Serial.println("\n\n");
    Serial.println("========================================");
    Serial.println("  ESP8266 TinyML Mini-WAF");
    Serial.println("========================================");
    Serial.println("Model: MLP(8) - F1: 99.99%");
    Serial.println("Features: 22 dimensions");
    Serial.println("Model size: 772 bytes");
    Serial.println("========================================\n");
    
    // WiFi bağlantısı
    Serial.print("Connecting to WiFi: ");
    Serial.println(WIFI_SSID);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\n[+] WiFi connected!");
    Serial.print("    IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("    Listening on port: ");
    Serial.println(WAF_PORT);
    Serial.print("    Backend: ");
    Serial.print(BACKEND_HOST);
    Serial.print(":");
    Serial.println(BACKEND_PORT);
    Serial.println("\n[*] WAF is ready. Waiting for requests...\n");
    
    // WAF server'ı başlat
    wafServer.begin();
}

// ===== MAIN LOOP =====
void loop() {
    // Yeni client bağlantısını bekle
    WiFiClient client = wafServer.available();
    if (!client) {
        return;
    }
    
    requestCount++;
    
    if (DEBUG_MODE) {
        Serial.println("\n========================================");
        Serial.print("[*] New request #");
        Serial.println(requestCount);
        Serial.println("========================================");
    }
    
    // HTTP request'i oku
    String requestLine = "";
    String headers[20];
    int headerCount = 0;
    bool firstLine = true;
    
    // Client'ın veri göndermesini bekle (max 1 saniye)
    unsigned long timeout = millis() + 1000;
    while (!client.available() && client.connected() && millis() < timeout) {
        delay(1);
    }
    
    if (!client.available()) {
        if (DEBUG_MODE) {
            Serial.println("[!] WARNING: No data available from client");
        }
        client.stop();
        return;
    }
    
    while (client.connected() && client.available()) {
        String line = client.readStringUntil('\n');
        line.trim();
        
        if (line.length() == 0) {
            // Boş satır = header'lar bitti
            break;
        }
        
        if (firstLine) {
            requestLine = line;
            firstLine = false;
            if (DEBUG_MODE) {
                Serial.print("Request: ");
                Serial.println(requestLine);
            }
        } else {
            if (headerCount < 20) {
                headers[headerCount] = line;
                headerCount++;
            }
        }
    }
    
    // Request line'ı parse et: "METHOD /path?query HTTP/1.1"
    String method = "";
    String path = "";
    String query = "";
    String userAgent = "";
    int contentLength = 0;
    
    parseRequestLine(requestLine, method, path, query);
    
    // Header'lardan önemli bilgileri çıkar
    for (int i = 0; i < headerCount; i++) {
        if (headers[i].startsWith("User-Agent:")) {
            userAgent = headers[i].substring(11);
            userAgent.trim();
        } else if (headers[i].startsWith("Content-Length:")) {
            contentLength = headers[i].substring(15).toInt();
        }
    }
    
    // Feature extraction
    float features[N_FEATURES];
    extractFeaturesFromRequest(
        method.c_str(),
        path.c_str(),
        query.c_str(),
        userAgent.c_str(),
        headers,
        headerCount,
        contentLength,
        features
    );
    
    // Feature scaling
    scale_features(features);
    
    // Model inference
    float probability = mlp_inference(features);
    int classification = (probability >= MALICIOUS_THRESHOLD) ? 1 : 0;
    
    if (DEBUG_MODE) {
        Serial.print("Probability: ");
        Serial.print(probability, 4);
        Serial.print(" | Classification: ");
        Serial.println(classification == 1 ? "MALICIOUS" : "BENIGN");
    }
    
    // Karar: benign ise forward et, malicious ise engelle
    if (classification == 0) {
        // BENIGN - Backend'e forward et
        allowedCount++;
        forwardToBackend(client, method, path, query, headers, headerCount);
    } else {
        // MALICIOUS - Engelle
        blockedCount++;
        blockRequest(client, probability);
    }
    
    client.stop();
    
    if (DEBUG_MODE) {
        Serial.print("Stats: Total=");
        Serial.print(requestCount);
        Serial.print(" | Allowed=");
        Serial.print(allowedCount);
        Serial.print(" | Blocked=");
        Serial.println(blockedCount);
    }
}

// ===== HELPER FUNCTIONS =====

void parseRequestLine(const String& requestLine, String& method, String& path, String& query) {
    // "GET /path?query HTTP/1.1" formatını parse et
    // Default değerler
    method = "";
    path = "";
    query = "";
    
    int firstSpace = requestLine.indexOf(' ');
    int secondSpace = requestLine.indexOf(' ', firstSpace + 1);
    
    if (firstSpace > 0 && secondSpace > firstSpace) {
        method = requestLine.substring(0, firstSpace);
        String fullPath = requestLine.substring(firstSpace + 1, secondSpace);
        
        int questionMark = fullPath.indexOf('?');
        if (questionMark > 0) {
            path = fullPath.substring(0, questionMark);
            query = fullPath.substring(questionMark + 1);
        } else {
            path = fullPath;
            query = "";
        }
    } else {
        // Parsing başarısız - debug için log
        if (DEBUG_MODE) {
            Serial.println("[!] WARNING: Failed to parse request line");
            Serial.print("    Raw line: '");
            Serial.print(requestLine);
            Serial.println("'");
        }
    }
}

void extractFeaturesFromRequest(
    const char* method,
    const char* path,
    const char* query,
    const char* userAgent,
    String headers[],
    int headerCount,
    int contentLength,
    float features[N_FEATURES]
) {
    // String array'i char* array'e çevir
    const char* headerPtrs[20];
    for (int i = 0; i < headerCount && i < 20; i++) {
        headerPtrs[i] = headers[i].c_str();
    }
    
    // Feature extraction (esp8266_features.h'den)
    extract_features(
        method,
        path,
        query,
        userAgent,
        headerPtrs,
        headerCount,
        contentLength,
        features
    );
}

void forwardToBackend(
    WiFiClient& client,
    const String& method,
    const String& path,
    const String& query,
    String headers[],
    int headerCount
) {
    if (DEBUG_MODE) {
        Serial.println("[+] ALLOWED - Forwarding to backend...");
    }
    
    // Backend'e bağlan
    WiFiClient backendClient;
    if (!backendClient.connect(BACKEND_HOST, BACKEND_PORT)) {
        Serial.println("[!] Backend connection failed!");
        client.println("HTTP/1.1 502 Bad Gateway\r\n\r\nBackend unavailable");
        return;
    }
    
    // Request'i backend'e ilet
    String fullPath = path;
    if (query.length() > 0) {
        fullPath += "?" + query;
    }
    
    // Debug: Request line'ı kontrol et
    if (method.length() == 0 || fullPath.length() == 0) {
        Serial.println("[!] ERROR: Empty method or path!");
        Serial.print("    Method: '"); Serial.print(method); Serial.println("'");
        Serial.print("    Path: '"); Serial.print(fullPath); Serial.println("'");
        client.println("HTTP/1.1 500 Internal Server Error\r\n\r\nWAF Error");
        backendClient.stop();
        return;
    }
    
    backendClient.print(method);
    backendClient.print(" ");
    backendClient.print(fullPath);
    backendClient.println(" HTTP/1.1");
    
    // Header'ları ilet
    for (int i = 0; i < headerCount; i++) {
        backendClient.println(headers[i]);
    }
    backendClient.println();
    
    // Backend'den gelen response'u client'a ilet
    unsigned long timeout = millis() + 5000; // 5 saniye timeout
    while (backendClient.connected() || backendClient.available()) {
        if (backendClient.available()) {
            char c = backendClient.read();
            client.write(c);
            timeout = millis() + 5000;
        }
        if (millis() > timeout) {
            Serial.println("[!] Backend timeout");
            break;
        }
    }
    
    backendClient.stop();
    
    if (DEBUG_MODE) {
        Serial.println("[+] Response forwarded to client");
    }
}

void blockRequest(WiFiClient& client, float probability) {
    if (DEBUG_MODE) {
        Serial.print("[!] BLOCKED - Malicious request detected (prob=");
        Serial.print(probability, 4);
        Serial.println(")");
    }
    
    // 403 Forbidden response
    client.println("HTTP/1.1 403 Forbidden");
    client.println("Content-Type: text/html");
    client.println("Connection: close");
    client.println();
    client.println("<!DOCTYPE html>");
    client.println("<html><head><title>403 Forbidden</title></head>");
    client.println("<body>");
    client.println("<h1>403 Forbidden</h1>");
    client.println("<p>Your request has been blocked by the Web Application Firewall.</p>");
    client.println("<p>Reason: Malicious pattern detected</p>");
    client.print("<p>Detection confidence: ");
    client.print(probability * 100.0f, 2);
    client.println("%</p>");
    client.println("<hr><p><small>ESP8266 TinyML Mini-WAF</small></p>");
    client.println("</body></html>");
}
