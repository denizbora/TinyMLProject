#!/usr/bin/env python3
"""
Apache/Nginx access.log -> CSV dönüştürücü + otomatik etiketleme.
Format: IP - - [timestamp] "METHOD /path?query HTTP/x.x" status size "referer" "user-agent" "-"
"""
import re
import csv
from urllib.parse import urlparse, parse_qs

# Regex pattern (Apache combined log format)
LOG_PATTERN = re.compile(
    r'^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\S+) "([^"]*)" "([^"]*)" "([^"]*)"'
)

# Malicious pattern'ler (path/query/UA'da bunlar varsa label=1)
LOGIN_KEYWORDS = [
    "admin", "login", "wp-admin", "wp-login", "phpmyadmin",
    "shell", "xmlrpc", "console", "manager", "cpanel", "roundcube",
    "wp-config", "config.php", "setup.php", "install.php"
]

SQLI_PATTERNS = [
    "union", "select", " or 1=1", "' or '1'='1",
    "%27", "--", "/*", "../", "..%2f", "%2e%2e/",
    "xp_cmdshell", "sleep(", "benchmark(", "waitfor"
]

XSS_PATTERNS = [
    "<script", "</script", "onerror=", "onload=", "javascript:",
    "<img", "alert(", "<iframe", "eval("
]

SUSPICIOUS_UA_KEYWORDS = [
    "sqlmap", "nikto", "nessus", "acunetix", "wpscan",
    "nmap", "scanner", "exploit", "hack", "injection"
]

def is_malicious(method, path, query, user_agent):
    """
    Basit kural tabanlı etiketleme:
    - path/query'de login keyword, sqli, xss pattern varsa -> 1
    - user_agent'ta suspicious keyword varsa -> 1
    - Diğer durumlarda -> 0
    """
    combined = (path + "?" + query).lower()
    ua_lower = user_agent.lower()

    for kw in LOGIN_KEYWORDS:
        if kw in combined:
            return 1
    for pat in SQLI_PATTERNS:
        if pat in combined:
            return 1
    for pat in XSS_PATTERNS:
        if pat in combined:
            return 1
    for kw in SUSPICIOUS_UA_KEYWORDS:
        if kw in ua_lower:
            return 1

    return 0


def parse_log_line(line):
    """
    Tek log satırını parse et, dict döndür.
    """
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    ip = match.group(1)
    timestamp = match.group(2)
    method = match.group(3)
    url = match.group(4)
    http_version = match.group(5)
    status = match.group(6)
    size = match.group(7)
    referer = match.group(8)
    user_agent = match.group(9)
    extra = match.group(10)

    # URL'yi parse et
    parsed = urlparse(url)
    path = parsed.path if parsed.path else "/"
    query = parsed.query if parsed.query else ""

    # Headers string (basit: referer varsa ekle)
    headers_parts = []
    if user_agent and user_agent != "-":
        headers_parts.append(f"User-Agent: {user_agent}")
    if referer and referer != "-":
        headers_parts.append(f"Referer: {referer}")
    headers_str = ";".join(headers_parts)

    # Content-Length (size'dan tahmin, GET için genelde 0)
    try:
        content_length = int(size) if size != "-" else 0
    except ValueError:
        content_length = 0

    # Label
    label = is_malicious(method, path, query, user_agent)

    return {
        "ip": ip,
        "method": method,
        "path": path,
        "query": query,
        "user_agent": user_agent if user_agent != "-" else "",
        "headers": headers_str,
        "content_length": content_length,
        "label": label
    }


def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    input_log = os.path.join(project_dir, "access.log")
    output_csv = os.path.join(project_dir, "http_requests_labeled.csv")

    print(f"[*] Parsing {input_log} ...")
    
    parsed_count = 0
    malicious_count = 0
    benign_count = 0

    with open(input_log, "r", encoding="utf-8", errors="ignore") as fin, \
         open(output_csv, "w", newline="", encoding="utf-8") as fout:
        
        writer = csv.DictWriter(fout, fieldnames=[
            "ip", "method", "path", "query", "user_agent", "headers", "content_length", "label"
        ])
        writer.writeheader()

        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue

            row = parse_log_line(line)
            if row is None:
                # parse başarısız
                continue

            writer.writerow(row)
            parsed_count += 1

            if row["label"] == 1:
                malicious_count += 1
            else:
                benign_count += 1

            if parsed_count % 50000 == 0:
                print(f"  Processed {parsed_count} lines... (benign: {benign_count}, malicious: {malicious_count})")

    print(f"[+] Done! Parsed {parsed_count} requests.")
    print(f"    Benign: {benign_count}, Malicious: {malicious_count}")
    print(f"[+] Output: {output_csv}")


if __name__ == "__main__":
    main()
