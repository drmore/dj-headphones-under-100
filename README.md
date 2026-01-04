# All DJ headphones under $100 — lowest price first

Static GitHub Pages site that **updates itself daily** using the **Amazon Product Advertising API (PA-API 5.0)**.

## One-time setup
1. Get your Amazon Associates US **Partner Tag** (tracking ID, usually ends in `-20`).
2. Enable PA-API and obtain:
   - Access key
   - Secret key
3. In your GitHub repo: Settings → Secrets and variables → Actions → add secrets:
   - `PAAPI_ACCESS_KEY`
   - `PAAPI_SECRET_KEY`
   - `PAAPI_PARTNER_TAG`
4. Enable GitHub Pages:
   - Settings → Pages → Build and deployment → Deploy from a branch
   - Branch: `main` / Folder: `/ (root)`
5. Run the workflow once:
   - Actions → Daily rebuild → Run workflow

## Local run (optional)
```bash
pip install -r requirements.txt
export PAAPI_ACCESS_KEY=...
export PAAPI_SECRET_KEY=...
export PAAPI_PARTNER_TAG=yourtag-20
python build_page.py
```

## Locale defaults
- Marketplace: `www.amazon.com`
- Host: `webservices.amazon.com`
- Region: `us-east-1`
