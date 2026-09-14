#!/usr/bin/env python3
"""
FINALRECON-AI - ULTIMATE AUTONOMOUS AI ROBOT EDITION
=====================================================
Version: 2026.9 - IP Address Unlock Edition
"""

import os
import sys
import re
import json
import time
import socket
import ssl
import ipaddress
import argparse
import datetime
import subprocess
import requests
import urllib3
from urllib import parse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# VERSION
# ============================================
VERSION = "2026.9"
BUILD_NUMBER = "2026.009.1"

# ============================================
# COLORS
# ============================================
class Fore:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

# ============================================
# CONFIG
# ============================================
CONFIG = {
    'timeout': 10,
    'dir_enum_th': 30,
    'port_scan_th': 50,
    'dir_enum_wlist': 'wordlists/dirb_common.txt',
    'export_dir': 'finalrecon-ai-results',
}

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8000, 8888, 9000]

COMMON_SUBDOMAINS = [
    'www', 'mail', 'ftp', 'webmail', 'smtp', 'pop', 'ns1', 'ns2', 'cpanel',
    'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test', 'ns', 'blog',
    'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3', 'mail2',
    'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static',
    'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki',
    'web', 'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal',
    'video', 'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns4', 'www3',
    'dns', 'search', 'staging', 'server', 'mx1', 'chat', 'wap', 'my', 'svn',
    'mail1', 'sites', 'proxy', 'ads', 'host', 'crm', 'cms', 'backup', 'mx2',
    'info', 'apps', 'download', 'remote', 'db', 'forums', 'store', 'relay',
    'files', 'app', 'live', 'owa', 'en', 'start', 'sms', 'office', 'exchange',
    'gateway', 'router', 'firewall', 'monitor', 'jenkins', 'gitlab', 'jira',
    'docker', 'k8s', 'aws', 'azure', 'gcp', 'cloud', 's3', 'storage', 'assets'
]

DEFAULT_WORDLIST = [
    'admin', 'login', 'wp-admin', 'administrator', 'backup', 'backups',
    'config', 'configs', 'db', 'database', 'sql', 'test', 'tests',
    'dev', 'development', 'staging', 'prod', 'production', 'api',
    'apis', 'v1', 'v2', 'docs', 'documentation', 'help', 'support',
    'uploads', 'upload', 'files', 'file', 'images', 'img', 'css',
    'js', 'javascript', 'assets', 'static', 'media', 'video', 'videos',
    'download', 'downloads', 'private', 'secret', 'secrets', 'hidden',
    'tmp', 'temp', 'cache', 'logs', 'log', 'error', 'errors', 'debug',
    'phpinfo.php', 'info.php', 'test.php', 'robots.txt', 'sitemap.xml',
    '.git', '.svn', '.env', '.htaccess', 'web.config', 'crossdomain.xml',
    'phpmyadmin', 'pma', 'mysql', 'adminer', 'cpanel', 'whm', 'webmail',
    'mail', 'email', 'smtp', 'pop3', 'imap', 'ftp', 'ssh', 'telnet',
    'vpn', 'proxy', 'gateway', 'router', 'switch', 'firewall', 'waf',
    'cdn', 'dns', 'ns1', 'ns2', 'mx', 'mail1', 'mail2', 'portal',
    'intranet', 'cms', 'crm', 'erp', 'hr', 'finance', 'forum', 'blog',
    'news', 'media', 'gallery', 'shop', 'store', 'cart', 'checkout',
    'user', 'users', 'profile', 'account', 'register', 'signup', 'login',
    'password', 'reset', 'forgot', 'status', 'health', 'monitor', 'stats',
    'security', 'secure', 'ssl', 'tls', 'cert', 'certificate', 'key',
    'token', 'session', 'cookie', 'header', 'debug', 'trace', 'info'
]

