
--[[
    webstats_common.lua - WebStats 统计系统核心模块
    ==================================================
    
    本模块提供 WebStats 系统的核心功能，包括：
    - 数据库连接管理
    - 日志数据处理与存储
    - 定时任务调度
    - 爬虫/客户端识别
    - IP/URL 统计
    
    架构说明：
    1. 单例模式：通过 getInstance() 获取全局唯一实例
    2. 共享内存：使用 ngx.shared.mw_total 作为日志缓存队列
    3. SQLite 数据库：每个站点独立一个数据库文件
    4. 定时任务：每 0.1 秒执行一次日志持久化
    
    主要数据流向：
    webstats_log.lua (日志采集) -> ngx.shared.mw_total (缓存队列) -> cron() (定时处理) -> SQLite (持久化)
    
    依赖模块：
    - cjson: JSON 编解码
    - lsqlite3: SQLite 数据库操作
    - webstats_config: 全局配置
    - webstats_sites: 站点配置
]]

local setmetatable = setmetatable
local _M = { _VERSION = '1.0' }
local mt = { __index = _M }

-- 依赖模块
local json = require "cjson"
local sqlite3 = require "lsqlite3"
local config = require "webstats_config"
local sites = require "webstats_sites"

-- 调试模式开关
local debug_mode = true
-- 共享内存队列键名
local total_key = "log_kv_total"

-- 未匹配到站点时使用的默认名称
local unset_server_name = "unset"
-- 日志 ID 最大值，超过后重置
local max_log_id = 99999999999999
-- Nginx 共享内存字典实例
local cache = ngx.shared.mw_total

-- 当前日期（日）
local day = os.date("%d")
local number_day = tonumber(day)
-- 数据库列名：day + 日期（如 day01）
local day_column = "day" .. number_day
-- 数据库列名：flow + 日期（如 flow01）
local flow_column = "flow" .. number_day

-- 日志文件存储目录
local log_dir = "{$SERVER_APP}/logs"

-- 当前站点的配置（模块级变量，供多个函数共享）
local auto_config = nil

-- 当前日期（用于更新日志文件）
local today = ngx.re.gsub(ngx.today(), '-', '')

--[[
    创建模块实例
    @return table 模块实例对象
]]
function _M.new(self)
    local self = {
        total_key = total_key,  -- 共享内存队列键名
        params = nil,           -- 请求参数
        site_config = nil,      -- 站点配置
        config = nil,           -- 全局配置
    }
    return setmetatable(self, mt)
end


--[[
    获取单例实例（懒加载）
    首次调用时创建实例并启动定时任务
    @return table 全局唯一的模块实例
]]
function _M.getInstance(self)
    if self.instance == nil then
        self.instance = self:new()
        self:cron()  -- 启动定时任务
    end
    assert(self.instance ~= nil)
    return self.instance
end


--[[
    初始化 SQLite 数据库连接
    @param input_sn string 站点名称
    @return table|nil SQLite 数据库对象，失败返回 nil
    
    SQLite 优化配置：
    - synchronous = 0: 关闭同步写入，提升性能（可能丢失数据）
    - cache_size = 8000: 设置页缓存大小为 8000 页
    - page_size = 32768: 设置页大小为 32KB
    - journal_mode = wal: 使用 WAL 模式，支持并发读写
    - journal_size_limit = 20GB: WAL 文件大小限制
]]
function _M.initDB(self, input_sn)
    local path = log_dir .. '/' .. input_sn .. "/logs.db"
    local db, err = sqlite3.open(path)

    if err then
        return nil
    end

    db:exec([[PRAGMA synchronous = 0]])
    db:exec([[PRAGMA cache_size = 8000]])
    db:exec([[PRAGMA page_size = 32768]])
    db:exec([[PRAGMA journal_mode = wal]])
    db:exec([[PRAGMA journal_size_limit = 21474836480]])
    return db
end

--[[
    获取共享内存队列键名
    @return string 队列键名
]]
function _M.getTotalKey(self)
    return self.total_key
end

--[[
    JSON 编码
    @param msg table 待编码的数据
    @return string JSON 字符串
]]
function _M.to_json(self, msg)
    return json.encode(msg)
end

--[[
    设置配置数据
    @param config table 全局配置
    @param site_config table 站点配置
]]
function _M.setConfData(self, config, site_config)
    self.config = config
    self.site_config = site_config
end

--[[
    设置请求参数
    @param params table 请求参数
]]
function _M.setParams(self, params)
    self.params = params
end

