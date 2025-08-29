# -*- coding: utf-8 -*-

from app import create_app, db, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app,
                 debug=True,
                 host='0.0.0.0',
                 port=5000,
                 use_reloader=True)
