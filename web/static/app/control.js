//默认显示7天周期图表

setTimeout(function(){
	Wday(0,'getload');
},100);
setTimeout(function(){
	Wday(0,'cpu');
},200);
setTimeout(function(){
	Wday(0,'mem');
},500);
setTimeout(function(){
	Wday(0,'disk');
},100);
setTimeout(function(){
	Wday(0,'network');
},1500);


$(".searcTime .st").click(function(){
	var status = $(this).data('status');
	if (status == 'show'){
		$(this).next().hide();
		$(this).data('status','hide');
	} else{
		$(this).next().show();
		$(this).data('status','show');
	}
});

//自定义时间-切换
$(".searcTime .st").hover(function(){
	$(this).data('status','show');
	$(this).next().show();
},function(){
	// $(this).next().hide();
	// $(this).next().hover(function(){
	// 	$(this).show();
	// },function(){
	// 	$(this).hide();
	// })
})

$(".searcTime .gt").click(function(){
	$(this).addClass("on").siblings().removeClass("on");
})


//渲染日期时间范围 start
var render_dlist = [
	'loadbtn_rtime',
	'cpubtn_rtime',
	'membtn_rtime',
	'diskbtn_rtime',
	'networkbtn_rtime'
];

for (var i = 0; i < render_dlist.length; i++) {
	
	laydate.render({
		elem: '#'+render_dlist[i]
		,type: 'datetime'
		,range: true
	});


	var b = getBeforeDate(28).replaceAll('/','-') + " 00:00:00";
	var e = getBeforeDate(0).replaceAll('/','-') + " 23:59:59";

	$('#'+render_dlist[i]).val(b + ' - ' + e);
}
//渲染日期时间范围 end


$('.sbtn').click(function(){
	$(".searcTime .st").next().hide();

	var rtime = $(this).parent().find(".rtime").val();
	var rarr = rtime.split(' - ');

	var b = (new Date(rarr[0]).getTime())/1000;
	var e = (new Date(rarr[1]).getTime())/1000;

	b = Math.round(b);
	e = Math.round(e);

	if ($(this).hasClass('loadbtn')){
		getload(b,e);
	} else if ($(this).hasClass('cpubtn')){
		cpu(b,e);
	}else if ($(this).hasClass('membtn')){
		mem(b,e);
	} else if ($(this).hasClass('diskbtn')){
		disk(b,e);
	}
});

//指定天数
function Wday(day,name){
	var now = (new Date().getTime())/1000;
	if(day==0){
		var b = (new Date(getToday() + " 00:00:01").getTime())/1000;
			b = Math.round(b);
		var e = Math.round(now);
	}
	if(day==1){
		var b = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
		var e = (new Date(getBeforeDate(day) + " 23:59:59").getTime())/1000;
		b = Math.round(b);
		e = Math.round(e);
	}
	else{
		var b = (new Date(getBeforeDate(day) + " 00:00:01").getTime())/1000;
			b = Math.round(b);
		var e = Math.round(now);
	}
	switch (name){
		case "cpu":
			cpu(b, e);
			break;
		case "mem":
			mem(b, e);
			break;
		case "disk":
			disk(b, e);
			break;
		case "network":
			network(b, e);
			break;
		case "getload":
			getload(b, e);
			break;
	}
}

function getToday(){
   var mydate = new Date();
   var str = "" + mydate.getFullYear() + "/";
   str += (mydate.getMonth()+1) + "/";
   str += mydate.getDate();
   return str;
}

getStatus();
//取监控状态
function getStatus(){
	loadT = layer.msg('正在读取,请稍候...',{icon:16,time:0})
	$.post('/system/set_control','type=-1',function(rdata){
		layer.close(loadT);

		if(rdata.status){
			$("#openJK").html("<input class='btswitch btswitch-ios' id='ctswitch' type='checkbox' checked><label class='btswitch-btn' for='ctswitch' onclick='setControl(\"openjk\", true)'></label>");
		} else {
			$("#openJK").html("<input class='btswitch btswitch-ios' id='ctswitch' type='checkbox'><label class='btswitch-btn' for='ctswitch' onclick='setControl(\"openjk\",false)'></label>");
		}

		if(rdata.stat_all_status){
			$("#statAll").html("<input class='btswitch btswitch-ios' id='stat_witch' type='checkbox' checked><label class='btswitch-btn' for='stat_witch' onclick='setControl(\"stat\",true)'></label>");
		} else{
			$("#statAll").html("<input class='btswitch btswitch-ios' id='stat_witch' type='checkbox'><label class='btswitch-btn' for='stat_witch' onclick='setControl(\"stat\",false)'></label>");
		}

		$("#save_day").val(rdata.day);

	},'json');
}


