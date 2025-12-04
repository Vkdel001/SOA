# Brevo Email Setup for zwennpay.online

## Step 1: Add Domain to Brevo

1. Log in to Brevo: https://app.brevo.com
2. Go to **Settings** → **Senders & IP**
3. Click **Domains** tab
4. Click **Add a Domain**
5. Enter: `zwennpay.online`
6. Click **Add**

## Step 2: Add DNS Records in GoDaddy

Brevo will show you DNS records to add. Go to GoDaddy DNS management and add these:

### SPF Record (TXT)
```
Type: TXT
Name: @
Value: v=spf1 include:spf.brevo.com ~all
TTL: 1 Hour
```

### DKIM Records (CNAME)
Brevo will provide 3 CNAME records like:

```
Type: CNAME
Name: mail._domainkey
Value: mail._domainkey.zwennpay.online.dkim.brevo.com.
TTL: 1 Hour

Type: CNAME
Name: mail2._domainkey
Value: mail2._domainkey.zwennpay.online.dkim.brevo.com.
TTL: 1 Hour

Type: CNAME
Name: mail3._domainkey
Value: mail3._domainkey.zwennpay.online.dkim.brevo.com.
TTL: 1 Hour
```

### DMARC Record (TXT) - Optional but recommended
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc@zwennpay.online
TTL: 1 Hour
```

## Step 3: Verify Domain in Brevo

1. After adding DNS records, wait 10-30 minutes
2. Go back to Brevo → Domains
3. Click **Verify** next to zwennpay.online
4. If successful, you'll see green checkmarks

## Step 4: Add Sender Email

1. In Brevo, go to **Senders & IP** → **Senders**
2. Click **Add a Sender**
3. Enter:
   - Name: ZwennPay
   - Email: noreply@zwennpay.online (or any email you want)
4. Click **Add**

## Step 5: Integrate with Your App (Optional)

If you want to send emails from your SOA app:

### Install Brevo SDK
```bash
pip3 install sib-api-v3-sdk
```

### Add to requirements.txt
```
sib-api-v3-sdk
```

### Example Code to Send Email

```python
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Configure API key
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = 'YOUR_BREVO_API_KEY'

# Create API instance
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Email content
send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
    to=[{"email": "customer@example.com", "name": "Customer Name"}],
    sender={"email": "noreply@zwennpay.online", "name": "ZwennPay"},
    subject="Your Statement of Account",
    html_content="<html><body><h1>Your statement is ready</h1></body></html>"
)

# Send email
try:
    api_response = api_instance.send_transac_email(send_smtp_email)
    print(api_response)
except ApiException as e:
    print("Exception when sending email: %s\n" % e)
```

### Get API Key from Brevo
1. Go to **Settings** → **SMTP & API**
2. Click **Create a new API key**
3. Copy the key

## Step 6: Test Email Sending

In Brevo dashboard:
1. Go to **Campaigns** → **Email**
2. Click **Send a test email**
3. Use your verified sender (noreply@zwennpay.online)
4. Send to your personal email to test

## Common Issues

### Domain not verifying
- Wait 30-60 minutes for DNS propagation
- Check DNS records are exactly as Brevo shows
- Use https://mxtoolbox.com to verify SPF and DKIM

### Emails going to spam
- Make sure DMARC is set up
- Warm up your domain by sending gradually increasing volumes
- Avoid spam trigger words in subject lines

### Authentication failed
- Double-check API key is correct
- Make sure sender email is verified in Brevo

## Email Limits

**Free Plan:**
- 300 emails/day
- Brevo logo in emails

**Paid Plans:**
- Starting at $25/month for 20,000 emails
- No Brevo branding
- Better deliverability

## Useful Links

- Brevo Dashboard: https://app.brevo.com
- DNS Checker: https://dnschecker.org
- SPF Checker: https://mxtoolbox.com/spf.aspx
- DKIM Checker: https://mxtoolbox.com/dkim.aspx
