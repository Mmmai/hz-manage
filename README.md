# 环境准备

mysql:8

mongodb:8

python-3.7.9

根据django/vuedjango/settings.py中的database访问信息创建数据库。

# 后端部署

依赖安装

pip install -r requirements.txt

启动django后端

cd django 

python manager.py makemigrations mapi mlog cmdb

python manager.py migrate mapi

python manager.py migrate mlog

python manager.py migrate cmdb

python manager.py runserver

# 前端部署

npm install 

npm run dev
