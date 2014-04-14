yum install hg

cd /opt/enr/nginx_src
wget http://nginx.org/download/nginx-1.4.1.tar.gz
tar xzf nginx-1.4.1.tar.gz

# http://wiki.nginx.org/HttpLuaModule#Installation:
git clone http://luajit.org/git/luajit-2.0.git
cd luajit-2.0
make
make install
cd ..
export LUAJIT_LIB=/usr/local/lib
export LUAJIT_INC=/usr/local/include/luajit-2.0
 

git clone https://github.com/simpl/ngx_devel_kit.git

git clone https://github.com/chaoslawful/lua-nginx-module.git

git clone https://github.com/couchbaselabs/couchbase-nginx-module.git
# https://github.com/couchbaselabs/couchbase-nginx-module#readme
wget http://packages.couchbase.com/clients/c/libcouchbase-2.0.3nginx2.tar.gz
tar xzf libcouchbase-2.0.3nginx2.tar.gz 
cd libcouchbase-2.0.3nginx2
autoconf
./configure --disable-plugins --disable-tests --disable-couchbasemock
make
make install


cd nginx-1.4.1
yum install pcre-devel

./configure --prefix=/opt/enr/nginx \
--sbin-path=/usr/sbin/nginx \
--conf-path=/opt/enr/all/conf/nginx.conf \
--error-log-path=/opt/enr/log/error.log \
--http-log-path=/opt/enr/log/access.log \
--pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx \
--with-http_ssl_module \
--with-http_realip_module \
--with-http_addition_module \
--with-http_sub_module \
--with-http_dav_module \
--with-http_flv_module \
--with-http_mp4_module \
--with-http_gunzip_module \
--with-http_gzip_static_module \
--with-http_random_index_module \
--with-http_secure_link_module \
--with-http_stub_status_module \
--with-mail \
--with-mail_ssl_module \
--with-file-aio \
--with-http_geoip_module \
--with-ipv6 \
--add-module=/opt/enr/c-third-party/nginx_src/ngx_devel_kit \
--add-module=/opt/enr/c-third-party/nginx_src/lua-nginx-module \
--add-module=/opt/enr/c-third-party/nginx_src/redis2-nginx-module \
--add-module=/opt/enr/nginx/share/protobuf-nginx \
--add-module=/opt/enr/proto/ngx_google_proto \
--with-cc-opt='-O2 -g'

make
make install
cd /etc/init.d
wget 'http://wiki.nginx.org/index.php?title=RedHatNginxInitScript&action=raw&anchor=nginx' -O nginx
