FROM letv:centos6
MAINTAINER bingzheng.zhou <zhoubingzheng@letv.com>

RUN rpm -ivh http://pkg-repo.oss.letv.com/pkgs/centos6/letv-release.noarch.rpm
RUN yum install vim -y
RUN yum install nginx -y
RUN yum install cronie -y
RUN yum update bash -y
RUN yum install tar -y

COPY /root/git/nginx-manager/src/api  /opt/letv/nginx-manager/api

EXPOSE 8888
USER root

RUN mkdir -p /etc/nginx/sites-available
RUN mkdir -p /etc/nginx/sites-enabled

ENTRYPOINT python /opt/letv/nginx-manager/nginxManager.py && /bin/bash