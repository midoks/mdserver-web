function Terms (el, config) {
  if (typeof config == "undefined") config = {};
  this.el = el;
  this.id = config.ssh_info.id || '';
  this.bws = null; //websocket对象
  this.route = '/webssh'; // 访问的方法
  this.term = null; //term对象
  this.info = null; // 请求数据
  this.last_body = null;
  this.fontSize = 15; //终端字体大小
  this.ssh_info = config.ssh_info;
  this.run();
}
Terms.prototype = {
  // websocket持久化连接
  connect: function (callback) {
      var that = this;
      // 判断当前websocket连接是否存在
      if (!this.bws || this.bws.readyState == 3 || this.bws.readyState == 2) {
          this.bws = new WebSocket((window.location.protocol === 'http:' ? 'ws://' : 'wss://') + window.location.host + this.route);
          this.bws.addEventListener('message', function (ev) { that.on_message(ev) });
          this.bws.addEventListener('close', function (ev) { that.on_close(ev) });
          this.bws.addEventListener('error', function (ev) { that.on_error(ev) });
          this.bws.addEventListener('open', function (ev) { that.on_open(ev) });
          if (callback) callback(this.bws)
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
      result = ws_event.data;
      if (!result) return;
      that = this;
      if ((result.indexOf("@127.0.0.1:") != -1 || result.indexOf("@localhost:") != -1) && result.indexOf('Authentication failed') != -1) {
          that.term.write(result);
          host_trem.localhost_login_form(result);
          that.close();
          return;
      }
      if (result.length > 1 && that.last_body === false) {
          that.last_body = true;
      }
      that.term.write(result);
      that.set_term_icon(1);
      if (result == '\r\n登出\r\n' || result == '登出\r\n' || result == '\r\nlogout\r\n' || result == 'logout\r\n') {
          that.close();
          that.bws = null;

      }
  },
  
  //websocket关闭事件
  on_close: function (ws_event) {
      this.set_term_icon(0);
      this.bws = null;
  },

  /**
   * @name 设置终端标题状态
   * @param {number} status 终端状态
   * @return void 
  */
  set_term_icon: function (status) {
      var icon_list = ['icon-warning', 'icon-sucess', 'icon-info'];
      if (status == 1) {
          if ($("[data-id='" + this.id + "']").attr("class").indexOf('active') == -1) {
              status = 2;
          }
      }
      $("[data-id='" + this.id + "']").find('.icon').removeAttr('class').addClass(icon_list[status] + ' icon');
      if (status == 2) {
          that = this;
          setTimeout(function () {
              $("[data-id='" + that.id + "']").find('.icon').removeAttr('class').addClass(icon_list[1] + ' icon');
          }, 200);
      }
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
      if (!this.bws || this.bws.readyState == 3 || this.bws.readyState == 2) {
          this.connect();
      }
      //判断当前连接状态,如果!=1，则100ms后尝试重新发送
      if (this.bws.readyState === 1) {
          this.bws.send(data);
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
      this.bws.close();
      this.set_term_icon(0);
  },
  resize: function (size) {
      if (this.bws) {
          size['resize'] = 1;
          this.send(JSON.stringify(size));
      }

  },
  run: function (ssh_info) {
      var that = this;
      this.term = new Terminal({ fontSize: this.fontSize, screenKeys: true, useStyle: true });
      this.term.setOption('cursorBlink', true);
      this.last_body = false;
      this.term.open($(this.el)[0]);

      // this.term.FitAddon = new window.FitAddon();
      // this.term.loadAddon(this.term.FitAddon);
      // this.term.WebLinksAddon = new WebLinksAddon.WebLinksAddon();
      // this.term.loadAddon(this.term.WebLinksAddon);
      if (ssh_info) this.ssh_info = ssh_info;
      this.connect();
      that.term.onData(function (data) {
          try {
              that.bws.send(data);
          } catch (e) {
              that.term.write('\r\n连接丢失,正在尝试重新连接!\r\n');
              that.connect();
          }
      });
      this.term.focus();
  }
}
