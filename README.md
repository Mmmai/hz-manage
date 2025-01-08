# 环境准备

mysql:8
docker run -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=(密码与setting.py中的一致) -d mysql:8.0

create database hz-manage;

create database cmdb;

#已切换mysql，可以忽略

mongodb:8

docker run -it --name mongodb -e MONGO_INITDB_ROOT_USERNAME=cmdb -e  MONGO_INITDB_ROOT_PASSWORD=(密码与setting.py中的一致) -p 27017:27017 -d mongo:latest

/bin/bash

mongosh -u cmdb

use cmdb;

db.createUser({user:"admin", pwd:"(密码与setting.py中的一致)", roles:[{role: "dbOwner", db: "cmdb"}]})

python-3.7.9

部署redis

docker run --restart=always -p 6379:6379 --name redis -d redis:latest

根据django/vuedjango/settings.py中的database访问信息创建数据库。

# 后端部署

依赖安装

pip install -r requirements.txt

启动django后端

cd django

python .\manage.py makemigrations mapi mlog cmdb

python .\manage.py migrate mapi

python .\manage.py migrate mlog

python .\manage.py migrate cmdb --database=cmdb

python .\manage.py runserver

# 前端部署

cd hz-ui

npm install

npm run dev
