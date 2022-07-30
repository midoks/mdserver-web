log_by_lua_block {

	-- python3 ./plugins/webstats/index.py reload && ab -c 10 -n 1000 http://t1.cn/
	-- 
    -- 

	local ver = '0.2.0'
	local max_log_id = 99999999999999
	local debug_mode = true

	local unset_server_name = "unset"


	local cpath = "{$SERVER_APP}/lua/"
    if not package.cpath:find(cpath) then
        package.cpath = cpath .. "?.so;" .. package.cpath
    end
	if not package.path:find(cpath) then
		package.path = cpath .. "?.lua;" .. package.path
	end

	-- debug func
	local function D(msg)
		if not debug_mode then return true end
    	local fp = io.open('{$SERVER_APP}/debug.log', 'ab')
    	if fp == nil then
        	return nil
    	end
		local localtime = os.date("%Y-%m-%d %H:%M:%S")
		if server_name then
    		fp:write(tostring(msg) .. "\n")
		else
    		fp:write(localtime..":"..tostring(msg) .. "\n")
		end
    	fp:flush()
    	fp:close()
    	return true
	end



	-- cache start ---
	local cache = ngx.shared.mw_total
	local function cache_set(server_name, id ,key, val)
		local line_kv = "log_kv_"..server_name..'_'..id.."_"..key
		cache:set(line_kv, val)
	end

	local function cache_clear(server_name, id, key)
		local line_kv = "log_kv_"..server_name..'_'..id.."_"..key
		cache:delete(line_kv)
	end

	local function cache_get(server_name, id, key)
		local line_kv = "log_kv_"..server_name..'_'..id.."_"..key
		local value = cache:get(line_kv)
		return value
	end
	-- cache end ---

	-- domain config is import
	local db = nil
	local json = require "cjson" 
	local sqlite3 = require "lsqlite3"

	local server_name
	local request_header
	local method
	local config
	local auto_config
	local excluded

	local day
	local today
	local number_day
	local day_column
	local flow_column
	local spider_column
	--- default common var end ---

	local function init_var()
		config = require "config"

		request_header = ngx.req.get_headers()
		method = ngx.req.get_method()

		day = os.date("%d")
		today = os.date("%Y%m%d")
		
		number_day = tonumber(day)
		day_column = "day"..number_day
		flow_column = "flow"..number_day
		spider_column = "spider_flow"..number_day
	end

	local function get_auto_config(site)
		local config_data = config
		local global_config = config_data["global"]
		if config_data[site] == nil then
			auto_config = global_config
		else
			auto_config = config_data[site]
			for k, v in pairs(global_config) do
				if auto_config[k] == nil then
					auto_config[k] = v
				end
			end
		end
		return auto_config
	end


	local function get_store_key()
		return os.date("%Y%m%d%H", os.time())
	end

	local function get_length()
		local clen  = ngx.var.body_bytes_sent
		if clen == nil then clen = 0 end
		return tonumber(clen)
	end

	local function get_domain()
		local domain = request_header['host']
		if domain ~= nil then
			domain = string.gsub(domain, "_", ".")
		else
			domain = "unknown"
		end
		return domain
	end

	local function write_file_bylog(filename,body,mode)
		local fp = io.open(filename,mode)
		if fp == nil then
			return nil
		end
		fp:write(body)
		fp:flush()
		fp:close()
		return true
	end
	
	local function read_file_body_bylog(filename)
		local fp = io.open(filename,'rb')
		if not fp then
			return nil
		end
		fbody = fp:read("*a")
		fp:close()
		if fbody == '' then
			return nil
		end
		return fbody
	end

	local function load_update_day(input_server_name)
		local _file = "{$SERVER_APP}/logs/"..input_server_name.."/update_day.log"
		return read_file_body_bylog(_file)
	end

	local function write_update_day(input_server_name)
		local update_day = today
		local _file = "{$SERVER_APP}/logs/"..input_server_name.."/update_day.log"
		write_file_bylog(_file, update_day, "w")
	end

	local function arrlen_bylog(arr)
		if not arr then return 0 end
		count = 0
		for _,v in ipairs(arr) do
			count = count + 1
		end
		return count
	end
	
	local function split_bylog(str,reps )
		local resultStrList = {}
		string.gsub(str,'[^'..reps..']+',function(w) table.insert(resultStrList,w) end)
		return resultStrList
	end

	local function is_ipaddr_bylog(client_ip)
		local cipn = split_bylog(client_ip,'.')
		if arrlen_bylog(cipn) < 4 then return false end
		for _,v in ipairs({1,2,3,4})
		do
			local ipv = tonumber(cipn[v])
			if ipv == nil then return false end
			if ipv > 255 or ipv < 0 then return false end
		end
		return true
	end

	local function get_client_ip_bylog()
		local client_ip = "unknown"
		local cdn = auto_config['cdn']
		if cdn == true then
			for _,v in ipairs(auto_config['cdn_headers']) do
				if request_header[v] ~= nil and request_header[v] ~= "" then
					local ip_list = request_header[v]
					client_ip = split_bylog(ip_list,',')[1]
					break;
				end
			end
		end
		if type(client_ip) == 'table' then client_ip = "" end
		if client_ip ~= "unknown" and string.match(client_ip,"^[%w:]+$") then
			return client_ip
		end
		if string.match(client_ip,"%d+%.%d+%.%d+%.%d+") == nil or not is_ipaddr_bylog(client_ip) then
			client_ip = ngx.var.remote_addr
			if client_ip == nil then
				client_ip = "unknown"
			end
		end
		return client_ip
	end

	local function get_last_id(input_server_name)
		local last_insert_id_key = input_server_name .. "_last_id"
		new_id, err = cache:incr(last_insert_id_key, 1, 0)
		cache:incr(cache_count_id_key, 1, 0)
		if new_id >= max_log_id then
			cache:set(last_insert_id_key, 1)
			new_id = cache:get(last_insert_id_key)
		end
		return new_id
	end

	local function get_request_time()
		local request_time = math.floor((ngx.now() - ngx.req.start_time()) * 1000)
		if request_time == 0 then  request_time = 1 end
		return request_time
	end

	local function get_end_time()
		local s_time = os.time()
		local n_date = os.date("*t",s_time + 86400)
		n_date.hour = 0
		n_date.min = 0
		n_date.sec = 0
		d_time = os.time(n_date)
		return d_time - s_time
	end

	local function get_http_original()
		local data = ""
		local headers = request_header
		if not headers then return data end
		if method ~='GET' then 
			data = ngx.req.get_body_data()
			if not data then
				data = ngx.req.get_post_args(1000000)
			end
			if "string" == type(data) then
				headers["payload"] = data
			end

			if "table" == type(data) then
				headers = table.concat(headers, data)
			end
		end
		return json.encode(headers)
	end

	local function is_migrating(input_server_name)
		local file = io.open("{$SERVER_APP}/migrating", "rb")
		if file then return true end
		local file = io.open("{$SERVER_APP}/logs/"..input_server_name.."/migrating", "rb")
		if file then return true end
		return false
	end


	local function is_working(name)
		local work_status = cache:get(name.."_working")
		if work_status ~= nil and work_status == true then
			return true 
		end
		return false
	end

	local function lock_working(name)
		local working_key = name.."_working"
		cache:set(working_key, true, 60)
	end

	local function unlock_working(name)
		local working_key = name.."_working"
		cache:set(working_key, false)
	end



	local function get_server_name(c_name)
		local my_name = cache:get(c_name)
		if my_name then return my_name end

		-- D("get_server_name start")

		local determined_name = nil
		local sites = require "sites"
		-- D("get_server_name"..json.encode(sites))
		for _,v in ipairs(sites)
		do
			if c_name == v["name"] then
				cache:set(c_name, v['name'],3600)
				return v["name"]
			end
			for _,d_name in ipairs(v['domains'])
			do
				if c_name == d_name then
					cache:set(c_name,v['name'],3600)
					return v['name']
	            elseif string.find(d_name, "*") then
					new_domain = string.gsub(d_name, '*', '.*')
	            	if string.find(c_name, new_domain) then
						determined_name = v['name']
	            	end
				end
			end
		end

		-- D("get_server_name end")
		if determined_name then
	        cache:set(c_name, determined_name,3600)
			return determined_name
		end
	    cache:set(c_name, unset_server_name, 3600)
		return unset_server_name
	end

	---------------------       db start   ---------------------------
	local function update_stat(db, stat_table, key, columns)
		-- 根据指定表名，更新统计数据
		if not columns then return end
		local stmt = db:prepare(string.format("INSERT INTO %s(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM %s WHERE time=:time);", stat_table, stat_table))
		stmt:bind_names{time=key}
		local res, err = stmt:step()
		stmt:finalize()
		local update_sql = "UPDATE ".. stat_table .. " SET " .. columns
		update_sql = update_sql .. " WHERE time=" .. key
		status, errorString = db:exec(update_sql)
	end

	local function get_update_field(field, value)
		return field.."="..field.."+"..tostring(value)
	end
	---------------------       db end     ---------------------------


	local function match_client()
		-- 匹配客户端
		local ua = ''
		if request_header['user-agent'] then
			ua = request_header['user-agent']
		end
		if not ua then
			return false, nil
		end
		local client_stat_fields = ""
		local clients_map = {
        	["android"] = "android",
        	["iphone"] = "iphone",
        	["ipod"] = "iphone",
        	["ipad"] = "iphone",
			["firefox"] = "firefox",
        	["msie"] = "msie",
        	["trident"] = "msie",
        	["360se"] = "qh360",
        	["360ee"] = "qh360",
        	["360browser"] = "qh360",
        	["qihoo"] = "qh360",
        	["the world"] = "theworld",
        	["theworld"] = "theworld",
        	["tencenttraveler"] = "tt",
        	["maxthon"] = "maxthon",
        	["opera"] = "opera",
        	["qqbrowser"] = "qq",
        	["ucweb"] = "uc",
        	["ubrowser"] = "uc",
        	["safari"] = "safari",
        	["chrome"] = "chrome",
        	["metasr"] = "metasr",
        	["2345explorer"] = "pc2345",
        	["edge"] = "edeg",
        	["edg"] = "edeg",
			["windows"] = "windows",
        	["linux"] = "linux",
        	["macintosh"] = "mac",
			["mobile"] = "mobile"
		}
		local mobile_regx = "(Mobile|Android|iPhone|iPod|iPad)"
		local mobile_res = ngx.re.match(ua, mobile_regx, "ijo")
		--mobile
		if mobile_res then
			client_stat_fields = client_stat_fields..","..get_update_field("mobile", 1)
			mobile_res = string.lower(mobile_res[0])
			if mobile_res ~= "mobile" then
				client_stat_fields = client_stat_fields..","..get_update_field(clients_map[mobile_res], 1)
			end
		else
			--pc
			-- 匹配结果的顺序，与ua中关键词的顺序有关
			-- lua的正则不支持|语法
			-- 短字符串string.find效率要比ngx正则高
			local pc_regx1 = "(360SE|360EE|360browser|Qihoo|TheWorld|TencentTraveler|Maxthon|Opera|QQBrowser|UCWEB|UBrowser|MetaSr|2345Explorer|Edg[e]*)" 
			local pc_res = ngx.re.match(ua, pc_regx1, "ijo")
			local cls_pc = nil
			if not pc_res then
				if string.find(ua, "[Ff]irefox") then
					cls_pc = "firefox"
				elseif string.find(ua, "MSIE") or string.find(ua, "Trident") then
					cls_pc = "msie"
				elseif string.find(ua, "[Cc]hrome") then
					cls_pc = "chrome"
				elseif string.find(ua, "[Ss]afari") then
					cls_pc = "safari"
				end
			else
				cls_pc = string.lower(pc_res[0])
			end
			-- D("UA:"..ua)
			-- D("PC cls:"..tostring(cls_pc))
			if cls_pc then
				client_stat_fields = client_stat_fields..","..get_update_field(clients_map[cls_pc], 1)
			else
				-- machine and other
				local machine_res, err = ngx.re.match(ua, "(ApacheBench|[Cc]url|HeadlessChrome|[a-zA-Z]+[Bb]ot|[Ww]get|[Ss]pider|[Cc]rawler|[Ss]crapy|zgrab|[Pp]ython|java)", "ijo")
				if machine_res then
					client_stat_fields = client_stat_fields..","..get_update_field("machine", 1)
				else
					-- 移动端+PC端+机器以外 归类到 其他
					client_stat_fields = client_stat_fields..","..get_update_field("other", 1)
				end
			end

			local os_regx = "(Windows|Linux|Macintosh)"
			local os_res = ngx.re.match(ua, os_regx, "ijo")
			if os_res then
				os_res = string.lower(os_res[0])
				client_stat_fields = client_stat_fields..","..get_update_field(clients_map[os_res], 1)
			end
		end

		local other_regx = "MicroMessenger"
		local other_res = string.find(ua, other_regx)
		if other_res then
			client_stat_fields = client_stat_fields..","..get_update_field("weixin", 1)
		end
		if client_stat_fields then
			client_stat_fields = string.sub(client_stat_fields, 2)
		end
		return client_stat_fields
	end

	local function match_spider(client_ip)
		-- 匹配蜘蛛请求
		local ua = ''
		if request_header['user-agent'] then
			ua = request_header['user-agent']
		end
		if not ua then
			return false, nil, 0
		end
		local is_spider = false
		local spider_name = nil

		local spider_table = {
			["baidu"] = 1,  -- check
			["bing"] = 2,  -- check 
			["qh360"] = 3, -- check
			["google"] = 4,
			["bytes"] = 5,  -- check
			["sogou"] = 6,  -- check
			["youdao"] = 7,
			["soso"] = 8,
			["dnspod"] = 9,
			["yandex"] = 10,
			["yisou"] = 11,
			["other"] = 12,
			["mpcrawler"] = 13,
			["yahoo"] = 14, -- check
			["duckduckgo"] = 15
		}

		local res,err = ngx.re.match(ua, "(Baiduspider|Bytespider|360Spider|Sogou web spider|Sosospider|Googlebot|bingbot|AdsBot-Google|Google-Adwords|YoudaoBot|Yandex|DNSPod-Monitor|YisouSpider|mpcrawler)", "ijo")
		check_res = true
		if res then
			is_spider = true
			spider_match = string.lower(res[0])
			if string.find(spider_match, "baidu", 1, true) then
				spider_name = "baidu"
			elseif string.find(spider_match, "bytes", 1, true) then
				spider_name = "bytes"
			elseif string.find(spider_match, "360", 1, true) then
				spider_name = "qh360"
			elseif string.find(spider_match, "sogou", 1, true) then
				spider_name = "sogou"
			elseif string.find(spider_match, "soso", 1, true) then
				spider_name = "soso"
			elseif string.find(spider_match, "google", 1, true) then
				spider_name = "google"
			elseif string.find(spider_match, "bingbot", 1, true) then
				spider_name = "bing"
			elseif string.find(spider_match, "youdao", 1, true) then
				spider_name = "youdao"
			elseif string.find(spider_match, "dnspod", 1, true) then
				spider_name = "dnspod"
			elseif string.find(spider_match, "yandex", 1, true) then
				spider_name = "yandex"
			elseif string.find(spider_match, "yisou", 1, true) then
				spider_name = "yisou"
			elseif string.find(spider_match, "mpcrawler", 1, true) then
				spider_name = "mpcrawler"
			end
		end

		if is_spider then 
			return is_spider, spider_name, spider_table[spider_name]
		end

		-- Curl|Yahoo|HeadlessChrome|包含bot|Wget|Spider|Crawler|Scrapy|zgrab|python|java|Adsbot|DuckDuckGo
		local other_res, err = ngx.re.match(ua, "(Yahoo|Slurp|DuckDuckGo)", "ijo")
		if other_res then
			other_res = string.lower(other_res[0])
			if string.find(other_res, "yahoo", 1, true) then
				spider_name = "yahoo"
			elseif string.find(other_res, "slurp", 1, true) then
				spider_name = "yahoo"
			elseif string.find(other_res, "duckduckgo", 1, true) then
				spider_name = "duckduckgo"
			end
			return true, spider_name, spider_table[spider_name]
		end
		return false, nil, 0
	end

	local function statistics_ipc(input_server_name,ip)
		-- 判断IP是否重复的时间限定范围是请求的当前时间+24小时
		local ipc = 0
		local ip_token = input_server_name..'_'..ip
		if not cache:get(ip_token) then
			ipc = 1
			cache:set(ip_token,1,get_end_time())
		end
		return ipc
	end

	local function statistics_request(ip, is_spider,body_length)
		-- 计算pv uv
		local pvc = 0
		local uvc = 0

		if not is_spider and method == 'GET' and ngx.status == 200 and body_length > 512 then
			local ua = ''
			if request_header['user-agent'] then
				ua = string.lower(request_header['user-agent'])
			end
	
			out_header = ngx.resp.get_headers()
			if out_header['content-type'] then
				if string.find(out_header['content-type'],'text/html', 1, true) then
					pvc = 1
					if request_header['user-agent'] then
						if string.find(ua,'mozilla') then
							local today = os.date("%Y-%m-%d")
							local uv_token = ngx.md5(ip .. request_header['user-agent'] .. today)
							if not cache:get(uv_token) then
								uvc = 1
								cache:set(uv_token,1,get_end_time())
							end
						end
					end
				end
			end
		end
		return pvc, uvc
	end

	--------------------- exclude_func start --------------------------
	local function load_global_exclude_ip()
    	local load_key = "global_exclude_ip_load"
		-- update global exclude ip
		local global_exclude_ip = auto_config["exclude_ip"]
		if global_exclude_ip then
			for i, _ip in pairs(global_exclude_ip)
			do 
				-- global
				-- D("set global exclude ip: ".._ip)
				if not cache:get("global_exclude_ip_".._ip) then
					cache:set("global_exclude_ip_".._ip, true)
				end
			end
		end
    	-- set tag
    	cache:set(load_key, true)
	end

	local function load_exclude_ip(input_server_name)

		local load_key = input_server_name .. "_exclude_ip_load"
		local site_config = config[input_server_name]

		local site_exclude_ip = nil
		if site_config then
			site_exclude_ip = site_config["exclude_ip"]
		end

		-- update server_name exclude ip
		if site_exclude_ip then
			for i, _ip in pairs(site_exclude_ip)
			do 
				-- D("set exclude ip: ".._ip)
				cache:set(input_server_name .. "_exclude_ip_".._ip, true)
			end
		end

    	-- set tag
    	cache:set(load_key, true)
		return true
	end

	local function filter_status()
		if not auto_config['exclude_status'] then return false end
		local the_status = tostring(ngx.status)
		for _,v in ipairs(auto_config['exclude_status'])
		do
			if the_status == v then
				return true
			end
		end
		return false
	end

	local function exclude_extension()
		if not ngx.var.uri then return false end
		if not auto_config['exclude_extension'] then return false end
		for _,v in ipairs(auto_config['exclude_extension'])
		do
			if ngx.re.find(ngx.var.uri,"[.]"..v.."$",'ijo') then
				return true
			end
		end
		return false
	end

	local function exclude_url()
		if not ngx.var.uri then return false end
		if not auto_config['exclude_url'] then return false end
		local the_uri = string.sub(ngx.var.request_uri, 2)
		local url_conf = auto_config["exclude_url"]
		for i,conf in pairs(url_conf)
		do
			local mode = conf["mode"]
			local url = conf["url"]
			if mode == "regular" then
				if ngx.re.find(the_uri, url, "ijo") then
					return true
				end
			else
				if the_uri == url then
					return true
				end
			end
		end
		return false
	end

	local function exclude_ip(input_server_name, ip)
		-- 排除IP匹配，分网站单独的配置和全局配置两种方式
		local site_config = config[input_server_name]
		local server_exclude_ips = nil
		local check_server_exclude_ip = false
		if site_config then
			server_exclude_ips = site_config["exclude_ip"]
			if not server_exclude_ips then
				return false
			end
			for  k, _ip in pairs(server_exclude_ips)
			do
				check_server_exclude_ip = true
				break
			end
		end
		-- D("server[" ..input_server_name.."]check exclude ip : "..tostring(check_server_exclude_ip))
		if check_server_exclude_ip then
			if cache:get(input_server_name .. "_exclude_ip_"..ip) then 
				-- D("-Exclude server ip:"..ip)
				return true
			end
		else
			if cache:get("global_exclude_ip_"..ip) then 
				-- D("*Excluded global ip:"..ip)
				return true
			end
		end
		return false
	end
	--------------------- exclude_func end ---------------------------
	
	local function statistics_uri(db, uri, uri_md5, body_length)
		-- count the number of URI requests and traffic
		local open_statistics_uri = config['global']["statistics_uri"]
		if not open_statistics_uri then return true end

		local stat_sql = nil
		stat_sql = "INSERT INTO uri_stat(uri_md5,uri) SELECT \""..uri_md5.."\",\""..uri.."\" WHERE NOT EXISTS (SELECT uri_md5 FROM uri_stat WHERE uri_md5=\""..uri_md5.."\");"
		local res, err = db:exec(stat_sql)
		
		stat_sql = "UPDATE uri_stat SET "..day_column.."="..day_column.."+1,"..flow_column.."="..flow_column.."+"..body_length.." WHERE uri_md5=\""..uri_md5.."\""
		local res, err = db:exec(stat_sql)
		return true
	end

	local function statistics_ip(db, ip, body_length)
		local open_statistics_ip = config['global']["statistics_ip"]	
		if not open_statistics_ip then return true end
		
		local stat_sql = nil
		stat_sql = "INSERT INTO ip_stat(ip) SELECT \""..ip.."\" WHERE NOT EXISTS (SELECT ip FROM ip_stat WHERE ip=\""..ip.."\");"
		local res, err = db:exec(stat_sql)
		
		stat_sql = "UPDATE ip_stat SET "..day_column.."="..day_column.."+1,"..flow_column.."="..flow_column.."+"..body_length.." WHERE ip=\""..ip.."\""
		local res, err = db:exec(stat_sql)
		return true
	end

	local function cache_logs()

		-- make new id
		local new_id = get_last_id(server_name)

		local excluded = false
		local ip = get_client_ip_bylog()
		excluded = filter_status() or exclude_extension() or exclude_url() or exclude_ip(server_name, ip)

		local ip_list = request_header["x-forwarded-for"]
		if ip and not ip_list then
			ip_list = ip
		end

		local remote_addr = ngx.var.remote_addr
		if not string.find(ip_list, remote_addr) then
			if remote_addr then
				ip_list = ip_list .. "," .. remote_addr
			end
		end

		-- local request_time = ngx.var.request_time
		local request_time = get_request_time()
		local client_port = ngx.var.remote_port
		local real_server_name = server_name
		local uri = ngx.var.uri
		local status_code = ngx.status
		local protocol = ngx.var.server_protocol
		local request_uri = ngx.var.request_uri
		local time_key = get_store_key()
		local method = ngx.req.get_method()
		local body_length = get_length()
		local domain = get_domain()
		local referer = ngx.var.http_referer

		kv = {
			id=new_id,
			time_key=time_key,
			time=os.time(),
			ip=ip,
			domain=domain,
			server_name=server_name,
			real_server_name=real_server_name,
			method=method, 
			status_code=status_code,
			uri=uri,
			request_uri=request_uri,
			body_length=body_length,
			referer=referer,
			user_agent=request_header['user-agent'],
			protocol=protocol,
			is_spider=0,
			request_time=request_time,
			excluded=excluded,
			request_headers='',
			ip_list=ip_list,
			client_port=client_port
		}

		local request_stat_fields = "req=req+1,length=length+"..body_length
		local spider_stat_fields = "x"
		local client_stat_fields = "x"

		if not excluded then

			if status_code == 500 or (method=="POST" and config["record_post_args"]==true) or (status_code==403 and config["record_get_403_args"]==true) then
				local data = ""
				local ok, err = pcall(function() data=get_http_original() end)
				if ok and not err then
					kv["request_headers"] = data
				end
				-- D("Get http orgininal ok:"..tostring(ok))
				-- D("Get http orgininal res:"..tostring(data))
			end


			if ngx.re.find("500,501,502,503,504,505,506,507,509,510,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,449,451", tostring(status_code), "jo") then
				local field = "status_"..status_code
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+1"
			end
			-- D("method:"..method)
			local lower_method = string.lower(method)
			if ngx.re.find("get,post,put,patch,delete", lower_method, "ijo") then
				local field = "http_"..lower_method
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+1"
			end


			local ipc = 0
     		local pvc = 0
     		local uvc = 0

     		is_spider, request_spider, spider_index = match_spider(ip)
     		if not is_spider then
     			client_stat_fields = match_client()
				if not client_stat_fields or #client_stat_fields == 0 then
					client_stat_fields = request_stat_fields..",other=other+1"
				end

				pvc, uvc = statistics_request(ip, is_spider,body_length)
				ipc = statistics_ipc(server_name,ip)
			else
				kv["is_spider"] = spider_index
				local field = "spider"
				spider_stat_fields = request_spider.."="..request_spider.."+"..1
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+"..1
			end
     		-- D("Is spider:"..tostring(is_spider==true))
			-- D("Request spider:".. tostring(request_spider))
			if ipc > 0 then 
				request_stat_fields = request_stat_fields..",ip=ip+1"
			end
			if uvc > 0 then 
				request_stat_fields = request_stat_fields..",uv=uv+1"
			end
			if pvc > 0 then
				request_stat_fields = request_stat_fields..",pv=pv+1"
			end
		end

		local stat_fields = request_stat_fields..";"..client_stat_fields..";"..spider_stat_fields
		-- D("stat_fields:"..stat_fields)
		cache_set(server_name, new_id, "stat_fields", stat_fields)
		cache_set(server_name, new_id, "log_kv", json.encode(kv))
 	end

 	local function store_logs_line(db, stmt, input_server_name, lineno)
 		local logvalue = cache_get(input_server_name, lineno, "log_kv")
		if not logvalue then return false end
		local logline = json.decode(logvalue)

		local time = logline["time"]
		local id = logline["id"]
		local protocol = logline["protocol"]
		local client_port = logline["client_port"]
		local status_code = logline["status_code"]
		local uri = logline["uri"]
		local request_uri = logline["request_uri"]
		local method = logline["method"]
		local body_length = logline["body_length"]
		local referer = logline["referer"]
		local ip = logline["ip"]
		local ip_list = logline["ip_list"]
		local request_time = logline["request_time"]
		local is_spider = logline["is_spider"]
		local domain = logline["domain"]
		local server_name = logline["server_name"]
		local user_agent = logline["user_agent"]
		local request_headers = logline["request_headers"]
		local excluded = logline["excluded"] 

		local request_stat_fields = nil 
		local client_stat_fields = nil
		local spider_stat_fields = nil
		local stat_fields = cache_get(input_server_name, id, "stat_fields")
		if stat_fields == nil then
			-- D("Log stat fields is nil.")
			-- D("Logdata:"..logvalue)
		else
			stat_fields = split_bylog(stat_fields, ";")
			request_stat_fields = stat_fields[1]
			client_stat_fields = stat_fields[2]
			spider_stat_fields = stat_fields[3]

			if "x" == client_stat_fields then
				client_stat_fields = nil
			end

			if "x" == spider_stat_fields then
				spider_stat_fields = nil
			end
		end

		local time_key = logline["time_key"]
		if not excluded then
			stmt:bind_names{
				time=time,
				ip=ip,
				domain=domain,
				server_name=server_name,
				method=method,
				status_code=status_code,
				uri=request_uri,
				body_length=body_length,
				referer=referer,
				user_agent=user_agent,
				protocol=protocol,
				request_time=request_time,
				is_spider=is_spider,
				request_headers=request_headers,
				ip_list=ip_list,
				client_port=client_port,
			}

			local res, err = stmt:step()
			if tostring(res) == "5" then
				-- D("step res:"..tostring(res))
				-- D("step err:"..tostring(err))
				-- D("the step database connection is busy, so it will be stored later.")
				return false
			end
			stmt:reset()
			-- D("store_logs_line ok")
			update_stat( db, "client_stat", time_key, client_stat_fields)
			update_stat( db, "spider_stat", time_key, spider_stat_fields)
			-- D("stat ok")

			-- only count non spider requests
			local ok, err = pcall(function() statistics_uri(db, request_uri, ngx.md5(request_uri), body_length) end)
			local ok, err = pcall(function() statistics_ip(db, ip, body_length) end)
		end

		update_stat( db, "request_stat", time_key, request_stat_fields)
		return true
 	end
	
	local function store_logs(input_server_name)
		if is_migrating(input_server_name) == true then
			-- D("migrating...")
			return
		end
		
		local last_insert_id_key = input_server_name.."_last_id"
		local store_start_id_key = input_server_name.."_store_start"
		local last_id = cache:get(last_insert_id_key)
		local store_start = cache:get(store_start_id_key)
		if store_start == nil then
			store_start = 1
		end
		local store_end = last_id
		if store_end == nil then
			store_end = 1
		end

		local worker_id = ngx.worker.id()
		if is_working(input_server_name) then
			-- D("other workers are being stored, please store later.")
			-- cache:delete(flush_data_key)
			return true
		end
		lock_working(input_server_name)

		local log_dir = "{$SERVER_APP}/logs"
		local db_path= log_dir .. '/' .. input_server_name .. "/logs.db"
		local db, err = sqlite3.open(db_path)

		-- if  tostring(err) ~= 'nil' then
		-- 	D("sqlite3 open error:"..tostring(err))
		-- 	return true
		-- end 

		local stmt2 = nil
		if db ~= nil then
			stmt2 = db:prepare[[INSERT INTO web_logs(
				time, ip, domain, server_name, method, status_code, uri, body_length,
				referer, user_agent, protocol, request_time, is_spider, request_headers, ip_list, client_port)
				VALUES(:time, :ip, :domain, :server_name, :method, :status_code, :uri,
				:body_length, :referer, :user_agent, :protocol, :request_time, :is_spider,
				:request_headers, :ip_list, :client_port)]]
		end

		if db == nil or stmt2 == nil then
			-- D("web data db error")
			-- cache:set(storing_key, false)
			if db and db:isopen() then
				db:close()
			end
			return true
		end
		db:exec([[PRAGMA synchronous = 0]])
		db:exec([[PRAGMA page_size = 4096]])
		db:exec([[PRAGMA journal_mode = wal]])
		db:exec([[PRAGMA journal_size_limit = 1073741824]])

		status, errorString = db:exec([[BEGIN TRANSACTION]])

		update_day = load_update_day(input_server_name)
		if not update_day or update_day ~= today then

			local update_sql = "UPDATE uri_stat SET "..day_column.."=0,"..flow_column.."=0"
			status, errorString = db:exec(update_sql)

			update_sql = "UPDATE ip_stat SET "..day_column.."=0,"..flow_column.."=0"
			status, errorString = db:exec(update_sql)
			write_update_day(input_server_name)
		end

		if store_end >= store_start then
			for i=store_start, store_end, 1 do
				-- D("store_start:"..store_start..":store_end:".. store_end)
				if store_logs_line(db, stmt2, input_server_name, i) then
					cache_clear(input_server_name, i, "log_kv")
					cache_clear(input_server_name, i, "stat_fields")
				end
			end
		end

		local res, err = stmt2:finalize()

		if tostring(res) == "5" then
			-- D("Finalize res:"..tostring(res))
			-- D("Finalize err:"..tostring(err))
		end

		local now_date = os.date("*t")
		local save_day = config['global']["save_day"]
		local save_date_timestamp = os.time{year=now_date.year,
			month=now_date.month, day=now_date.day-save_day, hour=0}
		-- delete expire data
		db:exec("DELETE FROM web_logs WHERE time<"..tostring(save_date_timestamp))

		local res, err = db:execute([[COMMIT]])
		if db and db:isopen() then
			db:close()
		end

		cache:set(store_start_id_key, store_end+1)
		unlock_working(input_server_name)
	end

	local function run_app()
		-- D("------------ debug start ------------")
		init_var()

		local c_name = ngx.var.server_name
		server_name = string.gsub(get_server_name(c_name),'_','.')
		get_auto_config(server_name)

		-- D("server_name:"..server_name)

		load_global_exclude_ip()
		load_exclude_ip(server_name)

		cache_logs()
		store_logs(server_name)

		-- D("------------ debug end -------------")
	end


	local function run_app_ok()
		if not debug_mode then return run_app() end

		local presult, err = pcall(
			function() 
				run_app()
			end
		)
		if not presult then
			D("debug error on :"..tostring(err))
			return true
		end
	end

	return run_app_ok()
}