--[[
    设置输入站点名称并获取合并后的配置
    将站点配置与全局配置合并，站点配置优先级更高
    @param input_sn string 站点名称
    @return table 合并后的配置
]]
function _M.setInputSn(self, input_sn)
    local global_config = config["global"]
    if config[input_sn] == nil then
        auto_config = global_config
    else
        auto_config = config[input_sn]
        -- 合并全局配置到站点配置（站点配置优先）
        for k, v in pairs(global_config) do
            if auto_config[k] == nil then
                auto_config[k] = v
            end
        end
    end
    return auto_config
end

--[[
    获取当前请求的域名
    @return string 域名，失败返回 "unknown"
]]
function _M.get_domain(self)
    local domain = ngx.req.get_headers()['host']
    if domain == nil then
        domain = "unknown"
    end
    return domain
end

--[[
    字符串分割函数
    @param str string|table 待分割的字符串或已分割的表
    @param reps string 分隔符
    @return table 分割后的数组
    
    注意：如果输入已经是 table 类型，直接返回原表（用于处理反向代理传递的数据）
]]
function _M.split(self, str, reps)
    if "table" == type(str) then
        return str
    end
    local arr = {}
    local pattern = "[^" .. reps .. "]+"
    for w in string.gmatch(str, pattern) do
        arr[#arr + 1] = w
    end
    return arr
end

--[[
    获取数组长度
    @param arr table 数组
    @return number 数组长度，空或 nil 返回 0
]]
function _M.arrlen(self, arr)
    if not arr then return 0 end
    return #arr
end

--[[
    验证 IPv4 地址格式
    @param client_ip string IP 地址
    @return boolean 是否为有效的 IPv4 地址
]]
function _M.is_ipaddr(self, client_ip)
    if not client_ip then return false end
    local parts = self:split(client_ip, '.')
    if #parts ~= 4 then return false end
    for i = 1, 4 do
        local ipv = tonumber(parts[i])
        if not ipv or ipv < 0 or ipv > 255 then return false end
    end
    return true
end


--[[
    根据域名/服务器名获取站点名称（带缓存）
    匹配规则：
    1. 精确匹配站点名称
    2. 精确匹配站点域名列表
    3. 通配符匹配（支持 * 通配符）
    @param input_sn string 输入的域名或服务器名
    @return string 匹配到的站点名称，未匹配返回 "unset"
    
    缓存策略：匹配结果缓存 24 小时（86400 秒）
]]
function _M.get_sn(self, input_sn)
    -- 优先从缓存获取
    local dst_name = cache:get(input_sn)
    if dst_name then return dst_name end

    -- 遍历所有站点进行匹配
    for _, v in ipairs(sites) do
        -- 精确匹配站点名称
        if input_sn == v["name"] then
            cache:set(input_sn, v['name'], 86400)
            return v["name"]
        end
        
        -- 遍历站点的域名列表
        for _, dst_domain in ipairs(v['domains']) do
            -- 精确匹配域名
            if input_sn == dst_domain then
                cache:set(input_sn, v['name'], 86400)
                return v['name']
            -- 通配符匹配（如 *.example.com）
            elseif string.find(dst_domain, "*", 1, true) then
                local pattern = "^" .. string.gsub(dst_domain, "*", ".*") .. "$"
                if ngx.re.match(input_sn, pattern, "ijo") then
                    cache:set(input_sn, v['name'], 86400)
                    return v['name']
                end
            end
        end
    end

    -- 未匹配到任何站点
    cache:set(input_sn, unset_server_name, 86400)
    return unset_server_name
end


--[[
    获取存储键（按小时分组）
    格式：YYYYMMDDHH（如 2026070213）
    @return string 存储键
]]
function _M.get_store_key(self)
    return os.date("%Y%m%d%H", ngx.time())
end

--[[
    根据指定时间获取存储键
    @param htime number 时间戳
    @return string 存储键
]]
function _M.get_store_key_with_time(self, htime)
    return os.date("%Y%m%d%H", htime)
end

--[[
    获取响应体大小
    @return number 响应体字节数
]]
function _M.get_length(self)
    local clen = ngx.var.body_bytes_sent
    if clen == nil then clen = 0 end
    return tonumber(clen)
end

--[[
    获取日志唯一 ID（自动递增）
    使用共享内存实现跨 Worker 进程的 ID 递增
    @param input_sn string 站点名称
    @return number 日志 ID
    
    溢出处理：ID 达到 max_log_id 后重置为 1
]]
function _M.get_last_id(self, input_sn)
    local last_insert_id_key = input_sn .. "_last_id"
    -- 原子递增，初始值为 0
    local new_id, err = cache:incr(last_insert_id_key, 1, 0)
    -- 溢出检查
    if new_id >= max_log_id then
        cache:set(last_insert_id_key, 1)
        new_id = cache:get(last_insert_id_key)
    end
    return new_id
end

--[[
    获取 HTTP 请求原始数据（请求头 + 请求体）
    仅对非 GET 请求记录请求体
    @return string JSON 格式的请求数据
]]
function _M.get_http_origin(self)
    local data = ""
    local headers = ngx.req.get_headers()
    if not headers then return data end
    
    local req_method = ngx.req.get_method()
    -- 仅记录非 GET 请求的请求体
    if req_method ~= 'GET' then
        data = ngx.var.request_body
        if not data then
            data = ngx.req.get_body_data()
        end

        if "string" == type(data) then
            headers["payload"] = data
        elseif "table" == type(data) then
            headers["payload"] = table.concat(data, "&")
        end
    end
    return json.encode(headers)
end

--[[
    定时任务前置准备（初始化统计记录）
    为当前小时和下一小时预创建统计记录，避免 UPDATE 时记录不存在
    
    处理流程：
    1. 获取锁防止并发执行
    2. 遍历所有站点
    3. 为每个站点初始化数据库连接
    4. 在事务中预创建统计记录（request_stat, client_stat, spider_stat）
    5. 提交事务并关闭数据库
    
    @return boolean 是否成功
]]
function _M.cronPre(self)
    self:lock_working('cron_init_stat')

    local ok, err = pcall(function()
        -- 获取当前小时和下一小时的存储键
        local time_key = self:get_store_key()
        local time_key_next = self:get_store_key_with_time(ngx.time() + 3600)

        -- 需要预创建的统计表
        local wc_stat = {'request_stat', 'client_stat', 'spider_stat'}

        -- 遍历所有站点
        for _, site_v in ipairs(sites) do
            local input_sn = site_v["name"]

            -- 安全地初始化数据库连接
            local db_ok, db = pcall(function() return self:initDB(input_sn) end)
            if not db_ok or not db then
                self:D("cronPre initDB failed for " .. tostring(input_sn) .. ": " .. tostring(db))
                return false
            end

            -- 开启事务
            db:exec([[BEGIN TRANSACTION]])

            local success = true
            -- 预创建当前小时和下一小时的统计记录
            for _, ws_v in ipairs(wc_stat) do
                if not self:_update_stat_pre(db, ws_v, time_key) then
                    success = false
                    break
                end
                if not self:_update_stat_pre(db, ws_v, time_key_next) then
                    success = false
                    break
                end
            end

            -- 提交或回滚事务
            if success then
                pcall(function() db:execute([[COMMIT]]) end)
            else
                pcall(function() db:exec([[ROLLBACK]]) end)
            end

            -- 安全关闭数据库
            pcall(function() db:close() end)

            if not success then
                return false
            end
        end

        return true
    end)

    self:unlock_working('cron_init_stat')

    if not ok then
        self:D("cronPre error: " .. tostring(err))
        return false
    end

    return err
end

--[[
    定时任务调度器
    启动一个每 0.1 秒执行一次的定时器，负责：
    1. 从共享内存队列中读取日志数据
    2. 将日志写入 SQLite 数据库
    3. 统计请求、客户端、爬虫数据
    4. 更新 IP 和 URI 统计
    5. 清理过期日志
    
    执行流程：
    1. 检查队列是否有数据
    2. 获取锁防止并发执行
    3. 初始化所有站点的数据库连接
    4. 批量处理队列中的日志数据
    5. 更新统计信息
    6. 清理过期日志
    7. 提交事务并关闭连接
]]
function _M.cron(self)

    --[[
        定时任务核心处理函数
        @param premature boolean 是否为定时器提前触发
    ]]
    local timer_every_get_data = function (premature)
        
        local llen = ngx.shared.mw_total:llen(total_key)
        if llen == 0 then
            return true
        end

        local cron_key = 'cron_every_1s'
        if self:is_working(cron_key) then
            return true
        end

        local ready_ok = self:cronPre()
        if not ready_ok then
            return true
        end

        self:lock_working(cron_key)

        local dbs = {}
        local stmts = {}
        local stat_fields = {}
        local ip_stats = {}
        local url_stats = {}
        local rollback_sites = {}

        local time_key = self:get_store_key()

        local function cleanup_and_unlock()
            for _, site_v in ipairs(sites) do
                local input_sn = site_v["name"]
                local stmt = stmts[input_sn]
                if stmt then
                    pcall(function() stmt:finalize() end)
                end
                local db = dbs[input_sn]
                if db and db:isopen() then
                    pcall(function() db:close() end)
                end
            end
            self:unlock_working(cron_key)
        end

        local ok, err = pcall(function()
            for _, site_v in ipairs(sites) do
                local input_sn = site_v["name"]
                if self:is_migrating(input_sn) then
                    return
                end

                if self:is_working('cron_init_stat') then
                    return
                end

                local db_ok, db = pcall(function() return self:initDB(input_sn) end)
                if not db_ok or not db then
                    self:D("initDB failed for " .. input_sn .. ": " .. tostring(db))
                    return
                end

                stat_fields[input_sn] = {}

                dbs[input_sn] = db
                self:clean_stats(db, input_sn)

                local stmt_ok, stmt = pcall(function()
                    return db:prepare[[INSERT INTO web_logs(
                            time, ip, domain, server_name, method, status_code, uri, body_length,
                            referer, user_agent, protocol, request_time, is_spider, request_headers, ip_list, client_port)
                            VALUES(:time, :ip, :domain, :server_name, :method, :status_code, :uri,
                            :body_length, :referer, :user_agent, :protocol, :request_time, :is_spider,
                            :request_headers, :ip_list, :client_port)]]
                end)
                
                if stmt_ok and stmt then
                    stmts[input_sn] = stmt
                    db:exec([[BEGIN TRANSACTION]])
                else
                    if db and db:isopen() then
                        db:close()
                    end
                    dbs[input_sn] = nil
                    return
                end
            end

            for i = 1, llen do
                local data = ngx.shared.mw_total:lpop(total_key)
                if not data then
                    break
                end

                local decode_ok, info = pcall(function() return json.decode(data) end)
                if not decode_ok then
                    self:D("json decode failed: " .. tostring(info))
                    ngx.shared.mw_total:rpush(total_key, data)
                    return
                end

                local input_sn = info['server_name']
                local db = dbs[input_sn]
                if not db then
                    ngx.shared.mw_total:rpush(total_key, data)
                    return
                end

                local stmt = stmts[input_sn]
                if not stmt then
                    ngx.shared.mw_total:rpush(total_key, data)
                    return
                end

                local insert_ok = self:store_logs_line(db, stmt, input_sn, info)
                if not insert_ok then
                    ngx.shared.mw_total:rpush(total_key, data)
                    rollback_sites[input_sn] = true
                    return
                end

                local log_kv = info["log_kv"]
                local excluded = log_kv['excluded']
                local stat_tmp_fields = info['stat_fields']

                local stat_fields_is = stat_fields[input_sn]
                for stf_k, stf_v in pairs(stat_tmp_fields) do
                    if excluded then
                        if stf_k == "spider_stat_fields" or stf_k == "client_stat_fields" then
                            break
                        end
                    end

                    local stf_is = stat_fields_is[stf_k]
                    if not stf_is then
                        stf_is = {}
                        stat_fields_is[stf_k] = stf_is
                    end
                    
                    for sv_k, sv_v in pairs(stf_v) do
                        stf_is[sv_k] = (stf_is[sv_k] or 0) + sv_v
                    end
                end

                if not excluded then
                    local ip = log_kv['ip']
                    local body_length = log_kv["body_length"]

                    local ip_stats_sn = ip_stats[input_sn]
                    if not ip_stats_sn then
                        ip_stats_sn = {}
                        ip_stats[input_sn] = ip_stats_sn
                    end

                    local ip_stat = ip_stats_sn[ip]
                    if not ip_stat then
                        ip_stats_sn[ip] = {ip_num = 1, body_length = body_length}
                    else
                        ip_stat.ip_num = ip_stat.ip_num + 1
                        ip_stat.body_length = ip_stat.body_length + body_length
                    end

                    local url_stats_sn = url_stats[input_sn]
                    if not url_stats_sn then
                        url_stats_sn = {}
                        url_stats[input_sn] = url_stats_sn
                    end
                    
                    local request_uri = log_kv["request_uri"]
                    local request_uri_md5 = ngx.md5(request_uri)
                    local url_stat = url_stats_sn[request_uri_md5]
                    if not url_stat then
                        url_stats_sn[request_uri_md5] = {url_num = 1, uri = request_uri, body_length = body_length}
                    else
                        url_stat.url_num = url_stat.url_num + 1
                        url_stat.body_length = url_stat.body_length + body_length
                    end
                end
            end

            local save_day = config['global']["save_day"]
            local now_date = os.date("*t")
            local save_date_timestamp = os.time{year = now_date.year, month = now_date.month, day = now_date.day - save_day, hour = 0}
            local delete_sql = "DELETE FROM web_logs WHERE time<" .. tostring(save_date_timestamp)

            for _, site_v in ipairs(sites) do
                local input_sn = site_v["name"]

                local stmt = stmts[input_sn]
                if stmt then
                    pcall(function() stmt:finalize() end)
                end

                local stat_fields_is = stat_fields[input_sn]
                local db = dbs[input_sn]

                if db then
                    if rollback_sites[input_sn] then
                        pcall(function() db:exec([[ROLLBACK]]) end)
                    else
                        for sti_k, sti_v in pairs(stat_fields_is) do
                            local vkk = ""
                            for sv_k, sv_v in pairs(sti_v) do
                                vkk = vkk .. sv_k .. "=" .. sv_k .. "+" .. sv_v .. ","
                            end
                            if vkk ~= "" then
                                vkk = string.sub(vkk, 1, string.len(vkk) - 1)
                                
                                if sti_k == 'request_stat_fields' then
                                    self:update_stat(db, "request_stat", time_key, vkk)
                                elseif sti_k == 'client_stat_fields' then
                                    self:update_stat(db, "client_stat", time_key, vkk)
                                elseif sti_k == 'spider_stat_fields' then
                                    self:update_stat(db, "spider_stat", time_key, vkk)
                                end
                            end
                        end

                        local local_ip_stats = ip_stats[input_sn]
                        if local_ip_stats then
                            for ip_addr, ip_val in pairs(local_ip_stats) do
                                self:update_statistics_ip(db, ip_addr, ip_val.ip_num, ip_val.body_length)
                            end
                        end

                        local local_url_stats = url_stats[input_sn]
                        if local_url_stats then
                            for url_md5, url_val in pairs(local_url_stats) do
                                self:update_statistics_uri(db, url_val.uri, url_md5, url_val.url_num, url_val.body_length)
                            end
                        end

                        db:exec(delete_sql)

                        pcall(function() db:execute([[COMMIT]]) end)
                    end
                end

                if db and db:isopen() then
                    pcall(function() db:close() end)
                end
            end
        end)

        if not ok then
            self:D("cron process error: " .. tostring(err))
            cleanup_and_unlock()
            return true
        end
        
        self:unlock_working(cron_key)
    end

    
    function timer_every_get_data_try()
        local presult, err = pcall(function() timer_every_get_data() end)
        if not presult then
            self:D("debug cron error on :" .. tostring(err))
            return true
        end
    end

    function timer_every_get_data_try_debug()
        ngx.update_time()
        local start_time = ngx.now()
        local start_llen = ngx.shared.mw_total:llen(total_key)
        
        local presult, err = pcall(function() timer_every_get_data() end)
        
        ngx.update_time()
        local end_time = ngx.now()
        local end_llen = ngx.shared.mw_total:llen(total_key)
        local duration = (end_time - start_time) * 1000
        local processed = start_llen - end_llen
        
        if not presult then
            self:D("debug cron error on :" .. tostring(err))
            return true
        end
        
        if start_llen > 0 then
            self:D(string.format("cron process: took %.2fms, start=%d, end=%d, processed=%d", 
                duration, start_llen, end_llen, processed))
        end
    end

    ngx.timer.every(0.1, timer_every_get_data_try)
end


function _M.store_logs_line(self, db, stmt, input_sn, info)
    local logline = info['log_kv']
    
    local excluded = logline["excluded"]
    if excluded then
        return true
    end

    local user_agent = logline["user_agent"]
    if "table" == type(user_agent) then
        user_agent = self:to_json(user_agent)
    end
    
    stmt:bind_names {
        time = logline["time"],
        ip = logline["ip"],
        domain = logline["domain"],
        server_name = logline["server_name"],
        method = logline["method"],
        status_code = logline["status_code"],
        uri = logline["request_uri"],
        body_length = logline["body_length"],
        referer = logline["referer"],
        user_agent = user_agent,
        protocol = logline["protocol"],
        request_time = logline["request_time"],
        is_spider = logline["is_spider"],
        request_headers = logline["request_headers"],
        ip_list = logline["ip_list"],
        client_port = logline["client_port"],
    }

    local res = stmt:step()
    if tostring(res) == "5" then
        stmt:reset()
        return false
    end
    stmt:reset()
    return true
end

function _M.statistics_ipc(self, input_sn, ip)
    -- 判断IP是否重复的时间限定范围是请求的当前时间+24小时
    local ipc = 0
    local ip_token = input_sn..'_'..ip
    if not cache:get(ip_token) then
        ipc = 1
        cache:set(ip_token,1, self:get_end_time())
    end
    return ipc
end

function _M.statistics_request(self, ip, is_spider, body_length)
    -- 计算pv uv
    local pvc = 0
    local uvc = 0
    local request_header = ngx.req.get_headers()
    if not is_spider and ngx.status == 200 and body_length > 0 then
        local ua = ''
        if request_header['user-agent'] then
            if "table" == type(request_header['user-agent']) then
                ua = self:to_json(request_header['user-agent'])
            else
                ua = request_header['user-agent']
            end
            ua = string.lower(ua)
        end

        pvc = 1
        if ua then
            local today = ngx.today()
            local uv_token = ngx.md5(ip .. ua .. today)
            if not cache:get(uv_token) then
                uvc = 1
                cache:set(uv_token,1, self:get_end_time())
            end
        end
    end
    return pvc, uvc
end

-- 仅计算GET/HTML
function _M.statistics_request_old(self, ip, is_spider, body_length)
    -- 计算pv uv
    local pvc = 0
    local uvc = 0
    local method = ngx.req.get_method()
    if not is_spider and method == 'GET' and ngx.status == 200 and body_length > 512 then
        local ua = ''
        if request_header['user-agent'] then
            ua = string.lower(request_header['user-agent'])
        end

        out_header = ngx.resp.get_headers()
        if out_header['content-type'] then
            if string.find(out_header['content-type'], 'text/html', 1, true) then
                pvc = 1
                if request_header['user-agent'] then
                    if string.find(ua,'mozilla') then
                        local today = ngx.today()
                        local uv_token = ngx.md5(ip .. request_header['user-agent'] .. today)
                        if not cache:get(uv_token) then
                            uvc = 1
                            cache:set(uv_token,1, self:get_end_time())
                        end
                    end
                end
            end
        end
    end
    return pvc, uvc
end

---------------------       db start   ---------------------------


function _M.update_statistics_uri(self, db, uri, uri_md5, day_num, body_length)
    local open_statistics_uri = config['global']["statistics_uri"]
    if not open_statistics_uri then return true end

    local insert_stmt = db:prepare("INSERT INTO uri_stat(uri_md5, uri) SELECT :uri_md5, :uri WHERE NOT EXISTS (SELECT uri_md5 FROM uri_stat WHERE uri_md5 = :uri_md5);")
    insert_stmt:bind_names{uri_md5 = uri_md5, uri = uri}
    insert_stmt:step()
    insert_stmt:finalize()

    local update_sql = "UPDATE uri_stat SET " .. day_column .. "=" .. day_column .. "+" .. day_num .. ", " .. flow_column .. "=" .. flow_column .. "+" .. body_length .. " WHERE uri_md5=\"" .. uri_md5 .. "\";"
    db:exec(update_sql)
    
    return true
end

function _M.statistics_uri(self, db, uri, uri_md5, body_length)
    -- count the number of URI requests and traffic
    local open_statistics_uri = config['global']["statistics_uri"]
    if not open_statistics_uri then return true end

    local stat_sql = nil
    stat_sql = "INSERT INTO uri_stat(uri_md5,uri) SELECT \""..uri_md5.."\",\""..uri.."\" WHERE NOT EXISTS (SELECT uri_md5 FROM uri_stat WHERE uri_md5=\""..uri_md5.."\");"
    local res, err = db:exec(stat_sql)
    
    stat_sql = "UPDATE uri_stat SET "..day_column.."="..day_column.."+1,"..flow_column.."="..flow_column.."+"..body_length.." WHERE uri_md5=\""..uri_md5.."\";"
    local res, err = db:exec(stat_sql)
    return true
end


function _M.update_statistics_ip(self, db, ip, day_num, body_length)
    local open_statistics_ip = config['global']["statistics_ip"]   
    if not open_statistics_ip then return true end
    
    local insert_stmt = db:prepare("INSERT INTO ip_stat(ip) SELECT :ip WHERE NOT EXISTS (SELECT ip FROM ip_stat WHERE ip = :ip);")
    insert_stmt:bind_names{ip = ip}
    insert_stmt:step()
    insert_stmt:finalize()

    local update_sql = "UPDATE ip_stat SET " .. day_column .. "=" .. day_column .. "+" .. day_num .. ", " .. flow_column .. "=" .. flow_column .. "+" .. body_length .. " WHERE ip=\"" .. ip .. "\";"
    db:exec(update_sql)
    
    return true
end

function _M.statistics_ip(self, db, ip, body_length)
    return self:update_statistics_ip(db, ip, 1, body_length)
end


function _M._update_stat_pre(self, db, stat_table, key)
    local local_sql = string.format("INSERT INTO %s(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM %s WHERE time=:time);", stat_table, stat_table)
    local update_stat_stmt = db:prepare(local_sql)

    if update_stat_stmt then
        update_stat_stmt:bind_names{time=key}
        update_stat_stmt:step()
        update_stat_stmt:finalize()
        return true
    end
    return false
end

function _M.update_stat_quick(self, db, stat_table, key,columns)
    if not columns then return end
    local update_sql = "UPDATE ".. stat_table .. " SET " .. columns .. " WHERE time=" .. key
    return db:exec(update_sql)
end


function _M.update_stat(self, db, stat_table, key, columns)
    if not columns then return end
    
    local insert_stmt = db:prepare("INSERT INTO " .. stat_table .. "(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM " .. stat_table .. " WHERE time=:time);")
    insert_stmt:bind_names{time = key}
    insert_stmt:step()
    insert_stmt:finalize()
    
    local update_sql = "UPDATE " .. stat_table .. " SET " .. columns .. " WHERE time=" .. key
    return db:exec(update_sql)
end
---------------------       db end   ---------------------------

-- debug func
function _M.D(self,msg)
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

function _M.is_migrating(self, input_sn)
    local file = io.open("{$SERVER_APP}/migrating", "rb")
    if file then return true end
    local file = io.open("{$SERVER_APP}/logs/"..input_sn.."/migrating", "rb")
    if file then return true end
    return false
end

function _M.is_working(self,sign)
    local work_status = cache:get(sign.."_working")
    if work_status ~= nil and work_status == true then
        return true 
    end
    return false
end

function _M.lock_working(self, sign)
    local working_key = sign.."_working"
    cache:set(working_key, true, 10)
end

function _M.unlock_working(self, sign)
    local working_key = sign.."_working"
    cache:set(working_key, false)
end

function _M.write_file(self, filename, body, mode)
        local fp = io.open(filename, mode)
        if fp == nil then
            return nil
        end
        fp:write(body)
        fp:flush()
        fp:close()
        return true
    end
    
function _M.read_file_body(self, filename)
    local fp = io.open(filename,'rb')
    if not fp then
        return nil
    end
    local fbody = fp:read("*a")
    fp:close()
    if fbody == '' then
        return nil
    end
    return fbody
end

function _M.load_update_day(self, input_sn)
    local _file = "{$SERVER_APP}/logs/"..input_sn.."/update_day.log"
    return self:read_file_body(_file)
end

function _M.write_update_day(self, input_sn)
    local _file = "{$SERVER_APP}/logs/"..input_sn.."/update_day.log"
    return self:write_file(_file, today, "w")
end

function _M.clean_stats(self, db, input_sn)
    -- 清空 uri,ip 汇总的信息[昨日]
    local update_day = self:load_update_day(input_sn)
    if not update_day or update_day ~= today then

        local update_sql = "UPDATE uri_stat SET "..day_column.."=0,"..flow_column.."=0"
        db:exec(update_sql)

        update_sql = "UPDATE ip_stat SET "..day_column.."=0,"..flow_column.."=0"
        db:exec(update_sql)
        self:write_update_day(input_sn)
    end
end

function _M.lpop(self)
    local cache = ngx.shared.mw_total
    return cache:lpop(total_key)
end

function _M.rpop(self)
    local cache = ngx.shared.mw_total
    return cache:rpop(total_key)
end


function _M.get_update_field(self, field, value)
    return field.."="..field.."+"..tostring(value)
end

function _M.get_request_time(self)
    local request_time = math.floor((ngx.now() - ngx.req.start_time()) * 1000)
    if request_time == 0 then  request_time = 1 end
    return request_time
end


function _M.get_end_time(self)
    local s_time = ngx.time()
    local n_date = os.date("*t",s_time + 86400)
    n_date.hour = 0
    n_date.min = 0
    n_date.sec = 0
    local d_time = ngx.time(n_date)
    return d_time - s_time
end


local spider_table = {
    ["baidu"] = 1,
    ["bing"] = 2,
    ["qh360"] = 3,
    ["google"] = 4,
    ["bytes"] = 5,
    ["sogou"] = 6,
    ["youdao"] = 7,
    ["soso"] = 8,
    ["dnspod"] = 9,
    ["yandex"] = 10,
    ["yisou"] = 11,
    ["other"] = 12,
    ["mpcrawler"] = 13,
    ["yahoo"] = 14,
    ["duckduckgo"] = 15
}

local spider_keywords = {
    ["baidu"] = "baidu",
    ["bytes"] = "bytes",
    ["360spider"] = "qh360",
    ["sogou"] = "sogou",
    ["soso"] = "soso",
    ["google"] = "google",
    ["bingbot"] = "bing",
    ["youdao"] = "youdao",
    ["dnspod"] = "dnspod",
    ["yandex"] = "yandex",
    ["yisou"] = "yisou",
    ["mpcrawler"] = "mpcrawler",
    ["yahoo"] = "yahoo",
    ["slurp"] = "other",
    ["duckduckgo"] = "other",
    ["semrush"] = "other",
    ["spider"] = "other",
    ["bot"] = "other",
    ["crawler"] = "other"
}

function _M.match_spider(self, ua)
    local is_spider = false
    local spider_name = ""
    
    if not ua then
        return false, "", 0
    end
    
    local lower_ua = string.lower(ua)
    
    for kw, name in pairs(spider_keywords) do
        if string.find(lower_ua, kw, 1, true) then
            is_spider = true
            spider_name = name
            break
        end
    end
    
    if is_spider then
        return is_spider, spider_name, spider_table[spider_name]
    end
    
    return false, "", 0
end


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
    ["edge"] = "edg",
    ["edg"] = "edg",
    ["windows"] = "windows",
    ["linux"] = "linux",
    ["macintosh"] = "mac",
    ["mobile"] = "mobile"
}

