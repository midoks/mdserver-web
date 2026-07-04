local app_dir = "{$SERVER_APP}"
local __C = require "webstats_common"
local C = __C:getInstance()
C:setAppDir(app_dir)
C:start_cron()
