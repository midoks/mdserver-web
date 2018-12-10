
$(document).ready(function() {
	$(".sub-menu a.sub-menu-a").click(function() {
		$(this).next(".sub").slideToggle("slow").siblings(".sub:visible").slideUp("slow");
	});
});

//转换单们到MB
function toSizeM(byteLen) {
    var a = parseInt(byteLen) / 1024 / 1024;
    return a || 0;
}

function randomStrPwd(b) {
	b = b || 32;
	var c = "AaBbCcDdEeFfGHhiJjKkLMmNnPpRSrTsWtXwYxZyz2345678";
	var a = c.length;
	var d = "";
	for(i = 0; i < b; i++) {
		d += c.charAt(Math.floor(Math.random() * a))
	}
	return d
}

function msgTpl(msg, args){
	if (typeof args == 'string'){
		return msg.replace('{1}', args);
	} else if (typeof args == 'object'){
		for (var i = 0; i < args.length; i++) {
			rep = '{' + (i + 1) + '}';
			msg = msg.replace(rep, args[i]);
		}	
	}
	return msg;
}

function refresh() {
	window.location.reload()
}

var mdw = {
};

function repeatPwd(a) {
	$("#MyPassword").val(RandomStrPwd(a))
}



function GetBakPost(b) {
	$(".baktext").hide().prev().show();
	var c = $(".baktext").attr("data-id");
	var a = $(".baktext").val();
	if(a == "") {
		a = lan.bt.empty;
	}
	setWebPs(b, c, a);
	$("a[data-id='" + c + "']").html(a);
	$(".baktext").remove()
}

$(".menu-icon").click(function() {
	$(".sidebar-scroll").toggleClass("sidebar-close");
	$(".main-content").toggleClass("main-content-open");
	if($(".sidebar-close")) {
		$(".sub-menu").find(".sub").css("display", "none")
	}
});
var Upload, percentage;

Date.prototype.format = function(b) {
	var c = {
		"M+": this.getMonth() + 1,
		"d+": this.getDate(),
		"h+": this.getHours(),
		"m+": this.getMinutes(),
		"s+": this.getSeconds(),
		"q+": Math.floor((this.getMonth() + 3) / 3),
		S: this.getMilliseconds()
	};
	if(/(y+)/.test(b)) {
		b = b.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length))
	}
	for(var a in c) {
		if(new RegExp("(" + a + ")").test(b)) {
			b = b.replace(RegExp.$1, RegExp.$1.length == 1 ? c[a] : ("00" + c[a]).substr(("" + c[a]).length))
		}
	}
	return b
};

function getLocalTime(a) {
	a = a.toString();
	if(a.length > 10) {
		a = a.substring(0, 10)
	}
	return new Date(parseInt(a) * 1000).format("yyyy/MM/dd hh:mm:ss")
}

function toSize(a) {
	var d = [" B", " KB", " MB", " GB", " TB", " PB"];
	var e = 1024;
	for(var b = 0; b < d.length; b++) {
		if(a < e) {
			return(b == 0 ? a : a.toFixed(2)) + d[b]
		}
		a /= e
	}
}