local mobile_keywords = {"mobile", "android", "iphone", "ipod", "ipad"}
local pc_browser_keywords = {
    ["360se"] = "qh360",
    ["360ee"] = "qh360",
    ["360browser"] = "qh360",
    ["qihoo"] = "qh360",
    ["theworld"] = "theworld",
    ["tencenttraveler"] = "tt",
    ["maxthon"] = "maxthon",
    ["opera"] = "opera",
    ["qqbrowser"] = "qq",
    ["ucweb"] = "uc",
    ["ubrowser"] = "uc",
    ["metasr"] = "metasr",
    ["2345explorer"] = "pc2345",
    ["edge"] = "edg",
    ["firefox"] = "firefox",
    ["chrome"] = "chrome",
    ["safari"] = "safari",
    ["msie"] = "msie",
    ["trident"] = "msie"
}
local os_keywords = {"windows", "linux", "macintosh"}
local machine_keywords = {"apachebench", "curl", "headlesschrome", "wget", "spider", "crawler", "scrapy", "zgrab", "python", "java"}

local function _match_client_table(self, ua)
    local client_stat_fields = {}
    
    if not ua then
        return client_stat_fields
    end
    
    if "table" == type(ua) then
        ua = self:to_json(ua)
    end
    
    local lower_ua = string.lower(ua)
    
    local is_mobile = false
    for _, kw in ipairs(mobile_keywords) do
        if string.find(lower_ua, kw, 1, true) then
            is_mobile = true
            client_stat_fields["mobile"] = 1
            if kw ~= "mobile" then
                client_stat_fields[clients_map[kw]] = 1
            end
            break
        end
    end
    
    if not is_mobile then
        local cls_pc = nil
        for kw, name in pairs(pc_browser_keywords) do
            if string.find(lower_ua, kw, 1, true) then
                cls_pc = name
                break
            end
        end
        
        if cls_pc then
            client_stat_fields[cls_pc] = 1
        else
            local is_machine = false
            for _, kw in ipairs(machine_keywords) do
                if string.find(lower_ua, kw, 1, true) then
                    is_machine = true
                    break
                end
            end
            
            if is_machine then
                client_stat_fields["machine"] = 1
            else
                client_stat_fields["other"] = 1
            end
        end
        
        for _, kw in ipairs(os_keywords) do
            if string.find(lower_ua, kw, 1, true) then
                client_stat_fields[clients_map[kw]] = 1
                break
            end
        end
    end
    
    if string.find(lower_ua, "micromessenger", 1, true) then
        client_stat_fields["weixin"] = 1
    end
    
    return client_stat_fields