//设置监控状态
function setControl(act, value=false){

	if (act == 'openjk'){
		var type = $("#ctswitch").prop('checked')?'0':'1';
		var day = $("#save_day").val();
		if(day < 1){
			layer.msg('保存天数不合法!',{icon:2});
			return;
		}
	} else if (act == 'stat'){
		var type = $("#stat_witch").prop('checked')?'2':'3';
	} else if (act == 'save_day'){
		var type = $("#ctswitch").prop('checked')?'1':'0';
		var day = $("#save_day").val();

		if(type == 0){
			layer.msg('先开启监控!',{icon:2});
			return;
		}

		if(day < 1){
			layer.msg('保存天数不合法!',{icon:2});
			return;
		}
	}
	
	loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0})
	$.post('/system/set_control','type='+type+'&day='+day,function(rdata){
		showMsg(rdata.msg, function(){
			layer.close(loadT);
		},{icon:rdata.status?1:2})
	},'json');
}


//清理记录
function closeControl(){
	layer.confirm('您真的清空所有监控记录吗？',{title:'清空记录',icon:3,closeBtn:1}, function() {
		loadT = layer.msg('正在处理,请稍候...',{icon:16,time:0})
		$.post('/system/set_control','type=del',function(rdata){
			showMsg(rdata.msg, function(){
				layer.close(loadT);
			},{icon:rdata.status?1:2})
		},'json');
	});
}


//定义周期时间
function getBeforeDate(n){
    var n = n;
    var d = new Date();
    var year = d.getFullYear();
    var mon=d.getMonth()+1;
    var day=d.getDate();
    if(day <= n){
		if(mon>1) {
		  	mon = mon-1;
		} else {
			year = year-1;
			mon = 12;
		}
	}
	d.setDate(d.getDate()-n);
	year = d.getFullYear();
	mon=d.getMonth()+1;
	day=d.getDate();
  	s = year+"/"+(mon<10?('0'+mon):mon)+"/"+(day<10?('0'+day):day);
	return s;
}
//cpu
function cpu(b,e){
	$.get('/system/get_cpu_io?start='+b+'&end='+e,function(rdata){
		var rdata = rdata.data;
		var theme = getChartTheme();
		var xData = [];
		var yData = [];
		//var zData = [];
		
		for(var i = 0; i < rdata.length; i++){
			xData.push(rdata[i].addtime);
			yData.push(rdata[i].pro);
			//zData.push(rdata[i].mem);
		}
		option = {
			backgroundColor: 'transparent',
			tooltip: {
				trigger: 'axis',
				backgroundColor: theme.surface,
				borderColor: theme.border,
				textStyle: { color: theme.text },
				extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
				axisPointer: { type: 'line', lineStyle: { color: theme.border } },
				formatter: '{b}<br />{a}: {c}%'
			},
			grid: {
				left: '2%',
				right: '3%',
				bottom: '12%',
				containLabel: true
			},
			xAxis: {
				type: 'category',
				boundaryGap: false,
				data: xData,
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted }
			},
			yAxis: {
				type: 'value',
				name: lan.public.pre,
				boundaryGap: [0, '100%'],
				min:0,
				max: 100,
				splitLine:{ lineStyle:{ color: theme.border } },
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted },
				nameTextStyle: { color: theme.muted }
			},
			dataZoom: [{
				type: 'inside',
				start: 0,
				end: 100,
				zoomLock:true
			}, {
				type: 'slider',
				start: 0,
				end: 100,
				height: 18,
				backgroundColor: applyColorAlpha(theme.border, 0.2),
				fillerColor: applyColorAlpha(theme.primary, 0.18),
				borderColor: 'transparent',
				textStyle: { color: theme.muted },
				handleStyle: {
					color: theme.surface,
					borderColor: theme.border
				}
			}],
			series: [
				{
					name:'CPU',
					type:'line',
					smooth:true,
					showSymbol: false,
					sampling: 'average',
					lineStyle: { width: 2, color: theme.primary },
					itemStyle: { color: theme.primary },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
							offset: 0,
							color: applyColorAlpha(theme.primary, 0.35)
						}, {
							offset: 1,
							color: applyColorAlpha(theme.primary, 0.08)
						}])
					},
					data: yData
				}
			]
		};
		initEchartWhenReady('cupview', option);
	},'json');
}

