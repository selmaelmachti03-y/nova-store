import sqlite3
from pathlib import Path

DATABASE = Path(__file__).with_name("store.db")

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL,
            price REAL NOT NULL CHECK(price >= 0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
            image_url TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
    """)
    count = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        seed_products = [
            ("Everyday Tote", "حقيبة عملية بتصميم بسيط ومناسبة للاستعمال اليومي.", "Accessories", 249.00, 12, "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85"),
            ("Minimal Watch", "ساعة أنيقة بتفاصيل هادئة ولمسة عصرية.", "Accessories", 399.00, 8, "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=900&q=85"),
            ("Ceramic Mug Set", "مجموعة كؤوس سيراميك بتصميم ناعم للقهوة والشاي.", "Home", 129.00, 20, "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85"),
            ("Daily Sneakers", "حذاء مريح بإطلالة نظيفة وسهلة التنسيق.", "Fashion", 520.00, 7, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=85"),
            ("Soft Knit", "قطعة محبوكة ناعمة للأيام الباردة.", "Fashion", 289.00, 10, "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=85"),
            ("Desk Organizer", "منظم مكتبي عملي للحفاظ على مساحة مرتبة.", "Home", 159.00, 15, "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?auto=format&fit=crop&w=900&q=85"),
        ]
        db.executemany(
            "INSERT INTO products (name, description, category, price, stock, image_url) VALUES (?, ?, ?, ?, ?, ?)",
            seed_products
        )
    db.commit()
    db.close()
