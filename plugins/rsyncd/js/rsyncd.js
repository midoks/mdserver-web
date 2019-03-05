

function smbRead(){
	var readme = '<ul class="help-info-text c7">';
    readme += '<li>mac上连接`cmd+k`</li>';
    readme += '<li>不产生.DS_Store文件: defaults write com.apple.desktopservices DSDontWriteNetworkStores true</li>';
    readme += '<li>windows上连接例子: \\192.168.1.194</li>';
    
    readme += '</ul>';

    $('.soft-man-con').html(readme);   
}