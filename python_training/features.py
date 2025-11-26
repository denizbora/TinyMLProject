#!/usr/bin/env python3
"""
HTTP request feature extraction (22 boyutlu sayısal vektör).
"""
import csv
import math
from typing import List, Dict, Tuple

LOGIN_KEYWORDS = [
    "admin", "login", "wp-admin", "wp-login", "phpmyadmin",
    "shell", "xmlrpc", "console", "manager", "cpanel", "roundcube"
]

SQLI_PATTERNS = [
    "union", "select", " or 1=1", "' or '1'='1",
    "%27", "'", "\"", "--", "/*", "../", "..%2f", "%2e%2e/"
]

XSS_PATTERNS = [
    "<script", "</script", "onerror=", "onload=", "javascript:",
    "<img", "alert("
]

SUSPICIOUS_UA_KEYWORDS = [
    "sqlmap", "nikto", "nessus", "acunetix", "wpscan",
    "nmap", "curl", "wget", "bot", "crawler", "spider", "scanner"
]

COMMON_HEADERS = {
    "host", "user-agent", "accept", "accept-language",
    "accept-encoding", "connection", "cookie", "referer",
    "content-length", "content-type", "upgrade-insecure-requests"
}


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(s)
    ent = 0.0
    for count in freq.values():
        p = count / length
        ent -= p * math.log2(p)
    return ent


def contains_any(haystack: str, patterns: List[str]) -> int:
    h = haystack.lower()
    for p in patterns:
        if p in h:
            return 1
    return 0


def parse_headers_str(headers_str: str) -> Dict[str, str]:
    headers = {}
    if not headers_str:
        return headers
    parts = headers_str.split(';')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if ':' in part:
            name, value = part.split(':', 1)
            headers[name.strip().lower()] = value.strip()
    return headers


def extract_features_from_row(row: Dict[str, str]) -> Tuple[List[float], int]:
    """
    row: {'ip','method','path','query','user_agent','headers','content_length','label'}
    Returns: (features[22], label)
    """
    method = (row.get("method") or "").upper()
    path = row.get("path") or ""
    query = row.get("query") or ""
    ua = row.get("user_agent") or ""
    headers_str = row.get("headers") or ""
    content_length_str = row.get("content_length") or "0"
    label_str = row.get("label") or "0"

    # 0-3: method one-hot
    m_get = 1 if method == "GET" else 0
    m_post = 1 if method == "POST" else 0
    m_head = 1 if method == "HEAD" else 0
    m_other = 1 if (method not in ("GET", "POST", "HEAD")) else 0

    # 4: path_length
    path_length = len(path)

    # Query parsing
    num_params = 0
    max_param_len = 0
    if query:
        params = query.split('&')
        num_params = len(params)
        for p in params:
            if '=' in p:
                _, v = p.split('=', 1)
            else:
                v = p
            if len(v) > max_param_len:
                max_param_len = len(v)

    combined = path + "?" + query if query else path

    has_login_keyword = contains_any(combined, LOGIN_KEYWORDS)
    has_sqli_pattern = contains_any(combined, SQLI_PATTERNS)
    has_xss_pattern = contains_any(combined, XSS_PATTERNS)
    path_entropy = shannon_entropy(combined)

    headers = parse_headers_str(headers_str)
    num_headers = len(headers)
    user_agent_length = len(ua)
    has_suspicious_ua = contains_any(ua, SUSPICIOUS_UA_KEYWORDS)

    try:
        content_length = int(content_length_str)
    except ValueError:
        content_length = 0

    has_uncommon_header = 0
    for hname in headers.keys():
        if hname not in COMMON_HEADERS:
            has_uncommon_header = 1
            break

    accept_language_length = len(headers.get("accept-language", ""))
    host_length = len(headers.get("host", ""))
    referer_length = len(headers.get("referer", ""))

    # İlk POC: IP davranışsal özellikleri kapalı (0)
    req_count_last_10s = 0.0
    login_admin_hits_last_60s = 0.0
    unique_paths_last_60s = 0.0

    features = [
        float(m_get),                      # f0
        float(m_post),                     # f1
        float(m_head),                     # f2
        float(m_other),                    # f3
        float(path_length),                # f4
        float(num_params),                 # f5
        float(max_param_len),              # f6
        float(has_login_keyword),          # f7
        float(has_sqli_pattern),           # f8
        float(has_xss_pattern),            # f9
        float(path_entropy),               # f10
        float(num_headers),                # f11
        float(user_agent_length),          # f12
        float(has_suspicious_ua),          # f13
        float(content_length),             # f14
        float(has_uncommon_header),        # f15
        float(accept_language_length),     # f16
        float(host_length),                # f17
        float(referer_length),             # f18
        float(req_count_last_10s),         # f19
        float(login_admin_hits_last_60s),  # f20
        float(unique_paths_last_60s)       # f21
    ]

    label = int(label_str)
    return features, label


def load_dataset_from_csv(path: str):
    """
    CSV'den feature vektörlerini yükle.
    Returns: (X, y) - X: list of feature lists, y: list of labels
    """
    X, y = [], []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            feats, label = extract_features_from_row(row)
            X.append(feats)
            y.append(label)
    return X, y
