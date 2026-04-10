import os
import json
import jwt
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# ── Twilio Setup ──────────────────────────────────────────────────────────────
twilio_client = TwilioClient(
    os.environ.get("TWILIO_ACCOUNT_SID"),
    os.environ.get("TWILIO_AUTH_TOKEN"),
)
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# ── JWT Setup ─────────────────────────────────────────────────────────────────
JWT_SECRET = os.environ.get("JWT_SECRET", "change_me_in_prod")
JWT_ALGO = "HS256"
JWT_EXPIRY_HOURS = 24

# ── Database Setup ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "switchyard.proxy.rlwy.net"),
    "user":     os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "uxnLFmmHCnLVblKklWKEGxJFrcgqxUcu"),
    "database": os.environ.get("DB_NAME", "railway"),
    "port":     int(os.environ.get("DB_PORT", 26497)),
}

def _db():
    return mysql.connector.connect(**DB_CONFIG)

# ── Gemini Setup ──────────────────────────────────────────────────────────────
import google.generativeai as genai
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ══════════════════════════════════════════════════════════════════════════════
# TOOL FUNCTIONS — these are called by Gemini AI
# ══════════════════════════════════════════════════════════════════════════════

def tool_search_products(query="", category="", max_results=5):
    """Search products from database"""
    conn = _db()
    cur = conn.cursor(dictionary=True)
    try:
        placeholder = "cat_placeholder_%"
        sql = "SELECT product_id, p_name, price, discount, stock, features, warranty, category FROM PRODUCT WHERE p_name NOT LIKE %s"
        params = [placeholder]

        if category:
            sql += " AND category = %s"
            params.append(category)
        if query:
            sql += " AND (p_name LIKE %s OR features LIKE %s)"
            params += [f"%{query}%", f"%{query}%"]

        sql += f" LIMIT {int(max_results)}"
        cur.execute(sql, params)
        products = cur.fetchall()

        for p in products:
            disc = p.get("discount") or 0
            p["effective_price"] = round(p["price"] * (1 - disc / 100), 2)

        return {"products": products, "count": len(products)}
    except Error as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def tool_get_order_status(order_id=None, user_email=None, verified_user_id=None):
    """Get order status from database"""
    if not verified_user_id:
        return {"error": "Please login first to view order details."}

    conn = _db()
    cur = conn.cursor(dictionary=True)
    try:
        if order_id:
            cur.execute("""
                SELECT o.order_id, o.order_date, o.total_amount,
                       u.username, u.email,
                       GROUP_CONCAT(p.p_name SEPARATOR ', ') AS items,
                       IFNULL(o.status, 'Processing') AS status
                FROM ORDERS o
                JOIN USER u ON o.user_id = u.user_id
                LEFT JOIN ORDER_ITEM oi ON oi.order_id = o.order_id
                LEFT JOIN PRODUCT p ON p.product_id = oi.product_id
                WHERE o.order_id = %s AND o.user_id = %s
                GROUP BY o.order_id
            """, (order_id, verified_user_id))
        elif user_email:
            cur.execute("""
                SELECT o.order_id, o.order_date, o.total_amount,
                       u.username, u.email,
                       GROUP_CONCAT(p.p_name SEPARATOR ', ') AS items,
                       IFNULL(o.status, 'Processing') AS status
                FROM ORDERS o
                JOIN USER u ON o.user_id = u.user_id
                LEFT JOIN ORDER_ITEM oi ON oi.order_id = o.order_id
                LEFT JOIN PRODUCT p ON p.product_id = oi.product_id
                WHERE u.email = %s AND o.user_id = %s
                GROUP BY o.order_id
                ORDER BY o.order_date DESC LIMIT 5
            """, (user_email, verified_user_id))
        else:
            return {"error": "Please provide order ID or email."}

        orders = cur.fetchall()
        for o in orders:
            if isinstance(o.get("order_date"), datetime):
                o["order_date"] = o["order_date"].isoformat()
        return {"orders": orders, "count": len(orders)}
    except Error as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def tool_get_categories():
    """Get all product categories"""
    conn = _db()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT DISTINCT category FROM PRODUCT
            WHERE p_name NOT LIKE 'cat_placeholder_%'
            ORDER BY category
        """)
        cats = [r[0] for r in cur.fetchall()]
        return {"categories": cats}
    except Error as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TOOL DISPATCHER
# ══════════════════════════════════════════════════════════════════════════════

def dispatch_tool(name, args, verified_user_id=None):
    if name == "search_products":
        result = tool_search_products(**args)
    elif name == "get_order_status":
        result = tool_get_order_status(**args, verified_user_id=verified_user_id)
    elif name == "get_categories":
        result = tool_get_categories()
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, default=str)


# ══════════════════════════════════════════════════════════════════════════════
# GEMINI AI AGENT
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are Nova, a friendly AI customer support agent for TechMart, an online electronics store.

You can help customers with:
- Product search, prices, stock, features, warranty
- Order status tracking (only for logged in users)
- Product category listing
- Product recommendations based on budget and needs

Rules:
- Always be friendly and use simple language
- Use emojis occasionally to be warm 😊
- Never make up product details — always use the tools
- For order details, always verify the user is authenticated
- End every conversation with: Is there anything else I can help you with? 😊
- Keep replies short and helpful
"""

