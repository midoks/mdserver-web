log_by_lua_block {
	--[[
	    webstats_log.lua - WebStats 日志采集模块
	    =========================================
	    
	    本模块在 Nginx 的 log_by_lua_block 阶段执行，负责：
	    - 采集请求日志数据
	    - 过滤不需要统计的请求
	    - 识别爬虫和客户端类型
	    - 计算 PV/UV/IP 等指标
	    - 将日志数据发送到共享内存队列
	    
	    执行时机：每次请求完成后（log_by_lua_block 阶段）
	    
	    主要数据流向：
	    请求完成 -> log_by_lua_block -> 数据采集 -> 过滤处理 -> 爬虫/客户端识别 -> 统计计算 -> 入队
	    
	    依赖模块：
	    - cjson: JSON 编解码
	    - webstats_common: 核心工具模块
	    - webstats_config: 全局配置
	    - webstats_sites: 站点配置
	]]

	-- 添加 Lua 模块搜索路径
	local cpath = "{$SERVER_APP}/lua/"
    if not package.cpath:find(cpath) then
        package.cpath = cpath .. "?.so;" .. package.cpath
    end
	if not package.path:find(cpath) then
		package.path = cpath .. "?.lua;" .. package.path
	end

	-- 调试模式开关
	local debug_mode = true

	-- 引入核心模块（单例模式）
	local __C = require "webstats_common"
	local C = __C:getInstance()

	-- 依赖模块
	local json = require "cjson" 
	local config = require "webstats_config"
	local sites = require "webstats_sites"

	-- 获取站点名称（通过域名匹配）
	local server_name = C:get_sn(ngx.var.server_name)

	-- 设置配置数据
	C:setConfData(config, sites)
	-- 获取合并后的站点配置
	local auto_config = C:setInputSn(server_name)

	-- 获取请求头部和方法
	local request_header = ngx.req.get_headers()
	local method = ngx.req.get_method()

	-- 共享内存字典实例（必须在使用前定义）
	local cache = ngx.shared.mw_total
	-- 日志队列键名
	local total_key = "log_kv_total"

	--[[
	    状态码过滤表
	    需要记录详细信息的状态码（4xx 和 5xx 错误）
	]]
	local status_codes_to_log = {
	["400"] = true, ["401"] = true, ["402"] = true, ["403"] = true, ["404"] = true,
	["405"] = true, ["406"] = true, ["407"] = true, ["408"] = true, ["409"] = true,
	["410"] = true, ["411"] = true, ["412"] = true, ["413"] = true, ["414"] = true,
	["415"] = true, ["416"] = true, ["417"] = true, ["418"] = true, ["421"] = true,
	["422"] = true, ["423"] = true, ["424"] = true, ["425"] = true, ["426"] = true,
	["449"] = true, ["451"] = true, ["499"] = true, ["500"] = true, ["501"] = true,
	["502"] = true, ["503"] = true, ["504"] = true, ["505"] = true, ["506"] = true,
	["507"] = true, ["509"] = true, ["510"] = true
	}

	--[[
	    HTTP 方法过滤表
	    需要统计的 HTTP 方法
	]]
	local http_methods = {["get"] = true, ["post"] = true, ["put"] = true, ["patch"] = true, ["delete"] = true}

	--[[
    排除函数模块
    ============
    
    以下函数用于判断请求是否应该被排除（不统计），包括：
    - IP 排除：全局和站点级别的排除 IP
    - 状态码排除：指定状态码的请求不统计
    - 扩展名排除：指定扩展名的文件不统计
    - URL 排除：指定 URL 路径不统计
]]

	--[[
	    加载全局排除 IP 列表到缓存
	    将配置中的全局排除 IP 存入共享内存，避免每次请求都读取配置
	]]
	local function load_global_exclude_ip()
    	local load_key = "global_exclude_ip_load"
		local global_exclude_ip = auto_config["exclude_ip"]
		if global_exclude_ip then
			for _, _ip in pairs(global_exclude_ip) do
				if not cache:get("global_exclude_ip_" .. _ip) then
					cache:set("global_exclude_ip_" .. _ip, true)
				end
			end
		end
    	cache:set(load_key, true)
	end

	--[[
	    加载站点级排除 IP 列表到缓存
	    @param input_server_name string 站点名称
	    @return boolean 是否成功
	]]
	local function load_exclude_ip(input_server_name)
		local load_key = input_server_name .. "_exclude_ip_load"
		local site_config = config[input_server_name]

		local site_exclude_ip = nil
		if site_config then
			site_exclude_ip = site_config["exclude_ip"]
		end

		if site_exclude_ip then
			for _, _ip in pairs(site_exclude_ip) do
				cache:set(input_server_name .. "_exclude_ip_" .. _ip, true)
			end
		end

    	cache:set(load_key, true)
		return true
	end

	--[[
	    根据状态码判断是否排除
	    检查当前请求的状态码是否在排除列表中
	    @return boolean 是否排除
	]]
	local function filter_status()
		if not auto_config['exclude_status'] then return false end
		local the_status = tostring(ngx.status)
		for _, v in ipairs(auto_config['exclude_status']) do
			if the_status == v then
				return true
			end
		end
		return false
	end

	--[[
	    根据文件扩展名判断是否排除
	    检查请求的 URI 是否以排除的扩展名结尾
	    @return boolean 是否排除
	]]
	local function exclude_extension()
		local uri = ngx.var.uri
		if not uri then return false end
		
		local exclude_ext = auto_config['exclude_extension']
		if not exclude_ext then return false end
		
		local lower_uri = string.lower(uri)
		for _, ext in ipairs(exclude_ext) do
			if string.find(lower_uri, "." .. ext .. "$", 1, true) then
				return true
			end
		end
		return false
	end

	--[[
	    根据 URL 判断是否排除
	    支持精确匹配和正则匹配两种模式
	    @return boolean 是否排除
	]]
	local function exclude_url()
		local request_uri = ngx.var.request_uri
		if not request_uri then return false end
		
		local url_conf = auto_config['exclude_url']
		if not url_conf then return false end
		
		-- 去掉开头的 '/'
		local the_uri = string.sub(request_uri, 2)
		for _, conf in ipairs(url_conf) do
			local mode = conf["mode"]
			local url = conf["url"]
			if mode == "regular" then
				-- 正则匹配模式
				if ngx.re.find(the_uri, url, "ijo") then
					return true
				end
			else
				-- 精确匹配模式
				if the_uri == url then
					return true
				end
			end
		end
		return false
	end

	--[[
	    根据 IP 判断是否排除
	    先检查站点级排除 IP，再检查全局排除 IP
	    @param input_server_name string 站点名称
	    @param ip string 客户端 IP
	    @return boolean 是否排除
	]]
	local function exclude_ip(input_server_name, ip)
		local site_config = config[input_server_name]
		if site_config then
			local server_exclude_ips = site_config["exclude_ip"]
			if server_exclude_ips then
				for _, _ip in pairs(server_exclude_ips) do
					if cache:get(input_server_name .. "_exclude_ip_" .. ip) then
						return true
					end
					break
				end
			end
		end
		
		return cache:get("global_exclude_ip_" .. ip) ~= nil
	end

	--[[
	    日志采集函数
	    采集请求数据，识别爬虫/客户端，计算统计指标，然后入队
	    
	    执行流程：
	    1. 获取日志 ID 和客户端 IP
	    2. 判断是否需要排除（状态码/扩展名/URL/IP）
	    3. 构建 IP 列表（含代理链）
	    4. 采集请求数据（URI、状态码、响应大小等）
	    5. 构建日志记录
	    6. 识别爬虫/客户端类型
	    7. 计算 PV/UV/IP 指标
	    8. 将数据入队到共享内存
	    
	    @param input_sn string 站点名称
	]]
	local function cache_logs(input_sn)
		-- 获取日志唯一 ID
		local new_id = C:get_last_id(input_sn)
		-- 获取客户端真实 IP（支持 CDN 转发）
		local ip = C:get_client_ip()
		-- 判断是否排除（状态码/扩展名/URL/IP）
		local excluded = filter_status() or exclude_extension() or exclude_url() or exclude_ip(input_sn, ip)

		-- 构建 IP 列表（包含代理链）
		local ip_list = request_header["x-forwarded-for"]
		if ip and not ip_list then
			ip_list = ip
		end

		local remote_addr = ngx.var.remote_addr
		if "table" == type(ip_list) then
			ip_list = json.encode(ip_list)
		end

		if remote_addr and not string.find(ip_list, remote_addr, 1, true) then
			ip_list = ip_list .. "," .. remote_addr
		end

		-- 采集请求数据
		local request_time = C:get_request_time()       -- 请求耗时（毫秒）
		local client_port = ngx.var.remote_port          -- 客户端端口
		local uri = tostring(ngx.var.uri)                -- 请求路径
		local status_code = ngx.status                   -- 状态码
		local protocol = ngx.var.server_protocol         -- 协议（HTTP/1.1 等）
		local request_uri = ngx.var.request_uri          -- 完整请求路径（含参数）
		local body_length = C:get_length()               -- 响应体大小
		local domain = C:get_domain()                    -- 域名
		local referer = ngx.var.http_referer             -- 来源页
		local user_agent = request_header['user-agent']  -- 用户代理
		local now_time = ngx.time()                      -- 当前时间戳

		-- 构建日志记录
		local kv = {
			id = new_id,
			time_key = os.date("%Y%m%d%H", now_time),  -- 小时级存储键
			time = now_time,
			ip = ip,
			domain = domain,
			server_name = input_sn,
			real_server_name = input_sn,
			method = method,
			status_code = status_code,
			uri = uri,
			request_uri = request_uri,
			body_length = body_length,
			referer = referer,
			user_agent = user_agent,
			protocol = protocol,
			is_spider = 0,              -- 是否爬虫
			request_time = request_time,
			excluded = excluded,        -- 是否排除
			request_headers = '',       -- 请求头（异常时记录）
			ip_list = ip_list,          -- IP 列表（含代理链）
			client_port = client_port
		}

		-- 初始化统计字段
		local request_stat_fields = {req = 1, length = body_length}
		local spider_stat_fields = {}
		local client_stat_fields = {}

		-- 非排除请求的额外处理
		if not excluded then
			-- 记录异常请求的原始数据（500/POST/403）
			if status_code == 500 or (method == "POST" and config['global']["record_post_args"] == true) or (status_code == 403 and config['global']["record_get_403_args"] == true) then
				local ok, data = pcall(function() return C:get_http_origin() end)
				if ok and data then
					kv["request_headers"] = data
				end
			end

			-- 统计状态码
			if status_codes_to_log[tostring(status_code)] then
				request_stat_fields["status_" .. status_code] = 1
			end

			-- 统计 HTTP 方法
			local lower_method = string.lower(method)
			if http_methods[lower_method] then
				request_stat_fields["http_" .. lower_method] = 1
			end

			-- 识别爬虫/客户端
			local is_spider, request_spider, spider_index = C:match_spider(user_agent)
			if not is_spider then
				-- 非爬虫：识别客户端类型，计算 PV/UV/IP
				client_stat_fields = C:match_client_arr(user_agent)
				local pvc, uvc = C:statistics_request(ip, is_spider, body_length)
				local ipc = C:statistics_ipc(input_sn, ip)
				
				if ipc > 0 then request_stat_fields["ip"] = 1 end
				if uvc > 0 then request_stat_fields["uv"] = 1 end
				if pvc > 0 then request_stat_fields["pv"] = 1 end
			else
				-- 爬虫：记录爬虫类型
				kv["is_spider"] = spider_index
				spider_stat_fields[request_spider] = 1
				request_stat_fields["spider"] = 1
			end
		end

		-- 构建最终数据结构
		local data = {
			server_name = input_sn,
			stat_fields = {
				request_stat_fields = request_stat_fields,
				client_stat_fields = client_stat_fields,
				spider_stat_fields = spider_stat_fields,
			},
			log_kv = kv,
		}

		-- 入队到共享内存队列
		cache:rpush(total_key, json.encode(data))
	end

	--[[
	    应用入口函数
	    加载排除 IP 列表，然后采集日志
	]]
	local function run_app()
		load_global_exclude_ip()
		load_exclude_ip(server_name)
		cache_logs(server_name)
	end


	--[[
	    应用入口包装函数（带错误捕获）
	    在调试模式下，使用 pcall 捕获异常并记录日志
	]]
	local function run_app_ok()
		if not debug_mode then return run_app() end

		local presult, err = pcall(function() run_app() end)
		if not presult then
			C:D("debug error on :" .. tostring(err))
			return true
		end
	end

	-- 执行应用
	return run_app_ok()
}