//内存
function mem(b,e){
	$.get('/system/get_cpu_io?start='+b+'&end='+e,function(rdata){
		var rdata = rdata.data;
		var theme = getChartTheme();
		var xData = [];
		//var yData = [];
		var zData = [];
		
		for(var i = 0; i < rdata.length; i++){
			xData.push(rdata[i].addtime);
			//yData.push(rdata[i].pro);
			zData.push(rdata[i].mem);
		}
		option = {
			backgroundColor: 'transparent',
			tooltip: {
				trigger: 'axis',
				backgroundColor: theme.surface,
				borderColor: theme.border,
				textStyle: { color: theme.text },
				extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
				axisPointer: { type: 'line', lineStyle: { color: theme.border } },
				formatter: '{b}<br />{a}: {c}%'
			},
			grid: {
				left: '2%',
				right: '3%',
				bottom: '12%',
				containLabel: true
			},
			xAxis: {
				type: 'category',
				boundaryGap: false,
				data: xData,
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted }
			},
			yAxis: {
				type: 'value',
				name: lan.public.pre,
				boundaryGap: [0, '100%'],
				min:0,
				max: 100,
				splitLine:{ lineStyle:{ color: theme.border } },
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted },
				nameTextStyle: { color: theme.muted }
			},
			dataZoom: [{
				type: 'inside',
				start: 0,
				end: 100,
				zoomLock:true
			}, {
				type: 'slider',
				start: 0,
				end: 100,
				height: 18,
				backgroundColor: applyColorAlpha(theme.border, 0.2),
				fillerColor: applyColorAlpha(theme.secondary, 0.18),
				borderColor: 'transparent',
				textStyle: { color: theme.muted },
				handleStyle: {
					color: theme.surface,
					borderColor: theme.border
				}
			}],
			series: [
				{
					name:lan.index.process_mem,
					type:'line',
					smooth:true,
					showSymbol: false,
					sampling: 'average',
					lineStyle: { width: 2, color: theme.secondary },
					itemStyle: { color: theme.secondary },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
							offset: 0,
							color: applyColorAlpha(theme.secondary, 0.32)
						}, {
							offset: 1,
							color: applyColorAlpha(theme.secondary, 0.08)
						}])
					},
					data: zData
				}
			]
		};
		initEchartWhenReady('memview', option);
	},'json');
}

