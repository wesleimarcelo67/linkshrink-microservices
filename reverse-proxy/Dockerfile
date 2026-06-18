FROM golang:1.25 as libcoraza-builder

# install all dependences
RUN apt update && \
    apt install --no-install-recommends gcc git automake make autoconf libtool gnupg1 ca-certificates libc-dev openssl curl gnupg wget libpcre2-dev zlib1g-dev -y && \
    apt-get clean

# install golang
#RUN wget https://go.dev/dl/go1.24.0.linux-amd64.tar.gz && \
#    tar -C /usr/local/ -xzf "go1.24.0.linux-amd64.tar.gz" && \
#    rm go1.24.0.linux-amd64.tar.gz
#
#ENV PATH="${PATH}:/usr/local/go/bin"

# install libcoraza
RUN git clone https://github.com/corazawaf/libcoraza libcoraza && \
    cd libcoraza && \
    git log --pretty=format:"%h %s (%an)" > ChangeLog && \
    ./build.sh && \
    ./configure --disable-dependency-tracking && \
    make

# coraza.h location /go/libcoraza/coraza/coraza.h
# libcoraza.a location /go/libcoraza/libcoraza.a
# libcoraza.so location /go/libcoraza/libcoraza.so

FROM nginx:1.29-trixie as nginx-coraza

COPY --from=libcoraza-builder /go/libcoraza/coraza/ /usr/local/include/coraza
COPY --from=libcoraza-builder /go/libcoraza/libcoraza.a /usr/local/lib
COPY --from=libcoraza-builder /go/libcoraza/libcoraza.so /usr/local/lib

RUN apt-get update -qq; \
  apt-get install -qq --no-install-recommends \
  gcc \
  gnupg1 \
  ca-certificates  \
  libc-dev \
  make \
  openssl \
  git \
  gnupg \
  wget \
  libpcre2-dev \
  zlib1g-dev

RUN wget https://nginx.org/download/nginx-1.31.1.tar.gz && \
    tar -xzf nginx-1.31.1.tar.gz && rm nginx-1.31.1.tar.gz

RUN git clone https://github.com/corazawaf/coraza-nginx.git && \
    mkdir -p /usr/src && \
    mv coraza-nginx /usr/src

RUN cd nginx-1.31.1 && \
    CONFARGS=$(nginx -V 2>&1 | sed -n -e 's/^.*arguments: //p'); \
    ./configure --with-compat "$CONFARGS" --add-dynamic-module=/usr/src/coraza-nginx; \
    make modules; \
    mkdir -p /usr/lib/nginx/modules; \
    find objs/*.so -print; \
    cp objs/ngx_*.so /usr/lib/nginx/modules

FROM nginx:1.31.1-trixie

COPY --from=nginx-coraza /usr/src/coraza-nginx/t /tmp/t
#COPY --from=nginx-coraza /usr/src/coraza-nginx/coraza.conf /etc/nginx/conf.d/coraza.conf
COPY ./coraza-test.conf /etc/nginx/conf.d/coraza.conf
COPY --from=nginx-coraza /usr/lib/nginx/modules/ /usr/lib/nginx/modules/
COPY --from=libcoraza-builder /go/libcoraza/libcoraza.so /usr/local/lib

COPY ./nginx-basic.conf /etc/nginx/nginx.conf

RUN apt-get update -qq && \
    apt-get install -qq --no-install-recommends perl git && \
    git clone https://github.com/nginx/nginx-tests.git && \
    cd nginx-tests/ && \
    cp /tmp/t/* . && \
    export TEST_NGINX_BINARY=$(which nginx) && \
    export PERL5LIB=/nginx-tests/lib/ && \
    export TEST_NGINX_GLOBALS="load_module \"/usr/lib/nginx/modules/ngx_http_coraza_module.so\"; user root;" && \
    prove -v coraza*.t 2>&1 || true

RUN mkdir -p /var/log/nginx /var/log/coraza && \
    touch /var/log/coraza_debug.log /var/log/coraza_audit.log && \
    chown -R nginx:nginx /var/log/coraza /var/log/coraza_debug.log /var/log/coraza_audit.log && \
    chmod 755 /var/log/coraza && \
    chmod 644 /var/log/coraza_debug.log /var/log/coraza_audit.log

RUN mkdir -p /var/log/nginx /var/log/coraza && \
    touch /var/log/coraza_audit.log /var/log/coraza_debug.log && \
    chown -R nginx:nginx /var/log/coraza /var/log/coraza_audit.log /var/log/coraza_debug.log

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]