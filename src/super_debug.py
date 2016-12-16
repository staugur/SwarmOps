# -*- coding:utf8 -*-
# Performance optimization model(Maybe Only Linux)

if __name__ == "__main__":
    from main import app
    from werkzeug.contrib.profiler import ProfilerMiddleware
    from config import GLOBAL
    Host = GLOBAL.get('Host')
    Port = GLOBAL.get('Port')
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [60])
    app.run(debug=True, host=Host, port=Port)
