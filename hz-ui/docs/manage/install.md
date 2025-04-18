---
title: 安装
---
## 依赖环境

建议配置如下：

| 内存    | cpu       | 空间 | 操作系统                                                                 |
| ------- | --------- | ---- | ------------------------------------------------------------------------ |
| > 128GB | > 64 core | 1 TB | 内核版本>3，例如：redhat7.5/openeuler20/ubuntu20等可运行docker的操作系统 |

## 环境配置

关闭防火墙

安装docker、docker-compose环境

## 开始安装

解压teligen-ui_(版本).tar.gz

```shell
cd /opt/
tar xvf teligen-ui_(版本).tar.gz -C /opt/
```

导入镜像

```shell
cd /opt/teligen-ui
docker load -i mysql.tar.gz
docker load -i redis.tar.gz
docker load -i nginx.tar.gz
docker load -i manage-django.tar.gz
```

按需修改参数

.env

```plaintext
#web
WEB_PORT=8843
#数据库
DATABASE_HOST=mysql
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=thinker
MANAGE_DATABASE=manage
CMDB_DATABASE=cmdb
REDIS_HOST=redis
REDIS_PORT=6379
#数据目录
DATA_DIR=./data
```

> 建议修改DATA_DIR目录，其它可默认

启动服务

```shell
cd /opt/teligen-ui
docker-compose up -d 
```

查看服务

```shell
docker-compose ps 
```

## 访问页面

https://部署IP:8843/

默认用户名密码为：admin/thinker

![1736820273050](image/install/1736820273050.png)
