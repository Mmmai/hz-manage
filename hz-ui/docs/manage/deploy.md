---
title: 构建部署
---

## 本地开发

### 启动服务

```bash
# 后端
cd django
python manage.py runserver 0.0.0.0:8000

# 前端（新终端）
cd hz-ui
npm run dev

# 文档（新终端）
cd hz-ui
npm run docs:dev
```

### 代理配置

Vite 已配置代理（`vite.config.js`），将 `/api` 请求转发到后端 8000 端口。

---

## 生产构建

### 前端构建

```bash
cd hz-ui
npm run build
```

输出：`dist/` 目录

### 文档构建

```bash
cd hz-ui
npm run docs:build
```

输出：`docs/.vuepress/dist/` 目录

---

## 生产架构

```
┌─────────────────────────────────────────────────────────────┐
│                    构建阶段                                   │
├─────────────────────────────────────────────────────────────┤
│  npm run build          →  dist/                             │
│  npm run docs:build     →  docs/.vuepress/dist/              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Nginx 部署                                │
├─────────────────────────────────────────────────────────────┤
│  dist/                     →  /usr/share/nginx/html         │
│  docs/.vuepress/dist/      →  /usr/share/nginx/docs         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    运行时请求路由                             │
├─────────────────────────────────────────────────────────────┤
│  /api/*      →  proxy_pass backend:8000                     │
│  /docs/*     →  alias /usr/share/nginx/docs                 │
│  /*          →  root /usr/share/nginx/html                  │
└─────────────────────────────────────────────────────────────┘
```

## Nginx 部署

### 目录结构

```
/usr/share/nginx/
├── html          # 前端 dist/*
└── docs          # 文档 docs/.vuepress/dist/*
```

### 配置示例

```nginx
server {
    listen 443 ssl;

    # 前端
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # 文档
    location /docs {
        alias /usr/share/nginx/docs/;
        try_files $uri $uri/ /docs/index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
