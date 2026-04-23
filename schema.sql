from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from db import get_db_connection
import mysql.connector
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key="AIzaSyAa1lfvYSgMDP4TYYjg9zkuo6RCnhzYKvc") # Ideally use env variable
model = genai.GenerativeModel('models/gemini-2.5-flash')

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Change for production

@app.route('/')
def home():
    if 'user_id' in session and session.get('role') == 'Student':
        return redirect(url_for('menu'))
    elif 'user_id' in session and session.get('role') == 'Parent':
        return redirect(url_for('order_history'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'Student')", (username, password))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            flash(f'Error: {e}')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = role 
            
            if role == 'Parent':
                return redirect(url_for('order_history'))
            else:
                return redirect(url_for('menu'))
        else:
            flash('Invalid credentials')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = request.args.get('q')
    if query:
        cursor.execute("SELECT * FROM menu WHERE name LIKE %s", (f"%{query}%",))
    else:
        cursor.execute("SELECT * FROM menu")
        
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('menu.html', items=items)

@app.route('/cart')
def cart():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('cart.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()
    order_type = data.get('type') # 'Vend Receipt' or 'Place Order'
    cart_items = data.get('items')
    
    if not cart_items:
        return jsonify({'success': False, 'message': 'Cart empty'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Cast to float/int to ensure correct calculation and types
        total = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
        
        cursor.execute("INSERT INTO orders (user_id, total_amount, order_type, status) VALUES (%s, %s, %s, 'Pending')", 
                       (session['user_id'], total, order_type))
        order_id = cursor.lastrowid
        
        for item in cart_items:
            cursor.execute("INSERT INTO order_items (order_id, menu_id, quantity, price) VALUES (%s, %s, %s, %s)",
                           (order_id, item['id'], int(item['quantity']), float(item['price'])))
            
        conn.commit()
        return jsonify({'success': True, 'message': 'Order placed successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/history')
def order_history():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, o.total_amount, o.order_type, o.status, o.created_at,
               GROUP_CONCAT(CONCAT(m.name, ' x', oi.quantity) SEPARATOR ', ') as ordered_items
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN menu m ON oi.menu_id = m.id
        WHERE o.user_id = %s
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (session['user_id'],))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('history.html', orders=orders)

@app.route('/api/history')
def api_history():
    if 'user_id' not in session: 
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, o.total_amount, o.order_type, o.status, o.created_at,
               GROUP_CONCAT(CONCAT(m.name, ' x', oi.quantity) SEPARATOR ', ') as ordered_items
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN menu m ON oi.menu_id = m.id
        WHERE o.user_id = %s
        GROUP BY o.id
        ORDER BY o.created_at DESC
    """, (session['user_id'],))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'orders': orders})

# --- REVIEWS API ---
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reviews ORDER BY created_at DESC")
    reviews = cursor.fetchall()
    conn.close()
    return jsonify({'success': True, 'reviews': reviews})

@app.route('/api/reviews', methods=['POST'])
def add_review():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment')
    
    if not rating or not comment:
         return jsonify({'success': False, 'message': 'Missing data'}), 400
         
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reviews (user_id, username, rating, comment) VALUES (%s, %s, %s, %s)",
                   (session['user_id'], session['username'], rating, comment))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Review added!'})

# --- CHATBOT API ---
@app.route('/api/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'success': False, 'message': 'No message provided'}), 400

    # Fetch menu items for context
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Corrected columns based on schema
    cursor.execute("SELECT name, price, description, health, calories, protein, carbs, fats FROM menu")
    menu_items = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # improved context building
    menu_context = "Current Menu (with Nutritional Info):\n"
    for item in menu_items:
        desc = item.get('description', 'No description')
        health = item.get('health', 'N/A')
        cals = item.get('calories', 'N/A')
        prot = item.get('protein', 'N/A')
        carb = item.get('carbs', 'N/A')
        fat = item.get('fats', 'N/A')
        
        menu_context += f"- {item['name']} (₹{item['price']}): {desc} | Health: {health} | Calories: {cals} | Protein: {prot} | Carbs: {carb} | Fats: {fat}\n"

    system_prompt = f"""
    You are a helpful AI assistant for the 'Cafeteria Compass' canteen app.
    Your goal is to help students and parents with ordering food, checking the menu, and answering questions about the canteen.
    
    {menu_context}
    
    Rules:
    1. Suggest combinations of items that fit within the budget (if provided).
    2. Suggest a mix of healthy (green) and tasty (red/amber) options if possible.
    3. Calculate a "Health Score" for your suggested plan on a scale of 1-10 (10 being very healthy).
    4. Be conversational and encouraging.
    5. If the budget is very low, suggest the most affordable filling options.
    6. CRITICAL: When suggesting specific items or meals, YOU MUST DISPLAY their nutritional info (Calories, Protein, Carbs, Fats).
    7. For weekly plans, provide a daily or total weekly estimate of these values.
    8. STRICT RULE: You must ONLY suggest items that are listed in the "Here is the menu" section above. Do NOT suggest generic items (e.g. "Fruit Salad" unless it is in the menu) or items not available.
    9. WEEKLY SCORE: If providing a weekly plan, you MUST display a specific "Weekly Health Score: X/10" at the very end of your response, based on the overall balance of the suggested meals.
    
    FORMATTING RULES:
    - Use bullet points (•) for lists.
    - Use clear line breaks between options or days.
    - Do NOT output large blocks of text.
    - Do NOT use asterisks (*) or markdown bolding (**text**). Use plain text or caps for emphasis.
    - Example Format:
    • Item Name (₹Price)
        - Calories: ...
        - Protein: ...
    
    User: {user_message}
    """
    
    try:
        response = model.generate_content(system_prompt)
        return jsonify({'success': True, 'reply': response.text})
    except Exception as e:
        print(f"Gemini Error: {e}")
        return jsonify({'success': False, 'message': 'AI is currently unavailable.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