TOOLS_GEMINI = {
    "function_declarations": [
        {
            "name": "search_products",
            "description": "Search products by keyword or category. Returns price, stock, features, warranty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword to search"},
                    "category": {"type": "string", "description": "Product category"},
                    "max_results": {"type": "integer", "description": "Max results to return"},
                },
            },
        },
        {
            "name": "get_order_status",
            "description": "Get order status for authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "description": "Order ID number"},
                    "user_email": {"type": "string", "description": "User email address"},
                },
            },
        },
        {
            "name": "get_categories",
            "description": "Get all available product categories.",
            "parameters": {"type": "object", "properties": {}},
        },
    ]
}


def run_agent(user_message, conversation_history, verified_user_id=None):
    """Main AI agent function"""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
            tools=[TOOLS_GEMINI],
        )

        gemini_history = []
        for h in conversation_history:
            role = "user" if h["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [h["content"]]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_message)

        for _ in range(5):
            fn_calls = [p for p in response.parts if hasattr(p, "function_call") and p.function_call.name]
            if not fn_calls:
                break

            tool_results = []
            for part in fn_calls:
                fc = part.function_call
                args = dict(fc.args)
                result = dispatch_tool(fc.name, args, verified_user_id)
                tool_results.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fc.name,
                            response={"result": json.loads(result)},
                        )
                    )
                )
            response = chat.send_message(tool_results)

        text_parts = [p.text for p in response.parts if hasattr(p, "text") and p.text]
        return " ".join(text_parts) or "I'm sorry, I could not process your request. Please try again."

    except Exception as e:
        print(f"[AI Agent Error]: {e}")
        return "I'm sorry, I'm having trouble right now. Please try again in a moment."


# ══════════════════════════════════════════════════════════════════════════════
# JWT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def verify_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return str(payload["user_id"])
    except jwt.PyJWTError:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# WHATSAPP FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def send_whatsapp_message(to_number, message):
    """Send WhatsApp message via Twilio"""
    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_number}",
            body=message,
        )
        return True
    except Exception as e:
        print(f"[WhatsApp Error]: {e}")
        return False


def notify_order_status_change(order_id, new_status):
    """Send WhatsApp notification when order status changes"""
    conn = _db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT u.username, u.phone, u.email, o.total_amount
            FROM ORDERS o
            JOIN USER u ON u.user_id = o.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        row = cur.fetchone()

        if not row or not row.get("phone"):
            print(f"[WhatsApp] No phone number found for order {order_id}")
            return False

        status_emoji = {
            "Processing": "⏳",
            "Shipped": "🚚",
            "Delivered": "✅",
            "Cancelled": "❌",
        }.get(new_status, "📦")

        msg = (
            f"Hello {row['username']}! {status_emoji}\n\n"
            f"Your order #{order_id} has been updated!\n"
            f"Status: *{new_status}*\n"
            f"Total: ₹{row['total_amount']}\n\n"
            f"Visit our website for more details.\n"
            f"Thank you for shopping with TechMart! 😊"
        )
        return send_whatsapp_message(row["phone"], msg)
    except Error as e:
        print(f"[WhatsApp DB Error]: {e}")
        return False
    finally:
        cur.close()
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# WHATSAPP WEBHOOK HANDLER
# ══════════════════════════════════════════════════════════════════════════════

