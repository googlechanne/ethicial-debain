# FinalRecon-AI - Ultimate Autonomous AI Robot Edition

![Version](https://img.shields.io/badge/version-2026.9-blue)
![Build](https://img.shields.io/badge/build-2026.009.1-green)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-red)

**FINALRECON-AI** is an advanced, autonomous AI-powered reconnaissance framework designed for security researchers, penetration testers, and ethical hackers. It combines multiple reconnaissance techniques into a single, intelligent, automated tool.

---

## 🚀 Features

### 🔓 IP Address Unlock/Block Check
- Detect if your IP is blocked by the target
- Attempt automatic IP unlock using multiple bypass methods
- Spoofed headers, User-Agent rotation, session clearing

### 🔐 API Key Detection
- Scan for 40+ API key patterns (AWS, Google, GitHub, Stripe, etc.)
- Web server API key detection (Apache, Nginx, IIS, Jenkins, etc.)
- Private key and token detection

### 📊 Reconnaissance Modules
- HTTP Header Enumeration
- SSL Certificate Analysis
- WHOIS Lookup
- DNS Enumeration
- Subdomain Enumeration
- Port Scanning
- Directory Bruteforce
- Web Crawler (Depth/Breadth-first)
- Technology Detection
- Email Harvesting
- JavaScript Analysis
- CORS Misconfiguration Check
- HTTP Methods Analysis
- Robots.txt Parser
- Wayback Machine URLs
- Vulnerability Scanning

### 📝 Source Code Analysis
- HTML Source Analysis
- Index.html Deep Analysis
- HTML Files Analysis
- Java Source Code Analysis
- PHP Source Code Analysis
- Python Source Code Analysis
- .env Files Analysis
- Git/SVN Exposure Detection
- Backup & Config File Detection

### 🌐 Browser App Analysis
- Framework Detection (React, Vue, Angular, Svelte)
- Build Tool Detection (Webpack, Vite, Parcel)
- State Management Detection (Redux, MobX, Vuex)
- PWA Analysis
- Service Worker Analysis
- UI Library Detection

### 🔐 SSL Key Unlock
- TLS Version Testing
- SSL Bypass Methods
- SNI Manipulation
- Custom SSL Context

---

## 📦 Installation

```bash
git clone https://github.com/googlechanne/ethicial-debain.git
cd ethicial-debain
pip3 install -r requirements.txt

Basic Scan
bash
python3 finalrecon-ai.py --url https://example.com
Full Reconnaissance
bash
python3 finalrecon-ai.py --url https://example.com --full
IP Address Check (Unlocked/Blocked)
bash
python3 finalrecon-ai.py --url https://example.com --ip-address
IP Address Enable (Unlock)
bash
python3 finalrecon-ai.py --url https://example.com --ip-address-enable
API Key Detection
bash
python3 finalrecon-ai.py --url https://example.com --api-key
Web Server API Key Detection
bash
python3 finalrecon-ai.py --url https://example.com --web-server-api-key
SSL Key Unlock
bash
python3 finalrecon-ai.py --url https://example.com --ssl-unlock
Source Code Analysis
bash
python3 finalrecon-ai.py --url https://example.com --source-code
Browser App Analysis
bash
python3 finalrecon-ai.py --url https://example.com --browser-app
Index.html Analysis
bash
python3 finalrecon-ai.py --url https://example.com --index.html
Everything (Full Power)
bash
python3 finalrecon-ai.py --url https://example.com --full --isp-info \
  --ip-address --api-key --web-server-api-key --source-code \
  --browser-app --ssl-unlock --index.html --html --java --php --python --env \
  -o2 json
