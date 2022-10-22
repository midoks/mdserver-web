local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end

-- 以上为预热操作
collectgarbage()

local config_domains = {
    [1] = {
        ["name"] = "t1.cn",
        ["path"] = "/www/wwwroot/t1.cn",
        ["domains"] = {
            [1] = "t1.cn",
            [2] = "t3.cn"
        }
    }
}

local function get_server_name(request_name)
    for _,v in ipairs(config_domains)
    do
        for _,cd_name in ipairs(v['domains'])
        do
            if request_name == cd_name then
                return v['name']
            end
        end
    end
    return request_name
end


local function get_server_name_cache(request_name)
    local cache_name = ngx.shared.limit:get(request_name)
    if cache_name then return cache_name end

    for _,v in ipairs(config_domains)
    do
        for _,cd_name in ipairs(v['domains'])
        do
            if request_name == cd_name then
                ngx.shared.limit:set(cd_name,v['name'],3600)
                return v['name']
            end
        end
    end
    return request_name
end


ngx.update_time()
local begin = ngx.now()
local N = 1e7
for i = 1, N do
    get_server_name("t3.cn")
end
ngx.update_time()

ngx.say("test get_server_name elapsed: ", (ngx.now() - begin) / N)




ngx.update_time()
local begin = ngx.now()
local N = 1e7
for i = 1, N do
    get_server_name_cache("t3.cn")
end
ngx.update_time()

ngx.say("test get_server_name_cache elapsed: ", (ngx.now() - begin) / N)