end

function _M.match_client_arr(self, ua)
    return _match_client_table(self, ua)
end

function _M.match_client(self, ua)
    local client_stat_fields = _match_client_table(self, ua)
    local fields_str = ""
    
    for k, v in pairs(client_stat_fields) do
        fields_str = fields_str .. "," .. self:get_update_field(k, v)
    end
    
    if fields_str ~= "" then
        fields_str = string.sub(fields_str, 2)
    end
    
    return fields_str
end

function _M.get_client_ip(self)
    local client_ip = "unknown"
    if auto_config and auto_config['cdn'] == true then
        local request_header = ngx.req.get_headers()
        for _, v in ipairs(auto_config['cdn_headers'] or {}) do
            if request_header[v] ~= nil and request_header[v] ~= "" then
                local ip_list = request_header[v]
                client_ip = self:split(ip_list, ',')[1]
                break
            end
        end
    end

    -- ipv6
    if type(client_ip) == 'table' then client_ip = "" end
    if client_ip ~= "unknown" and ngx.re.match(client_ip,"^([a-fA-F0-9]*):") then
        return client_ip
    end

    -- ipv4
    if  not ngx.re.match(client_ip,"\\d+\\.\\d+\\.\\d+\\.\\d+") == nil or not self:is_ipaddr(client_ip) then
        client_ip = ngx.var.remote_addr
        if client_ip == nil then
            client_ip = "unknown"
        end
    end

    return client_ip
end

return _M