from app import create_app, socketio
from threading import Thread
from app.utils.background_thread import background_thread

app = create_app()

if __name__ == '__main__':
    port = 5000
    
    thread = Thread(target=background_thread, args=(socketio,))
    thread.daemon = True
    thread.start()
    
    socketio.run(app, debug=False, host='0.0.0.0', port=port,use_reloader=False, allow_unsafe_werkzeug=True)
