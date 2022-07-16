### 兼容性测试报告

快速测试命令

```
cd /www/server/mdserver-web/scripts/quick && bash debug.sh
cd /www/server/mdserver-web/plugins/php/versions && bash all_test.sh
```


| 系统名称 			| 	面板 		|	OpenResty 	|
| ----------------- |---------------|---------------|
| CentOS 7.9 		|✅				|✅				|
| CentOS 8.4 		|✅				|✅				|
| CentOS 8 Stream 	|✅				|✅				|
| CentOS 9 Stream 	|✅				|✅				|
| Debian 10.3 		|✅				|✅				|
| Debian 11.3 		|✅				|✅				|
| Ubuntu 18.04 		|✅				|✅				|
| Ubuntu 20.04 		|✅				|✅				|
| Ubuntu 22.04 		|✅				|✅				|	
| Fedora 31 		|✅				|✅				|
| Fedora 32 		|✅				|✅				|
| AlmaLinix 9 		|✅				|✅				|
| RockyLinux 8.6 	|✅				|✅				|
| Arch Linux　 	 	|✅				|✅				|
| openSUSE 15.4 	|✅				|✅				|



| 系统名称 			| PHP52 |PHP53	|PHP54	|PHP55	|PHP56	|PHP70	|PHP71	|PHP72	|PHP73	|PHP74	|PHP80	|PHP81	|
| ----------------- |-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| CentOS 7.9 		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| CentOS 8.4 		|✅ 	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| CentOS 8 Stream 	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| CentOS 9 Stream 	|:x:	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Debian 10.3 		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Debian 11.3 		|:x:	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Ubuntu 18.04 		|:x:	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Ubuntu 20.04 		|:x:	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Ubuntu 22.04 		|:x:	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Fedora 31 		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Fedora 32 		|:x:	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| AlmaLinix 9 		|:x:	|✅		|✅		|:x:	|:x:	|:x:	|:x:	|:x:	|✅		|:x:	|:x:	|:x:	|
| RockyLinux 8.6 	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|
| Arch Linux 	 	|:x:	|✅		|✅		|:x:	|:x:	|:x:	|:x:	|:x:	|✅		|✅		|✅		|✅		|
| openSUSE 15.4 	|:x:	|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|✅		|



| 系统名称 			| MySQL55	|MySQL56	|MySQL57	|MySQL80	|
| ----------------- |-----------|-----------|-----------|-----------|
| CentOS 7.9 		|✅			|✅			|✅			|:x:		|
| CentOS 8.4 		|:x:		|✅			|✅			|✅			|	
| CentOS 8 Stream 	|✅			|✅			|✅			|✅			|		
| CentOS 9 Stream 	|✅			|:x:		|✅			|✅			|
| Debian 10.3 		|✅			|✅			|✅			|:x:		|	
| Debian 11.3 		|✅			|✅			|✅			|✅			|
| Ubuntu 18.04 		|✅			|✅			|✅			|:x:		|	
| Ubuntu 20.04 		|✅			|✅			|✅			|:x:		|
| Ubuntu 22.04 		|✅			|✅			|✅			|✅			|
| Fedora 31 		|✅			|✅			|✅			|✅			|	
| Fedora 32 		|✅			|✅			|✅			|✅			|	
| AlmaLinix 9 		|✅			|:x:		|:x:		|:x:		|	
| RockyLinux 8.6 	|✅			|✅			|✅			|✅			|
| Arch Linux 	 	|✅			|✅			|✅			|✅			|	
| openSUSE 15.4 	|✅			|✅			|✅			|:x:		|

