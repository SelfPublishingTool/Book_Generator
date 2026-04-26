import http.server
import socketserver
import threading
import time
import os
import subprocess
from pathlib import Path

PORT = 8000
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n🚀 AMBIENTE LOCAL ATTIVO")
        print(f"👉 Visualizza il libro qui: http://localhost:{PORT}/High_Protein_Meal_Prep_Cookbook.html")
        print(f"Ispirazione: Il server si aggiorna automaticamente se i file cambiano.\n")
        httpd.serve_forever()

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
                # Run the build script
                os.chdir("work")
                subprocess.run(["python3", "build_html.py"], capture_output=True)
                os.chdir("..")
                print("✅ Libro aggiornato con successo!")
            except Exception as e:
                print(f"❌ Errore durante la rigenerazione: {e}")
                os.chdir(Path(__file__).parent)
                
        time.sleep(1)

if __name__ == "__main__":
    # Initial build
    print("🔨 Primo avvio: generazione libro...")
    os.chdir("work")
    subprocess.run(["python3", "build_html.py"])
    os.chdir("..")
    
    # Start threads
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    watch_and_build()
