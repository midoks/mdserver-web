(function($){

$.fn.stamper = function(options) {
	var opts = $.extend({
		scale : 5, // 图片初始大小，在原始图片大小上的倍数
		speed : 600 // 动画持续时间，单位毫秒
	}, options);
	
	this.each(function(index) {
		var target = $(this);
		var imgId = target.attr("data-stamper-img-id");
		if (!imgId) {
			imgId = "jquery_stamper_img_" + (new Date().getTime()) + "_" + index;
			target.attr("data-stamper-img-id", imgId);
		}
		var img = new Image();
		img.src = opts.image;
		img.onload = function() {
			var orgiCoor = getImageCoordinate(target, img);
			var initCoor = getStartCoordinate(target, img, opts.scale);
			var imgObj = getImageElement(imgId).attr("src", img.src)
				.css({
					position : "absolute",
					opacity : "0",
					left : "-106px",
					top : "-116px",
					width : initCoor.w + "px",
					height : initCoor.h + "px"
				})
				.show()
				.animate({
					opacity : "1",
					left : "0px",
					top : "0px",
					width : orgiCoor.w + "px",
					height : orgiCoor.h + "px"
				}, opts.speed, opts.complete);
		};
	});
};

/** 获取img的DOM对象 **/
function getImageElement(id) {
	var img = $("#" + id);
	if (img.length == 0) {
		return $("<img id=\"" + id + "\" />").appendTo($(".ts-stamper")).hide();
	} else {
		return img.hide();
	}
}

/** 获取图片的落脚坐标点（以当前元素为基准）和尺寸信息，格式：{x:10,y:20,h:100,w:200} **/
function getImageCoordinate(target, image) {
	var offset = $(target).offset();
	var cx = offset.left + $(target).width()/2;
	var cy = offset.top + $(target).height()/2;
	return {
		x : cx - image.width/2,
		y : cy - image.height/2,
		w : image.width,
		h : image.height
	};
}

/** 给定倍数（multiple）获取图片的开始位置和大小信息，格式：{x:10,y:20,h:100,w:200} **/
function getStartCoordinate(target, image, multiple) {
	var offset = $(target).offset();
	var cx = offset.left + $(target).width()/2;
	var cy = offset.top + $(target).height()/2;
	var width = image.width * multiple;
	var height = image.height * multiple;
	return {
		x : cx - width/2,
		y : cy - height/2,
		w : width,
		h : height
	};
}
})(jQuery);

function startTest(){
	var name = $(".ts-btn").text();
	switch(name){
		case '开始跑分':
			startTestServer(name);
			break;
		case '正在跑分':
			stopTestServer();
			break;
		case '重新跑分':
			startTestServer(name);
			break;
	}
}
if(getCookie("#Total") >0){
	$(".old-score").html("上次跑分："+getCookie("#Total") + ' 分 <a href="javascript:btphb();" class="btlink" style="margin-left:10px">我的排名</a>').show();
}

