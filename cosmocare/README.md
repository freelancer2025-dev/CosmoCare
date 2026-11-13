# CosmoCare – Django Cosmetic E-Commerce

A responsive luxury black-and-gold cosmetic store starter with Django, product catalogue, accounts, cart, checkout, Razorpay integration, order QR codes, WhatsApp Cloud API notification hooks, reviews and Django Admin.

## 1. Requirements
- Python 3.10+
- VS Code (recommended)
- Internet connection for Bootstrap CDN, Razorpay Checkout and API messaging
- Razorpay test credentials for online payment testing
- Meta WhatsApp Cloud API credentials and an approved WhatsApp message template for live messaging

## 2. Run locally (Windows PowerShell)
```powershell
cd cosmocare
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations accounts catalog cart orders reviews
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000 and admin at http://127.0.0.1:8000/admin/.

If PowerShell blocks activation, use:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Or run `.venv\Scripts\python.exe` directly without activation.

## 3. Add initial catalogue
1. Sign in at `/admin/`.
2. Add Categories first (e.g. Face Care, Skin Care, Hair Care, Body Care, Makeup).
3. Add Products and upload product images.
4. Set stock, prices, sale price and featured flag.
5. Create a normal customer at `/accounts/register/` and add a delivery address under My Account.

## 4. Razorpay setup
1. Create a Razorpay account and obtain test Key ID and Key Secret.
2. Add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` to `.env`.
3. Set `SITE_BASE_URL` to your public HTTPS URL for deployed environments.
4. Configure a webhook pointing to `/payments/razorpay/webhook/` and set `RAZORPAY_WEBHOOK_SECRET`.
5. Subscribe to `payment.captured` and `payment.failed`.
6. Test in Razorpay test mode before switching to live credentials.

The checkout verifies the Razorpay checkout signature. The webhook independently verifies its HMAC signature. Never expose the secret key in browser JavaScript.

## 5. WhatsApp Cloud API setup
Set these in `.env`:
- `WHATSAPP_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_API_VERSION`
- `WHATSAPP_TEMPLATE_NAME`
- `WHATSAPP_LANGUAGE_CODE`

The notification service expects a WhatsApp-approved template with four body parameters in this order: customer name, order number, total amount, short order summary. Adapt the template payload to match the exact template approved in your Meta Business account. Customers must opt in to receive messages. A template must be approved for business-initiated notifications outside the customer-service window.

For reliable production delivery, move WhatsApp sending into a background job queue (Celery) and persist provider message IDs, delivery status and retries.

## 6. QR code behavior
A unique QR is generated for each confirmed order and points to its order page. The current order detail page requires the signed-in customer account; for public tracking, implement a dedicated token-based view that validates `public_token` before exposing only minimal tracking information. Do not encode addresses, phone numbers, payment IDs or secrets directly into a QR.

## 7. Important production hardening before launch
- Set `DEBUG=False`, a strong `SECRET_KEY`, correct `ALLOWED_HOSTS`, HTTPS and secure cookie settings.
- Use PostgreSQL, managed media storage and backups.
- Add rate limiting, email verification, password reset email configuration and stronger phone validation.
- Add an idempotent stock-restoration workflow for cancellations/refunds. Do not restore stock repeatedly if a webhook is retried.
- Implement Razorpay refund API calls and admin reconciliation; this starter intentionally records refund-pending rather than claiming a refund has happened.
- Ensure COD orders have a confirmation/dispatch workflow and fraud controls.
- Add privacy policy, terms, shipping, returns/refunds and contact pages.
- Add automated tests for payment verification, duplicate webhooks, stock, cancellation and permissions.
- Configure a real WhatsApp template and test delivery to opted-in test numbers.
- Review tax/GST invoices and applicable Indian e-commerce/privacy requirements with a qualified professional.

## 8. Current starter limitations
This is a functional foundation, not a production-certified store. The product review endpoint is a basic authenticated review form; production should restrict reviews to verified purchasers. Wishlist model/UI, coupon model/UI, customer returns, public QR tracking, refund API automation, notification logs and automated tests are planned extensions. The payment webhook is included, but production deployment should also use an idempotency strategy and monitor failed webhook processing.
