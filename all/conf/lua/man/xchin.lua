-- Exchange-initiated
local proto = "http"
if ngx.var.http_x_forwarded_proto then
    proto = ngx.var.http_x_forwarded_proto
end

local redir_url = proto .. "://s.opendsp.com/1x1.gif"
local ck = require "resty.cookie"
local cookie, err = ck:new()
local odsp = ""

if cookie then
    odsp, err = cookie:get(ngx.var.kyku)
end

local utils = require "utils"
local uid
if ngx.var.uid_set then
    uid = ngx.var.uid_set
else
    uid = ngx.var.uid_got
end

local base64_cookie = utils.encode_userid(ngx.var.kyku, uid)
local odsp_url_safe = ""

if base64_cookie then
    odsp_url_safe = utils.make_urlsafe(base64_cookie)
end

if not odsp then
    odsp = ngx.var.uid_set
    if odsp then
        local sub = odsp:gsub(ngx.var.kyku .. "=", "HEX0")
        ngx.var.comment = ngx.var.comment .. " SUBSTITUTION: " .. odsp .. ": " .. sub
        odsp = sub
        odsp = odsp:gsub("=", "%%3D")
    else
        ngx.var.comment = ngx.var.comment .. " WEIRD"
    end
else
    if ngx.var.uid_set then
        ngx.var.comment = ngx.var.comment .. " PROBLEM: Had a cookie " .. odsp .. " AND also reset it to " .. ngx.var.uid_set
    end
end

if not odsp then
    ngx.header["X-ODSP-Message"] = "No odsp"
    ngx.var.redir = redir_url .. " NO COOKIE"
    ngx.redirect(redir_url, ngx.HTTP_MOVED_TEMPORARILY)
end

local pc = ngx.req.get_query_args()["pc"]

if not pc then
    ngx.header["X-ODSP-Message"] = "No pc, expected it"
    ngx.var.redir = redir_url
    ngx.redirect(redir_url, ngx.HTTP_MOVED_TEMPORARILY)
    return
end

if pc == "spotx" then
    redir_url = proto .. "://sync.search.spotxchange.com/partner?adv_id=7190&img=1&uid=" .. odsp_url_safe
elseif pc == "openx" then
    local syncval = "%7B%22udat%3D%22X%22%2C%22uid%22%3A%22" .. odsp_url_safe .. "%22%7D"
    redir_url = proto .. "://us-u.openx.net/w/1.0/sd?id=537097544&val=" .. syncval .. "&r=" .. proto .. "%3A%2F%2Fs.opendsp.com%2Fman%2Fxchout%2F%3Fnpc%3Dopenx"
elseif pc == "adaptv" then
    redir_url = proto .. "://sync.adaptv.advertising.com/sync?type=gif&key=inpagegroupllc&uid=" .. odsp_url_safe
elseif pc == "lotame" then
    redir_url = proto .. "://bcp.crwdcntrl.net/map/c=6171/tp=OPND/tpid=" .. odsp_url_safe
elseif pc == "liverail" then
    redir_url = proto .. "://t4.liverail.com/?metric=csync&p=3047&s=" .. odsp_url_safe
elseif pc == "pubmatic" then
    redir_url = proto .. "://image2.pubmatic.com/AdServer/Pug?vcode=bz0yJnR5cGU9MSZjb2RlPTMxNzkmdGw9MTI5NjAw&piggybackCookie=" .. odsp_url_safe
elseif pc == "adx" then
    local gp = ngx.req.get_query_args()["google_push"]
    redir_url = proto .. "://cm.g.doubleclick.net/pixel?google_nid=inpage_group_wopendsp"
    if gp then
        redir_url = redir_url .. "&google_push=" .. gp
    end
    redir_url = redir_url .. "&google_hm=" .. odsp_url_safe
--  redir_url = redir_url .. "&google_cm"
    redir_url = redir_url .. "&nanoput=xchin"
elseif pc == "bidswitch" then
    local ssp = ngx.req.get_query_args()["ssp"]
    if not ssp then
        ssp = "pubmatic"
    end
    redir_url = proto .. "://x.bidswitch.net/sync?dsp_id=89&user_id=" .. odsp_url_safe .. "&expires=30&ssp=" .. ssp
elseif pc == "liveramp" then
    redir_url = proto .. "://idsync.rlcdn.com/401476.gif?partner_uid=" .. odsp_url_safe
end

ngx.var.redir = redir_url
if ngx.var.uid_reset == "" then
    ngx.var.uid_reset = nil
end

ngx.redirect(redir_url, ngx.HTTP_MOVED_TEMPORARILY)
