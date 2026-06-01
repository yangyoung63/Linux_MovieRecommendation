FROM nginx:alpine
# index.html을 Nginx의 기본 웹 서비스 폴더로 복사
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
