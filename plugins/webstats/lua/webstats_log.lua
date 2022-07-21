log_by_lua_block {

	-- python3 ./plugins/webstats/index.py reload && echo "" > /Users/midoks/Desktop/mwdev/server/webstats/debug.log && wget http://t1.cn/
	-- 
    -- 

	local ver = '0.0.1'
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
	local today
	local day
	local excluded
	--- default common var end ---

	local function init_var()
		config = require "config"

		request_header = ngx.req.get_headers()
		method = ngx.req.get_method()
		today = os.date("%Y%m%d")
		day = os.date("%d")

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

	local function arrlen_bylog(arr)
		if not arr then return 0 end
		count = 0
		for _,v in ipairs(arr) do
			count = count + 1
		end
		return count
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

	local function split_bylog(str,reps )
		local resultStrList = {}
		string.gsub(str,'[^'..reps..']+',function(w) table.insert(resultStrList,w) end)
		return resultStrList
	end

	local function get_client_ip_bylog()
		local client_ip = "unknown"
		local cdn = config['cdn']
		if cdn == true then
			for _,v in ipairs(config['cdn_headers']) do
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
				-- D("get_http_original:"..data)
				headers = table.concat(headers, data)
			end
		end
		return json.encode(headers)
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

		D("get_server_name start")

		local determined_name = nil
		local sites = require "sites"
		D("get_server_name"..json.encode(sites))
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
					D("ngx server name:"..ngx.var.server_name.."/new_domain:"..new_domain)
	            	if string.find(c_name, new_domain) then
	                	-- cache:set(c_name, v['name'],3600)
	                	-- return v['name']
						-- debug("find deter name:"..v['name'])
						determined_name = v['name']
	            	end
				end
			end
		end

		D("get_server_name end")
		if determined_name then
	        cache:set(c_name, determined_name,3600)
			return determined_name
		end
	    cache:set(c_name, unset_server_name, 3600)
		return unset_server_name
	end

	--------------------- exclude_func start --------------------------
	local function load_global_exclude_ip()
    	local load_key = "global_exclude_ip_load"
		-- update global exclude ip
		local global_exclude_ip = config["global"]["exclude_ip"]
		if global_exclude_ip then
			for i, _ip in pairs(global_exclude_ip)
			do 
				-- global
				if not cache:get("global_exclude_ip_".._ip) then
					D("set global exclude ip: ".._ip)
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
				D("set exclude ip: ".._ip)
				cache:set(input_server_name .. "_exclude_ip_".._ip, true)
			end
		end

    	-- set tag
    	cache:set(load_key, true)
		return true
	end

	local function filter_status()
		if not config['exclude_status'] then return false end
		local the_status = tostring(ngx.status)
		for _,v in ipairs(config['exclude_status'])
		do
			if the_status == v then
				return true
			end
		end
		return false
	end

	local function exclude_extension()
		if not ngx.var.uri then return false end
		if not config['exclude_extension'] then return false end
		for _,v in ipairs(config['exclude_extension'])
		do
			if ngx.re.find(ngx.var.uri,"[.]"..v.."$",'ijo') then
				return true
			end
		end
		return false
	end

	local function exclude_url()
		if not ngx.var.uri then return false end
		if not config['exclude_url'] then return false end
		local the_uri = string.sub(ngx.var.request_uri, 2)
		local url_conf = config["exclude_url"]
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
		D("server[" ..input_server_name.."]check exclude ip : "..tostring(check_server_exclude_ip))
		if check_server_exclude_ip then
			if cache:get(input_server_name .. "_exclude_ip_"..ip) then 
				D("-Exclude server ip:"..ip)
				return true
			end
		else
			if cache:get("global_exclude_ip_"..ip) then 
				D("*Excluded global ip:"..ip)
				return true
			end
		end
		return false
	end
	--------------------- exclude_func end ---------------------------
	
	---------------------       db start   ---------------------------
	local function update_stat(update_server_name, db, stat_table, key, columns)
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
	---------------------       db end     ---------------------------

	local function cache_logs()

		-- make new id
		local new_id = get_last_id(server_name)

		local excluded = false
		local ip = get_client_ip_bylog()
		excluded = filter_status() or exclude_extension() or exclude_url() or exclude_ip(server_name, ip)

		D("new_id:"..new_id)

		local ip_list = request_header["x-forwarded-for"]
		if ip and not ip_list then
			ip_list = ip
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
		local request_headers = get_http_original()

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
			request_headers=request_headers,
			ip_list=ip_list,
			client_port=client_port
		}

		local request_stat_fields = "req=req+1,length=length+"..body_length
		local spider_stat_fields = "x"
		local client_stat_fields = "x"

		if not excluded then

			if ngx.re.find("500,501,502,503,504,505,506,507,509,510,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,449,451", tostring(status_code), "jo") then
				local field = "status_"..status_code
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+1"
			end
			-- debug("method:"..method)
			local lower_method = string.lower(method)
			if ngx.re.find("get,post,put,patch,delete", lower_method, "ijo") then
				local field = "http_"..lower_method
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+1"
			end
		end

		local stat_fields = request_stat_fields..";"..client_stat_fields..";"..spider_stat_fields
		D("stat_fields:"..stat_fields)
		cache_set(server_name, new_id, "stat_fields", stat_fields)
		cache_set(server_name, new_id, "log_kv", json.encode(kv))
 	end

 	local function store_logs_line(db, stmt, input_server_name, lineno)
 		local logvalue = cache_get(input_server_name, lineno, "log_kv")
		if not logvalue then return false end
		D("store_logs_line:"..logvalue)
		local logline = json.decode(logvalue)

		local time = logline["time"]
		local id = logline["id"]
		local protocol = logline["protocol"]
		local client_port = logline["client_port"]
		local status_code = logline["status_code"]
		local uri = logline["uri"]
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
			D("Log stat fields is nil.")
			D("Logdata:"..logvalue)
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


		if not excluded then
			stmt:bind_names{
				time=time,
				ip=ip,
				domain=domain,
				server_name=server_name,
				method=method,
				status_code=status_code,
				uri=uri,
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
				D("Step res:"..tostring(res))
				D("Step err:"..tostring(err))
				D("Step数据库连接繁忙，稍候存储。")
				return false
			end
			stmt:reset()
			D("store_logs_line ok")

			update_stat(store_server_name, db, "client_stat", time_key, client_stat_fields)
			update_stat(store_server_name, db, "spider_stat", time_key, spider_stat_fields)
			D("stat ok")
		end

		local time_key = logline["time_key"]
		update_stat(input_server_name, db, "request_stat", time_key, request_stat_fields)
		return true
 	end
	
	local function store_logs(input_server_name)
		
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
		D("worker_id:"..worker_id)

		if is_working(input_server_name) then
			D("其他worker正在存储中，稍候存储。")
			-- cache:delete(flush_data_key)
			return
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
			D("web data db error")
			-- cache:set(storing_key, false)
			if db and db:isopen() then
				db:close()
			end
			return true
		end

		status, errorString = db:exec([[BEGIN TRANSACTION]])
		if store_end >= store_start then
			for i=store_start, store_end, 1 do
				D("store_start:"..store_start..":store_end:".. store_end)
				if store_logs_line(db, stmt2, input_server_name, i) then
					cache_clear(input_server_name, i, "log_kv")
					cache_clear(input_server_name, i, "stat_fields")
				end
			end
		end

		local res, err = stmt2:finalize()

		if tostring(res) == "5" then
			D("Finalize res:"..tostring(res))
			D("Finalize err:"..tostring(err))
			D("Finalize busy.")
			return true
		end

		local res, err = db:execute([[COMMIT]])
		if db and db:isopen() then
			db:close()
		end

		cache:set(store_start_id_key, store_end+1)
		unlock_working(input_server_name)
	end

	local function run_app()
		D("------------ debug start ------------")
		init_var()

		local c_name = ngx.var.server_name
		server_name = string.gsub(get_server_name(c_name),'_','.')
	
		D("c_name:"..c_name)
		D("server_name:"..server_name)

		load_global_exclude_ip()
		load_exclude_ip(server_name)

		cache_logs()
		store_logs(server_name)

		D("------------ debug end -------------")
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