function ChangePath(d) {
	setCookie("SetId", d);
	setCookie("SetName", "");
	var c = layer.open({
		type: 1,
		area: "650px",
		title: lan.bt.dir,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='changepath'><div class='path-top'><button type='button' class='btn btn-default btn-sm' onclick='BackFile()'><span class='glyphicon glyphicon-share-alt'></span> "+lan.public.return+"</button><div class='place' id='PathPlace'>"+lan.bt.path+"：<span></span></div></div><div class='path-con'><div class='path-con-left'><dl><dt id='changecomlist' onclick='BackMyComputer()'>"+lan.bt.comp+"</dt></dl></div><div class='path-con-right'><ul class='default' id='computerDefautl'></ul><div class='file-list divtable'><table class='table table-hover' style='border:0 none'><thead><tr class='file-list-head'><th width='40%'>"+lan.bt.filename+"</th><th width='20%'>"+lan.bt.etime+"</th><th width='10%'>"+lan.bt.access+"</th><th width='10%'>"+lan.bt.own+"</th><th width='10%'></th></tr></thead><tbody id='tbody' class='list-list'></tbody></table></div></div></div></div><div class='getfile-btn' style='margin-top:0'><button type='button' class='btn btn-default btn-sm pull-left' onclick='CreateFolder()'>"+lan.bt.adddir+"</button><button type='button' class='btn btn-danger btn-sm mr5' onclick=\"layer.close(getCookie('ChangePath'))\">"+lan.public.close+"</button> <button type='button' class='btn btn-success btn-sm' onclick='GetfilePath()'>"+lan.bt.path_ok+"</button></div>"
	});
	setCookie("ChangePath", c);
	var b = $("#" + d).val();
	tmp = b.split(".");
	if(tmp[tmp.length - 1] == "gz") {
		tmp = b.split("/");
		b = "";
		for(var a = 0; a < tmp.length - 1; a++) {
			b += "/" + tmp[a]
		}
		setCookie("SetName", tmp[tmp.length - 1])
	}
	b = b.replace(/\/\//g, "/");
	GetDiskList(b);
	ActiveDisk()
}

function GetDiskList(b) {
	var d = "";
	var a = "";
	var c = "path=" + b + "&disk=True";
	$.post("/files?action=GetDir", c, function(h) {
		if(h.DISK != undefined) {
			for(var f = 0; f < h.DISK.length; f++) {
				a += "<dd onclick=\"GetDiskList('" + h.DISK[f].path + "')\"><span class='glyphicon glyphicon-hdd'></span>&nbsp;" + h.DISK[f].path + "</dd>"
			}
			$("#changecomlist").html(a)
		}
		for(var f = 0; f < h.DIR.length; f++) {
			var g = h.DIR[f].split(";");
			var e = g[0];
			if(e.length > 20) {
				e = e.substring(0, 20) + "..."
			}
			if(isChineseChar(e)) {
				if(e.length > 10) {
					e = e.substring(0, 10) + "..."
				}
			}
			d += "<tr><td onclick=\"GetDiskList('" + h.PATH + "/" + g[0] + "')\" title='" + g[0] + "'><span class='glyphicon glyphicon-folder-open'></span>" + e + "</td><td>" + getLocalTime(g[2]) + "</td><td>" + g[3] + "</td><td>" + g[4] + "</td><td><span class='delfile-btn' onclick=\"NewDelFile('" + h.PATH + "/" + g[0] + "')\">X</span></td></tr>"
		}
		if(h.FILES != null && h.FILES != "") {
			for(var f = 0; f < h.FILES.length; f++) {
				var g = h.FILES[f].split(";");
				var e = g[0];
				if(e.length > 20) {
					e = e.substring(0, 20) + "..."
				}
				if(isChineseChar(e)) {
					if(e.length > 10) {
						e = e.substring(0, 10) + "..."
					}
				}
				d += "<tr><td title='" + g[0] + "'><span class='glyphicon glyphicon-file'></span>" + e + "</td><td>" + getLocalTime(g[2]) + "</td><td>" + g[3] + "</td><td>" + g[4] + "</td><td></td></tr>"
			}
		}
		$(".default").hide();
		$(".file-list").show();
		$("#tbody").html(d);
		if(h.PATH.substr(h.PATH.length - 1, 1) != "/") {
			h.PATH += "/"
		}
		$("#PathPlace").find("span").html(h.PATH);
		ActiveDisk();
		return
	})
}

function CreateFolder() {
	var a = "<tr><td colspan='2'><span class='glyphicon glyphicon-folder-open'></span> <input id='newFolderName' class='newFolderName' type='text' value=''></td><td colspan='3'><button id='nameOk' type='button' class='btn btn-success btn-sm'>"+lan.public.ok+"</button>&nbsp;&nbsp;<button id='nameNOk' type='button' class='btn btn-default btn-sm'>"+lan.public.cancel+"</button></td></tr>";
	if($("#tbody tr").length == 0) {
		$("#tbody").append(a)
	} else {
		$("#tbody tr:first-child").before(a)
	}
	$(".newFolderName").focus();
	$("#nameOk").click(function() {
		var c = $("#newFolderName").val();
		var b = $("#PathPlace").find("span").text();
		newTxt = b.replace(new RegExp(/(\/\/)/g), "/") + c;
		var d = "path=" + newTxt;
		$.post("/files?action=CreateDir", d, function(e) {
			if(e.status == true) {
				layer.msg(e.msg, {
					icon: 1
				})
			} else {
				layer.msg(e.msg, {
					icon: 2
				})
			}
			GetDiskList(b)
		})
	});
	$("#nameNOk").click(function() {
		$(this).parents("tr").remove()
	})
}

function NewDelFile(c) {
	var a = $("#PathPlace").find("span").text();
	newTxt = c.replace(new RegExp(/(\/\/)/g), "/");
	var b = "path=" + newTxt + "&empty=True";
	$.post("/files?action=DeleteDir", b, function(d) {
		if(d.status == true) {
			layer.msg(d.msg, {
				icon: 1
			})
		} else {
			layer.msg(d.msg, {
				icon: 2
			})
		}
		GetDiskList(a)
	})
}

function ActiveDisk() {
	var a = $("#PathPlace").find("span").text().substring(0, 1);
	switch(a) {
		case "C":
			$(".path-con-left dd:nth-of-type(1)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "D":
			$(".path-con-left dd:nth-of-type(2)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "E":
			$(".path-con-left dd:nth-of-type(3)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "F":
			$(".path-con-left dd:nth-of-type(4)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "G":
			$(".path-con-left dd:nth-of-type(5)").css("background", "#eee").siblings().removeAttr("style");
			break;
		case "H":
			$(".path-con-left dd:nth-of-type(6)").css("background", "#eee").siblings().removeAttr("style");
			break;
		default:
			$(".path-con-left dd").removeAttr("style")
	}
}

function BackMyComputer() {
	$(".default").show();
	$(".file-list").hide();
	$("#PathPlace").find("span").html("");
	ActiveDisk()
}

function BackFile() {
	var c = $("#PathPlace").find("span").text();
	if(c.substr(c.length - 1, 1) == "/") {
		c = c.substr(0, c.length - 1)
	}
	var d = c.split("/");
	var a = "";
	if(d.length > 1) {
		var e = d.length - 1;
		for(var b = 0; b < e; b++) {
			a += d[b] + "/"
		}
		GetDiskList(a.replace("//", "/"))
	} else {
		a = d[0]
	}
	if(d.length == 1) {}
}

function GetfilePath() {
	var a = $("#PathPlace").find("span").text();
	a = a.replace(new RegExp(/(\\)/g), "/");
	$("#" + getCookie("SetId")).val(a + getCookie("SetName"));
	layer.close(getCookie("ChangePath"))
}

function setCookie(a, c) {
	var b = 30;
	var d = new Date();
	d.setTime(d.getTime() + b * 24 * 60 * 60 * 1000);
	document.cookie = a + "=" + escape(c) + ";expires=" + d.toGMTString()
}

function getCookie(b) {
	var a, c = new RegExp("(^| )" + b + "=([^;]*)(;|$)");
	if(a = document.cookie.match(c)) {
		return unescape(a[2])
	} else {
		return null
	}
}

function aotuHeight() {
	var a = $("body").height() - 40;
	$(".main-content").css("min-height", a)
}
$(function() {
	aotuHeight()
});
$(window).resize(function() {
	aotuHeight()
});

function showHidePwd() {
	var a = "glyphicon-eye-open",
		b = "glyphicon-eye-close";
	$(".pw-ico").click(function() {
		var g = $(this).attr("class"),
			e = $(this).prev();
		if(g.indexOf(a) > 0) {
			var h = e.attr("data-pw");
			$(this).removeClass(a).addClass(b);
			e.text(h)
		} else {
			$(this).removeClass(b).addClass(a);
			e.text("**********")
		}
		var d = $(this).next().position().left;
		var f = $(this).next().position().top;
		var c = $(this).next().width();
		$(this).next().next().css({
			left: d + c + "px",
			top: f + "px"
		})
	})
}

function showMsg(msg, callback ,icon, time){

	if (typeof time == 'undefined'){
		time = 2000;
	}

	if (typeof icon == 'undefined'){
		icon = {};
	}

	var loadT = layer.msg(msg, icon);
	setTimeout(function() {
		layer.close(loadT);
		if (typeof callback == 'function'){
			callback();
		}
	}, time);
}

function openPath(a) {
	setCookie("Path", a);
	window.location.href = "/files"
}


function onlineEditFile(k, f) {
	if(k != 0) {
		var l = $("#PathPlace input").val();
		var h = encodeURIComponent($("#textBody").val());
		var a = $("select[name=encoding]").val();
		var loadT = layer.msg(lan.bt.save_file, {
			icon: 16,
			time: 0
		});
		$.post("/files/save_body", "data=" + h + "&path=" + encodeURIComponent(f) + "&encoding=" + a, function(m) {
			if(k == 1) {
				layer.close(loadT);
			}
			layer.msg(m.msg, {
				icon: m.status ? 1 : 2
			});
		},'json');
		return
	}
	var e = layer.msg(lan.bt.read_file, {
		icon: 16,
		time: 0
	});
	var g = f.split(".");
	var b = g[g.length - 1];
	var d;
	switch(b) {
		case "html":
			var j = {
				name: "htmlmixed",
				scriptTypes: [{
					matches: /\/x-handlebars-template|\/x-mustache/i,
					mode: null
				}, {
					matches: /(text|application)\/(x-)?vb(a|script)/i,
					mode: "vbscript"
				}]
			};
			d = j;
			break;
		case "htm":
			var j = {
				name: "htmlmixed",
				scriptTypes: [{
					matches: /\/x-handlebars-template|\/x-mustache/i,
					mode: null
				}, {
					matches: /(text|application)\/(x-)?vb(a|script)/i,
					mode: "vbscript"
				}]
			};
			d = j;
			break;
		case "js":
			d = "text/javascript";
			break;
		case "json":
			d = "application/ld+json";
			break;
		case "css":
			d = "text/css";
			break;
		case "php":
			d = "application/x-httpd-php";
			break;
		case "tpl":
			d = "application/x-httpd-php";
			break;
		case "xml":
			d = "application/xml";
			break;
		case "sql":
			d = "text/x-sql";
			break;
		case "conf":
			d = "text/x-nginx-conf";
			break;
		default:
			var j = {
				name: "htmlmixed",
				scriptTypes: [{
					matches: /\/x-handlebars-template|\/x-mustache/i,
					mode: null
				}, {
					matches: /(text|application)\/(x-)?vb(a|script)/i,
					mode: "vbscript"
				}]
			};
			d = j
	}
	$.post("/files/get_body", "path=" + encodeURIComponent(f), function(s) {
		if(s.status === false){
			layer.msg(s.msg,{icon:5});
			return;
		}
		layer.close(e);
		var u = ["utf-8", "GBK", "GB2312", "BIG5"];
		var n = "";
		var m = "";
		var o = "";
		for(var p = 0; p < u.length; p++) {
			m = s.encoding == u[p] ? "selected" : "";
			n += '<option value="' + u[p] + '" ' + m + ">" + u[p] + "</option>"
		}
		var r = layer.open({
			type: 1,
			shift: 5,
			closeBtn: 2,
			area: ["90%", "90%"],
			title: lan.bt.edit_title+"[" + f + "]",
			content: '<form class="bt-form pd20 pb70"><div class="line"><p style="color:red;margin-bottom:10px">'+lan.bt.edit_ps+'			<select class="bt-input-text" name="encoding" style="width: 74px;position: absolute;top: 31px;right: 19px;height: 22px;z-index: 9999;border-radius: 0;">' + n + '</select></p><textarea class="mCustomScrollbar bt-input-text" id="textBody" style="width:100%;margin:0 auto;line-height: 1.8;position: relative;top: 10px;" value="" />			</div>			<div class="bt-form-submit-btn" style="position:absolute; bottom:0; width:100%">			<button type="button" class="btn btn-danger btn-sm btn-editor-close">'+lan.public.close+'</button>			<button id="OnlineEditFileBtn" type="button" class="btn btn-success btn-sm">'+lan.public.save+'</button>			</div>			</form>'
		});
		$("#textBody").text(s.data.data);
		var q = $(window).height() * 0.9;
		$("#textBody").height(q - 160);
		var t = CodeMirror.fromTextArea(document.getElementById("textBody"), {
			extraKeys: {
				"Ctrl-F": "findPersistent",
				"Ctrl-H": "replaceAll",
				"Ctrl-S": function() {
					$("#textBody").text(t.getValue());
					onlineEditFile(2, f)
				}
			},
			mode: d,
			lineNumbers: true,
			matchBrackets: true,
			matchtags: true,
			autoMatchParens: true
		});
		t.focus();
		t.setSize("auto", q - 150);
		$("#OnlineEditFileBtn").click(function() {
			$("#textBody").text(t.getValue());
			onlineEditFile(1, f);
		});
		$(".btn-editor-close").click(function() {
			layer.close(r);
		});
	},'json');
}

function divcenter() {
	$(".layui-layer").css("position", "absolute");
	var c = $(window).width();
	var b = $(".layui-layer").outerWidth();
	var g = $(window).height();
	var f = $(".layui-layer").outerHeight();
	var a = (c - b) / 2;
	var e = (g - f) / 2 > 0 ? (g - f) / 2 : 10;
	var d = $(".layui-layer").offset().left - $(".layui-layer").position().left;
	var h = $(".layui-layer").offset().top - $(".layui-layer").position().top;
	a = a + $(window).scrollLeft() - d;
	e = e + $(window).scrollTop() - h;
	$(".layui-layer").css("left", a + "px");
	$(".layui-layer").css("top", e + "px")
}

function btcopy(password) {
	$("#bt_copys").attr('data-clipboard-text',password);
	$("#bt_copys").click();
}

var clipboard = new ClipboardJS('#bt_copys');
clipboard.on('success', function (e) {
    layer.msg('复制成功!',{icon:1});
});

clipboard.on('error', function (e) {
    layer.msg('复制失败，浏览器不兼容!',{icon:2});
});

function isChineseChar(b) {
	var a = /[\u4E00-\u9FA5\uF900-\uFA2D]/;
	return a.test(b)
}

function SafeMessage(j, h, g, f) {
	if(f == undefined) {
		f = ""
	}
	var d = Math.round(Math.random() * 9 + 1);
	var c = Math.round(Math.random() * 9 + 1);
	var e = "";
	e = d + c;
	sumtext = d + " + " + c;
	setCookie("vcodesum", e);
	var mess = layer.open({
		type: 1,
		title: j,
		area: "350px",
		closeBtn: 2,
		shadeClose: true,
		content: "<div class='bt-form webDelete pd20 pb70'><p>" + h + "</p>" + f + "<div class='vcode'>"+lan.bt.cal_msg+"<span class='text'>" + sumtext + "</span>=<input type='number' id='vcodeResult' value=''></div><div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm bt-cancel'>"+lan.public.cancel+"</button> <button type='button' id='toSubmit' class='btn btn-success btn-sm' >"+lan.public.ok+"</button></div></div>"
	});
	$("#vcodeResult").focus().keyup(function(a) {
		if(a.keyCode == 13) {
			$("#toSubmit").click()
		}
	});
	$(".bt-cancel").click(function(){
		layer.close(mess);
	});
	$("#toSubmit").click(function() {
		var a = $("#vcodeResult").val().replace(/ /g, "");
		if(a == undefined || a == "") {
			layer.msg('请正确输入计算结果!');
			return
		}
		if(a != getCookie("vcodesum")) {
			layer.msg('请正确输入计算结果!');
			return
		}
		layer.close(mess);
		g();
	})
}
//isAction();

function isAction() {
	hrefs = window.location.href.split("/");
	name = hrefs[hrefs.length - 1];
	if(!name) {
		$("#memuA").addClass("current");
		return
	}
	$("#memuA" + name).addClass("current")
}
var W_window = $(window).width();
if(W_window <= 980) {
	$(window).scroll(function() {
		var a = $(window).scrollTop();
		$(".sidebar-scroll").css({
			position: "absolute",
			top: a
		})
	})
} else {
	$(".sidebar-scroll").css({
		position: "fixed",
		top: "0"
	})
}
$(function() {
	$(".fb-ico").hover(function() {
		$(".fb-text").css({
			left: "36px",
			top: 0,
			width: "80px"
		})
	}, function() {
		$(".fb-text").css({
			left: 0,
			width: "36px"
		})
	}).click(function() {
		$(".fb-text").css({
			left: 0,
			width: "36px"
		});
		$(".zun-feedback-suggestion").show()
	});
	$(".fb-close").click(function() {
		$(".zun-feedback-suggestion").hide()
	});
	$(".fb-attitudes li").click(function() {
		$(this).addClass("fb-selected").siblings().removeClass("fb-selected")
	})
});
$("#dologin").click(function() {
	layer.confirm(lan.bt.loginout, {icon:3,
		closeBtn: 2
	}, function() {
		window.location.href = "/login?dologin=True"
	});
	return false
});

function setPassword(a) {
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		if(p1 == "" || p1.length < 8) {
			layer.msg(lan.bt.pass_err_len, {
				icon: 2
			});
			return
		}
		
		//准备弱口令匹配元素
		var checks = ['admin888','123123123','12345678','45678910','87654321','asdfghjkl','password','qwerqwer'];
		pchecks = 'abcdefghijklmnopqrstuvwxyz1234567890';
		for(var i=0;i<pchecks.length;i++){
			checks.push(pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]+pchecks[i]);
		}
		
		//检查弱口令
		cps = p1.toLowerCase();
		var isError = "";
		for(var i=0;i<checks.length;i++){
			if(cps == checks[i]){
				isError += '['+checks[i]+'] ';
			}
		}
		
		if(isError != ""){
			layer.msg(lan.bt.pass_err+isError,{icon:5});
			return;
		}
		
		
		if(p1 != p2) {
			layer.msg(lan.bt.pass_err_re, {
				icon: 2
			});
			return
		}
		$.post("/config?action=setPassword", "password1=" + encodeURIComponent(p1) + "&password2=" + encodeURIComponent(p2), function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {
					icon: 1
				})
			} else {
				layer.msg(b.msg, {
					icon: 2
				})
			}
		});
		return
	}
	layer.open({
		type: 1,
		area: "290px",
		title: lan.bt.pass_title,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'><div class='line'><span class='tname'>"+lan.public.pass+"</span><div class='info-r'><input class='bt-input-text' type='text' name='password1' id='p1' value='' placeholder='"+lan.bt.pass_new_title+"' style='width:100%'/></div></div><div class='line'><span class='tname'>"+lan.bt.pass_re+"</span><div class='info-r'><input class='bt-input-text' type='text' name='password2' id='p2' value='' placeholder='"+lan.bt.pass_re_title+"' style='width:100%' /></div></div><div class='bt-form-submit-btn'><span style='float: left;' title='"+lan.bt.pass_rep+"' class='btn btn-default btn-sm' onclick='randPwd(10)'>"+lan.bt.pass_rep_btn+"</span><button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">"+lan.public.close+"</button> <button type='button' class='btn btn-success btn-sm' onclick=\"setPassword(1)\">"+lan.public.edit+"</button></div></div>"
	});
}


