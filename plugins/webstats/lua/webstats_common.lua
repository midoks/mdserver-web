
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
local method = ngx.req.get_headers()

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


function _M.getInstance(self)
    if rawget(self, "instance") == nil then
        rawset(self, "instance", self.new())
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
    db:exec([[PRAGMA page_size = 4096]])
    db:exec([[PRAGMA journal_mode = wal]])
    db:exec([[PRAGMA journal_size_limit = 1073741824]])
    return db
end

function _M.getTotalKey(self)
    return self.total_key
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
        auto_config = config[site]
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
    if domain ~= nil then
        domain = ngx.re.gsub(domain, "_", ".")
    else
        domain = "unknown"
    end
    return domain
end

function _M.split(self, str, reps)
    local arr = {}
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

-- 后台任务
function _M.cron(self)
    local timer_every_get_data = function (premature)

        local llen, _ = ngx.shared.mw_total:llen(total_key)
        if llen < 1 then
            return true
        end

        ngx.update_time()
        local begin = ngx.now()
        
        

        local dbs = {}
        
        for i,v in ipairs(sites) do
            local input_sn = v["name"]
            -- 迁移合并时不执行
            if self:is_migrating(input_sn) then
                return true
            end

            local db = self:initDB(input_sn)

            if db then
                dbs[input_sn] = db
                self:clean_stats(db,input_sn)
                db:exec([[BEGIN TRANSACTION]])
            end
        end

        -- self:D( tostring (dbs["t1.cn"]) )

        local cron_key = 'cron_every_1s'
        if self:is_working(cron_key) then
            return true
        end

        self:lock_working(cron_key)
        
        -- 每秒100条
        for i=1,llen do
            local data, _ = ngx.shared.mw_total:lpop(total_key)
            if data then
                local info = json.decode(data)
                local input_sn = info['server_name']
                local db = dbs[input_sn]
                if db then

                    if self:is_working(input_sn) then
                        ngx.shared.mw_total:rpush(total_key, data)
                        self:unlock_working(cron_key)
                        return true
                    end

                    local local_stmt2 = db:prepare[[INSERT INTO web_logs(
                        time, ip, domain, server_name, method, status_code, uri, body_length,
                        referer, user_agent, protocol, request_time, is_spider, request_headers, ip_list, client_port)
                        VALUES(:time, :ip, :domain, :server_name, :method, :status_code, :uri,
                        :body_length, :referer, :user_agent, :protocol, :request_time, :is_spider,
                        :request_headers, :ip_list, :client_port)]]

                    self:store_logs(db, local_stmt2, info)
                end
            end
        end

        for _, local_db in pairs(dbs) do
            if local_db then

                local now_date = os.date("*t")
                local save_day = config['global']["save_day"]
                local save_date_timestamp = os.time{year=now_date.year,
                    month=now_date.month, day=now_date.day-save_day, hour=0}
                -- delete expire data
                local_db:exec("DELETE FROM web_logs WHERE time<"..tostring(save_date_timestamp))
            end

            if local_db and local_db:isopen() then
                local_db:execute([[COMMIT]])
                local_db:close()
            end
        end 
        

        -- local tmp_log = "{$SERVER_APP}/logs/tmp_" .. tostring( ngx.now() ) .. ".log"
        -- -- 空闲空间小于10M,立即存盘
        -- -- local capacity_bytes = ngx.shared.mw_total:free_space()
        -- -- self:D("capacity_bytes:"..capacity_bytes)
        -- os.execute("sleep " .. 1)
        -- local nlen = llen - 100
        -- for i = 1,llen do
        --     local data = "" 
        --     local tmp, _ = ngx.shared.mw_total:lpop(total_key)
        --     if tmp then
        --         data = data .. tmp .. "\n"
        --     end

        --     if data ~= "" then
        --         self:write_file(tmp_log, data, "ab")
        --     end
        -- end
        
        self:unlock_working(cron_key)

        ngx.update_time()
        self:D(tostring(llen)..", elapsed: " .. tostring(ngx.now() - begin))
    end

    ngx.timer.every(1, timer_every_get_data)
end

function _M.store_logs(self, db, stmt2, info)
    local input_sn = info["server_name"]

    self:lock_working(input_sn)

    self:store_logs_line(db, stmt2, input_sn, info)

    local res, err = stmt2:finalize()
    if tostring(res) == "5" then
        self:D("Finalize res:"..tostring(res)..",Finalize err:"..tostring(err))
    end

    self:unlock_working(input_sn)
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

    local request_stat_fields = nil 
    local client_stat_fields = nil
    local spider_stat_fields = nil
    local stat_fields = info['stat_fields']
    if stat_fields == nil then
        -- D("Log stat fields is nil.")
        -- D("Logdata:"..logvalue)
    else
        stat_fields = self:split(stat_fields, ";")
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
            self:D("step res:"..tostring(res) ..",step err:"..tostring(err))
            self:D("the step database connection is busy, so it will be stored later.")
            return false
        end
        stmt:reset()

        local res ,err = self:update_stat( db, "client_stat", time_key, client_stat_fields)
        -- self:D("step res:"..tostring(res) ..",step err:"..tostring(err))
        local res ,err = self:update_stat( db, "spider_stat", time_key, spider_stat_fields)
        -- self:D("step res:"..tostring(res) ..",step err:"..tostring(err))
        -- self:D("stat ok"..)

        -- only count non spider requests
        local ok, err = self:statistics_uri(db, request_uri, ngx.md5(request_uri), body_length)
        local ok, err = self:statistics_ip(db, ip, body_length)
        -- self:D("stat url ip ok")
    end

    self:update_stat( db, "request_stat", time_key, request_stat_fields)
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




function _M.update_stat(self,db, stat_table, key, columns)
    -- 根据指定表名，更新统计数据
    if not columns then return end
    local stmt = db:prepare(string.format("INSERT INTO %s(time) SELECT :time WHERE NOT EXISTS(SELECT time FROM %s WHERE time=:time);", stat_table, stat_table))
    stmt:bind_names{time=key}
    local res, err = stmt:step()
    stmt:finalize()
    local update_sql = "UPDATE ".. stat_table .. " SET " .. columns
    update_sql = update_sql .. " WHERE time=" .. key
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
    find_spider, _ = ngx.re.match(ua, "(Yahoo|Slurp|DuckDuckGo)", "ijo")
    if res then
        spider_match = string.lower(find_spider[0])
        if string.find(spider_match, "yahoo", 1, true) then
            spider_name = "yahoo"
        elseif string.find(spider_match, "slurp", 1, true) then
            spider_name = "yahoo"
        elseif string.find(spider_match, "duckduckgo", 1, true) then
            spider_name = "duckduckgo"
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

function _M.get_client_ip(self)
    local client_ip = "unknown"
    local cdn = auto_config['cdn']
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