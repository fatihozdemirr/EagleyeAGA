from app import create_app, socketio
from threading import Thread
from app.utils.background_thread import background_thread
import os

app = create_app()

def kill_process_on_port(port):
    command = f"lsof -t -i:{port}"
    pid = os.popen(command).read().strip()
    if pid:
        print(f"Port {port} üzerinde çalışan süreç PID: {pid}, sonlandırılıyor...")
        os.system(f"kill -9 {pid}")
    else:
        print(f"Port {port} boş.")


if __name__ == '__main__':
    port = 5000
    kill_process_on_port(port)
    thread = Thread(target=background_thread, args=(socketio,))
    thread.daemon = True
    thread.start()
    
    socketio.run(app, debug=False, host='0.0.0.0', port=port,use_reloader=False, allow_unsafe_werkzeug=True)