function randPwd(){
	var pwd = RandomStrPwd(12);
	$("#p1").val(pwd);
	$("#p2").val(pwd);
	layer.msg(lan.bt.pass_rep_ps,{time:2000})
}

function setUserName(a) {
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		if(p1 == "" || p1.length < 3) {
			layer.msg(lan.bt.user_len, {
				icon: 2
			});
			return
		}
		if(p1 != p2) {
			layer.msg(lan.bt.user_err_re, {
				icon: 2
			});
			return
		}
		$.post("/config?action=setUsername", "username1=" + encodeURIComponent(p1) + "&username2=" + encodeURIComponent(p2), function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {
					icon: 1
				});
				$("input[name='username_']").val(p1)
			} else {
				layer.msg(b.msg, {
					icon: 2
				})
			}
		});
		return
	}
	layer.open({
		type: 1,
		area: "290px",
		title: lan.bt.user_title,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'><div class='line'><span class='tname'>"+lan.bt.user+"</span><div class='info-r'><input class='bt-input-text' type='text' name='password1' id='p1' value='' placeholder='"+lan.bt.user_new+"' style='width:100%'/></div></div><div class='line'><span class='tname'>"+lan.bt.pass_re+"</span><div class='info-r'><input class='bt-input-text' type='text' name='password2' id='p2' value='' placeholder='"+lan.bt.pass_re_title+"' style='width:100%'/></div></div><div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">"+lan.public.close+"</button> <button type='button' class='btn btn-success btn-sm' onclick=\"setUserName(1)\">"+lan.public.edit+"</button></div></div>"
	})
}
var openWindow = null;
var downLoad = null;
var speed = null;

