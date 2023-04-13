local hc = require "resty.upstream.healthcheck"
local ok, err = hc.spawn_checker {
   shm = "healthcheck",
   type = "http",
   upstream = "{$UPSTREAM_NAME}",
   http_req = "GET / HTTP/1.0\r\nHost: {$UPSTREAM_NAME}\r\n\r\n",
   interval = 2000,
   timeout = 6000,
   fall = 3,
   rise = 2,
   valid_statuses = {200, 302},
   concurrency = 20,
}

if not ok then
   ngx.log(ngx.ERR, "=======> load balance health checker error: ", err)
   return
end