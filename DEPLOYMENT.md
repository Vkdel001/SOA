# Deployment Guide

## 1. Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ZwennPay Statement Generator"

# Add remote repository
git remote add origin https://github.com/Vkdel001/SOA.git

# Push to GitHub
git push -u origin main
```

If you get an error about branch name, try:
```bash
git branch -M main
git push -u origin main
```

## 2. Deploy to AlmaLinux Server

### On Your Local Machine:

```bash
# SSH into your server
ssh root@your-server-ip
```

### On Your Server:

```bash
# Navigate to web directory
cd /var/www

# Clone the repository
git clone https://github.com/Vkdel001/SOA.git
cd SOA

# Install Python 3 and pip (if not installed)
dnf install python3 python3-pip -y

# Install dependencies
pip3 install -r requirements.txt

# Create necessary folders
mkdir -p uploads output static

# Upload your logo file to static folder
# (Use SCP or FTP to upload zwennPay.jpg to /var/www/SOA/static/)

# Install and configure Gunicorn (production WSGI server)
pip3 install gunicorn

# Test the application
python3 app.py
```

### Set up as a System Service:

Create a systemd service file:
```bash
nano /etc/systemd/system/soa.service
```

Add this content:
```ini
[Unit]
Description=ZwennPay Statement of Account Generator
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/SOA
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable soa

# Start the service
systemctl start soa

# Check status
systemctl status soa
```

### Configure Nginx (Reverse Proxy):

```bash
# Install Nginx
dnf install nginx -y

# Create Nginx configuration
nano /etc/nginx/conf.d/soa.conf
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/SOA/static;
    }
}
```

Start Nginx:
```bash
# Enable and start Nginx
systemctl enable nginx
systemctl start nginx

# Open firewall ports
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### SELinux Configuration (if enabled):

```bash
# Allow Nginx to connect to network
setsebool -P httpd_can_network_connect 1

# Set correct SELinux context
chcon -R -t httpd_sys_content_t /var/www/SOA
```

## 3. Update Deployment

When you make changes:

```bash
# On local machine - push changes
git add .
git commit -m "Your update message"
git push

# On server - pull changes
cd /var/www/SOA
git pull
systemctl restart soa
```

## 4. Useful Commands

```bash
# View application logs
journalctl -u soa -f

# Restart service
systemctl restart soa

# Stop service
systemctl stop soa

# Check Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

## 5. Access the Application

Open browser and go to:
- `http://your-server-ip`
- or `http://your-domain.com`
