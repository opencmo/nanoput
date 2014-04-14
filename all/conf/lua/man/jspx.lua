function explode(div, str)
    if (div == '') then
        return false
    end
    local pos, arr = 0, {}
    for st, sp in function() return string.find(str, div, pos, true) end do
        table.insert(arr, string.sub(str, pos, st - 1))
        pos = sp + 1
    end
    table.insert(arr, string.sub(str, pos))
    return arr
end

local exclude_vendors = require "exclude_vendors"

function get_vendors (pixel_id)
    return exclude_vendors[pixel_id]
end

local js = ""
local proto = "http"
if ngx.var.http_x_forwarded_proto then
    proto = ngx.var.http_x_forwarded_proto
end
local path = ngx.req.get_query_args()["path"]

local jsp = true
local njs = ngx.req.get_query_args()["njs"]

if njs then
    jsp = false
end

if jsp then
    js = js .. [[<script type="text/javascript">
]]
end
js = js .. [[var axel = Math.random() + "";
var a = axel * 10000000000000;
]]

if path then
    -- Getting pxid from path for old pixels
    if not tonumber(ngx.var.pxid) then
        local cid,dcid,sid,pxid = path:match("man/osfa/([^/]+)/([^/]+)/([^/]+)/([^/]+)")
        ngx.var.pxid = pxid
    end

    js = js .. [[document.write('<img src="]]
    local sep = "&"
    if string.find(path, "?") == nil then
        sep = "?"
    end
    js = js .. proto .. '://' .. ngx.var.host .. "/" .. path .. sep .. "nxch=1"
    js = js .. [[" width="1" height="1" />');
]]
end

-- Important
-- Order is determined in
-- SELECT GROUP_CONCAT(data_sync_partner_id) FROM ld_data_sync_partner;
-- and should not change
local goodPcs = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 }
local availablePcs = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 }
local goodPcValues = { 'adaptv', 'adx', 'brx', 'bidswitch', 'liveramp', 'lotame', 'neustar', 'openx', 'pubmatic', 'rubicon', 'smaato', 'spotx', 'dbm' }
local neededPcValues = {}

local pcs = ngx.req.get_query_args()["pcs"]
if pcs then
    -- TODO
    goodPcs = explode(",", pcs)
end

local npcs
local exchanges = {}
local exch = ngx.req.get_query_args()["exch"]

exchanges["adx"] = "5,6,9"

if tonumber(ngx.var.pxid) then
    npcs = get_vendors(ngx.var.pxid)
else
    npcs = ngx.req.get_query_args()["npcs"]
end

if exch then
    if exchanges[exch] then
        if npcs then
            for npc in string.gmatch(exchanges[exch], "[^,]+") do
                if not string.find(npcs, npc) then
                    npcs = npcs .. "," .. npc
                end
            end
        else
            npcs = exchanges[exch]
        end
    end
end

local npcArr = {}
if npcs then
    js = js .. "// COMMENT: Have NPCs: " .. npcs .. "<br>\n"
    npcArr = explode(",", npcs)
end

local skip1 = false

for pcCount = 1, #goodPcValues do
    skip1 = false
    for npcCount = 1, #npcArr do
        local npcIdx = npcArr[npcCount]
        npcIdx = tonumber(npcIdx)
        if pcCount == npcIdx then
            skip1 = true
        end
    end
    if skip1 == true then
    else
        local newIdx = #neededPcValues + 1
        neededPcValues[#neededPcValues + 1] = goodPcValues[pcCount]
    end
end

for neededPcCount = 1, #neededPcValues do
    js = js .. [[document.write('<img src="]]
    js = js .. proto .. '://' .. ngx.var.host .. "/man/xchout/?pc=" .. neededPcValues[neededPcCount] .. "&x="
    js = js .. [['+a+'" width="1" height="1" />');
]]
end

if jsp then
    js = js .. [[
        </script>
        <noscript>
]]
    if path then
        js = js .. [[<img src="]]
        js = js .. proto .. '://' .. ngx.var.host .. '/' .. path
        js = js .. [[" width="1" height="1" />
]]
    end

    for neededPcCount = 1, #neededPcValues do
        js = js .. "// COMMENT: " .. neededPcCount .. ": " .. neededPcValues[neededPcCount] .. "\n"
        js = js .. [[<img src="]]
        js = js .. proto .. '://' .. ngx.var.host .. "/man/xchout/?pc=" .. neededPcValues[neededPcCount]
        js = js .. [[" width="1" height="1" />
]]
    end

    js = js .. "</noscript>";
end

ngx.say(js);
if ngx.var.uid_reset == "" then
    ngx.var.uid_reset = nil
end
