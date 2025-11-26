#!/usr/bin/env python3
"""
ESP8266 WAF test script'i.
Çeşitli benign ve malicious HTTP istekleri göndererek WAF'ın tepkisini test eder.
"""
import requests
import time
from colorama import init, Fore, Style

# Colorama init
init(autoreset=True)

# ESP8266 WAF adresi (kendi ESP8266 IP'nizi buraya yazın)
WAF_URL = "http://192.168.1.50"  # ESP8266'nızın IP adresi

# Test senaryoları
TEST_CASES = [
    # BENIGN requests
    {
        "name": "Normal homepage request",
        "path": "/",
        "expected": "benign",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
    },
    {
        "name": "Normal product page",
        "path": "/product/12345",
        "expected": "benign",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1"
    },
    {
        "name": "Normal search query",
        "path": "/search?q=laptop&category=electronics",
        "expected": "benign",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) Firefox/89.0"
    },
    {
        "name": "Normal API request",
        "path": "/api/v1/users",
        "expected": "benign",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) Safari/604.1"
    },
    
    # MALICIOUS requests - Admin panel scanning
    {
        "name": "Admin panel scan",
        "path": "/admin",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "WordPress admin scan",
        "path": "/wp-admin",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "WordPress login scan",
        "path": "/wp-login.php",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "phpMyAdmin scan",
        "path": "/phpmyadmin",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "Shell upload attempt",
        "path": "/shell.php",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    
    # MALICIOUS requests - SQL injection
    {
        "name": "SQL injection - union",
        "path": "/product?id=1' UNION SELECT * FROM users--",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "SQL injection - or 1=1",
        "path": "/login?user=admin' OR '1'='1",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "SQL injection - encoded quote",
        "path": "/search?q=test%27%20OR%201=1--",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    
    # MALICIOUS requests - XSS
    {
        "name": "XSS - script tag",
        "path": "/search?q=<script>alert('XSS')</script>",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "XSS - onerror",
        "path": "/profile?name=<img src=x onerror=alert(1)>",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "XSS - javascript protocol",
        "path": "/redirect?url=javascript:alert(document.cookie)",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    
    # MALICIOUS requests - Path traversal
    {
        "name": "Path traversal - basic",
        "path": "/download?file=../../../etc/passwd",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    {
        "name": "Path traversal - encoded",
        "path": "/file?path=..%2f..%2f..%2fetc%2fpasswd",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0"
    },
    
    # MALICIOUS requests - Suspicious User-Agent
    {
        "name": "SQLMap scanner",
        "path": "/",
        "expected": "malicious",
        "user_agent": "sqlmap/1.0"
    },
    {
        "name": "Nikto scanner",
        "path": "/",
        "expected": "malicious",
        "user_agent": "Mozilla/5.00 (Nikto/2.1.6)"
    },
    {
        "name": "Nmap scanner",
        "path": "/",
        "expected": "malicious",
        "user_agent": "Mozilla/5.0 (compatible; Nmap Scripting Engine)"
    },
    {
        "name": "Curl command",
        "path": "/api/users",
        "expected": "malicious",
        "user_agent": "curl/7.68.0"
    },
]


def test_request(test_case):
    """
    Tek bir test case'i çalıştır.
    """
    url = WAF_URL + test_case["path"]
    headers = {"User-Agent": test_case["user_agent"]}
    
    print(f"\n{'='*70}")
    print(f"Test: {test_case['name']}")
    print(f"Path: {test_case['path']}")
    print(f"User-Agent: {test_case['user_agent']}")
    print(f"Expected: {test_case['expected'].upper()}")
    print('-'*70)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        # WAF'ın kararını analiz et
        if response.status_code == 403:
            result = "malicious"
            print(f"{Fore.RED}Result: BLOCKED (403 Forbidden)")
        elif response.status_code == 200:
            result = "benign"
            print(f"{Fore.GREEN}Result: ALLOWED (200 OK)")
        elif response.status_code == 502:
            result = "backend_error"
            print(f"{Fore.YELLOW}Result: Backend Error (502)")
        else:
            result = "unknown"
            print(f"{Fore.YELLOW}Result: Unknown ({response.status_code})")
        
        # Beklenen sonuçla karşılaştır
        if result == test_case["expected"]:
            print(f"{Fore.GREEN}✓ TEST PASSED")
            return True
        elif result == "backend_error":
            print(f"{Fore.YELLOW}⚠ Backend unavailable (test skipped)")
            return None
        else:
            print(f"{Fore.RED}✗ TEST FAILED")
            print(f"  Expected: {test_case['expected']}, Got: {result}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}✗ REQUEST TIMEOUT")
        return False
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}✗ CONNECTION ERROR - Is ESP8266 running?")
        return False
    except Exception as e:
        print(f"{Fore.RED}✗ ERROR: {str(e)}")
        return False


def main():
    print(f"\n{Style.BRIGHT}{'='*70}")
    print(f"  ESP8266 TinyML Mini-WAF Test Suite")
    print(f"{'='*70}{Style.RESET_ALL}")
    print(f"\nTarget: {WAF_URL}")
    print(f"Total tests: {len(TEST_CASES)}")
    print(f"\n{Style.BRIGHT}Starting tests...{Style.RESET_ALL}")
    
    passed = 0
    failed = 0
    skipped = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{Style.BRIGHT}[{i}/{len(TEST_CASES)}]{Style.RESET_ALL}", end=" ")
        result = test_request(test_case)
        
        if result is True:
            passed += 1
        elif result is False:
            failed += 1
        else:
            skipped += 1
        
        time.sleep(2)  # Rate limiting - ESP8266 needs more time
    
    # Sonuçları özetle
    print(f"\n\n{Style.BRIGHT}{'='*70}")
    print(f"  TEST RESULTS")
    print(f"{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Passed:  {passed}/{len(TEST_CASES)}")
    print(f"{Fore.RED}Failed:  {failed}/{len(TEST_CASES)}")
    print(f"{Fore.YELLOW}Skipped: {skipped}/{len(TEST_CASES)}")
    
    success_rate = (passed / (len(TEST_CASES) - skipped) * 100) if (len(TEST_CASES) - skipped) > 0 else 0
    print(f"\n{Style.BRIGHT}Success Rate: {success_rate:.1f}%{Style.RESET_ALL}")
    
    if failed == 0 and skipped == 0:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 ALL TESTS PASSED!{Style.RESET_ALL}")
    elif failed == 0:
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}⚠ All tests passed (some skipped due to backend){Style.RESET_ALL}")
    else:
        print(f"\n{Fore.RED}{Style.BRIGHT}❌ SOME TESTS FAILED{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
