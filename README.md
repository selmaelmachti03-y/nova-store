# Nova Store — Flask E-commerce Portfolio Project

A responsive demo online store built with **Python, Flask, SQLite, HTML, and CSS**.

## Features
- Product catalogue with search, category filter, and price sorting
- Product detail pages
- Session-based shopping cart (add, update quantity, remove)
- Demo checkout with order and order-item records stored in SQLite
- Stock count decreases after an order is placed
- Admin page to add/delete products and view recent orders
- Responsive layout for desktop and mobile
- Parameterized SQL queries for user-provided search and form data

## Important demo notes
- Checkout is a portfolio demo only. It does **not** process real payments or arrange delivery.
- The admin route is disabled unless you set `ADMIN_PASSWORD`.
- Before any public deployment, set a strong `SECRET_KEY`, use HTTPS, add CSRF protection and rate limiting, and use a proper production server. For a real shop, add authentication, privacy/security review, backups, and a real payment provider.
- Product photos load from Unsplash URLs and need an internet connection. Replace the URLs with your own licensed images if desired.

## Run locally

### 1. Install Python
Use Python 3.10+.

### 2. Open a terminal in this folder and create a virtual environment

Windows:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install requirements
```bash
python -m pip install -r requirements.txt
```

### 4. Start the app
```bash
python app.py
```
Open http://127.0.0.1:5000 in your browser. The SQLite database and sample products are created automatically on first run.

### Optional: enable admin page
Set an admin password before running the app.

PowerShell:
```powershell
$env:ADMIN_PASSWORD="choose-a-strong-password"
$env:SECRET_KEY="replace-with-a-long-random-secret"
python app.py
```

macOS/Linux:
```bash
export ADMIN_PASSWORD="choose-a-strong-password"
export SECRET_KEY="replace-with-a-long-random-secret"
python app.py
```
Then open http://127.0.0.1:5000/admin.

## Push to GitHub

1. Create a new empty repository on GitHub, for example `nova-store`.
2. Do not add a README or `.gitignore` on GitHub because this project already includes them.
3. In a terminal opened inside the `nova-store` folder, run:
```bash
git init
git add .
git commit -m "Build Nova Store Flask ecommerce portfolio"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/nova-store.git
git push -u origin main
```
4. Replace `YOUR-USERNAME` with your GitHub username.

If Git says your identity is not configured:
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```
Then repeat the commit and push commands.

## Project structure
```text
nova-store/
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── success.html
│   ├── admin_login.html
│   └── admin.html
└── static/
    └── css/
        └── style.css
```

## Ideas for a next version
- Add tests with `pytest`
- Add customer accounts and password hashing
- Add pagination and product reviews
- Add image upload validation
- Add CSRF protection and server-side form validation
- Deploy using a production WSGI server and managed database
