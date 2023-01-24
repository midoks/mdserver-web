function Terms_WebSocketIO (el, config) {

    console.log(config);
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

var socket, gterm;

Terms_WebSocketIO.prototype = {
    // websocket持久化连接
    connect: function (callback) {
        if(!this.ws){
            this.ws = io.connect();
        }
    },

    //连接服务器成功
    on_open: function (ws_event) {
      var http_token = $("#request_token_head").attr('token');
      this.ssh_info['x-http-token'] = http_token;

      this.send(JSON.stringify(this.ssh_info || { 'x-http-token': http_token }))
      this.term.FitAddon.fit();
      this.resize({ cols: this.term.cols, rows: this.term.rows });
    },

    //服务器消息事件
    on_message: function (ws_event) {
        // console.log(ws_event.data);
        this.term.write(ws_event.data);
        if (ws_event.data == '\r\n登出\r\n' ||  ws_event.data == '登出\r\n' || 
            ws_event.data == '\r\nlogout\r\n' ||  ws_event.data == 'logout\r\n'||
            ws_event.data == '\r\nexit\r\n' ||  ws_event.data == 'exit\r\n') {
            this.term.destroy();
            clearInterval(this.term_timer);
        }
    },

    //websocket关闭事件
    on_close: function (ws_event) {
      this.ws = null;
    },

    //websocket错误事件
    on_error: function (ws_event) {
      if (ws_event.target.readyState === 3) {
          // var msg = '错误: 无法创建WebSocket连接，请在面板设置页面关闭【开发者模式】';
          // layer.msg(msg,{time:5000})
          // if(Term.state === 3) return
          // Term.term.write(msg)
          // Term.state = 3;
      } else {
          console.log(ws_event)
      }
    },
    //发送数据
    //@param event 唯一事件名称
    //@param data 发送的数据
    //@param callback 服务器返回结果时回调的函数,运行完后将被回收
    send: function (data, num) {
      var that = this;
      //如果没有连接，则尝试连接服务器
      if (!this.ws || this.bws.readyState == 3 || this.bws.readyState == 2) {
          this.connect();
      }
      //判断当前连接状态,如果!=1，则100ms后尝试重新发送
      if (this.ws.readyState === 1) {
          this.ws.send(data);
      } else {
          if (this.state === 3) return;
          if (!num) num = 0;
          if (num < 5) {
              num++;
              setTimeout(function () { that.send(data, num++); }, 100)
          }
      }
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
        
        // $('.terminal').detach().appendTo('#'+this.id);
        this.ws.emit('webssh_websocketio', this.ssh_info);
        this.ws.emit('webssh_websocketio', '\n');
        this.term.focus();
    }
}
