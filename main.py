import subprocess
import re
import psutil
import geoip2.database
import time
import threading
import os
import sys
import requests
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn

# ================= CONFIGURATION =================
CONDUIT_EXE = "conduit-windows-amd64.exe"
CONDUIT_URL = "https://github.com/Psiphon-Inc/conduit/releases/download/release-cli-1.2.0/conduit-windows-amd64.exe"
GEOIP_DB = "GeoLite2-Country.mmdb"
GEOIP_URL = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb"
METRICS_URL = "http://127.0.0.1:9090/metrics"

# مدت زمان (ثانیه) برای ریستارت کردن اسنیفر جهت جلوگیری از کرش
SNIFFER_RESTART_INTERVAL = 300  
USER_TIMEOUT = 45 

# ================= GLOBALS =================
active_users = {} 
global_stats = {'upload': 0.0, 'download': 0.0}
conduit_ports_cache = set()
lock = threading.Lock()
console = Console()

# تنظیمات کاربر
user_limit = 50
bandwidth_limit = 40.0

APP_LOGO = """
  ██████╗ ██████╗ ███╗   ██╗██████╗ ██╗   ██╗██╗████████╗
 ██╔════╝██╔═══██╗████╗  ██║██╔══██╗██║   ██║██║╚══██╔══╝
 ██║     ██║   ██║██╔██╗ ██║██║  ██║██║   ██║██║   ██║   
 ██║     ██║   ██║██║╚██╗██║██║  ██║██║   ██║██║   ██║   
 ╚██████╗╚██████╔╝██║ ╚████║██████╔╝╚██████╔╝██║   ██║   
  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝   ╚═╝   
       CLI MONITORING TOOL | MADE BY GOODZILAH
"""