//磁盘io
function disk(b,e){
	$.get('/system/get_disk_io?start='+b+'&end='+e,function(rdata){
		var rdata = rdata.data;
		var theme = getChartTheme();
		var rData = [];
		var wData = [];
		var xData = [];
		//var yData = [];
		//var zData = [];
		
		for(var i = 0; i < rdata.length; i++){
			rData.push((rdata[i].read_bytes/1024/60).toFixed(3));
			wData.push((rdata[i].write_bytes/1024/60).toFixed(3));
			xData.push(rdata[i].addtime);
			//yData.push(rdata[i].read_count);
			//zData.push(rdata[i].write_count);
		}
		option = {
			backgroundColor: 'transparent',
			tooltip: {
				trigger: 'axis',
				backgroundColor: theme.surface,
				borderColor: theme.border,
				textStyle: { color: theme.text },
				extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
				axisPointer: { type: 'line', lineStyle: { color: theme.border } },
				formatter:"时间：{b0}<br />{a0}: {c0} Kb/s<br />{a1}: {c1} Kb/s"
			},
			legend: {
				data:['读取字节数','写入字节数'],
				bottom: '2%',
				textStyle: { color: theme.muted }
			},
			grid: {
				left: '2%',
				right: '3%',
				bottom: '12%',
				containLabel: true
			},
			xAxis: {
				type: 'category',
				boundaryGap: false,
				data: xData,
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted }
			},
			yAxis: {
				type: 'value',
				name: '单位:KB/s',
				boundaryGap: [0, '100%'],
				splitLine:{ lineStyle:{ color: theme.border } },
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted },
				nameTextStyle: { color: theme.muted }
			},
			dataZoom: [{
				type: 'inside',
				start: 0,
				end: 100,
				zoomLock:true
			}, {
				type: 'slider',
				start: 0,
				end: 100,
				height: 18,
				backgroundColor: applyColorAlpha(theme.border, 0.2),
				fillerColor: applyColorAlpha(theme.primary, 0.18),
				borderColor: 'transparent',
				textStyle: { color: theme.muted },
				handleStyle: {
					color: theme.surface,
					borderColor: theme.border
				}
			}],
			series: [
				{
					name:'读取字节数',
					type:'line',
					smooth:true,
					showSymbol: false,
					sampling: 'average',
					lineStyle: { width: 2, color: theme.primary },
					itemStyle: { color: theme.primary },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
							offset: 0,
							color: applyColorAlpha(theme.primary, 0.28)
						}, {
							offset: 1,
							color: applyColorAlpha(theme.primary, 0.08)
						}])
					},
					data: rData
				},
				{
					name:'写入字节数',
					type:'line',
					smooth:true,
					showSymbol: false,
					sampling: 'average',
					lineStyle: { width: 2, color: theme.tertiary },
					itemStyle: { color: theme.tertiary },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
							offset: 0,
							color: applyColorAlpha(theme.tertiary, 0.28)
						}, {
							offset: 1,
							color: applyColorAlpha(theme.tertiary, 0.08)
						}])
					},
					data: wData
				}
			]
		};
		initEchartWhenReady('diskview', option);
	},'json');
}

