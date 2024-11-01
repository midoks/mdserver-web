function Terms_WebSocketIO (el, config) {
    if (typeof config == "undefined") {
        config = {};
    }
    this.el = el;
    this.id = config.ssh_info.id || '';
    this.ws = null; //websocket对象
    this.route = 'webssh_websocketio'; // 访问的方法
    this.term = null; //term对象
    this.info = null; // 请求数据
    this.last_body = null;
    this.fontSize = 14; //终端字体大小
    this.ssh_info = config.ssh_info;
    this.term_timer = null;

    this.is_connected = false;

    this.callback_close = null;
    this.callback_connected = null;
    this.run();
}

Terms_WebSocketIO.prototype = {

    registerCloseCallBack:function(callback){
        this.callback_close =  callback;
    },

    registerConnectedCallBack:function(callback){
        this.callback_connected =  callback;
    },

    registerExitCallBack:function(callback){
        this.callback_exit =  callback;
    },

    connectWs: function (callback) {
        this.ws = io.connect();
        // console.log(this.ws);
    },

    connectSsh:function(){
        this.send(this.ssh_info);
        // this.send('\n');
    },

    close:function(){
        this.ws.disconnect();
        this.ws.close();
    },

    on_message: function (ws_event) {
        this.term.write(ws_event.data);
        if (ws_event.data == '\r\n登出\r\n' ||  ws_event.data == '登出\r\n' || 
            ws_event.data == '\r\nlogout\r\n' ||  ws_event.data == 'logout\r\n'||
            ws_event.data == '\r\nexit\r\n' ||  ws_event.data == 'exit\r\n') {
            this.term.destroy();
            this.ws.disconnect();
            this.ws.close();
            clearInterval(this.term_timer);

            if (this.callback_close){
                this.callback_close();
            }
        }
    },

    on_connect:function(ws_event){
        this.is_connected = true;
        if (this.callback_connected){
            this.callback_connected();
        }
    },

    on_reconnect:function(ws_event){
        this.is_connected = false;
        // if (this.callback_connected){
        //     this.callback_connected();
        // }
    },

    on_exit:function(){
        if (this.callback_exit){
            this.callback_exit();
        }
    },

    send:function(data){
        this.ws.emit(this.route, data);
    },

    resize: function (size) {
        if (this.ws && this.is_connected) {
            size['resize'] = 1;
            this.send(size)
        }
    },
    run: function (ssh_info) {
        this.connectWs();

        var that = this;    
        var termCols = 83;
        var termRows = 21;
        this.term = new Terminal({fontSize: this.fontSize,screenKeys: true, useStyle: true});

        this.term.open($('#'+this.id)[0]);
        this.term.setOption('cursorBlink', true);
        this.ws.on('server_response', function (ev) { that.on_message(ev)});
        this.ws.on('connect', function (ev) { that.on_connect(ev)});
        this.ws.on('reconnect', function (ev) { that.on_reconnect(ev)});
        this.ws.on('exit', function (ev) { that.on_exit(ev)});

        if (this.ws) {
            this.term_timer = setInterval(function () {
                if (that.is_connected){
                    that.send('');
                } else{
                    that.on_exit();
                }
            }, 600);
        }
        
        this.term.on('data', function (data) {
            if (that.is_connected){
                that.send(data);
            } else{
                that.term.write('\r\n连接丢失,正在尝试重新连接!\r\n');
                that.connectSsh();
            }
        });

        this.term.write('\r\n请稍等,正在链接中...\r\n');
        this.connectSsh();
        this.term.focus();
    }
}
