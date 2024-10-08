
- 常用开发命令

```
gunicorn -b :7200 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app

```