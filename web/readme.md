
- 常用开发命令

```
gunicorn -b :7201 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
gunicorn -b :7201 -w 1 app:app
gunicorn -c setting.py app:app

```