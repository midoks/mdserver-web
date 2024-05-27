
local setmetatable = setmetatable
local _M = { _VERSION = '1.0' }
local mt = { __index = _M }

local json = require "cjson"
local sqlite3 = require "lsqlite3"
local config = require "webstats_config"
local sites = require "webstats_sites"

local debug_mode = true
local total_key = "log_kv_total"

local unset_server_name = "unset"
local max_log_id = 99999999999999
local cache = ngx.shared.mw_total

local today = ngx.re.gsub(ngx.today(),'-','')
local request_header = ngx.req.get_headers()
local method = ngx.req.get_method()

local day = os.date("%d")
local number_day = tonumber(day)
local day_column = "day"..number_day
local flow_column = "flow"..number_day
local spider_column = "spider_flow"..number_day

-- _M.setInputSn  | need
local auto_config = nil

local log_dir = "{$SERVER_APP}/logs"

function _M.new(self)
    local self = {
        total_key = total_key,
        params = nil,
        site_config = nil,
        config = nil,
    }
    -- self.dbs = {}
    return setmetatable(self, mt)
end


-- function _M.getInstance(self)
--     if rawget(self, "instance") == nil then
--         rawset(self, "instance", self.new())
--         self.cron()
--     end
--     assert(self.instance ~= nil)
--     return self.instance
-- end


function _M.getInstance(self)
    if self.instance == nil then
        self.instance = self:new()
        self:cron()
    end
    assert(self.instance ~= nil)
    return self.instance
end


function _M.initDB(self, input_sn)
    local path = log_dir .. '/' .. input_sn .. "/logs.db"
    db, err = sqlite3.open(path)

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

function _M.getTotalKey(self)
    return self.total_key
end

function _M.to_json(self, msg)
    return json.encode(msg)
end

function _M.setConfData( self, config, site_config )
    self.config = config
    self.site_config = site_config
end

function _M.setParams( self, params )
    self.params = params
end

function _M.setInputSn(self, input_sn)
    local global_config = config["global"]
    if config[input_sn] == nil then
        auto_config = global_config
    else
        auto_config = config[input_sn]
        for k, v in pairs(global_config) do
            if auto_config[k] == nil then
                auto_config[k] = v
            end
        end
    end
    return auto_config
end

function _M.get_domain(self)
    local domain = ngx.req.get_headers()['host']
     -- domain = ngx.re.gsub(domain, "_", ".")
    if domain == nil then
        domain = "unknown"
    end
    return domain
end

function _M.split(self, str, reps)
    local arr = {}
    -- 修复反向代理代过来的数据
    if "table" == type(str) then
        return str
    end
    string.gsub(str,'[^'..reps..']+',function(w) table.insert(arr,w) end)
    return arr
end

function _M.arrlen(self, arr)
    if not arr then return 0 end
    local count = 0
    for _,v in ipairs(arr) do
        count = count + 1
    end
    return count
end

function _M.is_ipaddr(self, client_ip)
    local cipn = self:split(client_ip,'.')
    if self:arrlen(cipn) < 4 then return false end
    for _,v in ipairs({1,2,3,4})
    do
        local ipv = tonumber(cipn[v])
        if ipv == nil then return false end
        if ipv > 255 or ipv < 0 then return false end
    end
    return true
end


function _M.get_sn(self, input_sn)
    local dst_name = cache:get(input_sn)
    if dst_name then return dst_name end

    -- self:D(json.encode(sites))
    for _,v in ipairs(sites)
    do
        if input_sn == v["name"] then
            cache:set(input_sn, v['name'], 86400)
            return v["name"]
        end
        -- self:D("get_sn:"..json.encode(v))
        for _,dst_domain in ipairs(v['domains'])
        do
            if input_sn == dst_domain then
                cache:set(input_sn, v['name'], 86400)
                return v['name']
            elseif string.find(dst_domain, "*") then
                local new_domain = string.gsub(dst_domain, '*', '.*')
                if string.find(input_sn, new_domain) then
                    dst_domain = v['name']
                    cache:set(input_sn, dst_domain, 86400)
                end
            end
        end
    end

    cache:set(input_sn, unset_server_name, 86400)
    return unset_server_name
