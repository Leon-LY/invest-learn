#!/bin/bash
# ==============================================
# 基智学 - 服务器一键部署脚本
# 使用方法: chmod +x setup.sh && ./setup.sh
# ==============================================
set -e

echo "🚀 基智学 - 服务器部署开始..."
echo ""

# 1. 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi
echo "✅ Docker 已就绪: $(docker --version)"

# 2. 安装 docker-compose（如果没有）
if ! command -v docker-compose &> /dev/null; then
    echo "📦 安装 docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
echo "✅ docker-compose 已就绪"

# 3. 创建项目目录
echo ""
echo "📁 创建项目目录..."
mkdir -p /opt/invest-learn
cd /opt/invest-learn

# 4. 克隆项目（或更新）
if [ -d ".git" ]; then
    echo "📥 更新代码..."
    git pull origin master
else
    echo "📥 克隆项目..."
    git clone https://github.com/Leon-LY/invest-learn.git .
fi

# 5. 配置环境变量
echo ""
echo "🔐 配置环境变量..."
if [ ! -f ".env" ]; then
    DB_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)
    SECRET_KEY=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    cat > .env << EOF
DB_PASSWORD=${DB_PASSWORD}
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${SECRET_KEY}
EOF
    echo "✅ 生成随机密码"
else
    echo "✅ .env 已存在，跳过"
fi

# 6. 启动服务
echo ""
echo "🐳 启动 Docker 容器..."
docker-compose -f deploy/docker-compose.prod.yml down 2>/dev/null || true
docker-compose -f deploy/docker-compose.prod.yml up -d

# 7. 等待数据库就绪
echo ""
echo "⏳ 等待数据库就绪..."
sleep 10

# 8. 初始化数据库
echo ""
echo "📊 初始化数据库..."
docker-compose -f deploy/docker-compose.prod.yml exec -T backend python seed_data.py 2>/dev/null || echo "⚠️ 种子数据导入跳过（首次部署正常）"

# 9. 显示状态
echo ""
echo "============================================"
echo "🎉 部署完成！"
echo "============================================"
echo "后端 API:    http://$(curl -s ifconfig.me 2>/dev/null || echo '你的IP'):8000"
echo "API 文档:    http://$(curl -s ifconfig.me 2>/dev/null || echo '你的IP'):8000/api/docs"
echo "健康检查:    http://$(curl -s ifconfig.me 2>/dev/null || echo '你的IP'):8000/health"
echo ""
echo "📋 查看日志: docker-compose -f deploy/docker-compose.prod.yml logs -f"
echo "🔄 重启服务: docker-compose -f deploy/docker-compose.prod.yml restart"
echo "🛑 停止服务: docker-compose -f deploy/docker-compose.prod.yml down"
echo "============================================"
