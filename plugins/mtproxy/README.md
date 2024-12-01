# mtproxy
MTProxy代理


## 基本安装
```
cd /www/server/mdserver-web/plugins && rm -rf mtproxy  && git clone https://github.com/mw-plugin/mtproxy && cd mtproxy && rm -rf .git && cd /www/server/mdserver-web/plugins/mtproxy && bash install.sh install 1.0
```

## DEBUG
``` 
cd /www/server/mdserver-web && python3 /www/server/mdserver-web/plugins/mtproxy/index.py start
```