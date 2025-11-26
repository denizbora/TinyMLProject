// ESP8266 Feature Extraction
// 22 boyutlu feature vektörü oluşturur

#ifndef ESP8266_FEATURES_H
#define ESP8266_FEATURES_H

#include <Arduino.h>
#include <math.h>

// Pattern arrays
const char* LOGIN_KEYWORDS[] = {
    "admin", "login", "wp-admin", "wp-login", "phpmyadmin",
    "shell", "xmlrpc", "console", "manager", "cpanel", "roundcube"
};
const int LOGIN_KEYWORDS_COUNT = 11;

const char* SQLI_PATTERNS[] = {
    "union", "select", " or 1=1", "%27", "'", "\"", "--", "/*", 
    "../", "..%2f", "%2e%2e/"
};
const int SQLI_PATTERNS_COUNT = 11;

const char* XSS_PATTERNS[] = {
    "<script", "</script", "onerror=", "onload=", "javascript:", 
    "<img", "alert("
};
const int XSS_PATTERNS_COUNT = 7;

const char* SUSPICIOUS_UA_KEYWORDS[] = {
    "sqlmap", "nikto", "nessus", "acunetix", "wpscan",
    "nmap", "curl", "wget", "bot", "crawler", "spider", "scanner",
    "scripting engine", "compatible;", "nikto/"
};
const int SUSPICIOUS_UA_KEYWORDS_COUNT = 16;

const char* COMMON_HEADERS[] = {
    "host", "user-agent", "accept", "accept-language",
    "accept-encoding", "connection", "cookie", "referer",
    "content-length", "content-type", "upgrade-insecure-requests"
};
const int COMMON_HEADERS_COUNT = 11;

// Shannon entropy hesaplama
float shannon_entropy(const char* s) {
    if (s == NULL || s[0] == '\0') {
        return 0.0f;
    }
    
    int freq[256] = {0};
    int len = 0;
    
    for (const unsigned char* p = (const unsigned char*)s; *p; p++) {
        freq[*p]++;
        len++;
    }
    
    if (len == 0) return 0.0f;
    
    float ent = 0.0f;
    for (int i = 0; i < 256; i++) {
        if (freq[i] > 0) {
            float p = (float)freq[i] / (float)len;
            ent -= p * log2f(p);
        }
    }
    return ent;
}

// Case-insensitive substring search
bool contains_substring_ci(const char* haystack, const char* needle) {
    if (haystack == NULL || needle == NULL) return false;
    
    int h_len = strlen(haystack);
    int n_len = strlen(needle);
    
    if (n_len > h_len) return false;
    
    for (int i = 0; i <= h_len - n_len; i++) {
        bool match = true;
        for (int j = 0; j < n_len; j++) {
            char h_char = tolower(haystack[i + j]);
            char n_char = tolower(needle[j]);
            if (h_char != n_char) {
                match = false;
                break;
            }
        }
        if (match) return true;
    }
    return false;
}

// Pattern listesinde arama
int contains_any(const char* haystack, const char* patterns[], int pattern_count) {
    for (int i = 0; i < pattern_count; i++) {
        if (contains_substring_ci(haystack, patterns[i])) {
            return 1;
        }
    }
    return 0;
}

// Query string'den parametre sayısı ve max uzunluk
void parse_query_params(const char* query, int* num_params, int* max_param_len) {
    *num_params = 0;
    *max_param_len = 0;
    
    if (query == NULL || query[0] == '\0') return;
    
    char local_query[256];
    strncpy(local_query, query, sizeof(local_query) - 1);
    local_query[sizeof(local_query) - 1] = '\0';
    
    char* token = strtok(local_query, "&");
    while (token != NULL) {
        (*num_params)++;
        
        char* eq = strchr(token, '=');
        const char* val = token;
        if (eq != NULL) {
            val = eq + 1;
        }
        
        int vlen = strlen(val);
        if (vlen > *max_param_len) {
            *max_param_len = vlen;
        }
        
        token = strtok(NULL, "&");
    }
}

