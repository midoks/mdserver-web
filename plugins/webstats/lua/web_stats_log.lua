log_by_lua_block {

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
	local server_name
	local db = nil
	local json = require "cjson" 
	local sqlite3 = require "lsqlite3"
	local request_header = ngx.req.get_headers()
	
	local today,day,method,config,cache_count
	--- default common var end ---

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
					debug("ngx server name:"..ngx.var.server_name.."/new_domain:"..new_domain)
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

	
	local function cache_logs()

		-- make new id
		local new_id = nil
		local last_insert_id_key = server_name .. "_last_id"
		local err = nil

		new_id, err = cache:incr(last_insert_id_key, 1, 0)
		cache:incr(cache_count_id_key, 1, 0)
		if new_id >= max_log_id then
			cache:set(last_insert_id_key, 1)
			new_id = cache:get(last_insert_id_key)
		end

		D("new_id:"..new_id)

		local ip_list = request_header["x-forwarded-for"]
		local ip = ngx.var.remote_addr
		if ip and not ip_list then
			ip_list = ip
		end
		
		local client_port = ngx.var.remote_port
		local request_time = ngx.var.request_time
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
			-- user_agent=request_header['user-agent'], 
			protocol=protocol,
			is_spider=0,
			request_time=request_time,
			-- excluded=excluded,
			-- request_headers="",
			ip_list=ip_list,
			client_port=client_port
		}

		D(server_name..'__'..json.encode(kv))
		cache_set(server_name, new_id, "log_kv", json.encode(kv))
 	end

 	local function store_logs_line(db, stmt, input_server_name, lineno)
 		local logvalue = cache_get(input_server_name, lineno, "log_kv")
 		D("store_logs_line:"..logvalue)
		if not logvalue then return false end
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
			user_agent="d",
			protocol=protocol,
			request_time=request_time,
			is_spider=is_spider,
			request_headers=".",
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


		local log_dir = "{$SERVER_APP}/logs"
		local db_path= log_dir .. '/' .. input_server_name .. "/logs.db"
		local db, err = sqlite3.open(db_path)
		D("sqlite3 path:"..db_path)

		-- python3 ./plugins/webstats/index.py reload && echo "" > /Users/midoks/Desktop/mwdev/server/webstats/debug.log && wget http://t1.cn/

		D("sqlite3 error:"..tostring(err))
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
			D("网站监控报表数据库连接异常。")
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
					store_count = store_count + 1
					cache_clear(input_server_name, i, "log_kv")
					-- cache_clear(input_server_name, i, "STAT_FIELDS")
				end
			end
		end

		local res, err = stmt2:finalize()

		if tostring(res) == "5" then
			D("Finalize res:"..tostring(res))
			D("Finalize err:"..tostring(err))
			D("数据库连接繁忙，稍候存储.")
		end

		local res, err = db:execute([[COMMIT]])

		if db and db:isopen() then
			db:close()
		end

	end

	local function run_app()
		D("------------ debug start ------------")

		local c_name = ngx.var.server_name
		server_name = string.gsub(get_server_name(c_name),'_','.')
	
		D("c_name:"..c_name)
		D("server_name:"..server_name)

		cache_logs()
		store_logs(server_name)

		D("------------ debug end ------------")
	end


	local function run_app_ok()
		if not debug_mode then return run_app() end

		local presult, err = pcall(
			function() 
				run_app()
			end
		)
		if not presult then
			D("err on :"..tostring(err))
			return true
		end
	end

	return run_app_ok()
}