function task() {
	messagebox();
}

function ActionTask() {
	var a = layer.msg(lan.public.the_del, {
		icon: 16,
		time: 0,
		shade: [0.3, "#000"]
	});
	$.post("/files?action=ActionTask", "", function(b) {
		layer.close(a);
		layer.msg(b.msg, {
			icon: b.status ? 1 : 5
		})
	})
}

function RemoveTask(b) {
	var a = layer.msg(lan.public.the_del, {
		icon: 16,
		time: 0,
		shade: [0.3, "#000"]
	});
	$.post("/files?action=RemoveTask", "id=" + b, function(c) {
		layer.close(a);
		layer.msg(c.msg, {
			icon: c.status ? 1 : 5
		});
	}).error(function(){
		layer.msg(lan.bt.task_close,{icon:1});
	});
}

function GetTaskList(a) {
	a = a == undefined ? 1 : a;
	$.post("/task/list", "tojs=GetTaskList&table=tasks&limit=10&p=" + a, function(g) {
		console.log(g);
		var e = "";
		var b = "";
		var c = "";
		var f = false;
		for(var d = 0; d < g.data.length; d++) {
			switch(g.data[d].status) {
				case "-1":
					f = true;
					if(g.data[d].type != "download") {
						b = "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state'>"+lan.bt.task_install+" <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + g.data[d].id + ")\">"+lan.public.close+"</a></span><span class='opencmd'></span><pre class='cmd'></pre></li>"
					} else {
						b = "<li><div class='line-progress' style='width:0%'></div><span class='titlename'>" + g.data[d].name + "<a id='speed' style='margin-left:130px;'>0.0M/12.5M</a></span><span class='com-progress'>0%</span><span class='state'>"+lan.bt.task_downloading+" <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + g.data[d].id + ")\">"+lan.public.close+"</a></span></li>"
					}
					break;
				case "0":
					c += "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state'>"+lan.bt.task_sleep+"</span> | <a href=\"javascript:RemoveTask(" + g.data[d].id + ")\">"+lan.public.del+"</a></li>";
					break;
				case "1":
					e += "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state'>" + g.data[d].addtime + "  "+lan.bt.task_ok+"  "+ lan.bt.time + (g.data[d].end - g.data[d].start) + lan.bt.s+"</span></li>"
			}
		}
		$("#srunning").html(b + c);
		$("#sbody").html(e);
		return f
	})
}

function getTaskCount() {
	$.get("/task/count", "", function(a) {
		$(".task").text(a)
	})
}

