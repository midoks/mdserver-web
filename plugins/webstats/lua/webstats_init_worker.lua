-- -- 添加 Lua 模块搜索路径
local cpath = "{$SERVER_APP}/lua/"
if not package.cpath:find(cpath) then
    package.cpath = cpath .. "?.so;" .. package.cpath
end
if not package.path:find(cpath) then
    package.path = cpath .. "?.lua;" .. package.path
end

local app_dir = "{$SERVER_APP}"
local __C = require "webstats_common"
local C = __C:getInstance()
C:setAppDir(app_dir)
C:start_cron()
