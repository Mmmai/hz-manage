<template><div><h2 id="依赖环境" tabindex="-1"><a class="header-anchor" href="#依赖环境"><span>依赖环境</span></a></h2>
<p>建议配置如下：</p>
<table>
<thead>
<tr>
<th>内存</th>
<th>cpu</th>
<th>空间</th>
<th>操作系统</th>
</tr>
</thead>
<tbody>
<tr>
<td>&gt; 128GB</td>
<td>&gt; 64 core</td>
<td>1 TB</td>
<td>内核版本&gt;3，例如：redhat7.5/openeuler20/ubuntu20等可运行docker的操作系统</td>
</tr>
</tbody>
</table>
<h2 id="环境配置" tabindex="-1"><a class="header-anchor" href="#环境配置"><span>环境配置</span></a></h2>
<p>关闭防火墙</p>
<p>安装docker、docker-compose环境</p>
<h2 id="开始安装" tabindex="-1"><a class="header-anchor" href="#开始安装"><span>开始安装</span></a></h2>
<p>解压teligen-ui_(版本).tar.gz</p>
<div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre v-pre><code><span class="line"><span class="token builtin class-name">cd</span> /opt/</span>
<span class="line"><span class="token function">tar</span> xvf teligen-ui_<span class="token punctuation">(</span>版本<span class="token punctuation">)</span>.tar.gz <span class="token parameter variable">-C</span> /opt/</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div></div></div><p>导入镜像</p>
<div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre v-pre><code><span class="line"><span class="token builtin class-name">cd</span> /opt/teligen-ui</span>
<span class="line"><span class="token function">docker</span> load <span class="token parameter variable">-i</span> mysql.tar.gz</span>
<span class="line"><span class="token function">docker</span> load <span class="token parameter variable">-i</span> redis.tar.gz</span>
<span class="line"><span class="token function">docker</span> load <span class="token parameter variable">-i</span> nginx.tar.gz</span>
<span class="line"><span class="token function">docker</span> load <span class="token parameter variable">-i</span> manage-django.tar.gz</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>按需修改参数</p>
<p>.env</p>
<div class="language-plaintext line-numbers-mode" data-highlighter="prismjs" data-ext="plaintext" data-title="plaintext"><pre v-pre><code><span class="line">#web</span>
<span class="line">WEB_PORT=8843</span>
<span class="line">#数据库</span>
<span class="line">DATABASE_HOST=mysql</span>
<span class="line">DATABASE_PORT=3306</span>
<span class="line">DATABASE_USER=root</span>
<span class="line">DATABASE_PASSWORD=thinker</span>
<span class="line">MANAGE_DATABASE=manage</span>
<span class="line">CMDB_DATABASE=cmdb</span>
<span class="line">REDIS_HOST=redis</span>
<span class="line">REDIS_PORT=6379</span>
<span class="line">#数据目录</span>
<span class="line">DATA_DIR=./data</span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><blockquote>
<p>建议修改DATA_DIR目录，其它可默认</p>
</blockquote>
<p>启动服务</p>
<div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre v-pre><code><span class="line"><span class="token builtin class-name">cd</span> /opt/teligen-ui</span>
<span class="line"><span class="token function">docker-compose</span> up <span class="token parameter variable">-d</span> </span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div><div class="line-number"></div></div></div><p>查看服务</p>
<div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre v-pre><code><span class="line"><span class="token function">docker-compose</span> <span class="token function">ps</span> </span>
<span class="line"></span></code></pre>
<div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0"><div class="line-number"></div></div></div><h2 id="访问页面" tabindex="-1"><a class="header-anchor" href="#访问页面"><span>访问页面</span></a></h2>
<p>https://部署IP:8843/</p>
<p>默认用户名密码为：admin/thinker</p>
<p><img src="@source/manage/image/install/1736820273050.png" alt="1736820273050"></p>
</div></template>