function setSelectChecked(c, d) {
	var a = document.getElementById(c);
	for(var b = 0; b < a.options.length; b++) {
		if(a.options[b].innerHTML == d) {
			a.options[b].selected = true;
			break
		}
	}
}
getTaskCount();
function RecInstall() {
	$.post("/ajax?action=GetSoftList", "", function(l){
		var c = "";
		var g = "";
		var e = "";
		for(var h = 0; h < l.length; h++) {
			if(l[h].name == "Tomcat") {
				continue
			}
			var o = "";
			var m = "<input id='data_" + l[h].name + "' data-info='" + l[h].name + " " + l[h].versions[0].version + "' type='checkbox' checked>";
			for(var b = 0; b < l[h].versions.length; b++) {
				var d = "";
				if((l[h].name == "PHP" && (l[h].versions[b].version == "5.4" || l[h].versions[b].version == "54")) || (l[h].name == "MySQL" && l[h].versions[b].version == "5.5") || (l[h].name == "phpMyAdmin" && l[h].versions[b].version == "4.4")) {
					d = "selected";
					m = "<input id='data_" + l[h].name + "' data-info='" + l[h].name + " " + l[h].versions[b].version + "' type='checkbox' checked>"
				}
				o += "<option value='" + l[h].versions[b].version + "' " + d + ">" + l[h].name + " " + l[h].versions[b].version + "</option>"
			}
			var f = "<li><span class='ico'><img src='/static/img/" + l[h].name.toLowerCase() + ".png'></span><span class='name'><select id='select_" + l[h].name + "' class='sl-s-info'>" + o + "</select></span><span class='pull-right'>" + m + "</span></li>";
			if(l[h].name == "Nginx") {
				c = f
			} else {
				if(l[h].name == "Apache") {
					g = f
				} else {
					e += f
				}
			}
		}
		c += e;
		g += e;
		g = g.replace(new RegExp(/(data_)/g), "apache_").replace(new RegExp(/(select_)/g), "apache_select_");
		var k = layer.open({
			type: 1,
			title: lan.bt.install_title,
			area: ["658px", "423px"],
			closeBtn: 2,
			shadeClose: false,
			content: "<div class='rec-install'><div class='important-title'><p><span class='glyphicon glyphicon-alert' style='color: #f39c12; margin-right: 10px;'></span>"+lan.bt.install_ps+" <a href='javascript:jump()' style='color:#20a53a'>"+lan.bt.install_s+"</a> "+lan.bt.install_s1+"</p></div><div class='rec-box'><h3>"+lan.bt.install_lnmp+"</h3><div class='rec-box-con'><ul class='rec-list'>" + c + "</ul><p class='fangshi'>"+lan.bt.install_type+"：<label data-title='"+lan.bt.install_rpm_title+"' style='margin-right:0'>"+lan.bt.install_rpm+"<input type='checkbox' checked></label><label data-title='"+lan.bt.install_src_title+"'>"+lan.bt.install_src+"<input type='checkbox'></label></p><div class='onekey'>"+lan.bt.install_key+"</div></div></div><div class='rec-box' style='margin-left:16px'><h3>LAMP</h3><div class='rec-box-con'><ul class='rec-list'>" + g + "</ul><p class='fangshi'>"+lan.bt.install_type+"：<label data-title='"+lan.bt.install_rpm_title+"' style='margin-right:0'>"+lan.bt.install_rpm+"<input type='checkbox' checked></label><label data-title='"+lan.bt.install_src_title+"'>"+lan.bt.install_src+"<input type='checkbox'></label></p><div class='onekey'>一键安装</div></div></div></div>"
		});
		$(".fangshi input").click(function() {
			$(this).attr("checked", "checked").parent().siblings().find("input").removeAttr("checked")
		});
		$(".sl-s-info").change(function() {
			var p = $(this).find("option:selected").text();
			var n = $(this).attr("id");
			p = p.toLowerCase();
			$(this).parents("li").find("input").attr("data-info", p)
		});
		$("#apache_select_PHP").change(function() {
			var n = $(this).val();
			j(n, "apache_select_", "apache_")
		});
		$("#select_PHP").change(function() {
			var n = $(this).val();
			j(n, "select_", "data_")
		});

		function j(p, r, q) {
			var n = "4.4";
			switch(p) {
				case "5.2":
					n = "4.0";
					break;
				case "5.3":
					n = "4.0";
					break;
				case "5.4":
					n = "4.4";
					break;
				case "5.5":
					n = "4.4";
					break;
				default:
					n = "4.7"
			}
			$("#" + r + "phpMyAdmin option[value='" + n + "']").attr("selected", "selected").siblings().removeAttr("selected");
			$("#" + r + "_phpMyAdmin").attr("data-info", "phpmyadmin " + n)
		}
		$("#select_MySQL,#apache_select_MySQL").change(function() {
			var n = $(this).val();
			a(n)
		});
		
		$("#apache_select_Apache").change(function(){
			var apacheVersion = $(this).val();
			if(apacheVersion == '2.2'){
				layer.msg(lan.bt.install_apache22);
			}else{
				layer.msg(lan.bt.install_apache24);
			}
		});
		
		$("#apache_select_PHP").change(function(){
			var apacheVersion = $("#apache_select_Apache").val();
			var phpVersion = $(this).val();
			if(apacheVersion == '2.2'){
				if(phpVersion != '5.2' && phpVersion != '5.3' && phpVersion != '5.4'){
					layer.msg(lan.bt.insatll_s22+'PHP-' + phpVersion,{icon:5});
					$(this).val("5.4");
					$("#apache_PHP").attr('data-info','php 5.4');
					return false;
				}
			}else{
				if(phpVersion == '5.2'){
					layer.msg(lan.bt.insatll_s24+'PHP-' + phpVersion,{icon:5});
					$(this).val("5.4");
					$("#apache_PHP").attr('data-info','php 5.4');
					return false;
				}
			}
		});

		function a(n) {
			memSize = getCookie("memSize");
			max = 64;
			msg = "64M";
			switch(n) {
				case "5.1":
					max = 256;
					msg = "256M";
					break;
				case "5.7":
					max = 1500;
					msg = "2GB";
					break;
				case "5.6":
					max = 800;
					msg = "1GB";
					break;
				case "AliSQL":
					max = 800;
					msg = "1GB";
					break;
				case "mariadb_10.0":
					max = 800;
					msg = "1GB";
					break;
				case "mariadb_10.1":
					max = 1500;
					msg = "2GB";
					break
			}
			if(memSize < max) {
				layer.msg( lan.bt.insatll_mem.replace("{1}",msg).replace("{2}",n), {
					icon: 5
				})
			}
		}
		var de = null;
		$(".onekey").click(function() {
			if(de) return;
			var v = $(this).prev().find("input").eq(0).prop("checked") ? "1" : "0";
			var r = $(this).parents(".rec-box-con").find(".rec-list li").length;
			var n = "";
			var q = "";
			var p = "";
			var x = "";
			var s = "";
			de = true;
			for(var t = 0; t < r; t++) {
				var w = $(this).parents(".rec-box-con").find("ul li").eq(t);
				var u = w.find("input");
				if(u.prop("checked")) {
					n += u.attr("data-info") + ","
				}
			}
			q = n.split(",");
			loadT = layer.msg(lan.bt.install_to, {
				icon: 16,
				time: 0,
				shade: [0.3, "#000"]
			});
			for(var t = 0; t < q.length - 1; t++) {
				p = q[t].split(" ")[0].toLowerCase();
				x = q[t].split(" ")[1];
				s = "name=" + p + "&version=" + x + "&type=" + v + "&id=" + (t + 1);
				$.ajax({
					url: "/files?action=InstallSoft",
					data: s,
					type: "POST",
					async: false,
					success: function(y) {}
				});
			}
			layer.close(loadT);
			layer.close(k);
			setTimeout(function() {
				getTaskCount()
			}, 2000);
			layer.msg(lan.bt.install_ok, {
				icon: 1
			});
			setTimeout(function() {
				task()
			}, 1000)
		});
		InstallTips();
		fly("onekey")
	})
}

function jump() {
	layer.closeAll();
	window.location.href = "/soft"
}

function InstallTips() {
	$(".fangshi label").mouseover(function() {
		var a = $(this).attr("data-title");
		layer.tips(a, this, {
			tips: [1, "#787878"],
			time: 0
		})
	}).mouseout(function() {
		$(".layui-layer-tips").remove()
	})
}

function fly(a) {
	var b = $("#task").offset();
	$("." + a).click(function(d) {
		var e = $(this);
		var c = $('<span class="yuandian"></span>');
		c.fly({
			start: {
				left: d.pageX,
				top: d.pageY
			},
			end: {
				left: b.left + 10,
				top: b.top + 10,
				width: 0,
				height: 0
			},
			onEnd: function() {
				layer.closeAll();
				layer.msg(lan.bt.task_add, {
					icon: 1
				});
				getTaskCount()
			}
		});
	});
};


//检查选中项
function checkSelect(){
	setTimeout(function(){
		var checkList = $("input[name=id]");
		var count = 0;
		for(var i=0;i<checkList.length;i++){
			if(checkList[i].checked) count++;
		}
		if(count > 0){
			$("#allDelete").show();
		}else{
			$("#allDelete").hide();
		}
	},5);
}

//处理排序
function listOrder(skey,type,obj){
	or = getCookie('order');
	orderType = 'desc';
	if(or){
		if(or.split(' ')[1] == 'desc'){
			orderType = 'asc';
		}
	}
	
	setCookie('order',skey + ' ' + orderType);
	
	switch(type){
		case 'site':
			getWeb(1);
			break;
		case 'database':
			getData(1);
			break;
		case 'ftp':
			getFtp(1);
			break;
	}
	$(obj).find(".glyphicon-triangle-bottom").remove();
	$(obj).find(".glyphicon-triangle-top").remove();
	if(orderType == 'asc'){
		$(obj).append("<span class='glyphicon glyphicon-triangle-bottom' style='margin-left:5px;color:#bbb'></span>");
	}else{
		$(obj).append("<span class='glyphicon glyphicon-triangle-top' style='margin-left:5px;color:#bbb'></span>");
	}
}

