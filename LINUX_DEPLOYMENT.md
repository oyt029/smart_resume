# Linux服务器部署指南

本文档详细介绍如何在Linux服务器上部署简历智能匹配系统。

## 系统要求

### 最低配置
- CPU: 1核
- 内存: 2GB
- 存储: 5GB可用空间
- 系统: Ubuntu 20.04+/CentOS 7+/Debian 10+

### 推荐配置
- CPU: 2核以上
- 内存: 4GB以上
- 存储: 10GB以上
- 系统: Ubuntu 22.04 LTS

## 部署步骤

### 1. 系统初始化

```bash
# Ubuntu/Debian系统
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git nginx supervisor -y

# CentOS/RHEL系统
sudo yum update -y
sudo yum install python3 python3-pip git nginx supervisor -y
```

### 2. 创建专用用户（推荐）

```bash
# 创建应用用户
sudo useradd -r -s /bin/false smartresume
sudo mkdir -p /opt/smart_resume
sudo chown smartresume:smartresume /opt/smart_resume
```

### 3. 获取项目代码

```bash
# 切换到应用目录
cd /opt/smart_resume

# 克隆项目
sudo -u smartresume git clone https://github.com/oyt029/smart_resume.git .

# 设置权限
sudo chown -R smartresume:smartresume /opt/smart_resume
```

### 4. 创建Python虚拟环境

```bash
# 创建虚拟环境
sudo -u smartresume python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### 5. 安装依赖

```bash
# 安装项目依赖
sudo -u smartresume pip install -r requirements.txt

# 安装生产环境依赖
sudo -u smartresume pip install gunicorn[gevent] supervisor
```

### 6. 配置环境变量

```bash
# 复制环境配置文件
sudo -u smartresume cp .env.example .env

# 编辑配置文件
sudo -u smartresume vim .env
```

在`.env`文件中设置：
```env
ZHIPUAI_API_KEY=your_actual_api_key_here
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### 7. 测试运行

```bash
# 切换到应用用户
sudo -u smartresume bash

# 激活虚拟环境
source venv/bin/activate

# 测试运行
cd /opt/smart_resume
python app.py --host 0.0.0.0 --port 8000

# 在另一个终端测试
curl http://localhost:8000/health
```

### 8. 配置Gunicorn（生产环境）

创建Gunicorn配置文件 `/opt/smart_resume/gunicorn.conf.py`：

```python
# Gunicorn配置文件
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = "smartresume"
group = "smartresume"
tmp_upload_dir = None
errorlog = "/var/log/smart_resume/error.log"
accesslog = "/var/log/smart_resume/access.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "info"
```

### 9. 配置Supervisor（进程管理）

创建Supervisor配置文件 `/etc/supervisor/conf.d/smart_resume.conf`：

```ini
[program:smart_resume]
command=/opt/smart_resume/venv/bin/gunicorn -c /opt/smart_resume/gunicorn.conf.py app:app
directory=/opt/smart_resume
user=smartresume
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/smart_resume.log
environment=PATH="/opt/smart_resume/venv/bin"
```

创建日志目录：
```bash
sudo mkdir -p /var/log/smart_resume
sudo chown smartresume:smartresume /var/log/smart_resume
```

