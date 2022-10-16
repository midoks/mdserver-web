
local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end
-- 以上为预热操作
collectgarbage()


ngx.update_time()
local begin = ngx.now()
local N = 1e6
for i = 1, N do
    os.date("%Y%m%d")
    -- ngx.say(t)
end
ngx.update_time()

ngx.say("os.date elapsed: ", (ngx.now() - begin) / N)


ngx.update_time()
local begin = ngx.now()
local N = 1e6
for i = 1, N do
    ngx.re.gsub(ngx.today(),'-','')
    -- ngx.say(t)
end
ngx.update_time()

ngx.say("ngx.today() elapsed: ", (ngx.now() - begin) / N)
