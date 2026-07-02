log_by_lua_block {

	local cpath = "{$SERVER_APP}/lua/"
    if not package.cpath:find(cpath) then
        package.cpath = cpath .. "?.so;" .. package.cpath
    end
	if not package.path:find(cpath) then
		package.path = cpath .. "?.lua;" .. package.path
	end

	local ver = '0.2.4'
	local debug_mode = true

	local __C = require "webstats_common"
	local C = __C:getInstance()

	-- cache start ---
	local cache = ngx.shared.mw_total
	local function cache_set(server_name, id ,key, val)
		local line_kv = "log_kv_"..server_name..'_'..id.."_"..key
		-- cache:set(line_kv, val)
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
	local config = require "webstats_config"
	local sites = require "webstats_sites"

	-- string.gsub(C:get_sn(ngx.var.server_name),'_','.')
	local server_name = C:get_sn(ngx.var.server_name)


	C:setConfData(config, sites)

	local auto_config = C:setInputSn(server_name)

	local request_header = ngx.req.get_headers()
	local method = ngx.req.get_method()
	local excluded = false

	local day = os.date("%d")
	local number_day = tonumber(day)
	local day_column = "day"..number_day
	local flow_column = "flow"..number_day
	local spider_column = "spider_flow"..number_day
	--- default common var end ---

	local function init_var()
		return true
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
		if not ngx.var.request_uri then return false end
		if not auto_config['exclude_url'] then return false end
		local the_uri = string.sub(ngx.var.request_uri, 2)
		local url_conf = auto_config["exclude_url"]
		for i,conf in ipairs(url_conf)
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

	local function cache_logs_old(server_name)

		-- make new id
		local new_id = C:get_last_id(server_name)

		local excluded = false
		local ip = C:get_client_ip()
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
		local request_time = C:get_request_time()
		local client_port = ngx.var.remote_port
		local real_server_name = ngx.var.server_name
		local uri = ngx.var.uri
		local status_code = ngx.status
		local protocol = ngx.var.server_protocol
		local request_uri = ngx.var.request_uri
		local time_key = C:get_store_key()
		local method = method
		local body_length = C:get_length()
		local domain = C:get_domain()
		local referer = ngx.var.http_referer

		local kv = {
			id=new_id,
			time_key=time_key,
			time=ngx.time(),
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

			if status_code == 500 or (method=="POST" and config["record_post_args"] == true) or (status_code==403 and config["record_get_403_args"] == true) then
				local data = ""
				local ok, err = pcall(function() data = C:get_http_origin() end)
				if ok and not err then
					kv["request_headers"] = data
				end
			end

			if ngx.re.find("500,501,502,503,504,505,506,507,509,510,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,449,451,499", tostring(status_code), "jo") then
				local field = "status_"..status_code
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+1"
			end

			local lower_method = string.lower(method)
			if ngx.re.find("get,post,put,patch,delete", lower_method, "ijo") then
				local field = "http_"..lower_method
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+1"
			end


			local ipc = 0
     		local pvc = 0
     		local uvc = 0

     		local is_spider, request_spider, spider_index = C:match_spider(kv['user_agent'])
     		if not is_spider then

     			client_stat_fields = C:match_client(kv['user_agent'])
				if not client_stat_fields or #client_stat_fields == 0 then
					client_stat_fields = request_stat_fields..",other=other+1"
				end

				pvc, uvc = C:statistics_request(ip, is_spider,body_length)
				ipc = C:statistics_ipc(server_name,ip)
			else
				kv["is_spider"] = spider_index
				local field = "spider"
				spider_stat_fields = request_spider.."="..request_spider.."+"..1
				request_stat_fields = request_stat_fields .. ","..field.."="..field.."+"..1
			end

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

		cache_set(server_name, new_id, "stat_fields", stat_fields)
		cache_set(server_name, new_id, "log_kv", json.encode(kv))
 	end

	local function cache_logs(input_sn)

		-- make new id
		local new_id = C:get_last_id(input_sn)

		local excluded = false
		local ip = C:get_client_ip()
		excluded = filter_status() or exclude_extension() or exclude_url() or exclude_ip(input_sn, ip)

		local ip_list = request_header["x-forwarded-for"]
		if ip and not ip_list then
			ip_list = ip
		end

		local remote_addr = ngx.var.remote_addr

		-- 修复反向代理代过来的数据
		if "table" == type(ip_list) then
            ip_list = json.encode(ip_list)
        end

		if not string.find(ip_list, remote_addr) then
			if remote_addr then
				ip_list = ip_list .. "," .. remote_addr
			end
		end

		-- local request_time = ngx.var.request_time
		local request_time = C:get_request_time()
		local client_port = ngx.var.remote_port
		local real_server_name = input_sn
		local uri = tostring(ngx.var.uri)
		local status_code = ngx.status
		local protocol = ngx.var.server_protocol
		local request_uri = ngx.var.request_uri
		local time_key = C:get_store_key()
		local method = method
		local body_length = C:get_length()
		local domain = C:get_domain()
		local referer = ngx.var.http_referer

		local kv = {
			id=new_id,
			time_key=time_key,
			time=ngx.time(),
			ip=ip,
			domain=domain,
			server_name=input_sn,
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

		-- C:D(json.encode(kv))
		local request_stat_fields = {req=1,length=body_length}

		local spider_stat_fields = {}
		local client_stat_fields = {}

		if not excluded then
			if status_code == 500 or (method=="POST" and config['global']["record_post_args"] == true) or (status_code==403 and config['global']["record_get_403_args"] == true) then
				local data = ""
				local ok, err = pcall(function() data = C:get_http_origin() end)
				if ok and not err then
					kv["request_headers"] = data
				else
					C:D("debug request_headers error:"..tostring(err))
				end
			end

			if ngx.re.find("500,501,502,503,504,505,506,507,509,510,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,426,449,451,499", tostring(status_code), "jo") then
				local field = "status_"..status_code
				request_stat_fields[field] = 1
			end

			-- D("method:"..method)
			local lower_method = string.lower(method)
			if ngx.re.find("get,post,put,patch,delete", lower_method, "ijo") then
				local field = "http_"..lower_method
				request_stat_fields[field] = 1
			end


			local ipc = 0
     		local pvc = 0
     		local uvc = 0

     		local is_spider, request_spider, spider_index = C:match_spider(kv['user_agent'])
     		if not is_spider then

     			client_stat_fields = C:match_client_arr(kv['user_agent'])
				pvc, uvc = C:statistics_request(ip, is_spider,body_length)
				ipc = C:statistics_ipc(input_sn,ip)
			else
				kv["is_spider"] = spider_index
				local field = "spider"
				spider_stat_fields[request_spider] = 1
				request_stat_fields[field] = 1
			end

			if ipc > 0 then
				request_stat_fields["ip"] = 1
			end
			if uvc > 0 then 
				request_stat_fields["uv"] = 1
			end
			if pvc > 0 then
				request_stat_fields["pv"] = 1
			end
		end

		local stat_fields = {
			request_stat_fields=request_stat_fields,
			client_stat_fields=client_stat_fields,
			spider_stat_fields=spider_stat_fields,
		}

		local data = {
			server_name=input_sn,
			stat_fields=stat_fields,
			log_kv=kv,
		}

		local push_data = json.encode(data)
		-- C:D(json.encode(push_data))
		local key = C:getTotalKey()
		ngx.shared.mw_total:rpush(key, push_data)
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
			stat_fields = C:split(stat_fields, ";")
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

			C:update_stat( db, "client_stat", time_key, client_stat_fields)
			C:update_stat( db, "spider_stat", time_key, spider_stat_fields)
			-- C:D("stat ok")

			-- only count non spider requests
			local ok, err = C:statistics_uri(db, request_uri, ngx.md5(request_uri), body_length)
			local ok, err = C:statistics_ip(db, ip, body_length)
		end

		C:update_stat( db, "request_stat", time_key, request_stat_fields)
		return true
 	end
	
	local function store_logs(input_sn)
		if C:is_migrating(input_sn) == true then
			-- D("migrating...")
			return
		end
		
		local last_insert_id_key = input_sn.."_last_id"
		local store_start_id_key = input_sn.."_store_start"
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
		if C:is_working(input_sn) then
			-- D("other workers are being stored, please store later.")
			-- cache:delete(flush_data_key)
			return true
		end
		C:lock_working(input_sn)

		local log_dir = "{$SERVER_APP}/logs"
		local db_path = log_dir .. '/' .. input_sn .. "/logs.db"
		local db, err = sqlite3.open(db_path)

		if  tostring(err) ~= 'nil' then
			C:D("sqlite3 open error:"..tostring(err))
			return true
		end 

		db:exec([[PRAGMA synchronous = 0]])
		db:exec([[PRAGMA page_size = 4096]])
		db:exec([[PRAGMA journal_mode = wal]])
		db:exec([[PRAGMA journal_size_limit = 1073741824]])

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
		
		status, errorString = db:exec([[BEGIN TRANSACTION]])

		C:clean_stats(db, input_sn)

		if store_end >= store_start then
			for i=store_start, store_end, 1 do
				-- D("store_start:"..store_start..":store_end:".. store_end)
				if store_logs_line(db, stmt2, input_sn, i) then
					cache_clear(input_sn, i, "log_kv")
					cache_clear(input_sn, i, "stat_fields")
				end
			end
		end

		local res, err = stmt2:finalize()
		if tostring(res) == "5" then
			C:D("Finalize res:"..tostring(res)..",Finalize err:"..tostring(err))
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
		C:unlock_working(input_sn)
	end

	local function run_app()
		-- C:D("------------ debug start ------------")
		init_var()

		load_global_exclude_ip()
		load_exclude_ip(server_name)

		cache_logs(server_name)
		-- C:cron()

		-- cache_logs_old(server_name)
		-- store_logs(server_name)
		-- C:D("------------ debug end -------------")
	end


	local function run_app_ok()
		if not debug_mode then return run_app() end

		local presult, err = pcall( function() run_app() end)
		if not presult then
			C:D("debug error on :"..tostring(err))
			return true
		end
	end

	return run_app_ok()
}

