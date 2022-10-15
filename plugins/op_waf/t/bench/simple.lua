local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end

collectgarbage()

ngx.update_time()
local begin = ngx.now()
local N = 1e7
for i = 1, N do
    target()
end
ngx.update_time()

ngx.say("elapsed: ", (ngx.now() - begin) / N)