# ================= HELPERS =================

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def download_asset(file_name, url):
    target_path = os.path.join(get_base_path(), file_name)
    if os.path.exists(target_path):
        return

    console.print(Panel(f"[bold yellow]{file_name} not found![/bold yellow]\nDownloading...", title="Setup"))
    try:
        with requests.get(url, stream=True, timeout=15) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                DownloadColumn(),
                transient=True,
            ) as progress:
                task = progress.add_task(f"Downloading {file_name}...", total=total_size)
                with open(target_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
        console.print(f"[bold green]✓ {file_name} Ready.[/bold green]\n")
    except Exception as e:
        console.print(f"[bold red]Failed to download {file_name}. Check internet connection.\nError: {e}[/bold red]")
        time.sleep(3)

def mask_ip(ip):
    """آی‌پی را به صورت 142.***.***.*** نمایش می‌دهد"""
    parts = ip.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.***.***.***"
    return ip

# ================= LOGIC =================

download_asset(GEOIP_DB, GEOIP_URL)
reader = None
try:
    db_path = os.path.join(get_base_path(), GEOIP_DB)
    if os.path.exists(db_path):
        reader = geoip2.database.Reader(db_path)
except Exception as e:
    console.print(f"[yellow]Warning: GeoIP DB loading failed ({e}). Location will be Unknown.[/yellow]")

def get_conduit_ports_cached():
    global conduit_ports_cache
    new_ports = set()
    for proc in psutil.process_iter(['name']):
        if CONDUIT_EXE in proc.info['name'].lower():
            try:
                for conn in proc.net_connections(kind='udp'):
                    if conn.laddr: new_ports.add(conn.laddr.port)
            except: continue
    
    with lock:
        conduit_ports_cache = new_ports
    return new_ports

def update_ports_loop():
    while True:
        get_conduit_ports_cached()
        time.sleep(10)

def fetch_global_metrics():
    global global_stats
    while True:
        try:
            response = requests.get(METRICS_URL, timeout=1)
            if response.status_code == 200:
                data = response.text
                
                down = 0.0
                up = 0.0
                
                d_match = re.search(r'conduit_bytes_downloaded\s+([\d\.e\+\-]+)', data)
                if d_match: 
                    down = float(d_match.group(1))
                
                u_match = re.search(r'conduit_bytes_uploaded\s+([\d\.e\+\-]+)', data)
                if u_match: 
                    up = float(u_match.group(1))

                with lock:
                    global_stats['download'] = down
                    global_stats['upload'] = up
        except:
            pass 
        time.sleep(2)

def get_country(ip):
    if reader:
        try:
            res = reader.country(ip)
            return res.country.name if res.country.name else "Unknown"
        except: return "Unknown"
    return "Unknown"

def pktmon_manager():
    while True:
        subprocess.run(["pktmon", "stop"], capture_output=True)
        if os.path.exists("PktMon.etl"):
            try: os.remove("PktMon.etl")
            except: pass
            
        subprocess.run(["pktmon", "filter", "remove"], capture_output=True)
        subprocess.run(["pktmon", "filter", "add", "-t", "UDP"], capture_output=True)

        cmd = ["pktmon", "start", "--capture", "--log-mode", "real-time", "--pkt-size", "64", "--file-size", "1"]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='cp437', errors='replace')
        
        start_time = time.time()
        pattern = r"(\d{1,3}(?:\.\d{1,3}){3})\.\d+\s+>\s+[\d\.]+\.(\d+):\s+UDP,\s+length\s+(\d+)"

        try:
            for line in process.stdout:
                if time.time() - start_time > SNIFFER_RESTART_INTERVAL:
                    break 

                match = re.search(pattern, line)
                if match:
                    src_ip = match.group(1)
                    dst_port = int(match.group(2))
                    size = int(match.group(3))
                    
                    if dst_port in conduit_ports_cache and not src_ip.startswith(('127.', '192.', '10.', '172.')):
                        with lock:
                            now = time.time()
                            if src_ip not in active_users:
                                active_users[src_ip] = {
                                    'country': get_country(src_ip),
                                    'total_bytes': 0, 
                                    'last_bytes': 0,
                                    'speed': 0,
                                    'last_update': now,
                                    'first_seen': now, 
                                    'last_seen': now
                                }
                            u = active_users[src_ip]
                            u['total_bytes'] += size
                            u['last_bytes'] += size
                            u['last_seen'] = now
                            
                            if now - u['last_update'] >= 1.0:
                                u['speed'] = u['last_bytes'] / (now - u['last_update'])
                                u['last_bytes'] = 0
                                u['last_update'] = now
        except Exception:
            pass
        
        try: process.terminate()
        except: pass
        time.sleep(1) 

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024: return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def show_monitoring():
    threading.Thread(target=update_ports_loop, daemon=True).start()
    threading.Thread(target=fetch_global_metrics, daemon=True).start()
    threading.Thread(target=pktmon_manager, daemon=True).start()

    with Live(auto_refresh=False, console=console, screen=True) as live:
        try:
            while True:
                term_height = console.size.height
                available_rows = max(5, term_height - 20)
                now = time.time()
                
                with lock:
                    u_table = Table(title=Text("Active Clients (Real Time)", style="bold white on blue"), expand=True, border_style="cyan")
                    u_table.add_column("IP Address", style="bold white")
                    u_table.add_column("Country", style="bold green")
                    u_table.add_column("Speed Est.", style="bold yellow")
                    u_table.add_column("Session Usage", style="bold blue")
                    u_table.add_column("Duration", justify="right", style="dim")
                    
                    to_del = [ip for ip, d in active_users.items() if now - d['last_seen'] > USER_TIMEOUT]
                    for ip in to_del: del active_users[ip]

                    sorted_users = sorted(active_users.items(), key=lambda x: x[1]['last_seen'], reverse=True)
                    for ip, d in sorted_users[:available_rows]:
                        duration = int(now - d['first_seen'])
                        m, s = divmod(duration, 60)
                        h, m = divmod(m, 60)
                        time_str = f"{h:02d}:{m:02d}:{s:02d}"
                        
                        u_table.add_row(
                            mask_ip(ip),  # اعمال ماسک کردن آی‌پی
                            d['country'], 
                            f"{format_bytes(d['speed'])}/s", 
                            format_bytes(d['total_bytes']), 
                            time_str
                        )

                    c_stats = {}
                    for d in active_users.values():
                        c = d['country']
                        c_stats[c] = c_stats.get(c, {'n': 0, 'v': 0})
                        c_stats[c]['n'] += 1
                        c_stats[c]['v'] += d['total_bytes']
                    
                    s_table = Table(title=Text("Geo Distribution", style="bold white on magenta"), expand=True, border_style="magenta")
                    s_table.add_column("Country", style="white")
                    s_table.add_column("Users", justify="center", style="bold green")
                    s_table.add_column("Usage", justify="right", style="bold yellow")
                    for c, s in c_stats.items():
                        s_table.add_row(c, str(s['n']), format_bytes(s['v']))

                    total_down = format_bytes(global_stats['download'])
                    total_up = format_bytes(global_stats['upload'])
                    
                # اصلاح مشکل تگ‌های رنگی با استفاده از Text.from_markup
                header_text = (
                    f"[bold yellow]CONDUIT MONITOR[/bold yellow] | "
                    f"Users: [green]{len(active_users)}[/green] | "
                    f"Total Download: [cyan]{total_down}[/cyan] | "
                    f"Total Upload: [magenta]{total_up}[/magenta]"
                )
                
                header = Panel(Text.from_markup(header_text, justify="center"))
                
                grid = Table.grid(expand=True)
                grid.add_row(header)
                grid.add_row(u_table)
                grid.add_row(s_table)
                grid.add_row(Align.center("\n[blink bold red]PRESS CTRL+C TO RETURN TO MENU[/blink bold red]"))
                
                live.update(grid, refresh=True)
                time.sleep(1) 
        except KeyboardInterrupt: pass

