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

	local server_name,ip,today,day,body_length,method,config,cache_count

	local db = nil
	local cache = ngx.shared.mw_total
	
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

