# SSL Certificate Setup for soa.zwennpay.online

## Step 1: Point Subdomain to Your Server (GoDaddy)

1. Log in to GoDaddy
2. Go to "My Products" → "DNS" for zwennpay.online
3. Add this DNS record:

```
Type: A
Name: soa
Value: 102.222.106.225
TTL: 600 seconds
```

4. Save changes (DNS propagation takes 5-30 minutes)

## Step 2: Install Certbot (Let's Encrypt SSL)

On your server:

```bash
# Install EPEL repository (if not already installed)
dnf install -y epel-release

# Install Certbot and Nginx plugin
dnf install -y certbot python3-certbot-nginx

# Verify installation
certbot --version
```

## Step 3: Configure Nginx

```bash
# Create Nginx configuration for SOA subdomain
vi /etc/nginx/conf.d/soa.zwennpay.conf
```

Add this content:

```nginx
server {
    listen 80;
    server_name soa.zwennpay.online;

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

Save and exit (`:wq`)

```bash
# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

# Enable Nginx to start on boot
systemctl enable nginx
```

## Step 4: Open Firewall Ports

```bash
# If using firewalld
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# OR if using iptables
iptables -I INPUT -p tcp --dport 80 -j ACCEPT
iptables -I INPUT -p tcp --dport 443 -j ACCEPT
iptables-save > /etc/sysconfig/iptables
```

## Step 5: Test Subdomain (Before SSL)

Wait 5-10 minutes for DNS to propagate, then test:

```bash
# From your server
curl http://soa.zwennpay.online

# Or open in browser
http://soa.zwennpay.online
```

## Step 6: Install SSL Certificate

Once the subdomain is accessible via HTTP:

```bash
# Get SSL certificate (Certbot will auto-configure Nginx)
certbot --nginx -d soa.zwennpay.online

# Follow the prompts:
# - Enter your email address
# - Agree to terms (Y)
# - Share email with EFF (optional - Y or N)
# - Redirect HTTP to HTTPS (choose option 2 - recommended)
```

## Step 7: Auto-Renewal Setup

```bash
# Test auto-renewal
certbot renew --dry-run

# Check renewal timer
systemctl status certbot-renew.timer

# If timer doesn't exist, create a cron job
crontab -e

# Add this line (runs twice daily):
0 0,12 * * * certbot renew --quiet
```

## Step 8: Verify SSL

Open in browser:
```
https://soa.zwennpay.online
```

Check SSL rating:
```
https://www.ssllabs.com/ssltest/analyze.html?d=soa.zwennpay.online
```

## Troubleshooting

### DNS not propagating
```bash
# Check DNS from server
nslookup soa.zwennpay.online
dig soa.zwennpay.online

# Check from external tool
# Visit: https://dnschecker.org
```

### Certbot fails
```bash
# Make sure port 80 is accessible
curl http://soa.zwennpay.online

# Check Nginx logs
tail -f /var/log/nginx/error.log

# Verify Nginx is running
systemctl status nginx
```

### Certificate renewal fails
```bash
# Check certbot logs
journalctl -u certbot-renew

# Manually renew
certbot renew --force-renewal
```

## Final Configuration

After SSL is installed, your Nginx config will look like:

```nginx
server {
    listen 80;
    server_name soa.zwennpay.online;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name soa.zwennpay.online;

    ssl_certificate /etc/letsencrypt/live/soa.zwennpay.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/soa.zwennpay.online/privkey.pem;
    
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

## Access Your App

After setup:
- HTTP: http://soa.zwennpay.online (redirects to HTTPS)
- HTTPS: https://soa.zwennpay.online ✅

Certificate auto-renews every 90 days!

## Adding More Apps Later

For other apps, just create new subdomains and Nginx configs:

**Example for another app on port 5001:**

1. Add DNS record in GoDaddy: `app2` → `102.222.106.225`
2. Create `/etc/nginx/conf.d/app2.zwennpay.conf`
3. Point to different port: `proxy_pass http://127.0.0.1:5001;`
4. Get SSL: `certbot --nginx -d app2.zwennpay.online`
