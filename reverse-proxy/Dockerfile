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

FROM nginx:1.29-alpine as nginx-coraza

COPY --from=libcoraza-builder /go/libcoraza/coraza/ /usr/local/include/coraza
COPY --from=libcoraza-builder /go/libcoraza/libcoraza.a /usr/local/lib
COPY --from=libcoraza-builder /go/libcoraza/libcoraza.so /usr/local/lib

RUN apk update && \
    apk add --no-cache zlib-dev build-base pcre-dev git

RUN wget https://nginx.org/download/nginx-1.30.0.tar.gz && \
    tar -xzf nginx-1.30.0.tar.gz && rm nginx-1.30.0.tar.gz

RUN git clone https://github.com/corazawaf/coraza-nginx.git && \
    mkdir -p /usr/src && \
    mv coraza-nginx /usr/src

RUN cd nginx-1.30.0 && \
    CONFARGS=$(nginx -V 2>&1 | sed -n -e 's/^.*arguments: //p'); \
    ./configure --with-compat "$CONFARGS" --add-dynamic-module=/usr/src/coraza-nginx; \
    make modules; \
    mkdir -p /usr/lib/nginx/modules; \
    find objs/*.so -print; \
    cp objs/ngx_*.so /usr/lib/nginx/modules
# COPY ./nginx-basic.conf /etc/nginx/nginx.conf

# EXPOSE 80

# CMD ["nginx", "-g", "daemon off;"]