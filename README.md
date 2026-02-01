# 🛡️ Conduit Manager & Network Monitor CLI

```text
 ██████╗ ██████╗ ███╗   ██╗██████╗ ██╗   ██╗██╗████████╗
 ██╔════╝██╔═══██╗████╗  ██║██╔══██╗██║   ██║██║╚══██╔══╝
 ██║     ██║   ██║██╔██╗ ██║██║  ██║██║   ██║██║   ██║   
 ██║     ██║   ██║██║╚██╗██║██║  ██║██║   ██║██║   ██║   
 ╚██████╗╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝██║   ██║   
  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝   ╚═╝   
              W I N D O W S GO0DZ1LAH
```
---

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-win)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-BETA-purple)

**Conduit Monitor** is a Comprehensive Command Line Interface (CLI) Tool For Deploying and Monitoring Psiphon Conduit Nodes on Windows Servers for [Conduit](https://github.com/Psiphon-Inc/conduit) service. Empowering users to help bypass network restrictions with real-time traffic analysis and advanced bandwidth control.

> **Disclaimer:** This tool is strictly for network analysis and management purposes. The developer is not responsible for any misuse of this software.

---

---
## 🇬🇧 English Description

**Conduit Monitor** is a professional management suite designed specifically for Windows environments. This manager provides deep integration with Windows native monitoring tools (`PktMon`) to calculate precise bandwidth usage.

### ✨ Key Features
* **One-Click Deployment:** Automatically downloads Conduit binaries and GeoLite2 databases.
* **Real-time Traffic Sniffer:** Powered by Windows `PktMon`, it tracks every single peer's speed and total usage.
* **Resource Control:** Interactively set **Max Clients** (up to 1000 users) and **Bandwidth Caps** (Mbps) per session.
* **Geo-Location Mapping:** Instantly identify the origin country of connected peers using [GeoLite2](https://github.com/P3TERX/GeoLite.mmdb).
* **Process Stability:** Automated process handling with sniffer auto-restart logic to ensure 24/7 uptime.

---


## 📸 Screenshots | اسکرین شات‌ها

| Conduit Dashboard | Conduit Analytics |
|:---:|:---:|
| ![Dashboard](https://github.com/Go0Dz1laH/Conduit-Monitor-Windows/raw/main/Conduit-Dash.png) | ![Analytics](https://github.com/Go0Dz1laH/Conduit-Monitor-Windows/raw/main/Conduit-Analytics.png) |
| **Dashboard**: نمای اصلی و کنترل پنل مانیتورینگ | **Analytics**: صفحه تحلیل‌های پیشرفته و آمار |

---


## 🚀 Installation & Usage

### Method 1: Download EXE (Recommended)
You can download the latest standalone executable from the **[Releases Page](../../releases)**.
1. Download `Conduit-Manager-Windows.exe`.
2. Right-click and select **"Run as Administrator"** (Required for Packet Monitoring).

### Method 2: Run via Python (Source)
```bash
git clone https://github.com/Go0Dz1laH/Conduit-Monitor-Windows.git
cd Conduit-Monitor-Windows
pip install -r requirements.txt
python main.py
```
## راهنمای فارسی (Persian)

**مدیریت کاندوئیت** یک ابزار حرفه‌ای تحت خط فرمان (CLI) است که برای مدیریت و مانیتورینگ سرویس کاندوئیت طراحی شده است. این ابزار به شما امکان می‌دهد ترافیک شبکه را به صورت لحظه‌ای مشاهده کنید، مصرف کاربران را آنالیز کنید و محدودیت‌های لازم را اعمال نمایید.

### ✨ ویژگی‌های اصلی
* **مانیتورینگ زنده:** مشاهده کلاینت‌های متصل و پایش وضعیت نشست‌ها به صورت لحظه‌ای.
* **آنالیز دقیق ترافیک:** نمایش حجم مصرفی، سرعت دانلود/آپلود و کشور مبدأ کاربران.
* **مدیریت هوشمند منابع:** قابلیت تنظیم سقف تعداد کاربر و پهنای باند از داخل منوی برنامه.
* **راه‌اندازی خودکار:** دانلود خودکار هسته کاندوئیت و دیتابیس‌های جغرافیایی مورد نیاز.

---


## 🚀 آموزش نصب و استفاده
**روش اول: 
استفاده از فایل اجرایی (پیشنهادی)**
۱. به صفحه **[Releases Page](../../releases)** بروید و فایل `Conduit-Manager-Windows.exe` را دانلود کنید.
۲. روی فایل راست‌کلیک کرده و گزینه **Run as Administrator** را انتخاب کنید (برای مانیتورینگ شبکه الزامی است).

**روش دوم:
اجرا از طریق پایتون**
ابتدا مخزن را کلون کرده و پیش‌نیازها را نصب کنید:
```bash
git clone https://github.com/Go0Dz1laH/Conduit-Monitor-Windows.git
cd Conduit-Monitor-Windows
pip install -r requirements.txt
```
فایل پایتون رو اجرا کنید :
```bash
python main.py
```

---

## ⚖️ Legal & Credits
* **Conduit Client:** Powered by [Psiphon-Inc/conduit](https://github.com/Psiphon-Inc/conduit).
* **GeoIP Database:** Includes GeoLite2 data created by MaxMind.
* **Network Monitoring:** Utilizes Windows native `pktmon.exe` tool for traffic analysis.

---
**Developer:** [Go0Dz1laH](https://github.com/Go0Dz1laH) | **License:** MIT LICENSE
