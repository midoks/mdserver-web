
local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end
-- 以上为预热操作
collectgarbage()

local spider_match = "aa 220"


ngx.update_time()
local begin = ngx.now()
local N = 1e7
for i = 1, N do
    ngx.re.find(spider_match, "360", "ijo")
end
ngx.update_time()

ngx.say("ngx.re.find elapsed: ", (ngx.now() - begin) / N)



ngx.update_time()
local begin = ngx.now()
local N = 1e7
for i = 1, N do
    string.find(spider_match, "360", 1, true)
end
ngx.update_time()

ngx.say("string.find elapsed: ", (ngx.now() - begin) / N)

