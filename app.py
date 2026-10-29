import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from database import get_db, init_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")

@app.before_request
def setup_database():
    init_db()

@app.context_processor
def cart_count():
    cart = session.get("cart", {})
    return {"cart_count": sum(int(qty) for qty in cart.values())}

@app.route("/")
def index():
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "featured")
    db = get_db()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if category:
        query += " AND category = ?"
        params.append(category)
    if sort == "price-low":
        query += " ORDER BY price ASC"
    elif sort == "price-high":
        query += " ORDER BY price DESC"
    else:
        query += " ORDER BY id DESC"
    products = db.execute(query, params).fetchall()
    categories = db.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    db.close()
    return render_template("index.html", products=products, categories=categories,
                           search=search, selected_category=category, selected_sort=sort)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    db.close()
    if product is None:
        abort(404)
    return render_template("product.html", product=product)

@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    db = get_db()
    product = db.execute("SELECT id, stock FROM products WHERE id = ?", (product_id,)).fetchone()
    db.close()
    if product is None:
        abort(404)
    cart = session.get("cart", {})
    key = str(product_id)
    current = int(cart.get(key, 0))
    if current >= product["stock"]:
        flash("هاد الكمية ما بقاتش متوفرة فالمخزون.", "error")
    else:
        cart[key] = current + 1
        session["cart"] = cart
        flash("تزادت السلعة للسلة بنجاح.", "success")
    return redirect(request.referrer or url_for("index"))

@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    items = []
    total = 0
    if cart:
        db = get_db()
        for product_id, quantity in cart.items():
            product = db.execute("SELECT * FROM products WHERE id = ?", (int(product_id),)).fetchone()
            if product:
                qty = min(int(quantity), product["stock"])
                line_total = product["price"] * qty
                items.append({"product": product, "quantity": qty, "line_total": line_total})
                total += line_total
        db.close()
    return render_template("cart.html", items=items, total=total)

@app.post("/cart/update/<int:product_id>")
def update_cart(product_id):
    quantity = request.form.get("quantity", "1")
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1
    cart = session.get("cart", {})
    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        db = get_db()
        product = db.execute("SELECT stock FROM products WHERE id = ?", (product_id,)).fetchone()
        db.close()
        if product:
            cart[key] = min(quantity, product["stock"])
    session["cart"] = cart
    return redirect(url_for("view_cart"))

@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    flash("تحيدات السلعة من السلة.", "success")
    return redirect(url_for("view_cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("السلة خاوية. زيدي شي منتج قبل تأكيد الطلب.", "error")
        return redirect(url_for("index"))

    db = get_db()
    items, total = [], 0
    for product_id, quantity in cart.items():
        product = db.execute("SELECT * FROM products WHERE id = ?", (int(product_id),)).fetchone()
        if product:
            qty = min(int(quantity), product["stock"])
            if qty > 0:
                items.append({"product": product, "quantity": qty})
                total += product["price"] * qty

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        if not name or not email or not address:
            flash("عافاك عمّري جميع الخانات.", "error")
        elif not items:
            flash("ما كاين حتى منتج متوفر فالسلة.", "error")
            db.close()
            return redirect(url_for("view_cart"))
        else:
            cursor = db.execute(
                "INSERT INTO orders (customer_name, email, address, total) VALUES (?, ?, ?, ?)",
                (name, email, address, total)
            )
            order_id = cursor.lastrowid
            for item in items:
                product = item["product"]
                qty = item["quantity"]
                db.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                    (order_id, product["id"], qty, product["price"])
                )
                db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product["id"]))
            db.commit()
            db.close()
            session["cart"] = {}
            return render_template("success.html", order_id=order_id)
    db.close()
    return render_template("checkout.html", items=items, total=total)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Set ADMIN_PASSWORD in your environment before using this demo admin page.
    password = os.environ.get("ADMIN_PASSWORD")
    if not password:
        return "Admin page is disabled. Set the ADMIN_PASSWORD environment variable.", 503
    if request.method == "POST":
        supplied = request.form.get("password", "")
        if supplied != password:
            flash("كلمة السر غير صحيحة.", "error")
        else:
            session["is_admin"] = True
            return redirect(url_for("admin"))
    if not session.get("is_admin"):
        return render_template("admin_login.html")
    db = get_db()
    if request.args.get("logout") == "1":
        session.pop("is_admin", None)
        db.close()
        return redirect(url_for("index"))
    products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    orders = db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20").fetchall()
    db.close()
    return render_template("admin.html", products=products, orders=orders)

@app.post("/admin/products/add")
def admin_add_product():
    if not session.get("is_admin"):
        abort(403)
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    image_url = request.form.get("image_url", "").strip()
    try:
        price = round(float(request.form.get("price", "0")), 2)
        stock = int(request.form.get("stock", "0"))
    except ValueError:
        flash("الثمن أو المخزون غير صالح.", "error")
        return redirect(url_for("admin"))
    if not name or not category or price < 0 or stock < 0:
        flash("عافاك تأكدي من معلومات المنتج.", "error")
        return redirect(url_for("admin"))
    db = get_db()
    db.execute("INSERT INTO products (name, description, category, price, stock, image_url) VALUES (?, ?, ?, ?, ?, ?)",
               (name, description, category, price, stock, image_url))
    db.commit()
    db.close()
    flash("تزّاد المنتج بنجاح.", "success")
    return redirect(url_for("admin"))

@app.post("/admin/products/delete/<int:product_id>")
def admin_delete_product(product_id):
    if not session.get("is_admin"):
        abort(403)
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    db.close()
    flash("تحيد المنتج.", "success")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