//网络Io
function network(b,e){
	$.get('/system/get_network_io?start='+b+'&end='+e,function(rdata){
		var rdata = rdata.data;
		var theme = getChartTheme();
		var aData = [];
		var bData = [];
		var cData = [];
		var dData = [];
		var xData = [];
		var yData = [];
		var zData = [];
		
		for(var i = 0; i < rdata.length; i++){
			aData.push(rdata[i].total_up);
			bData.push(rdata[i].total_down);
			cData.push(rdata[i].down_packets);
			dData.push(rdata[i].up_packets);
			xData.push(rdata[i].addtime);
			yData.push(rdata[i].up);
			zData.push(rdata[i].down);
		}
		option = {
			backgroundColor: 'transparent',
			tooltip: {
				trigger: 'axis',
				backgroundColor: theme.surface,
				borderColor: theme.border,
				textStyle: { color: theme.text },
				extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
				axisPointer: { type: 'line', lineStyle: { color: theme.border } },
				formatter:"时间：{b0}<br />{a0}: {c0} Kb/s<br />{a1}: {c1} Kb/s"
			},
			legend: {
				data:[lan.index.net_up,lan.index.net_down],
				bottom: '2%',
				textStyle: { color: theme.muted }
			},
			grid: {
				left: '2%',
				right: '3%',
				bottom: '12%',
				containLabel: true
			},
			xAxis: {
				type: 'category',
				boundaryGap: false,
				data: xData,
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted }
			},
			yAxis: {
				type: 'value',
				name: '单位:KB/s',
				boundaryGap: [0, '100%'],
				splitLine:{ lineStyle:{ color: theme.border } },
				axisLine:{ lineStyle:{ color: theme.border } },
				axisLabel: { color: theme.muted },
				nameTextStyle: { color: theme.muted }
			},
			dataZoom: [{
				type: 'inside',
				start: 0,
				end: 100,
				zoomLock:true
			}, {
				type: 'slider',
				start: 0,
				end: 100,
				height: 18,
				backgroundColor: applyColorAlpha(theme.border, 0.2),
				fillerColor: applyColorAlpha(theme.secondary, 0.18),
				borderColor: 'transparent',
				textStyle: { color: theme.muted },
				handleStyle: {
					color: theme.surface,
					borderColor: theme.border
				}
			}],
			series: [
				{
					name:lan.index.net_up,
					type:'line',
					smooth:true,
					showSymbol: false,
					sampling: 'average',
					lineStyle: { width: 2, color: theme.primary },
					itemStyle: { color: theme.primary },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
							offset: 0,
							color: applyColorAlpha(theme.primary, 0.25)
						}, {
							offset: 1,
							color: applyColorAlpha(theme.primary, 0.06)
						}])
					},
					data: yData
				},
				{
					name:lan.index.net_down,
					type:'line',
					smooth:true,
					showSymbol: false,
					sampling: 'average',
					lineStyle: { width: 2, color: theme.secondary },
					itemStyle: { color: theme.secondary },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
							offset: 0,
							color: applyColorAlpha(theme.secondary, 0.25)
						}, {
							offset: 1,
							color: applyColorAlpha(theme.secondary, 0.06)
						}])
					},
					data: zData
				}
			]
		};
		initEchartWhenReady('network', option);
	},'json');
}
//负载
function getload_old(b,e){
	$.get('/system/get_load_average?start='+b+'&end='+e,function(rdata){
		var rdata = data.data;
		var aData = [];
		var bData = [];
		var xData = [];
		var yData = [];
		var zData = [];
		
		for(var i = 0; i < rdata.length; i++){
			xData.push(rdata[i].addtime);
			yData.push(rdata[i].pro);
			zData.push(rdata[i].one);
			aData.push(rdata[i].five);
			bData.push(rdata[i].fifteen);
		}
		option = {
			tooltip: {
				trigger: 'axis'
			},
			calculable: true,
			legend: {
				data:['系统资源使用率','1分钟','5分钟','15分钟'],
				selectedMode: 'single',
			},
			xAxis: {
				type: 'category',
				boundaryGap: false,
				data: xData,
				axisLine:{
					lineStyle:{
						color:"#666"
					}
				}
			},
			yAxis: {
				type: 'value',
				name: '',
				boundaryGap: [0, '100%'],
				splitLine:{
					lineStyle:{
						color:"#ddd"
					}
				},
				axisLine:{
					lineStyle:{
						color:"#666"
					}
				}
			},
			dataZoom: [{
				type: 'inside',
				start: 0,
				end: 100,
				zoomLock:true
			}, {
				start: 0,
				end: 100,
				handleIcon: 'M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.5,16.3,15.6,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19.6H6.7v-1.4h6.6V19.6z',
				handleSize: '80%',
				handleStyle: {
					color: '#fff',
					shadowBlur: 3,
					shadowColor: 'rgba(0, 0, 0, 0.6)',
					shadowOffsetX: 2,
					shadowOffsetY: 2
				}
			}],
			series: [
				{
					name:'系统资源使用率',
					type:'line',
					smooth:true,
					symbol: 'none',
					sampling: 'average',
					itemStyle: {
						normal: {
							color: 'rgb(255, 140, 0)'
						}
					},
					data: yData
				},
				{
					name:'1分钟',
					type:'line',
					smooth:true,
					symbol: 'none',
					sampling: 'average',
					itemStyle: {
						normal: {
							color: 'rgb(30, 144, 255)'
						}
					},
					data: zData
				},
				{
					name:'5分钟',
					type:'line',
					smooth:true,
					symbol: 'none',
					sampling: 'average',
					itemStyle: {
						normal: {
							color: 'rgb(0, 178, 45)'
						}
					},
					data: aData
				},
				{
					name:'15分钟',
					type:'line',
					smooth:true,
					symbol: 'none',
					sampling: 'average',
					itemStyle: {
						normal: {
							color: 'rgb(147, 38, 255)'
						}
					},
					data: bData
				}
			]
		};
		initEchartWhenReady('getloadview', option);
	},'json');
}
//系统负载
function getload(b,e){
	$.get('/system/get_load_average?start='+b+'&end='+e,function(rdata){
		var rdata = rdata.data;
		var theme = getChartTheme();
		var aData = [];
		var bData = [];
		var xData = [];
		var yData = [];
		var zData = [];
		
		for(var i = 0; i < rdata.length; i++){
			xData.push(rdata[i].addtime);
			yData.push(rdata[i].pro);
			zData.push(rdata[i].one);
			aData.push(rdata[i].five);
			bData.push(rdata[i].fifteen);
		}
		option = {
			backgroundColor: 'transparent',
			animation: false,
			tooltip: {
				trigger: 'axis',
				backgroundColor: theme.surface,
				borderColor: theme.border,
				textStyle: { color: theme.text },
				extraCssText: 'box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12); border-radius: 12px; padding: 10px;',
				axisPointer: { type: 'line', lineStyle: { color: theme.border } }
			},
			legend: {
				data:['1分钟','5分钟','15分钟'],
				right:'8%',
				top:'10px',
				textStyle: { color: theme.muted }
			},
			axisPointer: {
				link: {xAxisIndex: 'all'},
				lineStyle: {
					color: theme.border,
					width: 1
				}
			},
			grid: [{
					top: '60px',
					left: '5%',
					right: '55%',
					width: '40%',
					height: 'auto'
				},
				{
					top: '60px',
					left: '55%',
					width: '40%',
					height: 'auto'
				}
			],
			xAxis: [
				{
					type: 'category',
					axisLine: { lineStyle: { color: theme.border } },
					axisLabel: { color: theme.muted },
					data: xData
				},
				{
					type: 'category',
					gridIndex: 1,
					axisLine: { lineStyle: { color: theme.border } },
					axisLabel: { color: theme.muted },
					data: xData
				}
			],
			yAxis: [{
					scale: true,
					name: '资源使用率%',
					splitLine: {
						show: true,
						lineStyle:{ color: theme.border }
					},
					nameTextStyle: {
						color: theme.muted,
						fontSize: 12,
						align: 'left'
					},
					axisLine:{ lineStyle:{ color: theme.border } },
					axisLabel: { color: theme.muted }
				},
				{
					scale: true,
					name: '负载详情',
					gridIndex: 1,
					splitLine: {
						show: true,
						lineStyle:{ color: theme.border }
					},
					nameTextStyle: {
						color: theme.muted,
						fontSize: 12,
						align: 'left'
					},
					axisLine:{ lineStyle:{ color: theme.border } },
					axisLabel: { color: theme.muted }
				}
			],
			dataZoom: [{
				type: 'inside',
				start: 0,
				end: 100,
				xAxisIndex:[0,1],
				zoomLock:true
			}, {
				xAxisIndex: [0, 1],
	            type: 'slider',
				start: 0,
				end: 100,
				height: 18,
				backgroundColor: applyColorAlpha(theme.border, 0.2),
				fillerColor: applyColorAlpha(theme.secondary, 0.18),
				borderColor: 'transparent',
				textStyle: { color: theme.muted },
				handleStyle: {
					color: theme.surface,
					borderColor: theme.border
				},
				left:'5%',
				right:'5%'
			}],
			series: [
				{
					name: '资源使用率%',
					type: 'line',
					smooth: true,
					showSymbol: false,
					lineStyle: { width: 2, color: theme.primary },
					itemStyle: { color: theme.primary },
					areaStyle: {
						color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
							offset: 0,
							color: applyColorAlpha(theme.primary, 0.3)
						}, {
							offset: 1,
							color: applyColorAlpha(theme.primary, 0.08)
						}])
					},
					data: yData
				},
				{
					xAxisIndex: 1,
					yAxisIndex: 1,
					name: '1分钟',
					type: 'line',
					smooth: true,
					showSymbol: false,
					lineStyle: { width: 2, color: theme.secondary },
					itemStyle: { color: theme.secondary },
					data: zData
				},
				{
					xAxisIndex: 1,
					yAxisIndex: 1,
					name: '5分钟',
					type: 'line',
					smooth: true,
					showSymbol: false,
					lineStyle: { width: 2, color: theme.tertiary },
					itemStyle: { color: theme.tertiary },
					data: aData
				},
				{
					xAxisIndex: 1,
					yAxisIndex: 1,
					name: '15分钟',
					type: 'line',
					smooth: true,
					showSymbol: false,
					lineStyle: { width: 2, color: theme.accent },
					itemStyle: { color: theme.accent },
					data: bData
				}
			],
			textStyle: { color: theme.muted, fontSize: 12 }
		}
		initEchartWhenReady('getloadview', option);
	},'json');
}