_whatsapp_sessions = {}


def handle_whatsapp_webhook(form_data):
    """Handle incoming WhatsApp messages from Twilio"""
    from_number = form_data.get("From", "").replace("whatsapp:", "")
    body = form_data.get("Body", "").strip()

    session = _whatsapp_sessions.setdefault(from_number, {
        "history": [],
        "verified_user_id": None,
        "awaiting_token": False,
    })

    # Auth flow
    if session.get("awaiting_token"):
        user_id = verify_jwt(body)
        if user_id:
            session["verified_user_id"] = user_id
            session["awaiting_token"] = False
            reply = "✅ Identity verified! You can now ask about your orders."
        else:
            reply = "❌ Invalid token. Please try again or type 'help'."
        _whatsapp_sessions[from_number] = session
        return _twiml_reply(reply)

    # Special commands
    if body.lower() in ("login", "auth"):
        session["awaiting_token"] = True
        _whatsapp_sessions[from_number] = session
        return _twiml_reply(
            "To verify your identity, please send your JWT token.\n"
            "Get it from your account page on our website."
        )

    if body.lower() in ("logout", "signout"):
        session["verified_user_id"] = None
        session["history"] = []
        _whatsapp_sessions[from_number] = session
        return _twiml_reply("👋 You have been logged out successfully.")

    if body.lower() == "help":
        return _twiml_reply(
            "👋 Hello! I'm Nova, TechMart's AI assistant!\n\n"
            "I can help you with:\n"
            "🛍️ Product search and prices\n"
            "📦 Order tracking (type 'login' first)\n"
            "📋 Product categories\n"
            "💡 Product recommendations\n\n"
            "Just type your question and I'll help! 😊"
        )

    # Run AI agent
    reply = run_agent(
        user_message=body,
        conversation_history=session["history"],
        verified_user_id=session.get("verified_user_id"),
    )

    session["history"].append({"role": "user", "content": body})
    session["history"].append({"role": "assistant", "content": reply})
    session["history"] = session["history"][-20:]
    _whatsapp_sessions[from_number] = session

    return _twiml_reply(reply)


def _twiml_reply(message):
    """Convert message to TwiML XML format for Twilio"""
    safe = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{safe}</Message>
</Response>"""
def get_smart_recommendations(user_id=None):
    """Get personalized or trending product recommendations"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        if user_id:
            # Recommend based on previous orders or cart items if any
            cursor.execute("""
                SELECT p.* FROM PRODUCT p
                WHERE p.category IN (
                    SELECT DISTINCT p2.category 
                    FROM ORDER_ITEM oi 
                    JOIN PRODUCT p2 ON oi.product_id = p2.product_id
                    JOIN ORDERS o ON oi.order_id = o.order_id
                    WHERE o.user_id = %s
                )
                ORDER BY p.price DESC LIMIT 3
            """, (user_id,))
            recs = cursor.fetchall()
            if recs: return recs

        # Fallback to trending (highest stock/price as proxy for featured)
        cursor.execute("SELECT * FROM PRODUCT ORDER BY price DESC LIMIT 3")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def send_whatsapp_invoice(order_id):
    """Generate and send an invoice via WhatsApp"""
    conn = get_db_connection()
    if not conn: return
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT o.order_id, o.total_amount, u.username, u.user_id
            FROM ORDERS o JOIN USER u ON o.user_id = u.user_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        if not order: return
        
        cursor.execute("""
            SELECT oi.quantity, p.p_name, p.price
            FROM ORDER_ITEM oi JOIN PRODUCT p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        
        # Build message
        msg = f"🧾 *INVOICE: TechMart Electronics*\n\n"
        msg += f"Order ID: {order['order_id']}\n"
        msg += f"Customer: {order['username']}\n"
        msg += f"---------------------------\n"
        for item in items:
            msg += f"• {item['p_name']} x{item['quantity']} - ₹{item['price']}\n"
        msg += f"---------------------------\n"
        msg += f"Total: ₹{order['total_amount']}\n\n"
        msg += "Thank you for shopping with us!"
        
        # In a real app, user phone would be in DB. Using a dummy for now.
        dummy_phone = "whatsapp:+910000000000" 
        send_whatsapp_message(dummy_phone, msg)
        return True
    finally:
        cursor.close()
        conn.close()
