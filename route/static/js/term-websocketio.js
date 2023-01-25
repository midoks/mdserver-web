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
    this.run();
}

Terms_WebSocketIO.prototype = {

    registerCloseCallBack:function(callback){
        this.callback_close =  callback;
    },

    // websocket持久化连接
    connect: function (callback) {
        if(!this.ws){
            this.ws = io.connect();
        }
    },

    //连接服务器成功
    on_open: function (ws_event) {
      this.term.FitAddon.fit();
      this.resize({ cols: this.term.cols, rows: this.term.rows });
    },

    //服务器消息事件
    on_message: function (ws_event) {
        this.term.write(ws_event.data);
        if (ws_event.data == '\r\n登出\r\n' ||  ws_event.data == '登出\r\n' || 
            ws_event.data == '\r\nlogout\r\n' ||  ws_event.data == 'logout\r\n'||
            ws_event.data == '\r\nexit\r\n' ||  ws_event.data == 'exit\r\n') {
            this.term.destroy();
            clearInterval(this.term_timer);
            this.ws.disconnect();
            this.ws.close();
            if (this.callback_close){
                this.callback_close();
            }
        }
    },

    on_close: function (ws_event) {
      this.ws = null;
    },

    on_error: function (ws_event) {
    },

    send: function (data, num) {

    },

    //关闭连接
    close: function () {
      this.ws.close();
      this.set_term_icon(0);
    },
    resize: function (size) {
      if (this.ws) {
          size['resize'] = 1;
          this.send(JSON.stringify(size));
      }

    },
    run: function (ssh_info) {
        this.connect();

        var that = this;    
        var termCols = 83;
        var termRows = 21;
        this.term = new Terminal({ cols: termCols, rows: termRows, screenKeys: true, useStyle: true});

        this.term.open($('#'+this.id)[0]);
        this.term.setOption('cursorBlink', true);
        this.term.setOption('fontSize', this.fontSize);

        // console.log(this.term.cols,this.term.rows);
        // this.term.fit();
        // console.log(this.term.cols,this.term.rows);

        // this.term.FitAddon = new window.FitAddon();
        // this.term.loadAddon(this.term.FitAddon);
        // this.term.WebLinksAddon = new WebLinksAddon.WebLinksAddon();
        // this.term.loadAddon(this.term.WebLinksAddon);

        this.ws.on('server_response', function (ev) { that.on_message(ev)});

        if (this.ws) {
            that.ws.emit('webssh_websocketio', '');
            this.term_timer = setInterval(function () {
                that.ws.emit('webssh_websocketio', '');
            }, 500);
        }
        
        this.term.on('data', function (data) {
            that.ws.emit('webssh_websocketio', data);
        });
    
        this.ws.emit('webssh_websocketio', this.ssh_info);
        this.ws.emit('webssh_websocketio', '\n');
        this.term.focus();
    }
}
