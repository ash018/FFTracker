import os

capture_output = True
enable_stdio_inheritance = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

loglevel = 'debug'
errorlog = os.path.join(BASE_DIR, 'prod/err.log')
accesslog = os.path.join(BASE_DIR, 'prod/out.log')

pidfile = os.path.join(BASE_DIR, 'prod/gunicorn.pid')
bind = 'unix:' + os.path.join(BASE_DIR, 'conf.sock')

print('Binding to: ' + str(bind))

daemon = True
workers = 2
worker_class = 'sync'