end


function _M.get_store_key(self)
    return os.date("%Y%m%d%H", ngx.time())
end

function _M.get_store_key_with_time(self, htime)
    return os.date("%Y%m%d%H", htime)
end

function _M.get_length(self)
    local clen  = ngx.var.body_bytes_sent
    if clen == nil then clen = 0 end
    return tonumber(clen)
end

function _M.get_last_id(self, input_sn)
    local last_insert_id_key = input_sn .. "_last_id"
    local new_id, err = cache:incr(last_insert_id_key, 1, 0)
    cache:incr(cache_count_id_key, 1, 0)
    if new_id >= max_log_id then
        cache:set(last_insert_id_key, 1)
        new_id = cache:get(last_insert_id_key)
    end
    return new_id
end

function _M.get_http_origin(self)
    local data = ""
    local headers = ngx.req.get_headers()
    if not headers then return data end
    local req_method = ngx.req.get_method()
    if req_method ~='GET' then 
    
        -- proxy_pass, fastcgi_pass, uwsgi_pass, and scgi_pass
        data = ngx.var.request_body
        if not data then
            data = ngx.req.get_body_data()
        end

        -- API disabled in the context of log_by_lua
        -- if not data then
        --     ngx.req.read_body()
        --     data = ngx.req.get_post_args(1000000)
        -- end

        if "string" == type(data) then
            headers["payload"] = data
        end

        if "table" == type(data) then
            -- headers = table.concat(headers, data)
            headers["payload"] = table.concat(data, "&")
        end
    end
    return json.encode(headers)
end

function _M.cronPre(self)
    self:lock_working('cron_init_stat')

    local time_key = self:get_store_key()
    local time_key_next = self:get_store_key_with_time(ngx.time()+3600)


    for site_k, site_v in ipairs(sites) do
        local input_sn = site_v["name"]

        local db = self:initDB(input_sn)

        local wc_stat = {
            'request_stat',
            'client_stat',
            'spider_stat'
        }

        local v1 = true
        local v2 = true
        for _,ws_v in pairs(wc_stat) do
            v1 = self:_update_stat_pre(db, ws_v, time_key)
            v2 = self:_update_stat_pre(db, ws_v, time_key_next)
        end

        if db and db:isopen() then
            db:execute([[COMMIT]])
            db:close()
        end

        if  not v1 or not v2 then
            return false
        end
    end

    self:unlock_working('cron_init_stat')

    return true
end