# ============================================
# API KEY PATTERNS
# ============================================
API_KEY_PATTERNS = {
    'AWS Access Key': r'AKIA[0-9A-Z]{16}',
    'AWS Secret Key': r'aws[_-]?secret[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']',
    'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
    'Google OAuth': r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',
    'GitHub Token': r'gh[pousr]_[0-9a-zA-Z]{36}',
    'GitLab Token': r'glpat-[0-9a-zA-Z\-_]{20}',
    'Slack Token': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
    'Slack Webhook': r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+',
    'Discord Token': r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}',
    'Discord Webhook': r'https://discord(?:app)?\.com/api/webhooks/[0-9]+/[a-zA-Z0-9_-]+',
    'Telegram Bot Token': r'[0-9]{8,10}:[a-zA-Z0-9_-]{35}',
    'Twilio API Key': r'SK[0-9a-fA-F]{32}',
    'Twilio Account SID': r'AC[a-z0-9]{32}',
    'SendGrid API Key': r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}',
    'Mailgun API Key': r'key-[0-9a-zA-Z]{32}',
    'Mailchimp API Key': r'[0-9a-f]{32}-us[0-9]{1,2}',
    'Stripe Live Key': r'sk_live_[0-9a-zA-Z]{24}',
    'Stripe Test Key': r'sk_test_[0-9a-zA-Z]{24}',
    'Stripe Publishable': r'pk_(live|test)_[0-9a-zA-Z]{24}',
    'PayPal Client ID': r'AY[a-zA-Z0-9_-]{20,}',
    'Square Access Token': r'sq0atp-[0-9A-Za-z\-_]{22}',
    'MongoDB URI': r'mongodb(\+srv)?://[^\s"\']+',
    'PostgreSQL URI': r'postgres(ql)?://[^\s"\']+',
    'MySQL URI': r'mysql://[^\s"\']+',
    'Redis URI': r'redis://[^\s"\']+',
    'RSA Private Key': r'-----BEGIN RSA PRIVATE KEY-----',
    'DSA Private Key': r'-----BEGIN DSA PRIVATE KEY-----',
    'EC Private Key': r'-----BEGIN EC PRIVATE KEY-----',
    'OpenSSH Private Key': r'-----BEGIN OPENSSH PRIVATE KEY-----',
    'PGP Private Key': r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
    'JWT Token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
    'Basic Auth': r'Basic [A-Za-z0-9+/=]{20,}',
    'Bearer Token': r'Bearer [A-Za-z0-9\-._~+/]+=*',
    'OAuth Token': r'oauth[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Session Token': r'session[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Generic API Key': r'api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'API Secret': r'api[_-]?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Access Token': r'access[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Secret Key': r'secret[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Private Key': r'private[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Client Secret': r'client[_-]?secret["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Auth Token': r'auth[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Webhook URL': r'https?://[^\s"\']*webhook[^\s"\']*',
}

# ============================================
# WEB SERVER API KEY PATTERNS
# ============================================
WEB_SERVER_API_KEY_PATTERNS = {
    'Apache API Key': r'apache[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{16,})["\']',
    'Nginx API Key': r'nginx[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{16,})["\']',
    'IIS API Key': r'iis[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{16,})["\']',
    'Tomcat Manager': r'tomcat[_-]?(?:manager|admin)["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{8,})["\']',
    'Jenkins API Token': r'jenkins[_-]?(?:api[_-]?)?token["\']?\s*[:=]\s*["\']([a-f0-9]{32,})["\']',
    'GitLab CI Token': r'CI_JOB_TOKEN["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'GitHub Actions Token': r'GITHUB_TOKEN["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Docker Registry Token': r'docker[_-]?(?:registry[_-]?)?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Kubernetes Token': r'kubernetes[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Cloudflare API Key': r'cloudflare[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Cloudflare Token': r'cloudflare[_-]?token["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Heroku API Key': r'heroku[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-f0-9\-]{32,})["\']',
    'DigitalOcean Token': r'digitalocean[_-]?token["\']?\s*[:=]\s*["\']([a-f0-9]{64})["\']',
    'Vultr API Key': r'vultr[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
    'Linode API Key': r'linode[_-]?api[_-]?key["\']?\s*[:=]\s*["\']([a-f0-9]{64})["\']',
    'Web Server Admin': r'(?:web|server)[_-]?(?:admin|api)[_-]?(?:key|token|secret)["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{16,})["\']',
}

# ============================================
# IP BLOCK INDICATORS
# ============================================
IP_BLOCK_INDICATORS = [
    'blocked', 'denied', 'forbidden', 'access denied', 'ip blocked',
    'your ip', 'suspicious activity', 'too many requests',
    'rate limit', '429', '403', 'blacklisted', 'banned',
    'ip banned', 'ip address blocked', 'access forbidden',
    'you have been blocked', 'your ip has been blocked',
    'firewall', 'security block', 'waf block', 'cloudflare block',
    'anti-bot', 'bot detection', 'captcha required',
]

# ============================================
# IP UNLOCK INDICATORS
# ============================================
IP_UNLOCK_INDICATORS = [
    'unlocked', 'allowed', 'permitted', 'access granted',
    'whitelisted', 'whitelist', 'unblocked', 'access allowed',
    '200 ok', 'success', 'welcome', 'granted access',
]

# ============================================
# BROWSER APP FILES
# ============================================
BROWSER_APP_FILES = [
    'manifest.json', 'manifest.webmanifest', 'service-worker.js', 'sw.js',
    'worker.js', 'offline.html', '404.html', '500.html', 'browserconfig.xml',
    'app.js', 'app.min.js', 'app.css', 'main.js', 'main.css', 'index.js',
    'vendor.js', 'bundle.js', 'runtime.js', 'polyfills.js', 'scripts.js',
    'webpack.config.js', 'rollup.config.js', 'vite.config.js', 'gulpfile.js',
    'babel.config.js', '.babelrc', 'tsconfig.json', 'jsconfig.json',
    'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    '.env', '.env.local', '.env.development', '.env.production',
    'app.js.map', 'main.js.map', 'bundle.js.map',
    'jest.config.js', 'karma.conf.js', 'cypress.json',
    '.eslintrc.js', '.prettierrc', '.editorconfig', 'Dockerfile',
    'docker-compose.yml', 'nginx.conf', '.htaccess', 'web.config'
]

# ============================================
# BROWSER APP PATTERNS
# ============================================
BROWSER_APP_PATTERNS = {
    'frameworks': {
        'React': [r'react', r'react-dom', r'_react'],
        'Vue.js': [r'vue', r'v-model', r'v-bind'],
        'Angular': [r'angular', r'ng-app', r'ng-model'],
        'Svelte': [r'svelte'],
        'jQuery': [r'jquery', r'\$\(document\)'],
        'Alpine.js': [r'alpine', r'x-data'],
    },
    'build_tools': {
        'Webpack': [r'webpack', r'__webpack_require__'],
        'Vite': [r'vite', r'@vite/client'],
        'Parcel': [r'parcel'],
        'Rollup': [r'rollup'],
        'Babel': [r'babel'],
        'TypeScript': [r'typescript', r'tslib'],
    },
    'state_management': {
        'Redux': [r'redux', r'createStore'],
        'MobX': [r'mobx'],
        'Vuex': [r'vuex'],
        'Pinia': [r'pinia'],
        'Zustand': [r'zustand'],
    },
    'routing': {
        'React Router': [r'react-router', r'BrowserRouter'],
        'Vue Router': [r'vue-router'],
        'Next.js': [r'__NEXT_DATA__'],
        'Nuxt.js': [r'__NUXT__'],
    },
    'ui_libraries': {
        'Bootstrap': [r'bootstrap', r'col-md-'],
        'Tailwind': [r'tailwind'],
        'Material UI': [r'material-ui'],
        'Ant Design': [r'antd'],
    },
    'analytics': {
        'Google Analytics': [r'google-analytics', r'gtag'],
        'Google Tag Manager': [r'googletagmanager'],
        'Mixpanel': [r'mixpanel'],
        'Sentry': [r'sentry'],
    },
    'auth': {
        'OAuth': [r'oauth', r'access_token'],
        'JWT': [r'jwt', r'Bearer '],
        'Firebase': [r'firebase'],
        'Auth0': [r'auth0'],
    },
    'api_clients': {
        'Axios': [r'axios'],
        'Fetch API': [r'fetch\('],
        'GraphQL': [r'graphql'],
        'Apollo': [r'apollo'],
    },
}


# ============================================
# MAIN CLASS
# ============================================
class AutonomousAIRobot:
    def __init__(self, target=None, args=None):
        self.target = target
        self.args = args
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

        if args and hasattr(args, 'H') and args.H:
            for header in args.H:
                if ':' in header:
                    key, value = header.split(':', 1)
                    self.session.headers[key.strip()] = value.strip()

        if args and hasattr(args, 'proxy') and args.proxy:
            self.session.proxies = {'http': args.proxy, 'https': args.proxy}

        # Storage
        self.vulnerabilities_found = []
        self.firewalls_detected = []
        self.destroyed_firewalls = []
        self.isp_info = {}
        self.isp_info_enabled = False
        self.ip_blocked = False
        self.ip_unlocked = False
        self.ip_address_info = {}

        self.headers_info = {}
        self.ssl_info = {}
        self.whois_info = {}
        self.dns_info = {}
        self.subdomains_found = []
        self.open_ports = []
        self.directories_found = []
        self.technologies = []
        self.emails = []
        self.js_files = []
        self.api_endpoints = []
        self.cors_info = {}
        self.http_methods = []
        self.wayback_urls = []
        self.crawled_urls = []
        self.secrets_found = []
        self.forms_found = []

        # Source code
        self.comments_found = []
        self.hidden_fields = []
        self.inline_scripts = []
        self.meta_tags = []
        self.source_maps = []
        self.backup_files = []
        self.config_files = []
        self.git_exposure = []
        self.svn_exposure = []
        self.source_code_analysis_data = {}

        # Browser app
        self.browser_app_files = []
        self.browser_app_analysis_data = {}
        self.browser_frameworks = []
        self.browser_build_tools = []
        self.pwa_analysis = {}
        self.service_worker_analysis = {}

        # SSL unlock
        self.ssl_unlock_info = {}
        self.unlocked_ssl = []

        # File analysis
        self.index_html_analysis = {}
        self.html_files_analysis = {}
        self.java_files_analysis = {}
        self.php_files_analysis = {}
        self.python_files_analysis = {}
        self.env_files_analysis = {}

        # API Key detection
        self.api_keys_found = []
        self.web_server_api_keys_found = []

        # Ports
        self.custom_ports = COMMON_PORTS
        if args and hasattr(args, 'port') and args.port:
            self.custom_ports = args.port

        # Wordlist
        self.wordlist = CONFIG['dir_enum_wlist']
        if args and hasattr(args, 'wordlist') and args.wordlist:
            self.wordlist = args.wordlist

        if args and hasattr(args, 'isp_info') and args.isp_info:
            self.isp_info_enabled = True

        if self.target:
            self.parse_target()

        if not (args and hasattr(args, 'no_banner') and args.no_banner):
            self.print_banner()

        if self.target:
            self.start_autonomous_mode()

    def print_banner(self):
        art = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ███████╗██╗███╗   ██╗ █████╗ ██╗     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
║     ██╔════╝██║████╗  ██║██╔══██╗██║     ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
║     █████╗  ██║██╔██╗ ██║███████║██║     ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
║     ██╔══╝  ██║██║╚██╗██║██╔══██║██║     ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
║     ██║     ██║██║ ╚████║██║  ██║███████╗██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
║     ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
║                                                                              ║
║                    FINALRECON-AI - IP ADDRESS UNLOCK EDITION                ║
║                          Version: 2026.9 - AI Robot                         ║
║                                                                              ║
║                    🤖 AUTONOMOUS AI ROBOT MODE 🤖                           ║
║                                                                              ║
║              🔓 IP ADDRESS UNLOCK/BLOCK CHECK                               ║
║              🔐 API KEY DETECTION | WEB SERVER API KEYS                    ║
║              📊 Header Enum | SSL Analysis | WHOIS | DNS | Subdomain     ║
║              🔍 Port Scan | Dir Bruteforce | Crawler | Tech Detect      ║
║              📝 Source Code | HTML | Java | PHP | Python | ENV          ║
║              🌐 Browser App Analysis | Frameworks | PWA | Service Worker ║
║              🔐 SSL KEY UNLOCK | HSTS Bypass                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝"""
        print(Fore.CYAN + art + Fore.RESET + "\n")
        print(Fore.GREEN + "[>] Version: " + VERSION)
        print(Fore.GREEN + "[>] Build: " + BUILD_NUMBER)
        print()

    def parse_target(self):
        if not self.target:
            return

        if not self.target.startswith(('http://', 'https://')):
            self.target = 'http://' + self.target

        if self.target.endswith('/'):
            self.target = self.target[:-1]

        split_url = parse.urlsplit(self.target)
        self.protocol = split_url.scheme
        self.hostname = split_url.hostname

        if self.args and hasattr(self.args, 'port') and self.args.port:
            self.port = self.args.port[0] if isinstance(self.args.port, list) else self.args.port
        else:
            self.port = split_url.port or (443 if self.protocol == 'https' else 80)

        self.path = split_url.path or '/'

        try:
            ipaddress.ip_address(self.hostname)
            self.is_ip = True
            self.ip = self.hostname
        except ValueError:
            self.is_ip = False
            try:
                self.ip = socket.gethostbyname(self.hostname)
                print(Fore.CYAN + f"[*] IP Address: {self.ip}")
            except Exception as e:
                print(Fore.RED + f"[-] Unable to get IP: {e}")
                sys.exit(1)

        self.base_url = f"{self.protocol}://{self.hostname}:{self.port}"

    # ============================================
    # IP ADDRESS UNLOCK/BLOCK CHECK (NEW)
    # ============================================
    def check_ip_address(self):
        """Check if IP address is unlocked or blocked"""
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] IP ADDRESS UNLOCK/BLOCK CHECK")
        print(Fore.CYAN + "=" * 80)

        self.ip_address_info = {
            'ip': self.ip,
            'hostname': self.hostname,
            'target_url': self.base_url,
            'status': 'unknown',
            'http_status': None,
            'block_indicators': [],
            'unlock_indicators': [],
            'response_time': None,
            'response_size': None,
            'server': None,
            'checked_at': datetime.datetime.now().isoformat(),
            'actions_taken': [],
        }

        # Step 1: Basic connectivity test
        print(Fore.CYAN + f"\n[*] Step 1: Testing connectivity to {self.ip}...")

        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)
            end_time = time.time()

            self.ip_address_info['http_status'] = response.status_code
            self.ip_address_info['response_time'] = round((end_time - start_time) * 1000, 2)
            self.ip_address_info['response_size'] = len(response.content)
            self.ip_address_info['server'] = response.headers.get('Server', 'Unknown')

            print(Fore.GREEN + f"[+] HTTP Status: {response.status_code}")
            print(Fore.GREEN + f"[+] Response Time: {self.ip_address_info['response_time']} ms")
            print(Fore.GREEN + f"[+] Response Size: {self.ip_address_info['response_size']} bytes")
            print(Fore.GREEN + f"[+] Server: {self.ip_address_info['server']}")

            # Step 2: Check HTTP status code
            print(Fore.CYAN + f"\n[*] Step 2: Analyzing HTTP status code...")

            if response.status_code == 200:
                print(Fore.GREEN + f"[+] Status 200 OK - IP appears UNLOCKED")
                self.ip_address_info['status'] = 'unlocked'
                self.ip_unlocked = True

            elif response.status_code in [401, 403]:
                print(Fore.RED + f"[!] Status {response.status_code} - IP may be BLOCKED")
                self.ip_address_info['status'] = 'blocked'
                self.ip_blocked = True

            elif response.status_code == 429:
                print(Fore.RED + f"[!] Status 429 - RATE LIMITED")
                self.ip_address_info['status'] = 'rate_limited'
                self.ip_blocked = True

            elif response.status_code in [500, 502, 503, 504]:
                print(Fore.YELLOW + f"[!] Status {response.status_code} - Server error")
                self.ip_address_info['status'] = 'server_error'

            elif response.status_code in [301, 302, 303, 307, 308]:
                print(Fore.YELLOW + f"[!] Status {response.status_code} - Redirect")
                self.ip_address_info['status'] = 'redirect'

            else:
                print(Fore.YELLOW + f"[!] Status {response.status_code} - Unknown")
                self.ip_address_info['status'] = 'unknown'

            # Step 3: Check for block indicators in response
            print(Fore.CYAN + f"\n[*] Step 3: Scanning response for block indicators...")

            response_text = response.text.lower()
            response_headers = str(response.headers).lower()

            block_found = []
            for indicator in IP_BLOCK_INDICATORS:
                if indicator in response_text or indicator in response_headers:
                    block_found.append(indicator)
                    print(Fore.RED + f"[!] Block indicator found: '{indicator}'")

            if block_found:
                self.ip_address_info['block_indicators'] = block_found
                self.ip_address_info['status'] = 'blocked'
                self.ip_blocked = True
                print(Fore.RED + f"\n[!] IP {self.ip} is BLOCKED!")
                print(Fore.RED + f"[!] Total block indicators: {len(block_found)}")
            else:
                print(Fore.GREEN + f"[+] No block indicators found")

            # Step 4: Check for unlock indicators
            print(Fore.CYAN + f"\n[*] Step 4: Scanning response for unlock indicators...")

            unlock_found = []
            for indicator in IP_UNLOCK_INDICATORS:
                if indicator in response_text or indicator in response_headers:
                    unlock_found.append(indicator)

            if unlock_found:
                self.ip_address_info['unlock_indicators'] = unlock_found
                if self.ip_address_info['status'] != 'blocked':
                    self.ip_address_info['status'] = 'unlocked'
                    self.ip_unlocked = True
                print(Fore.GREEN + f"[+] Unlock indicators: {len(unlock_found)}")
            else:
                if self.ip_address_info['status'] != 'blocked':
                    print(Fore.YELLOW + f"[!] No unlock indicators found")

            # Step 5: Test with different paths
            print(Fore.CYAN + f"\n[*] Step 5: Testing multiple paths...")

            test_paths = ['/', '/index.html', '/robots.txt', '/login', '/admin']
            for path in test_paths:
                test_url = f"{self.base_url}{path}"
                try:
                    test_response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                    status_icon = "✓" if test_response.status_code < 400 else "✗"
                    status_color = Fore.GREEN if test_response.status_code < 400 else Fore.RED
                    print(status_color + f"    {status_icon} {path}: {test_response.status_code}")
                except Exception:
                    print(Fore.RED + f"    ✗ {path}: ERROR")

            # Step 6: Check IP via external API
            print(Fore.CYAN + f"\n[*] Step 6: Checking IP via external API...")
            try:
                api_url = f"http://ip-api.com/json/{self.ip}?fields=status,country,city,isp,org,proxy,hosting"
                api_response = requests.get(api_url, timeout=10)

                if api_response.status_code == 200:
                    api_data = api_response.json()
                    if api_data.get('status') == 'success':
                        self.ip_address_info['external_api'] = {
                            'country': api_data.get('country'),
                            'city': api_data.get('city'),
                            'isp': api_data.get('isp'),
                            'org': api_data.get('org'),
                            'is_proxy': api_data.get('proxy', False),
                            'is_hosting': api_data.get('hosting', False),
                        }

                        print(Fore.GREEN + f"    Country: {api_data.get('country')}")
                        print(Fore.GREEN + f"    City: {api_data.get('city')}")
                        print(Fore.GREEN + f"    ISP: {api_data.get('isp')}")

                        if api_data.get('proxy'):
                            print(Fore.RED + f"    [!] IP is a PROXY")
                        if api_data.get('hosting'):
                            print(Fore.YELLOW + f"    [!] IP is HOSTING")
            except Exception as e:
                print(Fore.RED + f"    [-] API Error: {e}")

            # Final Summary
            print(Fore.CYAN + "\n" + "=" * 60)
            print(Fore.CYAN + "[*] IP ADDRESS CHECK SUMMARY")
            print(Fore.CYAN + "=" * 60)

            status = self.ip_address_info['status']
            if status == 'unlocked':
                print(Fore.GREEN + f"[+] STATUS: UNLOCKED ✓")
                print(Fore.GREEN + f"[+] IP {self.ip} can access the target")
                print(Fore.GREEN + f"[+] HTTP Status: {self.ip_address_info['http_status']}")
                print(Fore.GREEN + f"[+] Response Time: {self.ip_address_info['response_time']} ms")
            elif status == 'blocked':
                print(Fore.RED + f"[!] STATUS: BLOCKED ✗")
                print(Fore.RED + f"[!] IP {self.ip} is blocked by the target")
                print(Fore.RED + f"[!] HTTP Status: {self.ip_address_info['http_status']}")
                if block_found:
                    print(Fore.RED + f"[!] Block Indicators: {', '.join(block_found[:5])}")
            elif status == 'rate_limited':
                print(Fore.YELLOW + f"[!] STATUS: RATE LIMITED ⚠")
                print(Fore.YELLOW + f"[!] IP {self.ip} is rate limited")
            else:
                print(Fore.YELLOW + f"[!] STATUS: {status.upper()}")

            print(Fore.CYAN + "=" * 60 + "\n")

            return self.ip_address_info

        except requests.exceptions.Timeout:
            print(Fore.RED + f"[-] Connection TIMEOUT - IP may be BLOCKED")
            self.ip_address_info['status'] = 'timeout'
            self.ip_blocked = True
            return self.ip_address_info

        except requests.exceptions.ConnectionError:
            print(Fore.RED + f"[-] Connection ERROR - IP may be BLOCKED")
            self.ip_address_info['status'] = 'connection_error'
            self.ip_blocked = True
            return self.ip_address_info

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")
            self.ip_address_info['status'] = 'error'
            return self.ip_address_info

    # ============================================
    # IP ADDRESS ENABLE (UNLOCK)
    # ============================================
    def enable_ip_address(self):
        """Attempt to unlock IP address"""
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] IP ADDRESS ENABLE (UNLOCK)")
        print(Fore.CYAN + "=" * 80)

        print(Fore.YELLOW + f"\n[*] Attempting to unlock IP: {self.ip}")
        print(Fore.YELLOW + f"[*] Target: {self.base_url}")

        self.ip_address_info['actions_taken'] = []

        # Method 1: Clear session
        print(Fore.CYAN + "\n[*] Method 1: Clearing session...")
        self.session.cookies.clear()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        print(Fore.GREEN + "[+] Session cleared")
        self.ip_address_info['actions_taken'].append('Session cleared')

        # Method 2: Rotate User-Agent
        print(Fore.CYAN + "\n[*] Method 2: Rotating User-Agent...")
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
        ]

        for ua in user_agents:
            try:
                self.session.headers['User-Agent'] = ua
                response = self.session.get(self.base_url, timeout=10, verify=False)
                if response.status_code == 200:
                    print(Fore.GREEN + f"[+] Success with UA: {ua[:50]}...")
                    self.ip_address_info['actions_taken'].append(f'User-Agent rotated: {ua[:30]}')
                    self.ip_unlocked = True
                    break
            except Exception:
                pass

        # Method 3: Add spoofed headers
        print(Fore.CYAN + "\n[*] Method 3: Adding spoofed headers...")
        spoofed_headers = {
            'X-Forwarded-For': '127.0.0.1',
            'X-Real-IP': '127.0.0.1',
            'X-Originating-IP': '127.0.0.1',
            'X-Remote-IP': '127.0.0.1',
            'X-Remote-Addr': '127.0.0.1',
            'X-Client-IP': '127.0.0.1',
            'CF-Connecting-IP': '127.0.0.1',
            'True-Client-IP': '127.0.0.1',
        }

        for header, value in spoofed_headers.items():
            self.session.headers[header] = value

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            if response.status_code == 200:
                print(Fore.GREEN + f"[+] Success with spoofed headers")
                self.ip_address_info['actions_taken'].append('Spoofed headers added')
                self.ip_unlocked = True
        except Exception:
            pass

        # Method 4: Try HTTP/2
        print(Fore.CYAN + "\n[*] Method 4: Testing alternative protocols...")
        try:
            # Try HTTPS if HTTP
            if self.protocol == 'http':
                https_url = self.base_url.replace('http://', 'https://')
                response = self.session.get(https_url, timeout=10, verify=False)
                if response.status_code == 200:
                    print(Fore.GREEN + f"[+] HTTPS works: {https_url}")
                    self.ip_address_info['actions_taken'].append('HTTPS protocol')
                    self.ip_unlocked = True
        except Exception:
            pass

        # Method 5: Add delay and retry
        print(Fore.CYAN + "\n[*] Method 5: Adding delay and retry...")
        time.sleep(2)
        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            if response.status_code == 200:
                print(Fore.GREEN + f"[+] Success after delay")
                self.ip_address_info['actions_taken'].append('Delay and retry')
                self.ip_unlocked = True
        except Exception:
            pass

        # Final check
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] IP ADDRESS ENABLE SUMMARY")
        print(Fore.CYAN + "=" * 60)

        if self.ip_unlocked:
            print(Fore.GREEN + f"[+] IP {self.ip} is now UNLOCKED!")
            print(Fore.GREEN + f"[+] Actions taken:")
            for action in self.ip_address_info['actions_taken']:
                print(Fore.GREEN + f"    [+] {action}")
        else:
            print(Fore.RED + f"[-] IP {self.ip} is still BLOCKED")
            print(Fore.RED + f"[-] Try using a proxy or VPN")

        print(Fore.CYAN + "=" * 60 + "\n")

        return self.ip_address_info

    # ============================================
    # HEADER ENUMERATION
    # ============================================
    def enumerate_headers(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] HTTP HEADER ENUMERATION")
        print(Fore.CYAN + "=" * 60)

        try:
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)

            self.headers_info = {
                'status_code': response.status_code,
                'server': response.headers.get('Server', 'Unknown'),
                'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                'content_type': response.headers.get('Content-Type', 'Unknown'),
                'content_length': response.headers.get('Content-Length', 'Unknown'),
                'strict_transport': response.headers.get('Strict-Transport-Security', 'Not Set'),
                'x_frame_options': response.headers.get('X-Frame-Options', 'Not Set'),
                'x_xss_protection': response.headers.get('X-XSS-Protection', 'Not Set'),
                'x_content_type': response.headers.get('X-Content-Type-Options', 'Not Set'),
                'content_security': response.headers.get('Content-Security-Policy', 'Not Set'),
                'referrer_policy': response.headers.get('Referrer-Policy', 'Not Set'),
                'all_headers': dict(response.headers),
            }

            print(Fore.GREEN + f"[+] Status Code: {self.headers_info['status_code']}")
            print(Fore.GREEN + f"[+] Server: {self.headers_info['server']}")
            print(Fore.GREEN + f"[+] Powered By: {self.headers_info['powered_by']}")
            print(Fore.GREEN + f"[+] Content-Type: {self.headers_info['content_type']}")

            print(Fore.CYAN + "\n[*] Security Headers:")
            security_headers = [
                ('Strict-Transport-Security', self.headers_info['strict_transport']),
                ('X-Frame-Options', self.headers_info['x_frame_options']),
                ('X-XSS-Protection', self.headers_info['x_xss_protection']),
                ('X-Content-Type-Options', self.headers_info['x_content_type']),
                ('Content-Security-Policy', self.headers_info['content_security']),
                ('Referrer-Policy', self.headers_info['referrer_policy']),
            ]

            for name, value in security_headers:
                if value != 'Not Set':
                    print(Fore.GREEN + f"    [+] {name}: {value}")
                else:
                    print(Fore.YELLOW + f"    [!] {name}: NOT SET")

            print(Fore.CYAN + "\n[*] All Headers:")
            for header, value in response.headers.items():
                print(Fore.WHITE + f"    {header}: {value}")

        except Exception as e:
            print(Fore.RED + f"[-] Header Enumeration Error: {e}")

        return self.headers_info

    # ============================================
    # SSL CERTIFICATE ANALYSIS
    # ============================================
    def analyze_ssl_certificate(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] SSL CERTIFICATE ANALYSIS")
        print(Fore.CYAN + "=" * 60)

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((self.hostname, 443), timeout=CONFIG['timeout']) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()

                    self.ssl_info = {
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'subject_alt_names': cert.get('subjectAltName', []),
                        'cipher': cipher,
                        'tls_version': version,
                    }

                    print(Fore.GREEN + f"[+] TLS Version: {version}")
                    print(Fore.GREEN + f"[+] Cipher Suite: {cipher[0] if cipher else 'Unknown'}")

                    print(Fore.CYAN + "\n[*] Certificate Subject:")
                    for key, value in self.ssl_info['subject'].items():
                        print(Fore.GREEN + f"    {key}: {value}")

                    print(Fore.CYAN + "\n[*] Certificate Issuer:")
                    for key, value in self.ssl_info['issuer'].items():
                        print(Fore.GREEN + f"    {key}: {value}")

                    print(Fore.CYAN + "\n[*] Validity:")
                    print(Fore.GREEN + f"    Not Before: {self.ssl_info['not_before']}")
                    print(Fore.GREEN + f"    Not After: {self.ssl_info['not_after']}")

                    print(Fore.CYAN + "\n[*] Subject Alternative Names:")
                    for san_type, san_value in self.ssl_info['subject_alt_names']:
                        print(Fore.GREEN + f"    {san_type}: {san_value}")

                    if version in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']:
                        print(Fore.RED + f"[!] WEAK PROTOCOL: {version}")

                    if cipher and cipher[2] < 128:
                        print(Fore.RED + f"[!] WEAK CIPHER: {cipher[0]}")

        except ssl.SSLError as e:
            print(Fore.RED + f"[-] SSL Error: {e}")
        except socket.timeout:
            print(Fore.RED + "[-] Connection timeout")
        except Exception as e:
            print(Fore.RED + f"[-] SSL Analysis Error: {e}")

        return self.ssl_info

    # ============================================
    # WHOIS LOOKUP
    # ============================================
    def whois_lookup(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] WHOIS LOOKUP")
        print(Fore.CYAN + "=" * 60)

        try:
            import whois
            w = whois.whois(self.hostname)
            self.whois_info = {
                'domain_name': str(w.domain_name) if w.domain_name else 'Unknown',
                'registrar': str(w.registrar) if w.registrar else 'Unknown',
                'creation_date': str(w.creation_date) if w.creation_date else 'Unknown',
                'expiration_date': str(w.expiration_date) if w.expiration_date else 'Unknown',
                'name_servers': w.name_servers if w.name_servers else [],
                'org': str(w.org) if w.org else 'Unknown',
                'country': str(w.country) if w.country else 'Unknown',
            }

            print(Fore.GREEN + f"[+] Domain: {self.whois_info['domain_name']}")
            print(Fore.GREEN + f"[+] Registrar: {self.whois_info['registrar']}")
            print(Fore.GREEN + f"[+] Creation: {self.whois_info['creation_date']}")
            print(Fore.GREEN + f"[+] Expiration: {self.whois_info['expiration_date']}")
            print(Fore.GREEN + f"[+] Name Servers: {', '.join(self.whois_info['name_servers']) if self.whois_info['name_servers'] else 'Unknown'}")
            print(Fore.GREEN + f"[+] Organization: {self.whois_info['org']}")
            print(Fore.GREEN + f"[+] Country: {self.whois_info['country']}")

        except ImportError:
            print(Fore.YELLOW + "[!] python-whois not installed.")
        except Exception as e:
            print(Fore.RED + f"[-] WHOIS Error: {e}")

        return self.whois_info

    # ============================================
    # DNS ENUMERATION
    # ============================================
    def dns_enumeration(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] DNS ENUMERATION")
        print(Fore.CYAN + "=" * 60)

        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA']

        try:
            import dns.resolver

            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(self.hostname, record_type)
                    records = [str(rdata) for rdata in answers]
                    self.dns_info[record_type] = records
                    print(Fore.GREEN + f"[+] {record_type} Records:")
                    for record in records:
                        print(Fore.WHITE + f"    {record}")
                except dns.resolver.NoAnswer:
                    pass
                except dns.resolver.NXDOMAIN:
                    print(Fore.RED + f"[-] Domain does not exist")
                    break
                except Exception:
                    pass

        except ImportError:
            print(Fore.YELLOW + "[!] dnspython not installed.")

        return self.dns_info

    # ============================================
    # SUBDOMAIN ENUMERATION
    # ============================================
    def subdomain_enumeration(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] SUBDOMAIN ENUMERATION")
        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + f"[*] Testing {len(COMMON_SUBDOMAINS)} subdomains...")

        found_subdomains = []

        def check_subdomain(subdomain):
            full_domain = f"{subdomain}.{self.hostname}"
            try:
                ip = socket.gethostbyname(full_domain)
                return (subdomain, full_domain, ip)
            except socket.gaierror:
                return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(check_subdomain, sub): sub for sub in COMMON_SUBDOMAINS}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    subdomain, full_domain, ip = result
                    found_subdomains.append({
                        'subdomain': subdomain,
                        'domain': full_domain,
                        'ip': ip
                    })
                    print(Fore.GREEN + f"[+] Found: {full_domain} -> {ip}")

        self.subdomains_found = found_subdomains
        print(Fore.CYAN + f"\n[+] Total: {len(found_subdomains)}")
        return found_subdomains

    # ============================================
    # PORT SCANNING
    # ============================================
    def port_scan(self, ports=None):
        if ports is None:
            ports = self.custom_ports

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] PORT SCANNING")
        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + f"[*] Scanning {len(ports)} ports...")

        open_ports = []

        def check_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.ip, port))
                sock.close()
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except OSError:
                        service = 'unknown'
                    return (port, service)
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=CONFIG['port_scan_th']) as executor:
            futures = {executor.submit(check_port, port): port for port in ports}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    port, service = result
                    open_ports.append({'port': port, 'service': service})
                    print(Fore.GREEN + f"[+] Port {port} OPEN ({service})")

                    if port in [21, 23, 445, 3306, 3389, 5900]:
                        print(Fore.RED + f"[!] DANGEROUS PORT: {port}")

        self.open_ports = open_ports
        print(Fore.CYAN + f"\n[+] Total: {len(open_ports)}")
        return open_ports

    # ============================================
    # DIRECTORY BRUTEFORCE
    # ============================================
    def directory_bruteforce(self, wordlist=None):
        if wordlist is None:
            wordlist = self.wordlist

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] DIRECTORY BRUTEFORCE")
        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + f"[*] Wordlist: {wordlist}")

        if not os.path.exists(wordlist):
            print(Fore.YELLOW + f"[!] Creating wordlist...")
            dir_name = os.path.dirname(wordlist)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(wordlist, 'w') as f:
                f.write('\n'.join(DEFAULT_WORDLIST))
            print(Fore.GREEN + f"[+] Created: {wordlist}")

        try:
            with open(wordlist, 'r') as f:
                words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(Fore.RED + f"[-] Error reading wordlist: {e}")
            return []

        print(Fore.CYAN + f"[*] Testing {len(words)} directories...")

        found_dirs = []

        def check_dir(word):
            url = f"{self.base_url}/{word}"
            try:
                response = self.session.get(url, timeout=10, verify=False, allow_redirects=False)
                if response.status_code in [200, 301, 302, 403]:
                    return (word, url, response.status_code, len(response.content))
            except Exception:
                pass
            return None

        with ThreadPoolExecutor(max_workers=CONFIG['dir_enum_th']) as executor:
            futures = {executor.submit(check_dir, word): word for word in words}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    word, url, status, size = result
                    found_dirs.append({
                        'path': word,
                        'url': url,
                        'status': status,
                        'size': size
                    })

                    status_color = Fore.GREEN if status == 200 else Fore.YELLOW if status in [301, 302] else Fore.RED
                    print(status_color + f"[+] Found: /{word} (Status: {status}, Size: {size})")

                    if any(s in word.lower() for s in ['admin', 'config', 'backup', 'db', 'sql', 'private', 'secret']):
                        print(Fore.RED + f"[!] SENSITIVE: /{word}")

        self.directories_found = found_dirs
        print(Fore.CYAN + f"\n[+] Total: {len(found_dirs)}")
        return found_dirs

    # ============================================
    # ISP INFORMATION
    # ============================================
    def get_isp_info(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] ISP INFORMATION")
        print(Fore.CYAN + "=" * 60)

        try:
            ip_api_url = f"http://ip-api.com/json/{self.ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
            response = requests.get(ip_api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.isp_info = {
                        'ip': data.get('query'),
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'isp': data.get('isp'),
                        'organization': data.get('org'),
                        'asn': data.get('as'),
                        'asn_name': data.get('asname'),
                        'timezone': data.get('timezone'),
                        'is_mobile': data.get('mobile', False),
                        'is_proxy': data.get('proxy', False),
                        'is_hosting': data.get('hosting', False),
                    }

                    print(Fore.GREEN + f"[+] IP: {self.isp_info['ip']}")
                    print(Fore.GREEN + f"[+] Country: {self.isp_info['country']} ({self.isp_info['country_code']})")
                    print(Fore.GREEN + f"[+] Region: {self.isp_info['region']}")
                    print(Fore.GREEN + f"[+] City: {self.isp_info['city']}")
                    print(Fore.GREEN + f"[+] ISP: {self.isp_info['isp']}")
                    print(Fore.GREEN + f"[+] Organization: {self.isp_info['organization']}")
                    print(Fore.GREEN + f"[+] ASN: {self.isp_info['asn_name']} ({self.isp_info['asn']})")
                    print(Fore.GREEN + f"[+] Timezone: {self.isp_info['timezone']}")
                    print(Fore.GREEN + f"[+] Is Proxy: {self.isp_info['is_proxy']}")

        except Exception as e:
            print(Fore.RED + f"[-] ISP Info Error: {e}")

        return self.isp_info

    # ============================================
    # TECHNOLOGY DETECTION
    # ============================================
    def detect_technologies(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] TECHNOLOGY DETECTION")
        print(Fore.CYAN + "=" * 60)

        try:
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)
            headers = response.headers
            html = response.text.lower()

            technologies = []

            header_tech = {
                'Server': 'Web Server',
                'X-Powered-By': 'Framework',
                'X-Generator': 'CMS',
                'CF-Ray': 'Cloudflare',
            }

            for header, tech in header_tech.items():
                if header in headers:
                    technologies.append({
                        'technology': tech,
                        'value': headers[header],
                        'source': f'Header: {header}'
                    })

            html_patterns = {
                'WordPress': [r'wp-content', r'wp-includes'],
                'Joomla': [r'joomla'],
                'Drupal': [r'drupal'],
                'React': [r'react'],
                'Angular': [r'ng-app'],
                'Vue.js': [r'v-model'],
                'jQuery': [r'jquery'],
                'Bootstrap': [r'bootstrap'],
                'Tailwind': [r'tailwind'],
                'Nginx': [r'nginx'],
                'Apache': [r'apache'],
                'PHP': [r'\.php'],
                'Laravel': [r'laravel'],
                'Django': [r'django'],
            }

            for tech, patterns in html_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html):
                        technologies.append({
                            'technology': tech,
                            'value': 'Detected',
                            'source': f'Pattern: {pattern}'
                        })
                        break

            seen = set()
            unique_tech = []
            for tech in technologies:
                key = tech['technology']
                if key not in seen:
                    seen.add(key)
                    unique_tech.append(tech)

            self.technologies = unique_tech

            print(Fore.CYAN + "[*] Technologies:")
            for tech in unique_tech:
                print(Fore.GREEN + f"    [+] {tech['technology']}: {tech['value']}")

            if not unique_tech:
                print(Fore.YELLOW + "    [!] No technologies detected")

        except Exception as e:
            print(Fore.RED + f"[-] Tech Detection Error: {e}")

        return self.technologies

    # ============================================
    # EMAIL HARVESTING
    # ============================================
    def harvest_emails(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] EMAIL HARVESTING")
        print(Fore.CYAN + "=" * 60)

        try:
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)
            html = response.text

            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = list(set(re.findall(email_pattern, html)))

            filtered_emails = [e for e in emails if not any(x in e.lower() for x in ['example.com', 'test.com'])]

            self.emails = filtered_emails

            if filtered_emails:
                print(Fore.GREEN + f"[+] Found {len(filtered_emails)} email(s):")
                for email in filtered_emails:
                    print(Fore.GREEN + f"    {email}")
            else:
                print(Fore.YELLOW + "[!] No emails found")

        except Exception as e:
            print(Fore.RED + f"[-] Email Error: {e}")

        return self.emails

    # ============================================
    # JAVASCRIPT ANALYSIS
    # ============================================
    def analyze_javascript(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] JAVASCRIPT ANALYSIS")
        print(Fore.CYAN + "=" * 60)

        try:
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)
            html = response.text

            js_patterns = [
                r'src=["\']([^"\']*\.js[^"\']*)["\']',
                r'href=["\']([^"\']*\.js[^"\']*)["\']',
            ]

            js_files = set()
            for pattern in js_patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    if match.startswith('//'):
                        js_files.add(f"{self.protocol}:{match}")
                    elif match.startswith('/'):
                        js_files.add(f"{self.base_url}{match}")
                    elif match.startswith('http'):
                        js_files.add(match)
                    else:
                        js_files.add(f"{self.base_url}/{match}")

            self.js_files = list(js_files)

            if js_files:
                print(Fore.GREEN + f"[+] Found {len(js_files)} JS file(s):")
                for js in list(js_files)[:10]:
                    print(Fore.GREEN + f"    {js}")

        except Exception as e:
            print(Fore.RED + f"[-] JS Error: {e}")

        return self.js_files

    # ============================================
    # CORS CHECK
    # ============================================
    def check_cors(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] CORS CHECK")
        print(Fore.CYAN + "=" * 60)

        try:
            test_origin = 'https://evil.com'
            response = self.session.get(self.base_url, headers={'Origin': test_origin},
                                        timeout=CONFIG['timeout'], verify=False)

            acao = response.headers.get('Access-Control-Allow-Origin', 'Not Set')
            acac = response.headers.get('Access-Control-Allow-Credentials', 'Not Set')

            self.cors_info = {'allow_origin': acao, 'allow_credentials': acac}

            print(Fore.GREEN + f"[+] Allow-Origin: {acao}")
            print(Fore.GREEN + f"[+] Allow-Credentials: {acac}")

            if acao == '*' or acao == test_origin:
                print(Fore.RED + "[!] CORS MISCONFIGURATION!")

        except Exception as e:
            print(Fore.RED + f"[-] CORS Error: {e}")

        return self.cors_info

    # ============================================
    # HTTP METHODS
    # ============================================
    def check_http_methods(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] HTTP METHODS CHECK")
        print(Fore.CYAN + "=" * 60)

        methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH', 'TRACE']
        allowed_methods = []

        for method in methods:
            try:
                response = self.session.request(method, self.base_url, timeout=10, verify=False)
                if response.status_code < 400:
                    allowed_methods.append(method)
                    print(Fore.GREEN + f"[+] {method}: Allowed")
                else:
                    print(Fore.YELLOW + f"[!] {method}: Not Allowed")
            except Exception:
                print(Fore.RED + f"[-] {method}: Error")

        self.http_methods = allowed_methods

        for method in ['TRACE', 'CONNECT', 'DELETE', 'PUT']:
            if method in allowed_methods:
                print(Fore.RED + f"[!] DANGEROUS METHOD: {method}")

        return allowed_methods

    # ============================================
    # ROBOTS.TXT
    # ============================================
    def parse_robots_txt(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] ROBOTS.TXT")
        print(Fore.CYAN + "=" * 60)

        try:
            response = self.session.get(f"{self.base_url}/robots.txt",
                                        timeout=CONFIG['timeout'], verify=False)
            if response.status_code == 200:
                print(Fore.GREEN + "[+] robots.txt found!")
                print(Fore.WHITE + response.text[:1000])

                disallowed = re.findall(r'Disallow:\s*(.+)', response.text)
                if disallowed:
                    print(Fore.CYAN + f"\n[*] Disallowed ({len(disallowed)}):")
                    for path in disallowed:
                        print(Fore.YELLOW + f"    {path.strip()}")
            else:
                print(Fore.YELLOW + f"[!] Not found (Status: {response.status_code})")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

    # ============================================
    # WAYBACK MACHINE
    # ============================================
    def get_wayback_urls(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] WAYBACK MACHINE")
        print(Fore.CYAN + "=" * 60)

        try:
            wayback_url = f"http://web.archive.org/cdx/search/cdx?url={self.hostname}/*&output=json&limit=100"
            response = requests.get(wayback_url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    urls = [row[2] for row in data[1:] if len(row) >= 3]
                    self.wayback_urls = list(set(urls))
                    print(Fore.GREEN + f"[+] Found {len(self.wayback_urls)} URL(s):")
                    for url in self.wayback_urls[:20]:
                        print(Fore.GREEN + f"    {url}")
                else:
                    print(Fore.YELLOW + "[!] No archived URLs")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        return self.wayback_urls

    # ============================================
    # WEB CRAWLER
    # ============================================
    def crawl_website(self, max_pages=50, depth=3, strategy='depth-first'):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] WEB CRAWLER")
        print(Fore.CYAN + "=" * 60)
        print(Fore.CYAN + f"[*] Max: {max_pages}, Depth: {depth}")

        visited = set()
        to_visit = deque([(self.base_url, 0)])
        crawled = []

        while to_visit and len(visited) < max_pages:
            if strategy == 'breadth-first':
                url, current_depth = to_visit.popleft()
            else:
                url, current_depth = to_visit.pop()

            if url in visited or current_depth > depth:
                continue

            visited.add(url)

            try:
                response = self.session.get(url, timeout=CONFIG['timeout'], verify=False)
                if response.status_code == 200:
                    crawled.append(url)
                    print(Fore.GREEN + f"[+] Crawled (d{current_depth}): {url}")

                    links = re.findall(r'href=["\']([^"\']+)["\']', response.text)
                    for link in links:
                        if link.startswith('http') and self.hostname in link:
                            if link not in visited:
                                to_visit.append((link, current_depth + 1))
                        elif link.startswith('/'):
                            full_url = f"{self.base_url}{link}"
                            if full_url not in visited:
                                to_visit.append((full_url, current_depth + 1))
            except Exception:
                pass

        self.crawled_urls = crawled
        print(Fore.CYAN + f"\n[+] Total: {len(crawled)}")
        return crawled

    # ============================================
    # API KEY DETECTION
    # ============================================
    def detect_api_keys(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] API KEY DETECTION")
        print(Fore.CYAN + "=" * 80)

        self.api_keys_found = []
        urls_to_scan = [self.base_url]

        if self.crawled_urls:
            urls_to_scan.extend(self.crawled_urls[:30])
        if self.js_files:
            urls_to_scan.extend(self.js_files[:20])

        common_files = [
            '/.env', '/.env.local', '/.env.production', '/config.json',
            '/config.js', '/app.js', '/main.js', '/bundle.js',
            '/package.json', '/composer.json', '/settings.py',
            '/.git/config', '/web.config', '/.htaccess',
        ]
        for cf in common_files:
            urls_to_scan.append(f"{self.base_url}{cf}")

        urls_to_scan = list(set(urls_to_scan))
        print(Fore.CYAN + f"\n[*] Scanning {len(urls_to_scan)} URLs for API keys...")

        for url in urls_to_scan:
            try:
                response = self.session.get(url, timeout=10, verify=False)
                if response.status_code == 200:
                    content = response.text

                    for key_type, pattern in API_KEY_PATTERNS.items():
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else str(match)

                            if len(str(match)) > 8:
                                key_info = {
                                    'type': key_type,
                                    'value': str(match)[:100],
                                    'url': url,
                                }
                                self.api_keys_found.append(key_info)
                                print(Fore.RED + f"[!] API KEY FOUND: {key_type}")
                                print(Fore.RED + f"    URL: {url}")
                                print(Fore.RED + f"    Value: {str(match)[:50]}...")

            except Exception:
                pass

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] API KEY DETECTION SUMMARY")
        print(Fore.CYAN + "=" * 60)
        print(Fore.RED + f"[+] API Keys Found: {len(self.api_keys_found)}")

        if self.api_keys_found:
            print(Fore.RED + "\n[!] FOUND API KEYS:")
            for key in self.api_keys_found:
                print(Fore.RED + f"    [{key['type']}] {key['value'][:50]}... at {key['url']}")

        print(Fore.CYAN + "=" * 60 + "\n")
        return self.api_keys_found

    # ============================================
    # WEB SERVER API KEY DETECTION
    # ============================================
    def detect_web_server_api_keys(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] WEB SERVER API KEY DETECTION")
        print(Fore.CYAN + "=" * 80)

        self.web_server_api_keys_found = []

        urls_to_scan = [
            f"{self.base_url}/.env",
            f"{self.base_url}/.env.local",
            f"{self.base_url}/.env.production",
            f"{self.base_url}/config.json",
            f"{self.base_url}/config.php",
            f"{self.base_url}/config.js",
            f"{self.base_url}/web.config",
            f"{self.base_url}/app.config",
            f"{self.base_url}/settings.py",
            f"{self.base_url}/settings.php",
            f"{self.base_url}/application.properties",
            f"{self.base_url}/application.yml",
            f"{self.base_url}/.htaccess",
            f"{self.base_url}/nginx.conf",
            f"{self.base_url}/apache.conf",
            f"{self.base_url}/docker-compose.yml",
            f"{self.base_url}/Dockerfile",
            f"{self.base_url}/.git/config",
            f"{self.base_url}/.gitlab-ci.yml",
            f"{self.base_url}/.travis.yml",
            f"{self.base_url}/Jenkinsfile",
            f"{self.base_url}/package.json",
            f"{self.base_url}/composer.json",
            f"{self.base_url}/requirements.txt",
            f"{self.base_url}/pom.xml",
        ]

        urls_to_scan = list(set(urls_to_scan))
        print(Fore.CYAN + f"\n[*] Scanning {len(urls_to_scan)} web server files...")

        for url in urls_to_scan:
            try:
                response = self.session.get(url, timeout=10, verify=False)
                if response.status_code == 200:
                    content = response.text

                    for key_type, pattern in WEB_SERVER_API_KEY_PATTERNS.items():
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0]

                            if len(str(match)) > 8:
                                key_info = {
                                    'type': key_type,
                                    'value': str(match)[:100],
                                    'url': url,
                                }
                                self.web_server_api_keys_found.append(key_info)
                                print(Fore.RED + f"[!] WEB SERVER API KEY: {key_type}")
                                print(Fore.RED + f"    URL: {url}")
                                print(Fore.RED + f"    Value: {str(match)[:50]}...")

                    for key_type, pattern in API_KEY_PATTERNS.items():
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            if isinstance(match, tuple):
                                match = match[0]

                            if len(str(match)) > 8:
                                existing = [k for k in self.web_server_api_keys_found
                                            if k['value'] == str(match)[:100] and k['url'] == url]
                                if not existing:
                                    key_info = {
                                        'type': f"Web Server: {key_type}",
                                        'value': str(match)[:100],
                                        'url': url,
                                    }
                                    self.web_server_api_keys_found.append(key_info)
                                    print(Fore.RED + f"[!] WEB SERVER {key_type}")
                                    print(Fore.RED + f"    URL: {url}")

            except Exception:
                pass

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] WEB SERVER API KEY SUMMARY")
        print(Fore.CYAN + "=" * 60)
        print(Fore.RED + f"[+] Web Server API Keys Found: {len(self.web_server_api_keys_found)}")

        if self.web_server_api_keys_found:
            print(Fore.RED + "\n[!] FOUND WEB SERVER API KEYS:")
            for key in self.web_server_api_keys_found:
                print(Fore.RED + f"    [{key['type']}] {key['value'][:50]}... at {key['url']}")

        print(Fore.CYAN + "=" * 60 + "\n")
        return self.web_server_api_keys_found

    # ============================================
    # SSL KEY UNLOCK
    # ============================================
    def ssl_key_unlock_scan(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] SSL KEY UNLOCK - HTTPS BYPASS")
        print(Fore.CYAN + "=" * 80)

        self.ssl_unlock_info = {
            'target': self.hostname,
            'ssl_enabled': False,
            'tls_versions': [],
            'bypass_methods': [],
        }

        print(Fore.CYAN + "\n[*] Step 1: Checking SSL/TLS...")
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((self.hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    self.ssl_unlock_info['ssl_enabled'] = True
                    cipher = ssock.cipher()
                    version = ssock.version()

                    self.ssl_unlock_info['tls_versions'].append(version)
                    print(Fore.GREEN + f"[+] SSL Enabled: True")
                    print(Fore.GREEN + f"[+] TLS Version: {version}")
                    print(Fore.GREEN + f"[+] Cipher: {cipher[0] if cipher else 'Unknown'}")
        except Exception as e:
            print(Fore.RED + f"[-] SSL Check Error: {e}")

        print(Fore.CYAN + "\n[*] Step 2: Testing TLS Versions...")
        tls_versions = [
            ('TLSv1.0', ssl.TLSVersion.TLSv1),
            ('TLSv1.1', ssl.TLSVersion.TLSv1_1),
            ('TLSv1.2', ssl.TLSVersion.TLSv1_2),
            ('TLSv1.3', ssl.TLSVersion.TLSv1_3),
        ]

        for name, version in tls_versions:
            try:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.minimum_version = version
                context.maximum_version = version

                with socket.create_connection((self.hostname, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                        print(Fore.GREEN + f"[+] {name}: SUPPORTED")
                        if name not in self.ssl_unlock_info['tls_versions']:
                            self.ssl_unlock_info['tls_versions'].append(name)
            except Exception:
                print(Fore.YELLOW + f"[!] {name}: NOT SUPPORTED")

        print(Fore.CYAN + "\n[*] Step 3: Attempting SSL Bypass...")

        print(Fore.YELLOW + "[*] Method 1: Disable SSL Verification...")
        try:
            response = requests.get(self.base_url, verify=False, timeout=10)
            print(Fore.GREEN + f"[+] Status: {response.status_code}")
            self.ssl_unlock_info['bypass_methods'].append("Disabled SSL Verification")
            self.unlocked_ssl.append("Disabled SSL Verification")
        except Exception as e:
            print(Fore.RED + f"[-] Failed: {e}")

        print(Fore.YELLOW + "[*] Method 2: Custom SSL Context...")
        try:
            http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
            response = http.request('GET', self.base_url)
            print(Fore.GREEN + f"[+] Status: {response.status}")
            self.ssl_unlock_info['bypass_methods'].append("Custom SSL Context")
            self.unlocked_ssl.append("Custom SSL Context")
        except Exception as e:
            print(Fore.RED + f"[-] Failed: {e}")

        print(Fore.YELLOW + "[*] Method 3: SNI Manipulation...")
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((self.hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname='example.com') as ssock:
                    print(Fore.GREEN + f"[+] Connected")
                    self.ssl_unlock_info['bypass_methods'].append("SNI Manipulation")
                    self.unlocked_ssl.append("SNI Manipulation")
        except Exception as e:
            print(Fore.RED + f"[-] Failed: {e}")

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] SSL KEY UNLOCK SUMMARY")
        print(Fore.CYAN + "=" * 60)

        if self.unlocked_ssl:
            self.ssl_unlock_info['unlock_status'] = 'unlocked'
            print(Fore.GREEN + f"[+] SSL UNLOCKED!")
            print(Fore.GREEN + f"[+] Methods: {len(self.unlocked_ssl)}")
            for method in self.unlocked_ssl:
                print(Fore.GREEN + f"    [+] {method}")
        else:
            print(Fore.RED + f"[-] SSL LOCKED")

        print(Fore.CYAN + "=" * 60 + "\n")
        return self.ssl_unlock_info

    # ============================================
    # BROWSER APP ANALYSIS
    # ============================================
    def browser_app_analysis_scan(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] BROWSER APP ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        self.browser_app_analysis_data = {
            'files_found': [],
            'frameworks': [],
            'build_tools': [],
            'state_management': [],
            'routing': [],
            'ui_libraries': [],
            'analytics': [],
            'auth': [],
            'api_clients': [],
            'pwa': {},
            'service_worker': {},
        }

        print(Fore.CYAN + "\n[*] Checking Browser App Files...")
        self.check_browser_app_files()

        print(Fore.CYAN + "\n[*] Analyzing Frameworks...")
        self.analyze_browser_frameworks()

        print(Fore.CYAN + "\n[*] Checking PWA...")
        self.check_pwa()

        print(Fore.CYAN + "\n[*] Checking Service Worker...")
        self.check_service_worker()

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] BROWSER APP SUMMARY")
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + f"[+] Files: {len(self.browser_app_analysis_data['files_found'])}")
        print(Fore.GREEN + f"[+] Frameworks: {len(self.browser_app_analysis_data['frameworks'])}")
        print(Fore.GREEN + f"[+] Build Tools: {len(self.browser_app_analysis_data['build_tools'])}")
        print(Fore.CYAN + "=" * 60 + "\n")

        return self.browser_app_analysis_data

    def check_browser_app_files(self):
        print(Fore.CYAN + "[*] Checking browser app files...")
        found_files = []

        for filename in BROWSER_APP_FILES:
            url = f"{self.base_url}/{filename}"
            try:
                response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)
                if response.status_code == 200:
                    file_type = 'unknown'
                    if filename.endswith('.js'):
                        file_type = 'javascript'
                    elif filename.endswith('.css'):
                        file_type = 'css'
                    elif filename.endswith('.json'):
                        file_type = 'json'
                    elif filename.endswith('.html'):
                        file_type = 'html'
                    elif filename.endswith('.map'):
                        file_type = 'source_map'
                    elif 'worker' in filename:
                        file_type = 'service_worker'
                    elif 'manifest' in filename:
                        file_type = 'manifest'
                    elif 'config' in filename or '.env' in filename:
                        file_type = 'config'

                    found_files.append({
                        'path': filename,
                        'url': url,
                        'status': response.status_code,
                        'size': len(response.content),
                        'type': file_type,
                    })
                    print(Fore.GREEN + f"[+] Found: {url} ({file_type})")
                    self.browser_app_files.append(url)

                    if file_type in ['config', 'source_map']:
                        print(Fore.RED + f"[!] SENSITIVE: {url}")
            except Exception:
                pass

        self.browser_app_analysis_data['files_found'] = found_files
        print(Fore.CYAN + f"[*] Total: {len(found_files)}")

    def analyze_browser_frameworks(self):
        print(Fore.CYAN + "[*] Analyzing frameworks...")
        try:
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)
            all_js = response.text

            for js_url in self.js_files[:20]:
                try:
                    js_response = self.session.get(js_url, timeout=5, verify=False)
                    all_js += js_response.text
                except Exception:
                    pass

            for category, patterns in BROWSER_APP_PATTERNS.items():
                for tech, tech_patterns in patterns.items():
                    for pattern in tech_patterns:
                        if re.search(pattern, all_js, re.IGNORECASE):
                            if category == 'frameworks':
                                self.browser_frameworks.append(tech)
                                self.browser_app_analysis_data['frameworks'].append(tech)
                                print(Fore.GREEN + f"[+] Framework: {tech}")
                            elif category == 'build_tools':
                                self.browser_build_tools.append(tech)
                                self.browser_app_analysis_data['build_tools'].append(tech)
                                print(Fore.GREEN + f"[+] Build Tool: {tech}")
                            elif category == 'state_management':
                                self.browser_app_analysis_data['state_management'].append(tech)
                                print(Fore.GREEN + f"[+] State: {tech}")
                            elif category == 'routing':
                                self.browser_app_analysis_data['routing'].append(tech)
                                print(Fore.GREEN + f"[+] Routing: {tech}")
                            elif category == 'ui_libraries':
                                self.browser_app_analysis_data['ui_libraries'].append(tech)
                                print(Fore.GREEN + f"[+] UI: {tech}")
                            elif category == 'analytics':
                                self.browser_app_analysis_data['analytics'].append(tech)
                                print(Fore.GREEN + f"[+] Analytics: {tech}")
                            elif category == 'auth':
                                self.browser_app_analysis_data['auth'].append(tech)
                                print(Fore.GREEN + f"[+] Auth: {tech}")
                            elif category == 'api_clients':
                                self.browser_app_analysis_data['api_clients'].append(tech)
                                print(Fore.GREEN + f"[+] API Client: {tech}")
                            break
        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

    def check_pwa(self):
        print(Fore.CYAN + "[*] Checking PWA...")
        pwa_info = {'manifest_found': False, 'manifest_url': None}

        for manifest_url in ['/manifest.json', '/manifest.webmanifest', '/static/manifest.json']:
            url = f"{self.base_url}{manifest_url}"
            try:
                response = self.session.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    pwa_info['manifest_found'] = True
                    pwa_info['manifest_url'] = url
                    print(Fore.GREEN + f"[+] PWA Manifest: {url}")
                    self.pwa_analysis = pwa_info
                    break
            except Exception:
                pass

        if not pwa_info['manifest_found']:
            print(Fore.YELLOW + "[!] No PWA manifest")
        return pwa_info

    def check_service_worker(self):
        print(Fore.CYAN + "[*] Checking Service Worker...")
        sw_info = {'found': False, 'url': None}

        for sw_url in ['/service-worker.js', '/sw.js', '/serviceworker.js', '/worker.js']:
            url = f"{self.base_url}{sw_url}"
            try:
                response = self.session.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    sw_info['found'] = True
                    sw_info['url'] = url
                    print(Fore.GREEN + f"[+] Service Worker: {url}")
                    self.service_worker_analysis = sw_info
                    break
            except Exception:
                pass

        if not sw_info['found']:
            print(Fore.YELLOW + "[!] No Service Worker")
        return sw_info

    # ============================================
    # SOURCE CODE ANALYSIS
    # ============================================
    def source_code_analysis_scan(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] SOURCE CODE ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        self.source_code_analysis_data = {
            'comments': [],
            'hidden_fields': [],
            'inline_scripts': [],
            'meta_tags': [],
            'source_maps': [],
            'backup_files': [],
            'config_files': [],
            'git_exposure': [],
            'svn_exposure': [],
        }

        self.analyze_html_source()
        self.check_backup_files()
        self.check_config_files()
        self.check_git_exposure()
        self.check_svn_exposure()

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] SOURCE CODE SUMMARY")
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + f"[+] Comments: {len(self.comments_found)}")
        print(Fore.GREEN + f"[+] Hidden Fields: {len(self.hidden_fields)}")
        print(Fore.GREEN + f"[+] Inline Scripts: {len(self.inline_scripts)}")
        print(Fore.GREEN + f"[+] Meta Tags: {len(self.meta_tags)}")
        print(Fore.GREEN + f"[+] Backup Files: {len(self.backup_files)}")
        print(Fore.GREEN + f"[+] Config Files: {len(self.config_files)}")
        print(Fore.CYAN + "=" * 60 + "\n")

        return self.source_code_analysis_data

    def analyze_html_source(self):
        print(Fore.CYAN + "\n[*] Analyzing HTML Source...")
        try:
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)
            html = response.text

            comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
            for comment in comments:
                comment = comment.strip()
                if comment and len(comment) > 3:
                    self.comments_found.append({
                        'type': 'HTML',
                        'content': comment[:200],
                        'url': self.base_url
                    })
                    print(Fore.YELLOW + f"[!] Comment: {comment[:100]}")

            hidden = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', html, re.IGNORECASE)
            for h in hidden:
                name_match = re.search(r'name=["\']([^"\']+)["\']', h)
                value_match = re.search(r'value=["\']([^"\']*)["\']', h)
                field = {
                    'name': name_match.group(1) if name_match else 'unknown',
                    'value': value_match.group(1) if value_match else '',
                }
                self.hidden_fields.append(field)
                print(Fore.YELLOW + f"[!] Hidden: {field['name']}")

            scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
            for i, script in enumerate(scripts):
                script = script.strip()
                if script and len(script) > 10:
                    self.inline_scripts.append({
                        'index': i,
                        'content': script[:500],
                        'length': len(script),
                    })
                    print(Fore.YELLOW + f"[!] Inline Script #{i}: {len(script)} bytes")

            meta = re.findall(r'<meta[^>]*>', html, re.IGNORECASE)
            for m in meta:
                name_match = re.search(r'name=["\']([^"\']+)["\']', m)
                content_match = re.search(r'content=["\']([^"\']*)["\']', m)
                tag = {
                    'name': name_match.group(1) if name_match else 'unknown',
                    'content': content_match.group(1) if content_match else '',
                }
                self.meta_tags.append(tag)

            if meta:
                print(Fore.GREEN + f"[+] Found {len(meta)} meta tags")

        except Exception as e:
            print(Fore.RED + f"[-] HTML Source Error: {e}")

    def check_backup_files(self):
        print(Fore.CYAN + "\n[*] Checking Backup Files...")
        backup_extensions = ['.bak', '.backup', '.old', '.orig', '.save', '.swp', '.tmp']
        common_files = ['index', 'config', 'settings', 'database', 'db', 'admin', 'login', 'backup']

        for base in common_files:
            for ext in backup_extensions:
                url = f"{self.base_url}/{base}{ext}"
                try:
                    response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)
                    if response.status_code == 200:
                        self.backup_files.append({
                            'url': url,
                            'status': response.status_code,
                            'size': len(response.content)
                        })
                        print(Fore.RED + f"[!] Backup File: {url}")
                except Exception:
                    pass

    def check_config_files(self):
        print(Fore.CYAN + "\n[*] Checking Config Files...")
        config_files = [
            '/.env', '/.env.local', '/config.php', '/config.js', '/config.json',
            '/wp-config.php', '/database.php', '/db.php', '/credentials.json',
            '/web.config', '/application.properties', '/settings.py', '/package.json',
        ]

        for path in config_files:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)
                if response.status_code == 200:
                    self.config_files.append({
                        'url': url,
                        'status': response.status_code,
                        'size': len(response.content),
                    })
                    print(Fore.RED + f"[!] Config File: {url}")
            except Exception:
                pass

    def check_git_exposure(self):
        print(Fore.CYAN + "\n[*] Checking Git Exposure...")
        for path in ['/.git/HEAD', '/.git/config', '/.git/index', '/.gitignore']:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)
                if response.status_code == 200:
                    self.git_exposure.append({'url': url, 'status': response.status_code})
                    print(Fore.RED + f"[!] Git Exposure: {url}")
            except Exception:
                pass

    def check_svn_exposure(self):
        print(Fore.CYAN + "\n[*] Checking SVN Exposure...")
        for path in ['/.svn/entries', '/.svn/wc.db', '/.svn/format']:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False, allow_redirects=False)
                if response.status_code == 200:
                    self.svn_exposure.append({'url': url, 'status': response.status_code})
                    print(Fore.RED + f"[!] SVN Exposure: {url}")
            except Exception:
                pass

    # ============================================
    # INDEX.HTML ANALYSIS
    # ============================================
    def analyze_index_html(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] INDEX.HTML ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        index_paths = ['/index.html', '/index.htm', '/index.php', '/index.asp', '/index.jsp']

        found_index = None

        for path in index_paths:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=CONFIG['timeout'], verify=False)
                if response.status_code == 200:
                    found_index = {
                        'url': url,
                        'status': response.status_code,
                        'size': len(response.content),
                        'content': response.text[:5000],
                    }
                    print(Fore.GREEN + f"[+] Found: {url}")
                    print(Fore.GREEN + f"    Status: {response.status_code}")
                    print(Fore.GREEN + f"    Size: {len(response.content)} bytes")
                    break
            except Exception:
                pass

        if not found_index:
            print(Fore.YELLOW + "[!] No index file found")
            return {}

        html = found_index['content']

        analysis = {
            'url': found_index['url'],
            'status': found_index['status'],
            'size': found_index['size'],
            'title': None,
            'meta_tags': [],
            'scripts': [],
            'styles': [],
            'forms': [],
            'inputs': [],
            'links': [],
            'images': [],
            'iframes': [],
            'comments': [],
            'inline_scripts': [],
            'hidden_fields': [],
        }

        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            analysis['title'] = title_match.group(1).strip()
            print(Fore.GREEN + f"[+] Title: {analysis['title']}")

        analysis['meta_tags'] = re.findall(r'<meta[^>]*>', html, re.IGNORECASE)
        print(Fore.GREEN + f"[+] Meta Tags: {len(analysis['meta_tags'])}")

        analysis['scripts'] = re.findall(r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
        print(Fore.GREEN + f"[+] Scripts: {len(analysis['scripts'])}")

        analysis['styles'] = re.findall(r'<link[^>]*href=["\']([^"\']*\.css[^"\']*)["\'][^>]*>', html, re.IGNORECASE)
        print(Fore.GREEN + f"[+] Styles: {len(analysis['styles'])}")

        analysis['forms'] = re.findall(r'<form[^>]*>', html, re.IGNORECASE)
        print(Fore.GREEN + f"[+] Forms: {len(analysis['forms'])}")

        analysis['inputs'] = re.findall(r'<input[^>]*>', html, re.IGNORECASE)
        print(Fore.GREEN + f"[+] Inputs: {len(analysis['inputs'])}")

        analysis['hidden_fields'] = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', html, re.IGNORECASE)
        if analysis['hidden_fields']:
            print(Fore.YELLOW + f"[!] Hidden Fields: {len(analysis['hidden_fields'])}")

        analysis['links'] = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        print(Fore.GREEN + f"[+] Links: {len(analysis['links'])}")

        analysis['images'] = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
        print(Fore.GREEN + f"[+] Images: {len(analysis['images'])}")

        analysis['iframes'] = re.findall(r'<iframe[^>]*>', html, re.IGNORECASE)
        if analysis['iframes']:
            print(Fore.YELLOW + f"[!] Iframes: {len(analysis['iframes'])}")

        analysis['comments'] = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
        if analysis['comments']:
            print(Fore.YELLOW + f"[!] Comments: {len(analysis['comments'])}")

        analysis['inline_scripts'] = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        analysis['inline_scripts'] = [s for s in analysis['inline_scripts'] if s.strip() and len(s.strip()) > 10]

        self.index_html_analysis = analysis
        print(Fore.CYAN + "=" * 60 + "\n")
        return analysis

    # ============================================
    # HTML FILES ANALYSIS
    # ============================================
    def analyze_html_files(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] HTML FILES ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        html_paths = [
            '/index.html', '/about.html', '/contact.html', '/login.html',
            '/register.html', '/admin.html', '/dashboard.html', '/profile.html',
            '/settings.html', '/help.html', '/404.html', '/500.html',
        ]

        found_html = []

        for path in html_paths:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    html = response.text

                    html_data = {
                        'url': url,
                        'status': response.status_code,
                        'size': len(response.content),
                        'title': None,
                        'comments': len(re.findall(r'<!--(.*?)-->', html, re.DOTALL)),
                        'forms': len(re.findall(r'<form[^>]*>', html, re.IGNORECASE)),
                        'inputs': len(re.findall(r'<input[^>]*>', html, re.IGNORECASE)),
                        'scripts': len(re.findall(r'<script[^>]*>', html, re.IGNORECASE)),
                        'links': len(re.findall(r'<a[^>]+href=', html, re.IGNORECASE)),
                    }

                    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
                    if title_match:
                        html_data['title'] = title_match.group(1).strip()

                    found_html.append(html_data)

                    print(Fore.GREEN + f"[+] {url}")
                    print(Fore.GREEN + f"    Title: {html_data['title']}")
                    print(Fore.GREEN + f"    Size: {html_data['size']}")
                    print(Fore.GREEN + f"    Forms: {html_data['forms']}, Inputs: {html_data['inputs']}")
            except Exception:
                pass

        self.html_files_analysis = {'files': found_html, 'total': len(found_html)}
        print(Fore.CYAN + f"\n[+] Total: {len(found_html)}")
        print(Fore.CYAN + "=" * 60 + "\n")
        return self.html_files_analysis

    # ============================================
    # JAVA FILES ANALYSIS
    # ============================================
    def analyze_java_files(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] JAVA SOURCE CODE ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        java_paths = [
            '/src/main/java/Application.java', '/src/main/java/Main.java',
            '/WEB-INF/classes/Application.class', '/api/java/Application.java',
            '/Application.java', '/Main.java', '/Servlet.java', '/Controller.java',
        ]

        found_java = []

        for path in java_paths:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    content = response.text

                    java_data = {
                        'url': url,
                        'status': response.status_code,
                        'size': len(content),
                        'package': None,
                        'imports': [],
                        'classes': [],
                        'methods': [],
                        'sensitive': [],
                        'jdbc': [],
                        'servlet': [],
                        'spring': [],
                        'hibernate': [],
                        'comments': [],
                    }

                    pkg_match = re.search(r'package\s+([\w.]+);', content)
                    if pkg_match:
                        java_data['package'] = pkg_match.group(1)

                    java_data['imports'] = re.findall(r'import\s+([\w.]+);', content)
                    java_data['classes'] = re.findall(r'(?:public|private|protected)?\s*class\s+(\w+)', content)
                    java_data['methods'] = re.findall(r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(', content)
                    java_data['comments'] = re.findall(r'//(.+)|/\*(.*?)\*/', content, re.DOTALL)
                    java_data['sensitive'] = re.findall(r'(?:String|char\[\])\s+\w*(?:password|secret|key|token)\w*\s*=\s*"([^"]+)"', content, re.IGNORECASE)
                    java_data['jdbc'] = re.findall(r'jdbc:[\w:]+', content)
                    java_data['servlet'] = re.findall(r'(HttpServlet|doGet|doPost)', content)
                    java_data['spring'] = re.findall(r'@(Controller|Service|Repository|Autowired|RequestMapping)', content)
                    java_data['hibernate'] = re.findall(r'@(Entity|Table|Column|Id)', content)

                    found_java.append(java_data)

                    print(Fore.GREEN + f"[+] Found: {url}")
                    if java_data['package']:
                        print(Fore.GREEN + f"    Package: {java_data['package']}")
                    if java_data['classes']:
                        print(Fore.GREEN + f"    Classes: {', '.join(java_data['classes'][:5])}")
                    if java_data['sensitive']:
                        print(Fore.RED + f"    [!] Sensitive: {len(java_data['sensitive'])}")
            except Exception:
                pass

        self.java_files_analysis = {'files': found_java, 'total': len(found_java)}
        print(Fore.CYAN + f"\n[+] Total: {len(found_java)}")
        print(Fore.CYAN + "=" * 60 + "\n")
        return self.java_files_analysis

    # ============================================
    # PHP FILES ANALYSIS
    # ============================================
    def analyze_php_files(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] PHP SOURCE CODE ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        php_paths = ['/index.php', '/config.php', '/admin.php', '/login.php',
                     '/register.php', '/api.php', '/db.php', '/functions.php']

        found_php = []
        for path in php_paths:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    content = response.text
                    php_data = {
                        'url': url,
                        'status': response.status_code,
                        'size': len(content),
                        'functions': re.findall(r'function\s+(\w+)', content),
                        'classes': re.findall(r'class\s+(\w+)', content),
                        'sensitive': re.findall(r'\$(\w*(?:password|secret|token|apikey)\w*)\s*=', content, re.IGNORECASE),
                        'system_calls': re.findall(r'(system|exec|shell_exec|passthru|popen)\s*\(', content),
                    }
                    found_php.append(php_data)
                    print(Fore.GREEN + f"[+] Found: {url}")
                    if php_data['sensitive']:
                        print(Fore.RED + f"    [!] Sensitive: {len(php_data['sensitive'])}")
            except Exception:
                pass

        self.php_files_analysis = {'files': found_php, 'total': len(found_php)}
        print(Fore.CYAN + f"\n[+] Total: {len(found_php)}")
        return self.php_files_analysis

    # ============================================
    # PYTHON FILES ANALYSIS
    # ============================================
    def analyze_python_files(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] PYTHON SOURCE CODE ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        python_paths = ['/app.py', '/main.py', '/server.py', '/run.py', '/wsgi.py',
                        '/manage.py', '/settings.py', '/urls.py', '/views.py', '/models.py']

        found_python = []
        for path in python_paths:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    content = response.text
                    py_data = {
                        'url': url,
                        'status': response.status_code,
                        'size': len(content),
                        'imports': re.findall(r'(?:from\s+[\w.]+\s+)?import\s+([\w., ]+)', content),
                        'functions': re.findall(r'def\s+(\w+)\s*\(', content),
                        'classes': re.findall(r'class\s+(\w+)', content),
                        'sensitive': re.findall(r'(\w*(?:password|secret|token|key)\w*)\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE),
                    }
                    found_python.append(py_data)
                    print(Fore.GREEN + f"[+] Found: {url}")
                    if py_data['sensitive']:
                        print(Fore.RED + f"    [!] Sensitive: {len(py_data['sensitive'])}")
            except Exception:
                pass

        self.python_files_analysis = {'files': found_python, 'total': len(found_python)}
        print(Fore.CYAN + f"\n[+] Total: {len(found_python)}")
        return self.python_files_analysis

    # ============================================
    # ENV FILES ANALYSIS
    # ============================================
    def analyze_env_files(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] ENV FILES ANALYSIS")
        print(Fore.CYAN + "=" * 80)

        env_paths = ['/.env', '/.env.local', '/.env.production', '/.env.development',
                     '/.env.staging', '/.env.test', '/.env.backup', '/.env.example']

        found_env = []
        for path in env_paths:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    content = response.text
                    env_data = {
                        'url': url,
                        'status': response.status_code,
                        'size': len(content),
                        'variables': [],
                        'sensitive': [],
                    }
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            env_data['variables'].append({'key': key, 'value': value[:50]})

                            sensitive_keys = ['PASSWORD', 'SECRET', 'TOKEN', 'KEY', 'API', 'PWD']
                            if any(s in key.upper() for s in sensitive_keys):
                                env_data['sensitive'].append({'key': key, 'value': value[:20] + '...'})

                    found_env.append(env_data)
                    print(Fore.GREEN + f"[+] Found: {url}")
                    if env_data['sensitive']:
                        print(Fore.RED + f"    [!] SENSITIVE DATA!")
                        for s in env_data['sensitive'][:5]:
                            print(Fore.RED + f"        {s['key']} = {s['value']}")
            except Exception:
                pass

        self.env_files_analysis = {'files': found_env, 'total': len(found_env)}
        print(Fore.CYAN + f"\n[+] Total: {len(found_env)}")
        return self.env_files_analysis

    # ============================================
    # FIREWALL & VULNERABILITY
    # ============================================
    def detect_firewall(self, response=None):
        firewalls = []
        if response and hasattr(response, 'headers'):
            patterns = ['cloudflare', 'aws waf', 'azure', 'mod_security', 'sucuri',
                        'wordfence', 'nginx', 'apache', 'varnish', 'squid', 'haproxy']

            for header, value in response.headers.items():
                header_lower = header.lower()
                value_lower = str(value).lower()

                for pattern in patterns:
                    if pattern.lower() in header_lower or pattern.lower() in value_lower:
                        if pattern not in firewalls:
                            firewalls.append(pattern)
                            print(Fore.RED + f"[!] Firewall: {pattern}")
                            self.firewalls_detected.append({'type': pattern, 'header': header, 'value': value})
        return firewalls

    def vulnerability_scan(self):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] VULNERABILITY SCANNING")
        print(Fore.CYAN + "=" * 60)

        tests = [
            ('/robots.txt', "Robots.txt exposure"),
            ('/.git/HEAD', "Git repository exposure"),
            ('/.env', "Environment file exposure"),
            ('/phpinfo.php', "PHP info exposure"),
            ('/phpmyadmin/', "phpMyAdmin exposure"),
            ('/wp-admin/', "WordPress admin exposure"),
            ('/admin/', "Admin panel exposure"),
        ]

        for path, description in tests:
            try:
                test_url = self.base_url + path
                response = self.session.get(test_url, timeout=CONFIG['timeout'], verify=False)
                if response.status_code in [200, 301, 302, 403]:
                    self.vulnerabilities_found.append({
                        'url': test_url,
                        'description': description,
                        'status': response.status_code
                    })
                    print(Fore.RED + f"[!] Vulnerability: {description}")
                    print(Fore.RED + f"    URL: {test_url}")
            except Exception:
                pass

        print(Fore.CYAN + f"\n[+] Total: {len(self.vulnerabilities_found)}")

    # ============================================
    # START AUTONOMOUS MODE
    # ============================================
    def start_autonomous_mode(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "🤖 AUTONOMOUS AI ROBOT MODE ACTIVATED!")
        print(Fore.RED + "=" * 80 + "\n")

        # Initial scan
        try:
            response = self.session.get(self.base_url, timeout=CONFIG['timeout'], verify=False)
            print(Fore.GREEN + f"[+] Target reachable! Status: {response.status_code}")
            self.detect_firewall(response)
        except Exception as e:
            print(Fore.RED + f"[-] Target unreachable: {e}")

        # NEW: IP Address Check
        if hasattr(self.args, 'ip_address') and self.args.ip_address:
            self.check_ip_address()

        # NEW: IP Address Enable (Unlock)
        if hasattr(self.args, 'ip_address_enable') and self.args.ip_address_enable:
            self.enable_ip_address()

        # ISP info
        if self.isp_info_enabled:
            self.get_isp_info()

        # API Key Detection
        if hasattr(self.args, 'api_key') and self.args.api_key:
            self.detect_api_keys()

        # Web Server API Key Detection
        if hasattr(self.args, 'web_server_api_key') and self.args.web_server_api_key:
            self.detect_web_server_api_keys()

        # SSL Key Unlock
        if hasattr(self.args, 'ssl_unlock') and self.args.ssl_unlock:
            self.ssl_key_unlock_scan()

        # Source Code Analysis
        if hasattr(self.args, 'source_code') and self.args.source_code:
            self.source_code_analysis_scan()

        # Browser App Analysis
        if hasattr(self.args, 'browser_app') and self.args.browser_app:
            self.browser_app_analysis_scan()

        # File type analysis
        if hasattr(self.args, 'index_html') and self.args.index_html:
            self.analyze_index_html()

        if hasattr(self.args, 'html') and self.args.html:
            self.analyze_html_files()

        if hasattr(self.args, 'java') and self.args.java:
            self.analyze_java_files()

        if hasattr(self.args, 'php') and self.args.php:
            self.analyze_php_files()

        if hasattr(self.args, 'python') and self.args.python:
            self.analyze_python_files()

        if hasattr(self.args, 'env') and self.args.env:
            self.analyze_env_files()

        # Standard modules
        if self.args:
            if hasattr(self.args, 'headers') and self.args.headers:
                self.enumerate_headers()
            if hasattr(self.args, 'sslinfo') and self.args.sslinfo:
                self.analyze_ssl_certificate()
            if hasattr(self.args, 'whois') and self.args.whois:
                self.whois_lookup()
            if hasattr(self.args, 'dns') and self.args.dns:
                self.dns_enumeration()
            if hasattr(self.args, 'sub') and self.args.sub:
                self.subdomain_enumeration()
            if hasattr(self.args, 'portscan') and self.args.portscan:
                self.port_scan()
            if hasattr(self.args, 'dir') and self.args.dir:
                self.directory_bruteforce()
            if hasattr(self.args, 'vuln') and self.args.vuln:
                self.vulnerability_scan()
            if hasattr(self.args, 'tech') and self.args.tech:
                self.detect_technologies()
            if hasattr(self.args, 'emails') and self.args.emails:
                self.harvest_emails()
            if hasattr(self.args, 'js') and self.args.js:
                self.analyze_javascript()
            if hasattr(self.args, 'cors') and self.args.cors:
                self.check_cors()
            if hasattr(self.args, 'methods') and self.args.methods:
                self.check_http_methods()
            if hasattr(self.args, 'robots') and self.args.robots:
                self.parse_robots_txt()
            if hasattr(self.args, 'wayback') and self.args.wayback:
                self.get_wayback_urls()
            if hasattr(self.args, 'crawl') and self.args.crawl:
                self.crawl_website(
                    max_pages=getattr(self.args, 'max_pages', 50),
                    depth=getattr(self.args, 'depth', 3)
                )
            if hasattr(self.args, 'full') and self.args.full:
                self.full_recon()

        self.print_summary()

    def full_recon(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] FULL RECONNAISSANCE")
        print(Fore.CYAN + "=" * 80)

        self.check_ip_address()
        self.enumerate_headers()
        self.analyze_ssl_certificate()
        self.whois_lookup()
        self.dns_enumeration()
        self.subdomain_enumeration()
        self.port_scan()
        self.directory_bruteforce()
        self.vulnerability_scan()
        self.detect_technologies()
        self.harvest_emails()
        self.analyze_javascript()
        self.check_cors()
        self.check_http_methods()
        self.parse_robots_txt()
        self.get_wayback_urls()
        self.crawl_website(max_pages=50, depth=3)
        self.source_code_analysis_scan()
        self.browser_app_analysis_scan()
        self.ssl_key_unlock_scan()
        self.analyze_index_html()
        self.analyze_html_files()
        self.analyze_java_files()
        self.analyze_php_files()
        self.analyze_python_files()
        self.analyze_env_files()
        self.detect_api_keys()
        self.detect_web_server_api_keys()
        self.get_isp_info()

        print(Fore.CYAN + "=" * 80 + "\n")

    def export_results(self, export_format='txt'):
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] EXPORTING RESULTS")
        print(Fore.CYAN + "=" * 60)

        export_dir = CONFIG['export_dir']
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"finalrecon_{self.hostname}_{timestamp}"

        results = {
            'target': self.target,
            'hostname': self.hostname,
            'ip': self.ip,
            'scan_time': timestamp,
            'ip_address_info': self.ip_address_info,
            'headers': self.headers_info,
            'ssl': self.ssl_info,
            'whois': self.whois_info,
            'dns': self.dns_info,
            'subdomains': self.subdomains_found,
            'open_ports': self.open_ports,
            'directories': self.directories_found,
            'vulnerabilities': self.vulnerabilities_found,
            'technologies': self.technologies,
            'emails': self.emails,
            'js_files': self.js_files,
            'api_endpoints': self.api_endpoints,
            'cors': self.cors_info,
            'http_methods': self.http_methods,
            'wayback_urls': self.wayback_urls,
            'crawled_urls': self.crawled_urls,
            'isp_info': self.isp_info,
            'source_code_analysis': self.source_code_analysis_data,
            'browser_app_analysis': self.browser_app_analysis_data,
            'ssl_unlock_info': self.ssl_unlock_info,
            'unlocked_ssl': self.unlocked_ssl,
            'index_html_analysis': self.index_html_analysis,
            'html_files_analysis': self.html_files_analysis,
            'java_files_analysis': self.java_files_analysis,
            'php_files_analysis': self.php_files_analysis,
            'python_files_analysis': self.python_files_analysis,
            'env_files_analysis': self.env_files_analysis,
            'api_keys_found': self.api_keys_found,
            'web_server_api_keys_found': self.web_server_api_keys_found,
        }

        if export_format == 'json':
            filepath = os.path.join(export_dir, f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=4, default=str)
            print(Fore.GREEN + f"[+] Exported: {filepath}")

        elif export_format == 'jsonl':
            filepath = os.path.join(export_dir, f"{filename}.jsonl")
            with open(filepath, 'w') as f:
                for key, value in results.items():
                    f.write(json.dumps({key: value}, default=str) + '\n')
            print(Fore.GREEN + f"[+] Exported: {filepath}")

        else:
            filepath = os.path.join(export_dir, f"{filename}.txt")
            with open(filepath, 'w') as f:
                f.write(f"FinalRecon-AI Scan Results\n")
                f.write(f"=" * 60 + "\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Hostname: {self.hostname}\n")
                f.write(f"IP: {self.ip}\n")
                f.write(f"Scan Time: {timestamp}\n\n")

                for section, data in results.items():
                    if data and section not in ['target', 'hostname', 'ip', 'scan_time']:
                        f.write(f"{section.upper()}\n" + "-" * 40 + "\n")
                        f.write(f"{json.dumps(data, indent=2, default=str)[:2000]}\n\n")

            print(Fore.GREEN + f"[+] Exported: {filepath}")

        return filepath

    def print_summary(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.GREEN + "[+] AI ROBOT MISSION COMPLETED!")
        print(Fore.CYAN + "=" * 80)

        # IP Status
        if self.ip_address_info:
            status = self.ip_address_info.get('status', 'unknown')
            if status == 'unlocked':
                print(Fore.GREEN + f"[+] IP Status: UNLOCKED ✓")
            elif status == 'blocked':
                print(Fore.RED + f"[!] IP Status: BLOCKED ✗")
            else:
                print(Fore.YELLOW + f"[!] IP Status: {status.upper()}")

        print(Fore.GREEN + f"[+] Vulnerabilities: {len(self.vulnerabilities_found)}")
        print(Fore.GREEN + f"[+] Firewalls Detected: {len(self.firewalls_detected)}")
        print(Fore.GREEN + f"[+] Subdomains: {len(self.subdomains_found)}")
        print(Fore.GREEN + f"[+] Open Ports: {len(self.open_ports)}")
        print(Fore.GREEN + f"[+] Directories: {len(self.directories_found)}")
        print(Fore.GREEN + f"[+] Technologies: {len(self.technologies)}")
        print(Fore.GREEN + f"[+] Emails: {len(self.emails)}")
        print(Fore.RED + f"[+] API Keys Found: {len(self.api_keys_found)}")
        print(Fore.RED + f"[+] Web Server API Keys: {len(self.web_server_api_keys_found)}")
        print(Fore.GREEN + f"[+] SSL Unlocked: {len(self.unlocked_ssl)}")
        print(Fore.CYAN + "=" * 80 + "\n")


# ============================================
# ARGUMENT PARSER
# ============================================
def parse_arguments():
    parser = argparse.ArgumentParser(
        description=f"FinalRecon-AI - IP Address Unlock Edition v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              EXAMPLES                                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  1. Basic URL Scan:                                                          ║
║     python finalrecon-ai.py --url https://example.com                       ║
║                                                                              ║
║  2. With ISP Info:                                                           ║
║     python finalrecon-ai.py --url https://example.com --isp-info            ║
║                                                                              ║
║  3. Full Scan:                                                               ║
║     python finalrecon-ai.py --url https://example.com --full                ║
║                                                                              ║
║  4. IP Address Check (Unlocked/Blocked):                                     ║
║     python finalrecon-ai.py --url https://example.com --ip-address          ║
║                                                                              ║
║  5. IP Address Enable (Unlock):                                              ║
║     python finalrecon-ai.py --url https://example.com --ip-address-enable   ║
║                                                                              ║
║  6. Custom Ports:                                                            ║
║     python finalrecon-ai.py --url https://example.com --port 80 --port 443  ║
║                                                                              ║
║  7. API Key Detection:                                                       ║
║     python finalrecon-ai.py --url https://example.com --api-key             ║
║                                                                              ║
║  8. Web Server API Keys:                                                     ║
║     python finalrecon-ai.py --url https://example.com --web-server-api-key  ║
║                                                                              ║
║  9. SSL Key Unlock:                                                          ║
║     python finalrecon-ai.py --url https://example.com --ssl-unlock          ║
║                                                                              ║
║  10. Source Code Analysis:                                                   ║
║      python finalrecon-ai.py --url https://example.com --source-code        ║
║                                                                              ║
║  11. Browser App Analysis:                                                   ║
║      python finalrecon-ai.py --url https://example.com --browser-app        ║
║                                                                              ║
║  12. Index.html Analysis:                                                    ║
║      python finalrecon-ai.py --url https://example.com --index.html         ║
║                                                                              ║
║  13. HTML Files:                                                             ║
║      python finalrecon-ai.py --url https://example.com --html               ║
║                                                                              ║
║  14. Java Files:                                                             ║
║      python finalrecon-ai.py --url https://example.com --java               ║
║                                                                              ║
║  15. IP Check + Full Scan:                                                   ║
║      python finalrecon-ai.py --url https://example.com --full \\            ║
║      --ip-address --ip-address-enable                                       ║
║                                                                              ║
║  16. Everything:                                                             ║
║      python finalrecon-ai.py --url https://example.com --full --isp-info \\ ║
║      --ip-address --api-key --web-server-api-key --source-code \\          ║
║      --browser-app --ssl-unlock --index.html --html --java -o2 json         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
    )

    # Target
    target_group = parser.add_argument_group('Target Options')
    target_group.add_argument("--url", required=True, help="Target URL (REQUIRED)")

    # Basic
    basic_group = parser.add_argument_group('Basic Options')
    basic_group.add_argument("--port", action="append", type=int, dest="port",
                             help="Custom port to scan")
    basic_group.add_argument("--isp-info", action="store_true", help="Get ISP information")
    basic_group.add_argument("--full", action="store_true", help="Full reconnaissance")
    basic_group.add_argument("-w", "--wordlist", help="Wordlist for bruteforce")

    # IP Address (NEW)
    ip_group = parser.add_argument_group('IP Address Options')
    ip_group.add_argument("--ip-address", action="store_true", dest="ip_address",
                          help="Check if IP is unlocked or blocked")
    ip_group.add_argument("--ip-address-enable", action="store_true", dest="ip_address_enable",
                          help="Enable (unlock) IP address")

    # Recon
    recon_group = parser.add_argument_group('Reconnaissance')
    recon_group.add_argument("--headers", action="store_true", help="HTTP headers")
    recon_group.add_argument("--sslinfo", action="store_true", help="SSL certificate analysis")
    recon_group.add_argument("--whois", action="store_true", help="WHOIS lookup")
    recon_group.add_argument("--dns", action="store_true", help="DNS enumeration")
    recon_group.add_argument("--sub", action="store_true", help="Subdomain enumeration")
    recon_group.add_argument("--dir", action="store_true", help="Directory bruteforce")
    recon_group.add_argument("--portscan", action="store_true", help="Port scan")
    recon_group.add_argument("--wayback", action="store_true", help="Wayback Machine")
    recon_group.add_argument("--crawl", action="store_true", help="Web crawler")
    recon_group.add_argument("--vuln", action="store_true", help="Vulnerability scan")
    recon_group.add_argument("--tech", action="store_true", help="Technology detection")
    recon_group.add_argument("--emails", action="store_true", help="Email harvesting")
    recon_group.add_argument("--js", action="store_true", help="JavaScript analysis")
    recon_group.add_argument("--cors", action="store_true", help="CORS check")
    recon_group.add_argument("--methods", action="store_true", help="HTTP methods")
    recon_group.add_argument("--robots", action="store_true", help="Robots.txt parser")

    # Source Code
    source_group = parser.add_argument_group('Source Code Analysis')
    source_group.add_argument("--source-code", action="store_true", dest="source_code",
                              help="Source code analysis")

    # API Key Detection
    api_group = parser.add_argument_group('API Key Detection')
    api_group.add_argument("--api-key", action="store_true", dest="api_key",
                           help="Detect API keys in source code")
    api_group.add_argument("--web-server-api-key", action="store_true", dest="web_server_api_key",
                           help="Detect web server API keys")

    # File type analysis
    file_group = parser.add_argument_group('File Type Analysis')
    file_group.add_argument("--index.html", action="store_true", dest="index_html",
                            help="Analyze index.html")
    file_group.add_argument("--html", action="store_true", dest="html",
                            help="Analyze HTML files")
    file_group.add_argument("--java", action="store_true", dest="java",
                            help="Analyze Java files")
    file_group.add_argument("--php", action="store_true", dest="php",
                            help="Analyze PHP files")
    file_group.add_argument("--python", action="store_true", dest="python",
                            help="Analyze Python files")
    file_group.add_argument("--env", action="store_true", dest="env",
                            help="Analyze .env files")

    # Browser App
    browser_group = parser.add_argument_group('Browser App Analysis')
    browser_group.add_argument("--browser-app", action="store_true", dest="browser_app",
                               help="Browser app analysis")

    # SSL Unlock
    ssl_group = parser.add_argument_group('SSL Key Unlock')
    ssl_group.add_argument("--ssl-unlock", action="store_true", dest="ssl_unlock",
                           help="SSL/HTTPS key unlock")

    # Crawl Options
    crawl_group = parser.add_argument_group('Crawl Options')
    crawl_group.add_argument("-d", "-depth", type=int, default=3, dest="depth",
                             help="Max crawl depth (default: 3)")
    crawl_group.add_argument("--max-pages", type=int, default=50,
                             help="Max pages to crawl (default: 50)")
    crawl_group.add_argument("-proxy", dest="proxy", help="HTTP proxy")
    crawl_group.add_argument("-H", "-headers", action="append", dest="H",
                             help="Custom header")

    # Output
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument("-o", "-output", dest="o", help="Output file")
    output_group.add_argument("-j", "-jsonl", action="store_true", dest="j",
                              help="JSONL output")
    output_group.add_argument("-o2", "--export", default='txt',
                              help="Export format (txt, json, jsonl)")
    output_group.add_argument("-nb", "--no-banner", action="store_true", dest="no_banner",
                              help="Hide banner")
    output_group.add_argument("-version", action="version", version=f"FinalRecon-AI v{VERSION}")

    return parser.parse_args()


# ============================================
# MAIN
# ============================================
def main():
    args = parse_arguments()

    if not args.url:
        print(Fore.RED + "[-] Error: --url is required!")
        print(Fore.CYAN + "[*] Example: python finalrecon-ai.py --url https://example.com --full")
        sys.exit(1)

    target = args.url

    robot = AutonomousAIRobot(target, args)

    if hasattr(args, 'export') and args.export != 'None':
        robot.export_results(args.export)

    print(Fore.GREEN + "\n[+] AI Robot Mission Completed Successfully!")
    return 0


# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Keyboard Interrupt. Exiting...")
        sys.exit(130)
    except Exception as e:
        print(Fore.RED + f"\n[-] Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
