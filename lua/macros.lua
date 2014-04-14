math.randomseed(os.time()*math.random(1,300000))
local rnd = math.random(1,10000000000)..math.random(1,10000000000)..math.random(
1,10000000000)..math.random(1,10000000000)..math.random(1,10000000000)..math.ran
dom(1,10000000000)
ngx.arg[1] = string.gsub(ngx.arg[1], "{RND}", rnd)
ngx.arg[2] = true 
        