function startTestServer(name){
	layer.confirm('测试过程可能需要几分钟时间且占用大量服务器资源，继续吗？',{title:'性能测试',closeBtn:2},function(){
			layer.closeAll('dialog');
			if(name == "重新跑分"){
				$(".btphb").remove();
				$(".ts-content").find(".ts-box-rotate").remove();
				$(".ts-h-s-num").html('<span>正在跑分中<img src="/static/img/ings.gif"></span>');
				$(".ts-btn-reset").removeAttr("onclick").width(140);
				$(".ts-cpu-over").removeClass("ts-cpu-over");
				$(".ts-disk-over").removeClass("ts-disk-over");
				$(".ts-mem-over").removeClass("ts-mem-over");
				$(".ts-h-s-img").removeClass("ts-h-s-img1");
				$(".ts-h-s-img").removeClass("ts-h-s-img2");
				$(".ts-h-s-img").removeClass("ts-h-s-img3");
				$(".ts-h-s-img").addClass("ts-h-s-imging");
				$(".ts-stamper").html("");
			}
			$(".old-score").fadeOut();
			$(".ts-btn").removeClass("ts-btn-start").text("正在跑分").animate({"left":"490px"});
			$(".ts-h-score").fadeIn();
			$(".ts-cpu").addClass("ts-cpu-ing").append("<div class='ts-box-rotate'></div>");
			$(".ts-info").html("正在测试整数运算性能[1万次]<img src='/static/img/ing.gif'>");
			var cpuscore = 0;
			$.get('/plugin?action=a&name=score&s=testCpu&type=1',function(rint){
				cpuscore += rint.score;
				$(".ts-info").html("正在测试浮点运算性能[2万次]<img src='/static/img/ing.gif'>");
				$.get('/plugin?action=a&name=score&s=testCpu&type=2',function(rfloat){
					cpuscore += rfloat.score;
					$(".ts-info").html("正在测试圆周率运算[1亿位]<img src='/static/img/ing.gif'>");
					$.get('/plugin?action=a&name=score&s=testCpu&type=3',function(rpi){
						cpuscore += rpi.score;
						$(".ts-info").html("正在测试二叉树排序算法[1万次]<img src='/static/img/ing.gif'>");
						$.get('/plugin?action=a&name=score&s=testCpu&type=4',function(r1){
							r1.score += cpuscore;
							$(".ts-cpu").removeClass("ts-cpu-ing").addClass("ts-cpu-over").find(".ts-box-rotate").remove();
							$(".ts-disk").addClass("ts-disk-ing").append("<div class='ts-box-rotate'></div>");
							$(".ts-cpu .ts-c-b-score").html(r1.score);
							$(".ts-cpu .ts-c-b-info").html(r1.cpuType + ' ' +r1.cpuCount + ' 核心');
							//$("#cpuType").html('型号:' + r1.cpuType);
							setCookie('cpuTotal',r1.score);
							setCookie('cpuCount',r1.cpuCount + ' 核心');
							setCookie('cpuType','型号:' + r1.cpuType);
							$(".ts-info").html("正在测试磁盘性能<img src='/static/img/ing.gif'>");
							$.get('/plugin?action=a&name=score&s=testDisk',function(r2){
								$(".ts-disk").removeClass("ts-disk-ing").addClass("ts-disk-over").find(".ts-box-rotate").remove();
								$(".ts-mem").addClass("ts-mem-ing").append("<div class='ts-box-rotate'></div>");
								$(".ts-disk .ts-c-b-score").html(r2.score);
								$(".ts-disk .ts-c-b-info").html('读: ' + r2.read + ' MB，写: ' + r2.write + ' MB');
								setCookie('diskTotal',r2.score);
								setCookie('diskRead','Read: ' + r2.read + ' MB');
								setCookie('diskWrite','Write: ' + r2.write + ' MB');
								$(".ts-info").html("正在测试内存<img src='/static/img/ing.gif'>");
								$.get('/plugin?action=a&name=score&s=testMem','',function(r3){
									$(".ts-mem").removeClass("ts-mem-ing").addClass("ts-mem-over").find(".ts-box-rotate").remove();
									$(".ts-mem .ts-c-b-score").html(parseInt(r3));
									$(".ts-mem .ts-c-b-info").html( r3 + ' MB');
									var total = r1.score+r2.score+ parseInt(r3);
									$(".ts-h-s-num span").html(total + ' 分').css({"font-size":"40px"});
									setCookie("#memTotal",r3 + ' MB');
									setCookie("#Total",total);
									$(".ts-btn").addClass("ts-btn-reset").text("重新跑分").css({"left":"550px","width":"80px"}).attr("onclick","startTestServer('重新跑分')");
									$(".ts-h-score").after('<div class="ts-btn btphb" onclick="btphb()" style="width: 80px; left: 450px;">我的排名</div>');
									if(total<2500){
										$(".ts-h-s-img").removeClass("ts-h-s-imging").addClass("ts-h-s-img1");
										scoreIco("1");
									}
									if(total>2500 && total<10000){
										$(".ts-h-s-img").removeClass("ts-h-s-imging").addClass("ts-h-s-img2");
										scoreIco("2");
									}
									if(total > 10000){
										$(".ts-h-s-img").removeClass("ts-h-s-imging").addClass("ts-h-s-img3");
										scoreIco("3");
									}
									
									var data = "soc="+total;
									$.get("/ajax?action=GetAd&name=zun",data,function(rad){
										$(".ts-info").html(rad);
									});
								});
							});
						});
					});
				});
			});
		});
}
function stopTestServer(){
	/*
	$(".ts-btn").addClass("ts-btn-start").removeClass("ts-btn-reset").text("开始测试").animate({"left":"233px"});
	$(".ts-h-score").fadeOut();
	$(".ts-info").html("跑分计算规则为：通过计算cpu运算能力，计算内存吞吐能力，计算磁盘读写能力");
	*/
	//layer.msg("测试中，不能停止",{shade:0.3});
	return false;
}
function scoreIco(ico) {
	var img = '';
	switch(ico){
		case "1":
			img = 'data:image/gif;base64,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';
			break;
		case "2":
			img = 'data:image/gif;base64,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';
			break;
		case "3":
			img = 'data:image/gif;base64,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';
			break;
	}
	$(".ts-stamper").stamper({
		image : img,
		scale : 3,
		speed : 300,
		complete : function() {
			//alert("完成啦~~~~");
		}
	})
}