function getChartTheme() {
	var styles = getComputedStyle(document.documentElement);
	function resolveCssVar(value) {
		if (!value) {
			return value;
		}
		var trimmed = value.trim();
		if (trimmed.indexOf('var(') !== 0) {
			return trimmed;
		}
		var match = trimmed.match(/var\((--[^,\s)]+)\s*(?:,\s*(.+))?\)/);
		if (!match) {
			return trimmed;
		}
		var resolved = styles.getPropertyValue(match[1]).trim();
		if (resolved) {
			return resolveCssVar(resolved);
		}
		if (match[2]) {
			return resolveCssVar(match[2].trim());
		}
		return trimmed;
	}
	return {
		primary: resolveCssVar(styles.getPropertyValue('--mw-primary')) || '#6750a4',
		secondary: resolveCssVar(styles.getPropertyValue('--mdui-color-secondary')) || '#4f8ef7',
		tertiary: resolveCssVar(styles.getPropertyValue('--mdui-color-tertiary')) || '#22c55e',
		accent: resolveCssVar(styles.getPropertyValue('--mdui-color-primary-container')) || '#a855f7',
		border: resolveCssVar(styles.getPropertyValue('--mw-border')) || '#e2e8f0',
		muted: resolveCssVar(styles.getPropertyValue('--mw-muted')) || '#64748b',
		surface: resolveCssVar(styles.getPropertyValue('--mw-surface')) || '#ffffff',
		text: resolveCssVar(styles.getPropertyValue('--mw-text')) || '#1f1f1f'
	};
}

