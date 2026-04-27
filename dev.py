import http.server
import socketserver
import threading
import time
import os
import subprocess
import socket
from pathlib import Path

DIRECTORY = "."
BASE_PORT = 8000

def find_free_port(start_port):
    port = start_port
    while port < start_port + 10:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                port += 1
    return port

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server(port):
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"\n🚀 AMBIENTE LOCAL ATTIVO")
            print(f"👉 Visualizza il libro qui: http://localhost:{port}/High_Protein_Meal_Prep_Cookbook.html")
            print(f"Ispirazione: Il server si aggiorna automaticamente se i file cambiano.\n")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Errore server: {e}")

def watch_and_build():
    files_to_watch = [
        Path("work/book.json"),
        Path("work/build_html.py")
    ]
    
    last_mtimes = {str(f): os.path.getmtime(f) if f.exists() else 0 for f in files_to_watch}
    
    while True:
        changed = False
        for f in files_to_watch:
            if f.exists():
                current_mtime = os.path.getmtime(f)
                if current_mtime > last_mtimes.get(str(f), 0):
                    last_mtimes[str(f)] = current_mtime
                    changed = True
        
        if changed:
            print("🔄 Modifica rilevata! Rigenerazione libro in corso...")
            try:
                # build_html.py handles its own paths now
                subprocess.run(["python3", "work/build_html.py"], capture_output=True)
                print("✅ Libro aggiornato con successo!")
            except Exception as e:
                print(f"❌ Errore durante la rigenerazione: {e}")
                
        time.sleep(1)

if __name__ == "__main__":
    # Initial build
    print("🔨 Primo avvio: generazione libro...")
    subprocess.run(["python3", "work/build_html.py"])
    
    port = find_free_port(BASE_PORT)
    
    # Start threads
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()
    
    try:
        watch_and_build()
    except KeyboardInterrupt:
        print("\n👋 Chiusura ambiente di sviluppo.")