function GetScore(){
	$.get('/plugin?action=a&name=score&s=GetScore',function(rdata){
		
	});
}
GetScore();
//我的排名
function btphb(){
	$.get("/ssl?action=GetUserInfo",function(rdata){
			if(rdata.status){
				var loadT = layer.msg("获取列表..",{icon:16,time:0});
				var tr = "";
				$.get("/plugin?action=a&name=score&s=GetScore",function(pm){
					layer.close(loadT);
					if(pm.status){
						for(var i=0; i<pm.data.length; i++){
							tr += '<tr><td>'+pm.data[i].address+'</td><td>'+pm.data[i].core+'核 | '+pm.data[i].memory+'MB | 读'+pm.data[i].disk.split(",")[0]+'MB/s | 写'+pm.data[i].disk.split(",")[1]+'MB/s</td><td>'+pm.data[i].virt+'</td><td>'+pm.data[i].isp+'</td><td>'+pm.data[i].total_score+'</td><td class="text-right"><a href="https://www.bt.cn/score?address='+pm.data[i].address+'" class="btlink" target="_blank">查看排名</a></td></tr>';
						}
						layer.open({
							type: 1,
							area: "700px",
							title: "我的服务器跑分",
							closeBtn: 2,
							shadeClose: false,
							content: '<div class="bt-form pd15" style="max-height:450px;overflow:auto">\
										<div class="divtable">\
											<table class="table table-hover">\
												<thead><tr><th>服务器IP</th><th>配置</th><th>平台</th><th>服务商</th><th>跑分</th><th class="text-right" width="80px">查看排名</th></tr></thead>\
												<tbody>'+tr+'</tbody>\
											</table>\
										</div>\
									</div>'
							
						})
					}
					
				})
			}
			else{
				bindBTName(2,'b');
			}
		});
}

//绑定修改宝塔账号
function bindBTName(a,type){
	var titleName = "绑定宝塔账号";
	if(type == "b"){
		btn = "<button type='button' class='btn btn-success btn-sm' onclick=\"bindBTName(1,'b')\">绑定</button>";
	}
	if(a == 1) {
		p1 = $("#p1").val();
		p2 = $("#p2").val();
		$.post(" /ssl?action=GetToken", "username=" + p1 + "&password=" + p2, function(b) {
			if(b.status) {
				$(".btn-bw").click();
				layer.msg(b.msg, {
					icon: 1
				});
				$.get("/plugin?action=a&name=score&s=SubmitScore",function(p){
					//layer.msg(p.msg,{icon:p.status?1:2});
				});
				btphb();
			} else {
				layer.msg(b.msg, {
					icon: 2
				})
			}
		});
		return
	}
	var bindw = layer.open({
		type: 1,
		area: "290px",
		title: titleName,
		closeBtn: 2,
		shift: 5,
		shadeClose: false,
		content: "<div class='bt-form pd20 pb55'><div class='line'><span class='tname'>账号</span><div class='info-r'><input class='bt-input-text' type='text' name='username' id='p1' value='' placeholder='宝塔官网账户' style='width:100%'/></div></div><div class='line'><span class='tname'>密码</span><div class='info-r'><input class='bt-input-text' type='password' name='password' id='p2' value='' placeholder='宝塔官网密码' style='width:100%'/></div></div><div class='line text-right'><a class='c8' href='https://www.bt.cn/register.html' target='_blank'>注册宝塔账号</a></div><div class='bt-form-submit-btn'><button type='button' class='btn btn-danger btn-sm btn-bw'>取消</button> "+btn+"</div></div>"
	})
	$(".btn-bw").click(function(){
		layer.close(bindw);
	});
}