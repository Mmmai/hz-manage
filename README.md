# 环境准备

mysql:8
docker run -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=(密码与setting.py中的一致) -d mysql:8.0

CREATE DATABASE IF NOT EXISTS autoOps
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_bin;
python-3.7.9

部署redis

docker run --restart=always -p 6379:6379 --name redis -d redis:latest

根据django/vuedjango/settings.py中的database访问信息创建数据库。
默认settings.py中的mysql和redis地址为域名访问，按需修改或者本机添加hosts中的域名映射即可

# 后端部署

依赖安装

pip install -r requirements.txt

启动django后端

cd django

python .\manage.py makemigrations 

python .\manage.py migrate 


uvicorn --host 0.0.0.0 --port 8000 vuedjango.asgi:application --workers 5

#windows

cd django

celery -A vuedjango worker -l info -P eventlet -B

#linux

cd django

celery -A vuedjango worker -l info -B

# 前端部署

cd hz-ui

npm install

npm run dev