启动Supervisor：
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start smart_resume
```

### 10. 配置Nginx反向代理

创建Nginx配置文件 `/etc/nginx/sites-available/smart_resume`：

```nginx
upstream smart_resume_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://smart_resume_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 静态文件缓存
    location /static/ {
        alias /opt/smart_resume/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 健康检查
    location /health {
        proxy_pass http://smart_resume_backend;
        access_log off;
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/smart_resume /etc/nginx/sites-enabled/
sudo nginx -t  # 测试配置
sudo systemctl restart nginx
```

### 11. SSL证书配置（可选但推荐）

使用Let's Encrypt免费SSL证书：

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y  # Ubuntu/Debian
# 或
sudo yum install certbot python3-certbot-nginx -y  # CentOS

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行：
0 12 * * * /usr/bin/certbot renew --quiet
```

### 12. 防火墙配置

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 监控和维护

### 1. 日志查看

```bash
# 应用日志
tail -f /var/log/smart_resume/error.log
tail -f /var/log/smart_resume/access.log

# Supervisor日志
tail -f /var/log/supervisor/smart_resume.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. 服务管理

```bash
# 查看服务状态
sudo supervisorctl status smart_resume

# 重启服务
sudo supervisorctl restart smart_resume

# 停止服务
sudo supervisorctl stop smart_resume

# 启动服务
sudo supervisorctl start smart_resume
```

### 3. 性能监控

```bash
# 查看系统资源使用
htop
free -h
df -h

# 查看网络连接
netstat -tulpn | grep :8000

# 查看应用进程
ps aux | grep smart_resume
```

## 故障排除

### 常见问题及解决方案

#### 1. 服务无法启动
```bash
# 检查错误日志
sudo tail -f /var/log/supervisor/smart_resume.log

# 手动测试运行
cd /opt/smart_resume
sudo -u smartresume ./venv/bin/python app.py --host 127.0.0.1 --port 8000
```

#### 2. Nginx 502错误
```bash
# 检查后端服务是否运行
sudo supervisorctl status smart_resume

# 检查端口占用
netstat -tulpn | grep :8000

# 重启服务
sudo supervisorctl restart smart_resume
```

#### 3. 权限问题
```bash
# 修正文件权限
sudo chown -R smartresume:smartresume /opt/smart_resume
sudo chmod -R 755 /opt/smart_resume

# 修正日志目录权限
sudo chown smartresume:smartresume /var/log/smart_resume
```

#### 4. 内存不足
```bash
# 减少工作进程数
# 编辑 gunicorn.conf.py
workers = 2  # 从4减少到2

# 重启服务
sudo supervisorctl restart smart_resume
```

## 备份策略

### 1. 代码备份
```bash
# 创建备份脚本 /opt/smart_resume/backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/smart_resume"
mkdir -p $BACKUP_DIR

# 备份代码
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /opt/smart_resume --exclude='/opt/smart_resume/venv' --exclude='/opt/smart_resume/uploads'

# 备份配置
cp /opt/smart_resume/.env $BACKUP_DIR/env_$DATE.backup

echo "Backup completed: $DATE"
```

```bash
# 设置定时备份
chmod +x /opt/smart_resume/backup.sh
crontab -e
# 添加每日备份任务
0 2 * * * /opt/smart_resume/backup.sh
```

### 2. 数据备份
如果使用数据库，需要定期备份数据库。

## 升级部署

### 1. 代码更新
```bash
# 停止服务
sudo supervisorctl stop smart_resume

# 备份当前版本
cp -r /opt/smart_resume /opt/smart_resume_backup_$(date +%Y%m%d)

# 拉取最新代码
cd /opt/smart_resume
sudo -u smartresume git pull origin main

# 更新依赖
sudo -u smartresume ./venv/bin/pip install -r requirements.txt

# 重启服务
sudo supervisorctl start smart_resume
```

### 2. 零停机部署
```bash
# 准备新版本
cd /opt
sudo -u smartresume git clone https://github.com/oyt029/smart_resume.git smart_resume_new
cd smart_resume_new
sudo -u smartresume ../smart_resume/venv/bin/pip install -r requirements.txt

# 切换版本
sudo supervisorctl stop smart_resume
sudo mv /opt/smart_resume /opt/smart_resume_old
sudo mv /opt/smart_resume_new /opt/smart_resume
sudo supervisorctl start smart_resume

# 验证后清理
# sudo rm -rf /opt/smart_resume_old
```

## 安全加固

### 1. 系统安全
```bash
# 禁用root SSH登录
sudo vim /etc/ssh/sshd_config
# PermitRootLogin no

# 更改SSH默认端口
# Port 2222

sudo systemctl restart ssh
```

### 2. 应用安全
```bash
# 限制文件上传大小
# 在Nginx配置中已设置 client_max_body_size 10M

# 设置文件权限
find /opt/smart_resume -type f -exec chmod 644 {} \;
find /opt/smart_resume -type d -exec chmod 755 {} \;
```

这个部署指南提供了完整的Linux生产环境部署方案，包括性能优化、安全加固和运维监控等方面的内容。