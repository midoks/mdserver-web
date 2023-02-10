local waf_root = "{$WAF_ROOT}"
local waf_cpath = waf_root.."/waf/lua/?.lua;"..waf_root.."/waf/conf/?.lua;"..waf_root.."/waf/html/?.lua;"
local waf_sopath = waf_root.."/waf/conf/?.so;"

if not package.path:find(waf_cpath) then
    package.path = waf_cpath  .. package.path
end

if not package.cpath:find(waf_sopath) then
    package.cpath = waf_sopath .. package.cpath
end

local json = require "cjson"

local __C = require "common"
local C = __C:getInstance()

-- cron
C:initCron()

local function timer_stats_total_log(premature)
    C:timer_stats_total()
end


ngx.shared.waf_limit:set("cpu_usage", 0, 10)
function timer_every_get_cpu(premature)
    local cpu_percent = C:read_file_body(waf_root.."/cpu.info")
    if cpu_percent then
        ngx.shared.waf_limit:set("cpu_usage", tonumber(cpu_percent), 10)
    else
        ngx.shared.waf_limit:set("cpu_usage", 0, 10)
    end
end

if 0 == ngx.worker.id() then
    ngx.timer.every(5, timer_every_get_cpu)

    -- 异步执行
    ngx.timer.every(3, timer_stats_total_log)
end