-- 后台任务
function _M.cron(self)

    local timer_every_get_data = function (premature)
        
        local llen, _ = ngx.shared.mw_total:llen(total_key)
        -- self:D("PID:"..tostring(ngx.worker.id())..",llen:"..tostring(llen))
        if llen == 0 then
            return true
        end

        -- self:D("dedebide:cron task is busy!")
        local ready_ok = self:cronPre()
        if not ready_ok then
            -- self:D("cron task is busy!")
            return true
        end

        local cron_key = 'cron_every_1s'
        if self:is_working(cron_key) then
            return true
        end

        ngx.update_time()
        local begin = ngx.now()

        local dbs = {}
        local stmts = {}
        local stat_fields = {}
        local ip_stats = {}
        local url_stats = {}

        local time_key = self:get_store_key()

        for site_k, site_v in ipairs(sites) do
            local input_sn = site_v["name"]
            -- self:D("input_sn:"..input_sn)
            -- 迁移合并时不执行
            if self:is_migrating(input_sn) then
                return true
            end

            -- 初始化统计表时不执行
            if self:is_working('cron_init_stat') then
                return true
            end

            local db = self:initDB(input_sn)

            stat_fields[input_sn] = {}

            if db then
                dbs[input_sn] = db
                self:clean_stats(db,input_sn)

                local tmp_stmt = {}
                local stmt = db:prepare[[INSERT INTO web_logs(
                        time, ip, domain, server_name, method, status_code, uri, body_length,
                        referer, user_agent, protocol, request_time, is_spider, request_headers, ip_list, client_port)
                        VALUES(:time, :ip, :domain, :server_name, :method, :status_code, :uri,
                        :body_length, :referer, :user_agent, :protocol, :request_time, :is_spider,
                        :request_headers, :ip_list, :client_port)]]
                tmp_stmt["web_logs"] = stmt
                stmts[input_sn] = tmp_stmt

                db:exec([[BEGIN TRANSACTION]])
            end
        end

        self:lock_working(cron_key)
        
        -- 每秒100条
        for i=1,llen do
            local data, _ = ngx.shared.mw_total:lpop(total_key)
            if not data then
                self:unlock_working(cron_key)
                break
            end

            local info = json.decode(data)

            -- self:D("info:"..json.encode(info))
            local input_sn = info['server_name']
            -- self:D("insert data input_sn:"..input_sn)
            local db = dbs[input_sn]
            local stat_fields_is = stat_fields[input_sn]
            if not db then
                ngx.shared.mw_total:rpush(total_key, data)
                self:unlock_working(cron_key)
                break
            end

            local input_stmts = stmts[input_sn]["web_logs"]
            if not input_stmts then
                ngx.shared.mw_total:rpush(total_key, data)
                self:unlock_working(cron_key)
                break
            end

            local insert_ok = self:store_logs_line(db, input_stmts, input_sn, info)
            if not insert_ok then
                ngx.shared.mw_total:rpush(total_key, data)
                self:unlock_working(cron_key)
                break
            end

            local excluded = info["log_kv"]['excluded']
            local stat_tmp_fields = info['stat_fields']

            -- 合并统计数据
            for stf_k,stf_v in pairs(stat_tmp_fields) do
                -- 排除请求过滤
                if excluded then
                    if stf_k == "spider_stat_fields" or stf_k == "client_stat_fields" then
                        break
                    end
                end

                if not stat_fields_is[stf_k] then
                    stat_fields_is[stf_k] = {}
                end
                
                for sv_k,sv_v in pairs(stf_v) do
                    if not stat_fields_is[stf_k][sv_k] then
                        stat_fields_is[stf_k][sv_k] = sv_v
                    else
                        stat_fields_is[stf_k][sv_k] = stat_fields_is[stf_k][sv_k] + 1
                    end
                end
            end

            stat_fields[input_sn] = stat_fields_is
            -- ip 统计合并
            -- url 统计
            if not excluded then
                local ip = info["log_kv"]['ip']
                local body_length = info["log_kv"]["body_length"]

                if not ip_stats[input_sn] then
                    ip_stats[input_sn] = {}
                end

                if not ip_stats[input_sn][ip] then
                    local tmp = {
                        ip_num=1,
                        body_length=body_length
                    }
                    ip_stats[input_sn][ip] = tmp
                else
                    ip_stats[input_sn][ip]["ip_num"] = ip_stats[input_sn][ip]["ip_num"]+1
                    ip_stats[input_sn][ip]["body_length"] = ip_stats[input_sn][ip]["body_length"]+body_length
                end

                
                -- uri统计
                if not url_stats[input_sn] then
                    url_stats[input_sn] = {}
                end
                local request_uri = info["log_kv"]["request_uri"]
                local request_uri_md5 = ngx.md5(request_uri)
                if not url_stats[input_sn][request_uri_md5] then
                    local tmp = {
                        url_num=1,
                        uri=request_uri,
                        body_length=body_length
                    }
                    url_stats[input_sn][request_uri_md5] = tmp
                else
                    url_stats[input_sn][request_uri_md5]["url_num"] = url_stats[input_sn][request_uri_md5]["url_num"]+1
                    url_stats[input_sn][request_uri_md5]["body_length"] = url_stats[input_sn][request_uri_md5]["body_length"]+body_length
                end
            end
            -- self:D("url_stats:.."..json.encode(url_stats))
        end

        for site_k, site_v in ipairs(sites) do
            local input_sn = site_v["name"]

            if stmts[input_sn] then
                for stmts_k,stmts_v in pairs(stmts[input_sn]) do
                    -- self:D("stmts_k:"..tostring(stmts_k))
                    local res, err = stmts_v:finalize()
                    if tostring(res) == "5" then
                        self:D(stmts_k..":Finalize res:"..tostring(res)..",Finalize err:"..tostring(err))
                    end
                end
            end


            local stat_fields_is = stat_fields[input_sn]
            local db = dbs[input_sn]
            local local_ip_stats = ip_stats[input_sn]
            local local_url_stats = url_stats[input_sn]

            if db then
                -- 统计【spider_stat,client_stat,request_stat】
                for sti_k,sti_v in pairs(stat_fields_is) do
                    local vkk = ""
                    for sv_k,sv_v in pairs(sti_v) do
                        vkk = vkk..sv_k.."="..sv_k.."+"..sv_v..","
                    end
                    if vkk ~= "" then
                        vkk = string.sub(vkk,1,string.len(vkk)-1) 
                    end
                    if sti_k == 'request_stat_fields' and vkk ~= '' then
                        self:update_stat( db, "request_stat", time_key, vkk)
                    end

                    if sti_k == 'client_stat_fields' and vkk ~= '' then
                        self:update_stat( db, "client_stat", time_key, vkk)
                    end

                    if sti_k == 'spider_stat_fields' and vkk ~= '' then
                        self:update_stat( db, "spider_stat", time_key, vkk)
                    end
                end

                -- ip统计
                if local_ip_stats then
                    for ip_addr,ip_val in pairs(local_ip_stats) do
                        self:update_statistics_ip( db, ip_addr,ip_val["ip_num"], ip_val["body_length"])
                    end
                end

                -- url统计
                if local_url_stats then
                    for url_md5,url_val in pairs(local_url_stats) do
                        self:update_statistics_uri( db, tostring(url_val["uri"]),url_md5, url_val["url_num"], url_val["body_length"])
                    end
                end

                -- delete expire data
                local now_date = os.date("*t")
                local save_day = config['global']["save_day"]
                local save_date_timestamp = os.time{year=now_date.year,
                    month=now_date.month, day=now_date.day-save_day, hour=0}
                
                db:exec("DELETE FROM web_logs WHERE time<"..tostring(save_date_timestamp))
            end

            if db and db:isopen() then
                db:execute([[COMMIT]])
                db:close()
            end
        end
        
        self:unlock_working(cron_key)
        ngx.update_time()
        -- self:D("PID:"..tostring(ngx.worker.id()).."--【"..tostring(llen).."】, elapsed: " .. tostring(ngx.now() - begin))
    end

    
    function timer_every_get_data_try()
       local presult, err = pcall( function() timer_every_get_data() end)
        if not presult then
            self:D("debug cron error on :"..tostring(err))
            return true
        end
    end

    ngx.timer.every(0.5, timer_every_get_data_try)