//添加面板快捷登录
function bindBTPanel(a,type,ip,btid,url,user,pw){
	var titleName = lan.bt.panel_add;
	if(type == "b"){
		btn = "<button type='button' class='btn btn-success btn-sm' onclick=\"bindBTPanel(1,'b')\">"+lan.public.add+"</button>";
	}
	else{
		titleName = lan.bt.panel_edit+ip;
		btn = "<button type='button' class='btn btn-default btn-sm' onclick=\"bindBTPaneldel('"+btid+"')\">"+lan.public.del+"</button><button type='button' class='btn btn-success btn-sm' onclick=\"bindBTPanel(1,'c','"+ip+"','"+btid+"')\" style='margin-left:7px'>"+lan.public.edit+"</button>";
	}
	if(url == undefined) url="http://";
	if(user == undefined) user="";
	if(pw == undefined) pw="";
	if(ip == undefined) ip="";
	if(a == 1) {
		var gurl = "/config?action=AddPanelInfo";
		var btaddress = $("#btaddress").val();
		if(!btaddress.match(/^(http|https)+:\/\/([\w-]+\.)+[\w-]+:\d+/)){
			layer.msg(lan.bt.panel_err_format+'<p>http://192.168.0.1:8888</p>',{icon:5,time:5000});
			return;
		}
		var btuser = encodeURIComponent($("#btuser").val());
		var btpassword = encodeURIComponent($("#btpassword").val());
		var bttitle = $("#bttitle").val();
		var data = "title="+bttitle+"&url="+encodeURIComponent(btaddress)+"&username="+btuser+"&password="+btpassword;
		if(btaddress =="" || btuser=="" || btpassword=="" || bttitle==""){
			layer.msg(lan.bt.panel_err_empty,{icon:8});
			return;
		}
		if(type=="c"){
			gurl = "/config?action=SetPanelInfo";
			data = data+"&id="+btid;
		}
		$.post(gurl, data, function(b) {
			if(b.status) {
				layer.closeAll();
				layer.msg(b.msg, {icon: 1});
				GetBtpanelList();
			} else {
				layer.msg(b.msg, {icon: 2})
			}
		});
		return
	}
	layer.open({
		type: 1,
		area: "400px",
		title: titleName,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb70'>\
		<div class='line'><span class='tname'>"+lan.bt.panel_address+"</span>\
		<div class='info-r'><input class='bt-input-text' type='text' name='btaddress' id='btaddress' value='"+url+"' placeholder='"+lan.bt.panel_address+"' style='width:100%'/></div>\
		</div>\
		<div class='line'><span class='tname'>"+lan.bt.panel_user+"</span>\
		<div class='info-r'><input class='bt-input-text' type='text' name='btuser' id='btuser' value='"+user+"' placeholder='"+lan.bt.panel_user+"' style='width:100%'/></div>\
		</div>\
		<div class='line'><span class='tname'>"+lan.bt.panel_pass+"</span>\
		<div class='info-r'><input class='bt-input-text' type='password' name='btpassword' id='btpassword' value='"+pw+"' placeholder='"+lan.bt.panel_pass+"' style='width:100%'/></div>\
		</div>\
		<div class='line'><span class='tname'>"+lan.bt.panel_ps+"</span>\
		<div class='info-r'><input class='bt-input-text' type='text' name='bttitle' id='bttitle' value='"+ip+"' placeholder='"+lan.bt.panel_ps+"' style='width:100%'/></div>\
		</div>\
		<div class='line'><ul class='help-info-text c7'><li>"+lan.bt.panel_ps_1+"</li><li>"+lan.bt.panel_ps_2+"</li><li>"+lan.bt.panel_ps_3+"</li></ul></div>\
		<div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm' onclick=\"layer.closeAll()\">"+lan.public.close+"</button> "+btn+"</div></div>"
	});
	$("#btaddress").on("input",function(){
		var str =$(this).val();
		var isip = /([\w-]+\.){2,6}\w+/;
		var iptext = str.match(isip);
		if(iptext) $("#bttitle").val(iptext[0]);
	}).blur(function(){
		var str =$(this).val();
		var isip = /([\w-]+\.){2,6}\w+/;
		var iptext = str.match(isip);
		if(iptext) $("#bttitle").val(iptext[0]);
	});
}
//删除快捷登录
function bindBTPaneldel(id){
	$.post("/config?action=DelPanelInfo","id="+id,function(rdata){
		layer.closeAll();
		layer.msg(rdata.msg,{icon:rdata.status?1:2});
		GetBtpanelList();
	})
}

function getSpeed(sele){
	if(!$(sele)) return;
	$.get('/ajax?action=GetSpeed',function(speed){
		if(speed.title === null) return;
		mspeed = '';
		if(speed.speed > 0){
			mspeed = '<span class="pull-right">'+ToSize(speed.speed)+'/s</span>';
		}
		body = '<p>'+speed.title+' <img src="/static/img/ing.gif"></p>\
		<div class="bt-progress"><div class="bt-progress-bar" style="width:'+speed.progress+'%"><span class="bt-progress-text">'+speed.progress+'%</span></div></div>\
		<p class="f12 c9"><span class="pull-left">'+speed.used+'/'+speed.total+'</span>'+mspeed+'</p>';
		$(sele).prev().hide();
		$(sele).css({"margin-left":"-37px","width":"380px"});
		$(sele).parents(".layui-layer").css({"margin-left":"-100px"});
		
		$(sele).html(body);
		setTimeout(function(){
			getSpeed(sele);
		},1000);
	});
}
//消息盒子
function messagebox() {
	layer.open({
		type: 1,
		title: lan.bt.task_title,
		area: "640px",
		closeBtn: 2,
		shadeClose: false,
		content: '<div class="bt-form">\
					<div class="bt-w-main">\
						<div class="bt-w-menu">\
							<p class="bgw" id="taskList" onclick="tasklist()">'+lan.bt.task_list+'(<span class="task_count">0</span>)</p>\
							<p onclick="remind()">'+lan.bt.task_msg+'(<span class="msg_count">0</span>)</p>\
							<p onclick="execLog()">执行日志</p>\
						</div>\
						<div class="bt-w-con pd15">\
							<div class="taskcon"></div>\
						</div>\
					</div>\
				</div>'
	});
	$(".bt-w-menu p").click(function(){
		$(this).addClass("bgw").siblings().removeClass("bgw");
	});
	tasklist();
}

//取执行日志
function execLog(){
	$.post('/task/get_exec_log',{},function(logs){
		var lbody = '<textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="exec_log">'+logs+'</textarea>';
		$(".taskcon").html(lbody);
		var ob = document.getElementById('exec_log');
		ob.scrollTop = ob.scrollHeight;
	});
}

function remind(a){
	a = a == undefined ? 1 : a;
	$.post("/task/list", "tojs=remind&table=tasks&result=2,4,6,8&limit=8&p=" + a, function(g) {
		var e = "";
		var f = false;
		var task_count = 0;
		for(var d = 0; d < g.data.length; d++) {
			if(g.data[d].status != '1'){
				task_count++;
				continue;
			}
			e += '<tr><td><input type="checkbox"></td><td><div class="titlename c3">'+g.data[d].name+'</span><span class="rs-status">【'+lan.bt.task_ok+'】<span><span class="rs-time">'+ lan.bt.time + (g.data[d].end - g.data[d].start) + lan.bt.s+'</span></div></td><td class="text-right c3">'+g.data[d].addtime+'</td></tr>'
		}
		var con = '<div class="divtable"><table class="table table-hover">\
					<thead><tr><th width="20"><input id="Rs-checkAll" type="checkbox" onclick="RscheckSelect()"></th><th>'+lan.bt.task_name+'</th><th class="text-right">'+lan.bt.task_time+'</th></tr></thead>\
					<tbody id="remind">'+e+'</tbody>\
					</table></div>\
					<div class="mtb15" style="height:32px">\
						<div class="pull-left buttongroup" style="display:none;"><button class="btn btn-default btn-sm mr5 rs-del" disabled="disabled">'+lan.public.del+'</button><button class="btn btn-default btn-sm mr5 rs-read" disabled="disabled">'+lan.bt.task_tip_read+'</button><button class="btn btn-default btn-sm">'+lan.bt.task_tip_all+'</button></div>\
						<div id="taskPage" class="page"></div>\
					</div>';
		
		$(".task_count").text(task_count);
		$(".msg_count").text(g.data.length);
		$(".taskcon").html(con);
		$("#taskPage").html(g.page);
		$("#Rs-checkAll").click(function(){
			if($(this).prop("checked")){
				$("#remind").find("input").prop("checked",true)
			}
			else{
				$("#remind").find("input").prop("checked",false)
			}
		});

	},'json');
}


