from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB_PATH = Path(__file__).with_name("canteen.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
                available INTEGER NOT NULL DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                total REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(item_id) REFERENCES menu_items(id)
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO menu_items (name, category, price, stock, available) VALUES (?, ?, ?, ?, 1)",
                [
                    ("Veg Meals", "Meals", 80, 25),
                    ("Chicken Rice", "Rice", 120, 15),
                    ("Masala Dosa", "Tiffin", 50, 20),
                    ("Tea", "Beverages", 15, 60),
                ],
            )

@app.route("/")
def index():
    with get_db() as conn:
        items = conn.execute("SELECT * FROM menu_items ORDER BY id DESC").fetchall()
        orders = conn.execute("""
            SELECT o.*, m.name AS item_name
            FROM orders o JOIN menu_items m ON m.id = o.item_id
            ORDER BY o.id DESC LIMIT 10
        """).fetchall()
        stats = {
            "items": conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0],
            "available": conn.execute("SELECT COUNT(*) FROM menu_items WHERE available=1 AND stock>0").fetchone()[0],
            "orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "sales": conn.execute("SELECT COALESCE(SUM(total), 0) FROM orders").fetchone()[0],
        }
    return render_template("index.html", items=items, orders=orders, stats=stats)

@app.route("/items/add", methods=["POST"])
def add_item():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    try:
        price = float(request.form.get("price", ""))
        stock = int(request.form.get("stock", ""))
        if not name or not category or price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        flash("Enter a valid item name, category, non-negative price and stock.", "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        conn.execute(
            "INSERT INTO menu_items (name, category, price, stock, available) VALUES (?, ?, ?, ?, 1)",
            (name, category, price, stock),
        )
    flash("Menu item added successfully.", "success")
    return redirect(url_for("index"))

@app.route("/items/<int:item_id>/edit", methods=["POST"])
def edit_item(item_id):
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    try:
        price = float(request.form.get("price", ""))
        stock = int(request.form.get("stock", ""))
        if not name or not category or price < 0 or stock < 0:
            raise ValueError
    except ValueError:
        flash("Please enter valid item details.", "error")
        return redirect(url_for("index"))
    with get_db() as conn:
        conn.execute(
            "UPDATE menu_items SET name=?, category=?, price=?, stock=? WHERE id=?",
            (name, category, price, stock, item_id),
        )
    flash("Menu item updated.", "success")
    return redirect(url_for("index"))

@app.route("/items/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    with get_db() as conn:
        used = conn.execute("SELECT COUNT(*) FROM orders WHERE item_id=?", (item_id,)).fetchone()[0]
        if used:
            flash("This item has order history, so it cannot be deleted. Set stock to 0 instead.", "error")
        else:
            conn.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
            flash("Menu item deleted.", "success")
    return redirect(url_for("index"))

@app.route("/items/<int:item_id>/availability", methods=["POST"])
def toggle_availability(item_id):
    with get_db() as conn:
        conn.execute("""
            UPDATE menu_items
            SET available = CASE WHEN available=1 THEN 0 ELSE 1 END
            WHERE id=?
        """, (item_id,))
    flash("Availability updated.", "success")
    return redirect(url_for("index"))

@app.route("/orders/add", methods=["POST"])
def add_order():
    customer = request.form.get("customer_name", "").strip()
    try:
        item_id = int(request.form.get("item_id", ""))
        quantity = int(request.form.get("quantity", ""))
        if not customer or quantity < 1:
            raise ValueError
    except ValueError:
        flash("Enter a customer name and quantity of at least 1.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        item = conn.execute("SELECT * FROM menu_items WHERE id=?", (item_id,)).fetchone()
        if item is None or not item["available"] or item["stock"] < quantity:
            flash("Item is unavailable or there is not enough stock.", "error")
            return redirect(url_for("index"))
        total = item["price"] * quantity
        conn.execute(
            "INSERT INTO orders (customer_name, item_id, quantity, total) VALUES (?, ?, ?, ?)",
            (customer, item_id, quantity, total),
        )
        conn.execute("UPDATE menu_items SET stock=stock-? WHERE id=?", (quantity, item_id))
    flash(f"Order placed. Total: ₹{total:.2f}", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
