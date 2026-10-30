# Avatthar AI Academy — Full Stack Website

A professional navy / soft-gold / white full-stack website using:

- HTML + Jinja templates
- CSS
- Vanilla JavaScript
- Python + Flask
- SQLite + SQLAlchemy
- Flask-Login admin authentication
- Internship application form with resume upload
- Admin dashboard and application status management
- WhatsApp integration
- Optional AI chatbot using the OpenAI Responses API

## 1. Install

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Configure environment

Copy `.env.example` to `.env`.

Set:

```env
SECRET_KEY=your-random-secret
WHATSAPP_NUMBER=919876543210
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-5.5
ADMIN_EMAIL=admin@avattharacademy.com
ADMIN_PASSWORD=your-strong-password
```

Keep `.env` private and never upload it to GitHub.

The chatbot uses the official OpenAI Python SDK and Responses API. If `OPENAI_API_KEY` is empty, the website still runs and the chatbot returns a configuration message.

## 3. Run

```bash
python run.py
```

Open:

`http://127.0.0.1:5000`

## 4. Admin

Open:

`http://127.0.0.1:5000/login`

Default values come from `.env`.

Change the default admin password before production.

## 5. WhatsApp

There are two WhatsApp features:

1. A floating WhatsApp button on the website.
2. A WhatsApp message link beside each internship applicant in the admin panel.

Set your number in `.env` using international format without `+`:

```env
WHATSAPP_NUMBER=919876543210
```

This is a click-to-WhatsApp integration. It does NOT provide automated WhatsApp Business API messaging.

For automated customer replies, templates, webhooks and business-initiated messages, connect the site to the WhatsApp Business Platform/Cloud API separately.

## 6. Important production improvements

Before public launch:

- Use PostgreSQL/MySQL instead of SQLite for higher traffic.
- Put Flask behind Gunicorn/Nginx or a production hosting platform.
- Add CSRF protection.
- Add rate limiting to the chatbot and application endpoints.
- Store uploaded resumes outside a public web directory.
- Add file virus scanning and stricter upload validation.
- Replace placeholder project visuals with your real project screenshots.
- Add your actual company address, phone, email and social profiles.
- Use HTTPS.
- Change the admin credentials.
- Add privacy policy and terms.
