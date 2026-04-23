import mysql.connector
from tabulate import tabulate
import datetime

def view_data():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Arnavganu@007',
            database='canteen_db'
        )
        cursor = conn.cursor()

        def print_clean_table(data, headers):
            """Prints a rounded table without internal row separators."""
            table_str = tabulate(data, headers=headers, tablefmt="rounded_grid")
            clean_lines = [line for line in table_str.split('\n') if not line.startswith('├')]
            print('\n'.join(clean_lines))

        # --- USERS ---
        print("\n=== 👥 USERS ===")
        cursor.execute("SELECT id, username, created_at FROM users")
        users = cursor.fetchall()
        
        users_table = []
        for u in users:
            users_table.append([u[0], f"'{u[1]}'", u[2].strftime('%Y-%m-%d %H:%M:%S')])
            
        print_clean_table(users_table, headers=["id", "username", "created_at"])

        # --- ORDERS ---
        print("\n=== 📦 ORDERS (Simplified) ===")
        query = """
            SELECT 
                o.id,
                u.username,
                m.name,
                oi.price,
                o.created_at,
                o.total_amount
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN users u ON o.user_id = u.id
            JOIN menu m ON oi.menu_id = m.id
            ORDER BY o.created_at DESC, o.id DESC
        """
        cursor.execute(query)
        orders = cursor.fetchall()
        
        orders_table = []
        last_order_id = None
        
        for o in orders:
            # o: (id, username, food_name, item_price, date, order_total)
            current_order_id = o[0]
            
            if current_order_id == last_order_id:
                user = ""
                date_str = ""
                order_total = ""
            else:
                user = f"'{o[1]}'"
                date_str = o[4].strftime("'%d/%m/%Y, %I:%M:%S %p'")
                order_total = f"₹{int(o[5])}"
                last_order_id = current_order_id
            
            food = f"'{o[2]}'"
            price = int(o[3])
            
            orders_table.append([
                user, 
                food, 
                price, 
                date_str, 
                order_total
            ])
            
        print_clean_table(orders_table, headers=["User", "Food Item", "Price", "Date", "Order Total"])

        # --- REVIEWS ---
        print("\n=== ⭐ REVIEWS (Recent) ===")
        cursor.execute("SELECT username, rating, comment FROM reviews ORDER BY created_at DESC LIMIT 20")
        reviews = cursor.fetchall()
        
        reviews_table = []
        for r in reviews:
             rating = "★" * r[1]
             raw_comment = r[2]
             clean_comment_text = raw_comment.encode('ascii', 'ignore').decode('ascii').strip()
             
             trunc_len = 50
             comment = (clean_comment_text[:trunc_len] + '..') if len(clean_comment_text) > trunc_len else clean_comment_text
             
             reviews_table.append([r[0], rating, comment])
             
        print_clean_table(reviews_table, headers=["User", "Rating", "Comment"])

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    view_data()