// Header isminin common olup olmadığını kontrol et
bool is_common_header(const char* header_name) {
    for (int i = 0; i < COMMON_HEADERS_COUNT; i++) {
        if (strcasecmp(header_name, COMMON_HEADERS[i]) == 0) {
            return true;
        }
    }
    return false;
}

// Ana feature extraction fonksiyonu
void extract_features(
    const char* method,
    const char* path,
    const char* query,
    const char* user_agent,
    const char* headers[],
    int num_headers,
    int content_length,
    float features[22]
) {
    // f0-f3: method one-hot
    features[0] = (strcasecmp(method, "GET") == 0) ? 1.0f : 0.0f;
    features[1] = (strcasecmp(method, "POST") == 0) ? 1.0f : 0.0f;
    features[2] = (strcasecmp(method, "HEAD") == 0) ? 1.0f : 0.0f;
    features[3] = (strcasecmp(method, "GET") != 0 && 
                   strcasecmp(method, "POST") != 0 && 
                   strcasecmp(method, "HEAD") != 0) ? 1.0f : 0.0f;
    
    // f4: path_length
    features[4] = (float)strlen(path);
    
    // f5-f6: num_params, max_param_length
    int num_params = 0;
    int max_param_len = 0;
    parse_query_params(query, &num_params, &max_param_len);
    features[5] = (float)num_params;
    features[6] = (float)max_param_len;
    
    // Combined path+query için buffer
    char combined[384];
    snprintf(combined, sizeof(combined), "%s?%s", path, query ? query : "");
    
    // f7: has_login_keyword
    features[7] = (float)contains_any(combined, LOGIN_KEYWORDS, LOGIN_KEYWORDS_COUNT);
    
    // f8: has_sqli_pattern
    features[8] = (float)contains_any(combined, SQLI_PATTERNS, SQLI_PATTERNS_COUNT);
    
    // f9: has_xss_pattern
    features[9] = (float)contains_any(combined, XSS_PATTERNS, XSS_PATTERNS_COUNT);
    
    // f10: path_entropy
    features[10] = shannon_entropy(combined);
    
    // f11: num_headers
    features[11] = (float)num_headers;
    
    // f12: user_agent_length
    features[12] = (float)strlen(user_agent ? user_agent : "");
    
    // f13: has_suspicious_ua
    features[13] = (float)contains_any(user_agent, SUSPICIOUS_UA_KEYWORDS, SUSPICIOUS_UA_KEYWORDS_COUNT);
    
    // f14: content_length
    features[14] = (float)content_length;
    
    // f15: has_uncommon_header
    features[15] = 0.0f;
    for (int i = 0; i < num_headers; i++) {
        if (headers[i] != NULL) {
            // Header name'i al (: öncesi)
            char header_name[64];
            const char* colon = strchr(headers[i], ':');
            if (colon != NULL) {
                int len = colon - headers[i];
                if (len > 63) len = 63;
                strncpy(header_name, headers[i], len);
                header_name[len] = '\0';
                
                if (!is_common_header(header_name)) {
                    features[15] = 1.0f;
                    break;
                }
            }
        }
    }
    
    // f16-f18: accept_language_length, host_length, referer_length
    features[16] = 0.0f;
    features[17] = 0.0f;
    features[18] = 0.0f;
    
    for (int i = 0; i < num_headers; i++) {
        if (headers[i] != NULL) {
            if (strncasecmp(headers[i], "Accept-Language:", 16) == 0) {
                features[16] = (float)strlen(headers[i] + 16);
            } else if (strncasecmp(headers[i], "Host:", 5) == 0) {
                features[17] = (float)strlen(headers[i] + 5);
            } else if (strncasecmp(headers[i], "Referer:", 8) == 0) {
                features[18] = (float)strlen(headers[i] + 8);
            }
        }
    }
    
    // f19-f21: IP bazlı davranışsal (şimdilik 0)
    features[19] = 0.0f;
    features[20] = 0.0f;
    features[21] = 0.0f;
}

#endif // ESP8266_FEATURES_H
