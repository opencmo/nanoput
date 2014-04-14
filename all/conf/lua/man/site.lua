ngx.var.dcpath = ngx.var.c .. "/" .. ngx.var.dc .. "/" .. ngx.var.segment .. "/" .. ngx.var.pxid .. "/"
if ngx.var.host == "s.opendsp.com" then
    ngx.var.converted_cookie = "px" .. ngx.var.pxid .. "=" .. os.time()
    ngx.header["Set-Cookie"] = { ngx.var.converted_cookie .. ";Domain=.opendsp.com;Path=/;Max-Age=2592000;" }
end
local secs = "N/A"
local dec_ck = ""
local proto = "http";
local step = 0
if ngx.var.http_x_forwarded_proto then
    proto = ngx.var.http_x_forwarded_proto
end
-- If we don't have uid
local retag = ngx.req.get_query_args()['retag']
if not retag then
    retag = ""
end
local redir = proto .. "://s.opendsp.com/1x1.gif"
local qs = ngx.var.query_string
if qs then
    qs = "?" .. qs
else
    qs = "?"
end
local nxch = ngx.req.get_query_args()['nxch']
if not nxch then
    redir = proto .. "://s.opendsp.com/man/xchout/" .. ngx.var.pxid .. "/" .. qs .. "&seg=" .. ngx.var.segment
end
local ok = ""
local comment = ""
local err = ""
local ok2 = ""
if ngx.var.host ~= "s.opendsp.com" then
    redir = proto .. "://s.opendsp.com/man/osfa/" .. ngx.var.dcpath
else
    step = 1
    local redis = require "resty.redis"
    local red = redis:new()
    red:set_timeout(100)
--  ok, err = red:connect("segments.opendsp.com", 6379)
    ok, err = red:connect("172.31.48.243", 6379)
    step = 2

    if not err or err == ngx.null then
        err = ""
    end
    if not ok or ok == ngx.null then
        ok = ""
    end

    if not ok then
        ok = ""
        step = 3
        ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. ",comment:" .. comment .. "}"
        ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY);
        return
    end
    step = 4
    dec_ck = ngx.var.uid_got
    if not dec_ck or dec_ck == ngx.null or dec_ck == nil then
        dec_ck = ngx.var.uid_set
        ok = ok .. "SET: " .. ngx.var.uid_set
        if not dec_ck or dec_ck == ngx.null or dec_ck == nil then
            err = "No uid_got or uid_set"
            step = 5
            ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. ",comment:" .. comment .. "}"
            ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY)
            return
        end
    end
    step = 6
    secs = math.floor(ngx.now())
    dec_ck = string.gsub(dec_ck, ngx.var.kyku .. "=", "")

    ok2, err = red:zadd("segment:" .. ngx.var.segment, secs, dec_ck)
    if not err or err == ngx.null then
        err = ""
    end

    ok2, err = red:zadd("segment_v2:last:" .. ngx.var.segment, secs, dec_ck)
    if not err or err == ngx.null then
        err = ""
    end
    fseg = "segment_v2:first:"..ngx.var.segment
    local seen = red:zscore(fseg, dec_ck)
    if not seen or seen == ngx.null then
         red:zadd(fseg, secs, dec_ck)
    else 
         comment = "Seen: "..seen.."; "  
    end
    -- This only works in 3.0.2 - we should move to newer redis.
    --    ok2, err = red:zadd(fseg, "NX", secs, dec_ck)
--    if not err or err == ngx.null then
--        err = ""
--    end

    if not ok2 or ok2 == ngx.null then
        ok2 = ""
        step = 7
        ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. ",comment:" .. comment .. "}"
        ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY);
        return
    end
    -- Hello
    -- Goodbye
    ok = ok .. "; " .. ok2
    step = 8
end
if not dec_ck then
    dec_ck = ""
    secs = "N/A"
end
if ngx.var.uid_reset == "" then
    ngx.var.uid_reset = nil
end
ngx.var.pechenka = dec_ck
if ngx.var.pechenka == "" then
    ngx.var.pechenka = nil
end
ngx.var.misc = "{err:" .. err .. ",redir:" .. redir .. ",step:" .. step .. ",ok:" .. ok .. ",segment:" .. ngx.var.segment .. ",secs:" .. secs .. ",uid:" .. dec_ck .. ",comment:" .. comment .. "}"
ngx.redirect(redir, ngx.HTTP_MOVED_TEMPORARILY)
