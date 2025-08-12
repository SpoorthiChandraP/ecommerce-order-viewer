from flask import Flask, request, jsonify, render_template
import sqlite3
import os

DB_PATH = os.path.join("data", "ecommerce.db")

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Helper functions for DB queries
def get_user(user_id):
    conn = get_db()
    user = conn.execute("""
        SELECT id, first_name, last_name, email, city, state
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()
    conn.close()
    return user

def get_orders_for_user(user_id):
    conn = get_db()
    orders = conn.execute("""
        SELECT order_id, status, created_at, num_of_item
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return orders

def get_items_for_order(order_id):
    conn = get_db()
    items = conn.execute("""
        SELECT oi.id, p.name AS product_name, p.brand, p.category,
               COUNT(oi.id) as quantity, p.retail_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
        GROUP BY p.id
    """, (order_id,)).fetchall()
    conn.close()
    return items

@app.route("/")
def home():
    return render_template("index.html")

# Web page routes using helper functions
@app.route("/user/<int:user_id>/orders")
def user_orders_page(user_id):
    user = get_user(user_id)
    if not user:
        return "User not found", 404
    orders = get_orders_for_user(user_id)
    return render_template("user_orders.html", user=user, orders=orders)

@app.route("/order/<int:order_id>/items")
def order_items_page(order_id):
    items = get_items_for_order(order_id)
    return render_template("order_items.html", order_id=order_id, items=items)

# API routes using helper functions
@app.route("/api/users")
def search_users():
    q = request.args.get("query", "")
    conn = get_db()
    cur = conn.execute("""
        SELECT id, first_name, last_name, email, city, state
        FROM users
        WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
        LIMIT 50
    """, (f"%{q}%", f"%{q}%", f"%{q}%"))
    results = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(results)

@app.route("/api/users/<int:user_id>/orders")
def user_orders(user_id):
    orders = get_orders_for_user(user_id)
    return jsonify([dict(row) for row in orders])

@app.route("/api/orders/<int:order_id>/items")
def order_items(order_id):
    items = get_items_for_order(order_id)
    return jsonify([dict(row) for row in items])

if __name__ == "__main__":
    app.run(debug=True)