def get_selection(title, options):
    while True:
        os.system('cls')
        console.print(Align.center(Text(APP_LOGO, style="bold cyan")))
        console.print(Panel(Align.center(f"[bold white]{title}[/bold white]"), border_style="yellow"))
        for i, opt in enumerate(options, 1):
            console.print(f"    [bold yellow]{i}.[/bold yellow] [bold white]{opt}[/bold white]")
        try:
            line_input = input("\n    Select: ")
            choice = int(line_input)
            if 1 <= choice <= len(options): return options[choice-1]
        except: pass

def check_conduit_status():
    for proc in psutil.process_iter(['name']):
        if CONDUIT_EXE in proc.info['name'].lower():
            return True, proc.info['name']
    return False, "Not Running"

def main_menu():
    global user_limit, bandwidth_limit
    while True:
        os.system('cls')
        is_running, _ = check_conduit_status()
        status_color = "green" if is_running else "red"
        status_text = "ONLINE" if is_running else "OFFLINE"
        
        console.print(Align.center(Text(APP_LOGO, style="bold gradient cyan to blue")))
        
        info_grid = Table.grid(expand=True)
        info_grid.add_column(justify="center")
        info_grid.add_row(
            Panel(
                f"[bold white]STATUS:[/bold white] [{status_color} bold]{status_text}[/{status_color} bold]\n"
                f"[bold white]LIMITS:[/bold white] [cyan]{user_limit} Users[/cyan] | [magenta]{bandwidth_limit} Mbps[/magenta]",
                title="System Info", border_style="blue", expand=False
            )
        )
        console.print(Align.center(info_grid))
        print("\n")
        
        menu_table = Table.grid(padding=(0, 4))
        menu_table.add_row("[bold yellow]1.[/bold yellow] Start Conduit", "[bold yellow]2.[/bold yellow] Open Monitor")
        menu_table.add_row("[bold yellow]3.[/bold yellow] Stop Conduit", "[bold yellow]4.[/bold yellow] Config")
        menu_table.add_row("[bold yellow]5.[/bold yellow] Exit", "")
        console.print(Align.center(menu_table))
        
        cmd = input("\n    Command: ")
        
        if cmd == '1':
            if not is_running:
                download_asset(CONDUIT_EXE, CONDUIT_URL)
                exe_path = os.path.join(get_base_path(), CONDUIT_EXE)
                run_cmd = f'"{exe_path}" start -m {user_limit} -b {float(bandwidth_limit)} -v --metrics-addr 127.0.0.1:9090'
                subprocess.Popen(run_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                console.print(f"    [bold green]Service Launched![/bold green]")
                time.sleep(2)
        elif cmd == '2':
            if is_running: 
                show_monitoring()
            else: 
                console.print("    [bold red]Conduit is not running![/bold red]")
                time.sleep(1)
        elif cmd == '3':
            subprocess.run(["taskkill", "/f", "/im", CONDUIT_EXE], capture_output=True)
            console.print("    [bold red]Service Stopped.[/bold red]")
            time.sleep(1)
        elif cmd == '4':
            user_limit = get_selection("USER LIMIT", [50, 100, 200, 500, 1000])
            bandwidth_limit = get_selection("BANDWIDTH (MBPS)", [40, 100, 200, 500, 1000])
        elif cmd == '5':
            subprocess.run(["pktmon", "stop"], capture_output=True)
            if os.path.exists("PktMon.etl"):
                try: os.remove("PktMon.etl")
                except: pass
            break

if __name__ == "__main__":
    os.system(f"title GOOZILAH MONITORING")
    user_limit = get_selection("SETUP: USER LIMIT", [50, 100, 200, 500])
    bandwidth_limit = get_selection("SETUP: BANDWIDTH", [40, 100, 200, 500, 1000])
    main_menu()