function GetReloads() {
	var a = 0;
	var mm = $(".bt-w-menu .bgw").html()
	if(mm == undefined || mm.indexOf(lan.bt.task_list) == -1) {
		clearInterval(speed);
		a = 0;
		speed = null;
		return
	}
	if(speed) return;
	speed = setInterval(function() {
		var mm = $(".bt-w-menu .bgw").html()
		if(mm == undefined || mm.indexOf(lan.bt.task_list) == -1) {
			clearInterval(speed);
			speed = null;
			a = 0;
			return
		}
		a++;
		$.post("/task/get_task_speed", "", function(h) {
			if(h.task == undefined) {
				$(".cmdlist").html(lan.bt.task_not_list);
				return
			}
			var b = "";
			var d = "";
			$("#task").text(h.task.length);
			$(".task_count").text(h.task.length);
			for(var g = 0; g < h.task.length; g++) {
				if(h.task[g].status == "-1") {
					if(h.task[g].type != "download") {
						var c = "";
						var f = h.msg.split("\n");
						for(var e = 0; e < f.length; e++) {
							c += f[e] + "<br>"
						}
						if(h.task[g].name.indexOf("扫描") != -1) {
							b = "<li><span class='titlename'>" + h.task[g].name + "</span><span class='state'>"+lan.bt.task_scan+" <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + h.task[g].id + ")\">"+lan.public.close+"</a></span><span class='opencmd'></span><div class='cmd'>" + c + "</div></li>"
						} else {
							b = "<li><span class='titlename'>" + h.task[g].name + "</span><span class='state'>"+lan.bt.task_install+" <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + h.task[g].id + ")\">"+lan.public.close+"</a></span><div class='cmd'>" + c + "</div></li>"
						}
					} else {
						b = "<li><div class='line-progress' style='width:" + h.msg.pre + "%'></div><span class='titlename'>" + h.task[g].name + "<a style='margin-left:130px;'>" + (ToSize(h.msg.used) + "/" + ToSize(h.msg.total)) + "</a></span><span class='com-progress'>" + h.msg.pre + "%</span><span class='state'>"+lan.bt.task_downloading+" <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + h.task[g].id + ")\">"+lan.public.close+"</a></span></li>"
					}
				} else {
					d += "<li><span class='titlename'>" + h.task[g].name + "</span><span class='state'>"+lan.bt.task_sleep+" | <a style='color:green' href=\"javascript:RemoveTask(" + h.task[g].id + ')">'+lan.public.del+'</a></span></li>'
				}
			}
			$(".cmdlist").html(b + d);
			$(".cmd").html(c);
			try{
				if($(".cmd")[0].scrollHeight) $(".cmd").scrollTop($(".cmd")[0].scrollHeight);
			}catch(e){
				return;
			}
		},'json').error(function(){});
	}, 1000);
}

//检查选中项
function RscheckSelect(){
	setTimeout(function(){
		var checkList = $("#remind").find("input");
		var count = 0;
		for(var i=0;i<checkList.length;i++){
			if(checkList[i].checked) count++;
		}
		if(count > 0){
			$(".buttongroup .btn").removeAttr("disabled");
		}else{
			$(".rs-del,.rs-read").attr("disabled","disabled");
		}
	},5);
}


function tasklist(a){
	var con='<ul class="cmdlist"></ul><span style="position:  fixed;bottom: 13px;">若任务长时间未执行，请尝试在首页点【重启面板】来重置任务队列</span>';
	$(".taskcon").html(con);
	a = a == undefined ? 1 : a;
	$.post("/task/list", "tojs=GetTaskList&table=tasks&limit=10&p=" + a, function(g) {
		var e = "";
		var b = "";
		var c = "";
		var f = false;
		var task_count =0;
		for(var d = 0; d < g.data.length; d++) {
			switch(g.data[d].status) {
				case "-1":
					f = true;
					if(g.data[d].type != "download") {
						b = "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state pull-right c6'>"+lan.bt.task_install+" <img src='/static/img/ing.gif'> | <a class='btlink' href=\"javascript:RemoveTask(" + g.data[d].id + ")\">"+lan.public.close+"</a></span><span class='opencmd'></span><pre class='cmd'></pre></li>"
					} else {
						b = "<li><div class='line-progress' style='width:0%'></div><span class='titlename'>" + g.data[d].name + "<a id='speed' style='margin-left:130px;'>0.0M/12.5M</a></span><span class='com-progress'>0%</span><span class='state'>"+lan.bt.task_downloading+" <img src='/static/img/ing.gif'> | <a href=\"javascript:RemoveTask(" + g.data[d].id + ")\">"+lan.public.close+"</a></span></li>"
					}
					task_count++;
					break;
				case "0":
					c += "<li><span class='titlename'>" + g.data[d].name + "</span><span class='state pull-right c6'>"+lan.bt.task_sleep+"</span> | <a href=\"javascript:RemoveTask(" + g.data[d].id + ")\" class='btlink'>"+lan.public.del+"</a></li>";
					task_count++;
					break;
			}
		}
		
		
		$(".task_count").text(task_count);
		$(".cmdlist").html(b + c);
		GetReloads();
		return f
	},'json')
}

//检查登陆状态
function check_login(){
	$.post('/check_login',{},function(rdata){
		if(rdata === true) return;
	});
}



//登陆跳转
function to_login(){
	layer.confirm('您的登陆状态已过期，请重新登陆!',{title:'会话已过期',icon:2,closeBtn: 1,shift: 5},function(){
		location.reload();
	});
}
//表格头固定
function table_fixed(name){
	var tableName = document.querySelector('#'+name);
	tableName.addEventListener('scroll',scroll_handle);
}
function scroll_handle(e){
	var scrollTop = this.scrollTop;
	$(this).find("thead").css({"transform":"translateY("+scrollTop+"px)","position":"relative","z-index":"1"});
}


$(function(){
	setInterval(function(){
		check_login();
	},60000);
});


function asyncLoadImage(obj, url){
	
	if (typeof(url) == 'undefined'){
		return;
	}
	loadImage(obj, url, showImage);

	function loadImage(obj,url,callback){
	    var img = new Image();
	    img.src = url;
	    
	    if(img.complete){
	        callback.call(img,obj);
	        return;
	    }
	    img.onload = function(){
	        callback.call(img,obj);
	    }
	}

	function showImage(obj){
	    obj.src = this.src;
	}
}

function loadImage(){
	$('img').each(function(i){
		// console.log($(this).attr('data-src'));
		if ($(this).attr('data-src') != ''){
			asyncLoadImage(this, $(this).attr('data-src'));
		} 
    });
}

/*** 其中功能,针对插件通过库使用 start ***/
function pluginService(_name, version){
	var data = {name:_name, func:'status'}
	if ( typeof(version) != 'undefined' ){
		data['version'] = version;
	} else {
		version = '';
	}
	// console.log(version);

	$.post('/plugins/run', data, function(data) {
        if(!data.status){
            layer.msg(data.msg,{icon:0,time:3000,shade: [0.3, '#000']});
            return;
        }
        if (data.data == 'start'){
            pluginSetService(_name, true, version);
        } else {
            pluginSetService(_name, false, version);
        }
    },'json');
}

function pluginSetService(_name ,status, version){
	var serviceCon ='<p class="status">当前状态：<span>'+(status ? '开启' : '关闭' )+
        '</span><span style="color: '+
        (status?'#20a53a;':'red;')+
        ' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="pluginOpService(\''+_name+'\',\''+(status?'stop':'start')+'\',\''+version+'\')">'+(status?'停止':'启动')+'</button>\
            <button class="btn btn-default btn-sm" onclick="pluginOpService(\''+_name+'\',\'restart\',\''+version+'\')">重启</button>\
            <button class="btn btn-default btn-sm" onclick="pluginOpService(\''+_name+'\',\'reload\',\''+version+'\')">重载配置</button>\
        </div>'; 
    $(".soft-man-con").html(serviceCon);
}