end


function _M.store_logs_line(self, db, stmt, input_sn, info)
    local logline = info['log_kv']

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

    local time_key = logline["time_key"]
    if not excluded then
        stmt:bind_names {
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
            -- self:D("json:"..json.encode(logline))
            -- self:D("the step database connection is busy, so it will be stored later | step res:"..tostring(res) ..",step err:"..tostring(err))
            if stmt then
                stmt:reset()
            end
            return false
        end
        stmt:reset()
    end
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
            ua = string.lower(request_header['user-agent'])
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
    -- count the number of URI requests and traffic
    local open_statistics_uri = config['global']["statistics_uri"]
    if not open_statistics_uri then return true end

    local stat_sql = nil
    stat_sql = "INSERT INTO uri_stat(uri_md5,uri) SELECT \""..uri_md5.."\",\""..uri.."\" WHERE NOT EXISTS (SELECT uri_md5 FROM uri_stat WHERE uri_md5=\""..uri_md5.."\");"
    local res, err = db:exec(stat_sql)
    
    stat_sql = "UPDATE uri_stat SET "..day_column.."="..day_column.."+"..day_num..","..flow_column.."="..flow_column.."+"..body_length.." WHERE uri_md5=\""..uri_md5.."\";"
    local res, err = db:exec(stat_sql)
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


function _M.update_statistics_ip(self, db, ip, day_num ,body_length)
    local open_statistics_ip = config['global']["statistics_ip"]   
    if not open_statistics_ip then return true end
    
    local stat_sql = nil
    stat_sql = "INSERT INTO ip_stat(ip) SELECT \""..ip.."\" WHERE NOT EXISTS (SELECT ip FROM ip_stat WHERE ip=\""..ip.."\");"
    local res, err = db:exec(stat_sql)
    
    stat_sql = "UPDATE ip_stat SET "..day_column.."="..day_column.."+"..day_num..","..flow_column.."="..flow_column.."+"..body_length.." WHERE ip=\""..ip.."\""
    local res, err = db:exec(stat_sql)
    return true
end

function _M.statistics_ip(self, db, ip, body_length)
    local open_statistics_ip = config['global']["statistics_ip"]   
    if not open_statistics_ip then return true end
    
    local stat_sql = nil
    stat_sql = "INSERT INTO ip_stat(ip) SELECT \""..ip.."\" WHERE NOT EXISTS (SELECT ip FROM ip_stat WHERE ip=\""..ip.."\");"
    local res, err = db:exec(stat_sql)
    
    stat_sql = "UPDATE ip_stat SET "..day_column.."="..day_column.."+1,"..flow_column.."="..flow_column.."+"..body_length.." WHERE ip=\""..ip.."\""
    local res, err = db:exec(stat_sql)
    return true
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
    -- 根据指定表名，更新统计数据
    if not columns then return end
    local local_sql = string.format("INSERT INTO %s(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM %s WHERE time=:time);", stat_table, stat_table)
    local stmt = db:prepare(local_sql)
    stmt:bind_names{time=key}
    local res, err = stmt:step()
    stmt:finalize()
    local update_sql = "UPDATE ".. stat_table .. " SET " .. columns .. " WHERE time=" .. key
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
    cache:set(working_key, true, 60)
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
    fbody = fp:read("*a")
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


function _M.match_spider(self, ua)
    -- 匹配蜘蛛请求
    local is_spider = false
    local spider_name = ""
    local spider_match = ""

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

    local find_spider, _ = ngx.re.match(ua, "(Baiduspider|Bytespider|360Spider|Sogou web spider|Sosospider|Googlebot|bingbot|AdsBot-Google|Google-Adwords|YoudaoBot|Yandex|DNSPod-Monitor|YisouSpider|mpcrawler)", "ijo")
    if find_spider then
        is_spider = true
        spider_match = string.lower(find_spider[0])
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
    find_spider, _ = ngx.re.match(ua, "(Yahoo|Slurp|DuckDuckGo|Semrush|Spider|Bot)", "ijo")
    if find_spider then
        spider_match = string.lower(find_spider[0])
        if string.find(spider_match, "yahoo", 1, true) then
            spider_name = "other"
        elseif string.find(spider_match, "slurp", 1, true) then
            spider_name = "other"
        elseif string.find(spider_match, "duckduckgo", 1, true) then
            spider_name = "other"
        elseif string.find(spider_match, "semrush", 1, true) then
            spider_name = "other"
        elseif string.find(spider_match, "spider", 1, true) then
            spider_name = "other"
        elseif string.find(spider_match, "bot", 1, true) then
            spider_name = "other"
        end
        return true, spider_name, spider_table[spider_name]
    end
    return false, "", 0
end


function _M.match_client(self, ua)
    local client_stat_fields = ""
    
    if not ua then
        return client_stat_fields
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
        client_stat_fields = client_stat_fields..","..self:get_update_field("mobile", 1)
        mobile_res = string.lower(mobile_res[0])
        if mobile_res ~= "mobile" then
            client_stat_fields = client_stat_fields..","..self:get_update_field(clients_map[mobile_res], 1)
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
            if ngx.re.find(ua, "[Ff]irefox") then
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
            client_stat_fields = client_stat_fields..","..self:get_update_field(clients_map[cls_pc], 1)
        else
            -- machine and other
            local machine_res, err = ngx.re.match(ua, "(ApacheBench|[Cc]url|HeadlessChrome|[a-zA-Z]+[Bb]ot|[Ww]get|[Ss]pider|[Cc]rawler|[Ss]crapy|zgrab|[Pp]ython|java)", "ijo")
            if machine_res then
                client_stat_fields = client_stat_fields..","..self:get_update_field("machine", 1)
            else
                -- 移动端+PC端+机器以外 归类到 其他
                client_stat_fields = client_stat_fields..","..self:get_update_field("other", 1)
            end
        end

        local os_regx = "(Windows|Linux|Macintosh)"
        local os_res = ngx.re.match(ua, os_regx, "ijo")
        if os_res then
            os_res = string.lower(os_res[0])
            client_stat_fields = client_stat_fields..","..self:get_update_field(clients_map[os_res], 1)
        end
    end

    local other_regx = "MicroMessenger"
    local other_res = ngx.re.find(ua, other_regx)
    if other_res then
        client_stat_fields = client_stat_fields..","..self:get_update_field("weixin", 1)
    end
    if client_stat_fields then
        client_stat_fields = string.sub(client_stat_fields, 2)
    end
    return client_stat_fields
end


function _M.match_client_arr(self, ua)
    local client_stat_fields = {}
    
    if not ua then
        return client_stat_fields
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
        client_stat_fields['mobile'] = 1
        mobile_res = string.lower(mobile_res[0])
        if mobile_res ~= "mobile" then
            client_stat_fields[clients_map[mobile_res]] = 1
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
            if ngx.re.find(ua, "[Ff]irefox") then
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
            client_stat_fields[clients_map[cls_pc]] = 1
        else
            -- machine and other
            local machine_res, err = ngx.re.match(ua, "(ApacheBench|[Cc]url|HeadlessChrome|[a-zA-Z]+[Bb]ot|[Ww]get|[Ss]pider|[Cc]rawler|[Ss]crapy|zgrab|[Pp]ython|java)", "ijo")
            if machine_res then
                client_stat_fields["machine"] = 1
            else
                -- 移动端+PC端+机器以外 归类到 其他
                client_stat_fields["other"] = 1
            end
        end

        local os_regx = "(Windows|Linux|Macintosh)"
        local os_res = ngx.re.match(ua, os_regx, "ijo")
        if os_res then
            os_res = string.lower(os_res[0])
            client_stat_fields[clients_map[os_res]] = 1
        end
    end

    local other_regx = "MicroMessenger"
    local other_res = ngx.re.find(ua, other_regx)
    if other_res then
        client_stat_fields["weixin"] = 1
    end
    return client_stat_fields
end

function _M.get_client_ip(self)
    local client_ip = "unknown"
    local cdn = auto_config['cdn']
    local request_header = ngx.req.get_headers()
    if cdn == true then
        for _,v in ipairs(auto_config['cdn_headers']) do
            if request_header[v] ~= nil and request_header[v] ~= "" then
                local ip_list = request_header[v]
                client_ip = self:split(ip_list,',')[1]
                break;
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