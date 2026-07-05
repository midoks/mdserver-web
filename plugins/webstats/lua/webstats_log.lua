--[[
    webstats_log.lua - WebStats 日志采集模块
    =========================================
    
    本模块在 Nginx 的 log_by_lua_file 阶段执行，负责：
    - 采集请求日志数据
    - 过滤不需要统计的请求
    - 识别爬虫和客户端类型
    - 计算 PV/UV/IP 等指标
    - 将日志数据发送到共享内存队列
    
    执行时机：每次请求完成后（log_by_lua_file 阶段）
    
    注意：log_by_lua* 上下文中部分 API 不可用，需使用 ngx.var.* 变量替代
]]

-- -- 添加 Lua 模块搜索路径
local cpath = "{$SERVER_APP}/lua/"
if not package.cpath:find(cpath) then
    package.cpath = cpath .. "?.so;" .. package.cpath
end
if not package.path:find(cpath) then
    package.path = cpath .. "?.lua;" .. package.path
end

-- 调试模式开关
local debug_mode = true
local app_dir = "{$SERVER_APP}"

local function run_app()
    local __C = require "webstats_common"
    local C = __C:getInstance()
    C:setAppDir(app_dir)

    local json = require "cjson" 
    local config = require "webstats_config"
    local sites = require "webstats_sites"

    local server_name = C:get_sn(ngx.var.server_name)
    
    local host = ngx.var.host
    local http_host = ngx.var.http_host
    if http_host then
        local port_start = string.find(http_host, ":", 1, true)
        if port_start then
            local port = string.sub(http_host, port_start + 1)
            host = host .. ":" .. port
        end
    end

    C:setConfData(config, sites)
    local auto_config = C:setInputSn(server_name)

    -- 在 log_by_lua* 上下文中使用 ngx.var 替代不可用的 API
    local method = ngx.var.request_method
    local user_agent = ngx.var.http_user_agent
    local x_forwarded_for = ngx.var.http_x_forwarded_for
    local referer = ngx.var.http_referer

    local cache = ngx.shared.mw_total
    local total_key = "log_kv_total"

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

    local http_methods = {["get"] = true, ["post"] = true, ["put"] = true, ["patch"] = true, ["delete"] = true}

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

    local function exclude_url()
        local request_uri = ngx.var.request_uri
        if not request_uri then return false end
        
        local url_conf = auto_config['exclude_url']
        if not url_conf then return false end
        
        local the_uri = string.sub(request_uri, 2)
        for _, conf in ipairs(url_conf) do
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

    local function cache_logs(input_sn)
        local new_id = C:get_last_id(input_sn)
        local ip = C:get_client_ip()
        local excluded = filter_status() or exclude_extension() or exclude_url() or exclude_ip(input_sn, ip)

        local ip_list = x_forwarded_for
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

        local request_time = C:get_request_time()
        local client_port = ngx.var.remote_port
        local uri = tostring(ngx.var.uri)
        local status_code = ngx.status
        local protocol = ngx.var.server_protocol
        local request_uri = ngx.var.request_uri
        local body_length = C:get_length()
        local domain = host or "unknown"

        local kv = {
            id = new_id,
            time_key = os.date("%Y%m%d%H", ngx.time()),
            time = ngx.time(),
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
            is_spider = 0,
            request_time = request_time,
            excluded = excluded,
            request_headers = '',
            ip_list = ip_list,
            client_port = client_port
        }

        local request_stat_fields = {req = 1, length = body_length}
        local spider_stat_fields = {}
        local client_stat_fields = {}

        if not excluded then
            if status_code == 500 or (method == "POST" and config['global']["record_post_args"] == true) or (status_code == 403 and config['global']["record_get_403_args"] == true) then
                kv["request_headers"] = json.encode({
                    user_agent = user_agent,
                    referer = referer,
                    host = host
                })
            end

            if status_codes_to_log[tostring(status_code)] then
                request_stat_fields["status_" .. status_code] = 1
            end

            local lower_method = method and string.lower(method) or ""
            if lower_method ~= "" and http_methods[lower_method] then
                request_stat_fields["http_" .. lower_method] = 1
            end

            local is_spider, request_spider, spider_index = C:match_spider(user_agent)
            if not is_spider then
                client_stat_fields = C:match_client_arr(user_agent)
                local pvc, uvc = C:statistics_request(ip, is_spider, body_length)
                local ipc = C:statistics_ipc(input_sn, ip)
                
                if ipc > 0 then request_stat_fields["ip"] = 1 end
                if uvc > 0 then request_stat_fields["uv"] = 1 end
                if pvc > 0 then request_stat_fields["pv"] = 1 end
            else
                kv["is_spider"] = spider_index
                spider_stat_fields[request_spider] = 1
                request_stat_fields["spider"] = 1
            end
        end

        local data = {
            server_name = input_sn,
            stat_fields = {
                request_stat_fields = request_stat_fields,
                client_stat_fields = client_stat_fields,
                spider_stat_fields = spider_stat_fields,
            },
            log_kv = kv,
        }

        cache:rpush(total_key, json.encode(data))
    end

    -- C:D("webstats_log run_app start, server_name=" .. tostring(server_name))
    -- C:D(tostring(total_key) ..":" .. tostring(ngx.shared.mw_total:llen(total_key)))
    load_global_exclude_ip()
    load_exclude_ip(server_name)
    cache_logs(server_name)
    -- C:D("webstats_log run_app end")
end

local function run_app_ok()
    -- if not debug_mode then return run_app() end
    local presult, err = pcall(function() run_app() end)
    if not presult then
        C:D("debug error on :" .. tostring(err))
        return true
    end
end

return run_app_ok()