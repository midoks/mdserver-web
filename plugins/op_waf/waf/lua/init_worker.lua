
local json = require "cjson"

local waf_root = "{$WAF_ROOT}"
local cpath = waf_root.."/waf/"

local __C = require "common"
local C = __C:getInstance()


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