function pluginOpService(a, b, v) {

    var c = "name=" + a + "&func=" + b;
    if(v != ''){
    	c = c + '&version='+v;
    }

    var d = "";

    switch(b) {
        case "stop":d = '停止';break;
        case "start":d = '启动';break;
        case "restart":d = '重启';break;
        case "reload":d = '重载';break;
    }
    layer.confirm( msgTpl('您真的要{1}{2}{3}服务吗？', [d,a,v]), {icon:3,closeBtn: 2}, function() {
        var e = layer.msg(msgTpl('正在{1}{2}{3}服务,请稍候...',[d,a,v]), {icon: 16,time: 0});
        $.post("/plugins/run", c, function(g) {
            layer.close(e);
            
            var f = g.data == 'ok' ? msgTpl('{1}{2}服务已{3}',[a,v,d]) : msgTpl('{1}{2}服务{3}失败!',[a,v,d]);
            layer.msg(f, {icon: g.data == 'ok' ? 1 : 2});
            
            if( b != "reload" && g.data == 'ok' ) {
                if ( b == 'start' ) {
                    pluginSetService(a, true, v);
                } else if ( b == 'stop' ){
                    pluginSetService(a, false, v);
                }
            }

            if( g.status && g.data != 'ok' ) {
                layer.msg(g.data, {icon: 2,time: 3000,shade: 0.3,shadeClose: true});
            }
   
        },'json').error(function() {
            layer.close(e);
            layer.msg('操作异常!', {icon: 1});
        });
    })
}


//配置修改 --- start
function pluginConfig(_name, version){
	if ( typeof(version) == 'undefined' ){
		version = '';
	}

    var con = '<p style="color: #666; margin-bottom: 7px">提示：Ctrl+F 搜索关键字，Ctrl+G 查找下一个，Ctrl+S 保存，Ctrl+Shift+R 查找替换!</p>\
    			<textarea class="bt-input-text" style="height: 320px; line-height:18px;" id="textBody"></textarea>\
                <button id="onlineEditFileBtn" class="btn btn-success btn-sm" style="margin-top:10px;">保存</button>\
                <ul class="help-info-text c7 ptb15">\
                    <li>此处为'+ _name + version +'主配置文件,若您不了解配置规则,请勿随意修改。</li>\
                </ul>';
    $(".soft-man-con").html(con);

    var loadT = layer.msg('配置文件路径获取中...',{icon:16,time:0,shade: [0.3, '#000']});
    $.post('/plugins/run', {name:_name, func:'conf',version:version},function (data) {
        layer.close(loadT);

        var loadT2 = layer.msg('文件内容获取中...',{icon:16,time:0,shade: [0.3, '#000']});
        var fileName = data.data;
        $.post('/files/get_body', 'path=' + fileName, function(rdata) {
            layer.close(loadT2);
            if (!rdata.status){
                layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }
            $("#textBody").empty().text(rdata.data.data);
            $(".CodeMirror").remove();
            var editor = CodeMirror.fromTextArea(document.getElementById("textBody"), {
                extraKeys: {
                    "Ctrl-Space": "autocomplete",
                    "Ctrl-F": "findPersistent",
                    "Ctrl-H": "replaceAll",
                    "Ctrl-S": function() {
                        pluginConfigSave(fileName);
                    }
                },
                lineNumbers: true,
                matchBrackets:true,
            });
            editor.focus();
            $(".CodeMirror-scroll").css({"height":"300px","margin":0,"padding":0});
            $("#onlineEditFileBtn").click(function(){
                $("#textBody").text(editor.getValue());
                pluginConfigSave(fileName);
            });
        },'json');
    },'json');
}


//配置保存
function pluginConfigSave(fileName) {
    var data = encodeURIComponent($("#textBody").val());
    var encoding = 'utf-8';
    var loadT = layer.msg('保存中...', {
        icon: 16,
        time: 0
    });
    $.post('/files/save_body', 'data=' + data + '&path=' + fileName + '&encoding=' + encoding, function(rdata) {
        layer.close(loadT);
        layer.msg(rdata.msg, {
            icon: rdata.status ? 1 : 2
        });
    },'json');
}


function pluginInitD(_name){
	$.post('/plugins/run', {name:_name, func:'initd_status'}, function(data) {
        if( !data.status ){
            layer.msg(data.msg,{icon:0,time:3000,shade: [0.3, '#000']});
            return;
        }
        if( data.data!='ok' && data.data!='fail' ){
            layer.msg(data.data,{icon:0,time:3000,shade: [0.3, '#000']});
            return;
        }
        if (data.data == 'ok'){
            pluginSetInitD(_name, true);
        } else {
            pluginSetInitD(_name, false);
        }
    },'json');
}

function pluginSetInitD(_name, status){
	var serviceCon ='<p class="status">当前状态：<span>'+(status ? '已加载' : '未加载' )+
        '</span><span style="color: '+
        (status?'#20a53a;':'red;')+
        ' margin-left: 3px;" class="glyphicon ' + (status?'glyphicon glyphicon-play':'glyphicon-pause')+'"></span></p><div class="sfm-opt">\
            <button class="btn btn-default btn-sm" onclick="pluginOpInitD(\''+_name+'\',\''+(status?'initd_uninstall':'initd_install')+'\')">'+(status?'卸载':'加载')+'</button>\
        </div>'; 
    $(".soft-man-con").html(serviceCon);
}

function pluginOpInitD(a, b) {
    var c = "name=" + a + "&func=" + b;
    var d = "";
    switch(b) {
        case "initd_install":d = '加载';break;
        case "initd_uninstall":d = '卸载';break;
    }
    layer.confirm( msgTpl('您真的要{1}{2}服务吗？', [d,a]), {icon:3,closeBtn: 2}, function() {
        var e = layer.msg(msgTpl('正在{1}{2}服务,请稍候...',[d,a]), {icon: 16,time: 0});
        $.post("/plugins/run", c, function(g) {
            layer.close(e);
            var f = g.data == 'ok' ? msgTpl('{1}服务已{2}',[a,d]) : msgTpl('{1}服务{2}失败!',[a,d]);
            layer.msg(f, {icon: g.data == 'ok' ? 1 : 2});
            
            if ( b == 'initd_install' && g.data == 'ok' ) {
                pluginSetInitD(a, true);
            }else{
                pluginSetInitD(a, false);
            }
            if(g.data != 'ok') {
                layer.msg(g.data, {icon: 2,time: 0,shade: 0.3,shadeClose: true});
            }
        },'json').error(function() {
            layer.close(e);
            layer.msg('系统异常!', {icon: 0});
        });
    })
}

function pluginErrorLogs(_name, version){
    if ( typeof(version) == 'undefined' ){
        version = '';
    }

    var loadT = layer.msg('错误日志路径获取中...',{icon:16,time:0,shade: [0.3, '#000']});
    $.post('/plugins/run', {name:_name, func:'error_log',version:version},function (data) {
        layer.close(loadT);

        var loadT2 = layer.msg('文件内容获取中...',{icon:16,time:0,shade: [0.3, '#000']});
        var fileName = data.data;
        $.post('/files/get_body', 'path=' + fileName, function(rdata) {
            layer.close(loadT2);
            if (!rdata.status){
                layer.msg(rdata.msg,{icon:0,time:2000,shade: [0.3, '#000']});
                return;
            }
            
            if(rdata.data.data == '') rdata.data.data = '当前没有日志!';
            var ebody = '<div class="soft-man-con"><textarea readonly="" style="margin: 0px;width: 500px;height: 520px;background-color: #333;color:#fff; padding:0 5px" id="error_log">'+rdata.data.data+'</textarea></div>';
            $(".soft-man-con").html(ebody);
            var ob = document.getElementById('error_log');
            ob.scrollTop = ob.scrollHeight; 
        },'json');
    },'json');
}
/*** 其中功能,针对插件通过库使用 end ***/