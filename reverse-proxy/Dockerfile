FROM nginx:1.21-alpine

COPY ./nginx-basic.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]