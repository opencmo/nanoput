if ngx.var.host == "s.opendsp.com" then
    ngx.var.converted_cookie = "px" .. ngx.var.pxid .. "=" .. os.time() .. ";Domain=.opendsp.com;Path=/;Max-Age=2592000;"
    ngx.header["Set-Cookie"] = { ngx.var.converted_cookie }
end
local secs = "N/A"
local dec_ck = ""
local proto = "http";
local step = 0
if ngx.var.http_x_forwarded_proto then
    proto = ngx.var.http_x_forwarded_proto
end

local redir = ngx.req.get_query_args()['r']
if not redir then
   redir = proto .. "://s.opendsp.com/1x1.gif"
end

local ts_id = ngx.req.get_query_args()['cid']
if not ts_id then
   ts_id = "all"
else
   ts_id = "ts="..ts_id
end

local redis = require "resty.redis"
local red = redis:new()
red:set_timeout(100)
--  ok, err = red:connect("172.30.0.220", 6379)  -- user10-va-opends.rj4y00.ng.0001.use1.cache.amazonaws.com
ok, err = red:connect("172.31.48.243", 6379)  -- segments1.dtlpy3.0001.use1.cache.amazonaws.com
dec_ck = ngx.var.uid_got
if not dec_ck or dec_ck == ngx.null or dec_ck == nil then
    dec_ck = ngx.var.uid_set
end

if not dec_ck or dec_ck == ngx.null or dec_ck == nil then
   ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY)
   return
end

secs = math.floor(ngx.now())
dec_ck = string.gsub(dec_ck, ngx.var.kyku .. "=", "")

ok2, err = red:zadd("segment_v2:last:" .. ngx.var.event..":sp:"..ts_id, secs, dec_ck)
fseg = "segment_v2:first:"..ngx.var.event..":sp:" .. ts_id
local seen = red:zscore(fseg, dec_ck)
if not seen or seen == ngx.null then
    red:zadd(fseg, secs, dec_ck)
end
ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY)
