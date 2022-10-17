
local function target()
    ngx.re.find("hello, world.", [[\w+\.]], "jo")
end
for i = 1, 100 do
    target()
end
-- 以上为预热操作
collectgarbage()

local function match_spider(ua)
	-- 匹配蜘蛛请求
	local is_spider = false
	local spider_name = ""
	local spider_match = ""

	local spider_table = {
		["baidu"] = 1,  -- check
		["bing"] = 2,  -- check 
		["qh360"] = 3, -- check
		["google"] = 4,
		["bytes"] = 5,  -- check
		["sogou"] = 6,  -- check
		["youdao"] = 7,
		["soso"] = 8,
		["dnspod"] = 9,
		["yandex"] = 10,
		["yisou"] = 11,
		["other"] = 12,
		["mpcrawler"] = 13,
		["yahoo"] = 14, -- check
		["duckduckgo"] = 15
	}

	local find_spider, _ = ngx.re.match(ua, "(Baiduspider|Bytespider|360Spider|Sogou web spider|Sosospider|Googlebot|bingbot|AdsBot-Google|Google-Adwords|YoudaoBot|Yandex|DNSPod-Monitor|YisouSpider|mpcrawler)", "ijo")
	if find_spider then
		is_spider = true
		spider_match = string.lower(find_spider[0])
		if string.find(spider_match, "baidu", 1, true) then
			spider_name = "baidu"
		elseif string.find(spider_match, "bytes", 1, true) then
			spider_name = "bytes"
		elseif string.find(spider_match, "360", 1, true) then
			spider_name = "qh360"
		elseif string.find(spider_match, "sogou", 1, true) then
			spider_name = "sogou"
		elseif string.find(spider_match, "soso", 1, true) then
			spider_name = "soso"
		elseif string.find(spider_match, "google", 1, true) then
			spider_name = "google"
		elseif string.find(spider_match, "bingbot", 1, true) then
			spider_name = "bing"
		elseif string.find(spider_match, "youdao", 1, true) then
			spider_name = "youdao"
		elseif string.find(spider_match, "dnspod", 1, true) then
			spider_name = "dnspod"
		elseif string.find(spider_match, "yandex", 1, true) then
			spider_name = "yandex"
		elseif string.find(spider_match, "yisou", 1, true) then
			spider_name = "yisou"
		elseif string.find(spider_match, "mpcrawler", 1, true) then
			spider_name = "mpcrawler"
		end
	end

	if is_spider then 
		return is_spider, spider_name, spider_table[spider_name]
	end

	-- Curl|Yahoo|HeadlessChrome|包含bot|Wget|Spider|Crawler|Scrapy|zgrab|python|java|Adsbot|DuckDuckGo
	find_spider, _ = ngx.re.match(ua, "(Yahoo|Slurp|DuckDuckGo)", "ijo")
	if res then
		spider_match = string.lower(find_spider[0])
		if string.find(spider_match, "yahoo", 1, true) then
			spider_name = "yahoo"
		elseif string.find(spider_match, "slurp", 1, true) then
			spider_name = "yahoo"
		elseif string.find(spider_match, "duckduckgo", 1, true) then
			spider_name = "duckduckgo"
		end
		return true, spider_name, spider_table[spider_name]
	end
	return false, "", 0
end



-- local is_spider, request_spider, spider_index = match_spider("Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)")

-- ngx.say(is_spider,request_spider, spider_index)

ngx.update_time()
local begin = ngx.now()
local N = 1e6
for i = 1, N do
    match_spider("Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)")
end
ngx.update_time()

ngx.say("match_spider elapsed: ", (ngx.now() - begin) / N)






