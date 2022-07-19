log_by_lua_block {

	local ver = '0.0.1'
	local debug_mode = true


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
	
	local ip,today,day,body_length,method,config,cache_count
	local db = nil
	
	

	local function run_app()
		D("debug start")

		local presult, err = pcall(
			function() 
				json = require "cjson" 
				sqlite3 = require "lsqlite3"
			end
		)
		
		if not presult then
			D("depend on :"..tostring(err))
			return true
		end

		D("debug end")
	end

	return run_app()
}

