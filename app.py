from flask import Flask, request, jsonify, render_template
import sqlite3
import os

DB_PATH = os.path.join("data", "ecommerce.db")

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")

# New route for user orders page
@app.route("/user/<int:user_id>/orders")
def user_orders_page(user_id):
    conn = get_db()
    
    # Get user information
    user = conn.execute("""
        SELECT id, first_name, last_name, email, city, state
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()
    
    if not user:
        conn.close()
        return "User not found", 404
    
    # Get user's orders
    orders = conn.execute("""
        SELECT order_id, status, created_at, num_of_item
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,)).fetchall()
    
    conn.close()
    
    return render_template("user_orders.html", user=user, orders=orders)

# New route for order items page
@app.route("/order/<int:order_id>/items")
def order_items_page(order_id):
    conn = get_db()
    
    # Get order items
    items = conn.execute("""
        SELECT oi.id, p.name AS product_name, p.brand, p.category,
               COUNT(oi.id) as quantity, p.retail_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
        GROUP BY p.id
    """, (order_id,)).fetchall()
    
    conn.close()
    
    return render_template("order_items.html", order_id=order_id, items=items)

# 1. Search for a user
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
    return jsonify([dict(row) for row in cur.fetchall()])

# 2. Get user's orders
@app.route("/api/users/<int:user_id>/orders")
def user_orders(user_id):
    conn = get_db()
    cur = conn.execute("""
        SELECT order_id, status, created_at, num_of_item
        FROM orders
        WHERE user_id = ?
    """, (user_id,))
    return jsonify([dict(row) for row in cur.fetchall()])

# 3. Get items in an order
@app.route("/api/orders/<int:order_id>/items")
def order_items(order_id):
    conn = get_db()
    cur = conn.execute("""
        SELECT oi.id, p.name AS product_name, p.brand, p.category,
               COUNT(oi.id) as quantity, p.retail_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
        GROUP BY p.id
    """, (order_id,))
    return jsonify([dict(row) for row in cur.fetchall()])

if __name__ == "__main__":
    app.run(debug=True)


# from flask import Flask, render_template, request, jsonify
# import sqlite3
# import os

# app = Flask(__name__)

# DATABASE = os.path.join(os.path.dirname(__file__), 'data', 'ecommerce.db')

# # --- Database connection helper ---
# def get_db_connection():
#     conn = sqlite3.connect(DATABASE)
#     conn.row_factory = sqlite3.Row
#     return conn


# # --- Home page (search) ---
# @app.route('/')
# def index():
#     return render_template('index.html')


# # --- API: Search users ---
# @app.route('/api/users')
# def api_users():
#     query = request.args.get('query', '').strip()
#     conn = get_db_connection()

#     if query:
#         users = conn.execute("""
#             SELECT id, first_name, last_name, email, city, state
#             FROM users
#             WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
#         """, (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
#     else:
#         users = []

#     conn.close()
#     return jsonify([dict(u) for u in users])


# # --- Orders page for a given user ---
# @app.route('/user/<int:user_id>')
# def view_user_orders(user_id):
#     conn = get_db_connection()
#     user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

#     if not user:
#         conn.close()
#         return f"<h2>User with ID {user_id} not found.</h2>", 404

#     orders = conn.execute("""
#         SELECT order_id, status, created_at, num_of_item
#         FROM orders
#         WHERE user_id=?
#         ORDER BY created_at DESC
#     """, (user_id,)).fetchall()

#     conn.close()
#     return render_template('users.html', user=user, orders=orders)


# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, render_template, request
# import sqlite3
# from datetime import datetime
# import os

# app = Flask(__name__)

# DB_PATH = os.path.join(os.path.dirname(__file__), "data", "your_database.db")  # update if needed

# def get_db_connection():
#     conn = sqlite3.connect(DB_PATH)
#     conn.row_factory = sqlite3.Row
#     return conn

# @app.route('/')
# def search_users():
#     query = request.args.get('q', '')
#     conn = get_db_connection()

#     if query:
#         users = conn.execute(
#             "SELECT id, first_name, last_name, email, city, state FROM users "
#             "WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?",
#             (f"%{query}%", f"%{query}%", f"%{query}%")
#         ).fetchall()
#     else:
#         users = []

#     conn.close()
#     return render_template('users.html', query=query, users=users)


# @app.route('/user/<int:user_id>')
# def view_user_orders(user_id):
#     conn = get_db_connection()
#     user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
#     orders = conn.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,)).fetchall()
#     conn.close()

#     # Format dates before sending to template
#     formatted_orders = []
#     for order in orders:
#         created_at = order['created_at']
#         try:
#             dt = datetime.fromisoformat(created_at)
#             created_at_str = dt.strftime('%Y-%m-%d')
#         except:
#             created_at_str = created_at  # leave as-is if parsing fails

#         formatted_orders.append({
#             **order,
#             'created_at': created_at_str
#         })

#     return render_template('user.html', user=user, orders=formatted_orders)


# if __name__ == '__main__':
#     app.run(debug=True)
