#!/bin/bash
# ==============================================================================
# Vcart E-Commerce Platform — AWS EC2 Automated Deployment Script
# Target Instance: i-09c682c4af38cc98b (or any Ubuntu 22.04 / 24.04 LTS EC2)
# ==============================================================================

set -e

echo "=========================================================="
echo " Starting Vcart Automated Deployment on AWS EC2..."
echo "=========================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run as root (use: sudo bash deploy_aws.sh)"
  exit 1
fi

APP_DIR="/var/www/vcart"
REPO_URL="https://github.com/vivekmenon2004/Vcart-Task-2.git"

echo "[1/8] Updating system packages and installing dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-pip python3-venv python3-dev build-essential libpq-dev nginx git curl ufw

echo "[2/8] Fetching Public IP and DNS..."
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" 2>/dev/null || true)
if [ -n "$TOKEN" ]; then
    PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || true)
    PUBLIC_DNS=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-hostname 2>/dev/null || true)
fi

if [ -z "$PUBLIC_IP" ]; then
    PUBLIC_IP=$(curl -s https://ifconfig.me || curl -s https://api.ipify.org || echo "127.0.0.1")
fi

echo "  -> Public IP: $PUBLIC_IP"
if [ -n "$PUBLIC_DNS" ]; then
    echo "  -> Public DNS: $PUBLIC_DNS"
fi

echo "[3/8] Setting up application repository at $APP_DIR..."
if [ -d "$APP_DIR/.git" ]; then
    echo "  -> Existing repository found. Pulling latest code..."
    cd "$APP_DIR"
    git fetch origin main
    git reset --hard origin/main
else
    echo "  -> Cloning repository from $REPO_URL..."
    mkdir -p "$APP_DIR"
    git clone "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

echo "[4/8] Setting up Python virtual environment..."
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv "$APP_DIR/venv"
fi
source "$APP_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"

echo "[5/8] Configuring Production Environment (.env)..."
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')

ALLOWED_HOSTS_VAL="$PUBLIC_IP,localhost,127.0.0.1"
CSRF_ORIGINS_VAL="http://$PUBLIC_IP,https://$PUBLIC_IP"

if [ -n "$PUBLIC_DNS" ] && [ "$PUBLIC_DNS" != "$PUBLIC_IP" ]; then
    ALLOWED_HOSTS_VAL="$ALLOWED_HOSTS_VAL,$PUBLIC_DNS"
    CSRF_ORIGINS_VAL="$CSRF_ORIGINS_VAL,http://$PUBLIC_DNS,https://$PUBLIC_DNS"
fi

cat <<EOF > "$APP_DIR/.env"
# Production Environment Configuration
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$ALLOWED_HOSTS_VAL
CSRF_TRUSTED_ORIGINS=$CSRF_ORIGINS_VAL

# Database: Leave empty to use local SQLite, or paste PostgreSQL DATABASE_URL
DATABASE_URL=

# Cloudinary: Leave empty to store media on local disk, or provide Cloudinary URL
CLOUDINARY_URL=
EOF

echo "[6/8] Running database migrations, static collection, and data seed..."
mkdir -p "$APP_DIR/media" "$APP_DIR/staticfiles"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Run seed data to populate categories, products, banners, and default admin
python manage.py seed_data

# Ensure permissions for www-data
chown -R www-data:www-data "$APP_DIR"
chmod -R 775 "$APP_DIR/media" "$APP_DIR/staticfiles"
chmod 664 "$APP_DIR/db.sqlite3" || true
chmod 775 "$APP_DIR"

echo "[7/8] Configuring systemd Gunicorn service..."
cat <<EOF > /etc/systemd/system/vcart.service
[Unit]
Description=Vcart Django E-Commerce Platform (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 60 vcart.wsgi:application
Restart=always
RestartSec=3
Environment="PATH=$APP_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vcart
systemctl restart vcart

echo "[8/8] Configuring Nginx reverse proxy..."
cat <<EOF > /etc/nginx/sites-available/vcart
server {
    listen 80;
    server_name $PUBLIC_IP $PUBLIC_DNS;

    client_max_body_size 50M;

    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location /media/ {
        alias $APP_DIR/media/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable site in nginx
ln -sf /etc/nginx/sites-available/vcart /etc/nginx/sites-enabled/vcart
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

# Configure firewall if ufw is present
if command -v ufw >/dev/null 2>&1; then
    ufw allow 'OpenSSH' || true
    ufw allow 80/tcp || true
    ufw allow 443/tcp || true
fi

echo ""
echo "=========================================================="
echo " 🎉 Vcart successfully deployed and running on AWS EC2!"
echo "=========================================================="
echo " 🌐 Storefront URL:      http://$PUBLIC_IP/"
echo " 📊 Operations Dashboard: http://$PUBLIC_IP/dashboard/"
echo " ⚙️ Django Admin Panel:   http://$PUBLIC_IP/admin/"
echo ""
echo " 🔐 Administrator Login:"
echo "    Username: admin"
echo "    Password: admin123"
echo ""
echo " 🔐 Demo Customer Login:"
echo "    Username: testuser"
echo "    Password: TestUser123!"
echo "=========================================================="