function applyColorAlpha(color, alpha) {
	if (!color) {
		return 'rgba(0, 0, 0, ' + alpha + ')';
	}
	if (color.indexOf('rgb') === 0) {
		var numbers = color.replace(/[^\d,]/g, '').split(',');
		if (numbers.length >= 3) {
			return 'rgba(' + numbers[0] + ', ' + numbers[1] + ', ' + numbers[2] + ', ' + alpha + ')';
		}
	}
	if (color.indexOf('#') === 0) {
		var hex = color.replace('#', '');
		if (hex.length === 3) {
			hex = hex.split('').map(function (item) { return item + item; }).join('');
		}
		if (hex.length === 6) {
			var r = parseInt(hex.slice(0, 2), 16);
			var g = parseInt(hex.slice(2, 4), 16);
			var b = parseInt(hex.slice(4, 6), 16);
			return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
		}
	}
	return color;
}

var chartResizeRegistry = {};

function initEchartWhenReady(elementId, option, onReady) {
	if (typeof echarts === 'undefined') {
		return;
	}
	var element = document.getElementById(elementId);
	if (!element) {
		return;
	}
	var attempt = 0;
	var maxAttempts = 30;
	var raf = window.requestAnimationFrame || function(callback) {
		return setTimeout(callback, 16);
	};
	function tryInit() {
		if (element.clientWidth === 0 || element.clientHeight === 0) {
			if (attempt++ < maxAttempts) {
				raf(tryInit);
			}
			return;
		}
		var chart = echarts.getInstanceByDom(element) || echarts.init(element);
		chart.setOption(option);
		if (!chartResizeRegistry[elementId]) {
			chartResizeRegistry[elementId] = true;
			window.addEventListener("resize", function() {
				chart.resize();
			});
		}
		if (onReady) {
			onReady(chart);
		}
	}
	tryInit();
}
