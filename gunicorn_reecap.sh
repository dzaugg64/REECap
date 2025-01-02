cd /home/reecap/reecap
/home/reecap/reecap/.venv/bin/gunicorn --worker-class eventlet -w 4 -b 127.0.0.1:5000 main:app
