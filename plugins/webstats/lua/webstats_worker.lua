local cpath = "{$SERVER_APP}/lua/"
if not package.cpath:find(cpath) then
    package.cpath = cpath .. "?.so;" .. package.cpath
end
if not package.path:find(cpath) then
	package.path = cpath .. "?.lua;" .. package.path
end

local __WS_C = require "webstats_common"
local WS_C = __WS_C:getInstance()

WS_C:cronPre()
WS_C:cron()

local webstats_cron_pre = function(premature)
    WS_C:cronPre()
end

if ngx.worker.id() == 0 then
    ngx.timer.every(60, webstats_cron_pre)
end