#!/bin/bash
# ==============================================
# 基智学 - 服务器一键部署脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/Leon-LY/invest-learn/master/deploy/setup.sh | bash
# ==============================================
set -e

echo "🚀 基智学 - 服务器部署开始..."
echo ""

# 1. 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

# 2. 确保 docker compose 可用
if ! docker compose version &> /dev/null; then
    echo "❌ docker compose 不可用，请升级 Docker"
    exit 1
fi
echo "✅ Docker Compose: $(docker compose version)"

# 3. 创建项目目录
echo ""
echo "📁 准备项目..."
mkdir -p /opt/invest-learn
cd /opt/invest-learn

# 4. 克隆 / 更新代码
if [ -d ".git" ]; then
    echo "📥 更新代码..."
    git pull origin master 2>/dev/null || git clone https://github.com/Leon-LY/invest-learn.git /tmp/invest-tmp && cp -r /tmp/invest-tmp/* . && rm -rf /tmp/invest-tmp
else
    echo "📥 克隆项目..."
    git clone https://github.com/Leon-LY/invest-learn.git /tmp/invest-tmp && cp -r /tmp/invest-tmp/* . && rm -rf /tmp/invest-tmp && git init && git remote add origin https://github.com/Leon-LY/invest-learn.git
fi

# 5. 环境变量
echo ""
echo "🔐 配置环境变量..."
if [ ! -f ".env" ]; then
    DB_PASS=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 12)
    SECRET=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)
    cat > .env << ENDSECRET
DB_PASSWORD=${DB_PASS}
SECRET_KEY=${SECRET}
JWT_SECRET_KEY=${SECRET}
ENDSECRET
    echo "✅ 已生成随机密码"
else
    echo "✅ .env 已存在"
fi

# 6. 启动服务
echo ""
echo "🐳 启动容器（拉取镜像可能需要几分钟）..."
docker compose -f deploy/docker-compose.prod.yml down 2>/dev/null || true
docker compose -f deploy/docker-compose.prod.yml up -d --build 2>&1 | tail -5

# 7. 等待 PostgreSQL 就绪
echo ""
echo "⏳ 等待数据库启动..."
for i in $(seq 1 30); do
    if docker compose -f deploy/docker-compose.prod.yml exec -T db pg_isready -U investlearn 2>/dev/null; then
        echo "✅ 数据库已就绪"
        break
    fi
    sleep 2
done

# 8. 初始化种子数据
echo ""
echo "🌱 导入学习内容..."
docker compose -f deploy/docker-compose.prod.yml exec -T backend python seed_data.py 2>/dev/null && echo "✅ 种子数据导入成功" || echo "⚠️ 种子数据已存在或导入跳过"

# 9. 完成
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ip.sb 2>/dev/null || echo "你的服务器IP")
echo ""
echo "============================================"
echo "🎉 部署成功！"
echo "============================================"
echo "🔗 后端 API:  http://${PUBLIC_IP}:8000"
echo "📖 API 文档:  http://${PUBLIC_IP}:8000/api/docs"
echo "💚 健康检查:  http://${PUBLIC_IP}:8000/health"
echo "============================================"
echo ""
echo "常用命令:"
echo "  查看日志:  docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml logs -f"
echo "  重启服务:  docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml restart"
echo "  停止服务:  docker compose -f /opt/invest-learn/deploy/docker-compose.prod.yml down"
