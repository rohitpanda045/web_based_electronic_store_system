from flask import request, jsonify, session, Response
from ai_controller import (
    run_agent,
    generate_jwt,
    verify_jwt,
    handle_whatsapp_webhook,
    notify_order_status_change,
)
import mysql.connector
from mysql.connector import Error
import os

# Store web chat conversations in memory
_web_sessions = {}


def register_ai_routes(app):
    """Register all AI routes onto the Flask app"""

    # ── 1. Get JWT Token ──────────────────────────────────────────────────────
    @app.route("/api/auth/token", methods=["POST"])
    def api_get_token():
        """Give logged in user a JWT token for WhatsApp authentication"""
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Not logged in"}), 401
        token = generate_jwt(str(session["user_id"]))
        return jsonify({"success": True, "token": token}), 200

    # ── 2. Website Chat ───────────────────────────────────────────────────────
    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        """Main chat endpoint for website widget"""
        data = request.get_json(silent=True) or {}
        user_message = (data.get("message") or "").strip()

        if not user_message:
            return jsonify({"success": False, "message": "Empty message"}), 400

        # Check if user is logged in
        verified_user_id = None
        if "user_id" in session:
            verified_user_id = str(session["user_id"])

        # Check for Bearer token
        if not verified_user_id:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
                verified_user_id = verify_jwt(token)

        # Get conversation history
        conv_id = data.get("conversation_id") or (
            f"user_{verified_user_id}" if verified_user_id else "anonymous"
        )
        history = _web_sessions.get(conv_id, [])

        # Run AI agent
        try:
            reply = run_agent(
                user_message=user_message,
                conversation_history=history,
                verified_user_id=verified_user_id,
            )
        except Exception as e:
            app.logger.error(f"[AI Agent Error]: {e}")
            return jsonify({
                "success": False,
                "message": "AI service temporarily unavailable.",
            }), 503

        # Save history
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        _web_sessions[conv_id] = history[-20:]

        return jsonify({
            "success": True,
            "reply": reply,
            "conversation_id": conv_id,
            "authenticated": verified_user_id is not None,
        }), 200

    # ── 3. WhatsApp Webhook ───────────────────────────────────────────────────
    @app.route("/webhook/whatsapp", methods=["POST"])
    def webhook_whatsapp():
        """Receive incoming WhatsApp messages from Twilio"""
        twiml = handle_whatsapp_webhook(request.form)
        return Response(twiml, mimetype="text/xml"), 200

    # ── 4. Update Order Status + Send WhatsApp Notification ──────────────────
    @app.route("/api/orders/update_status", methods=["POST"])
    def api_update_order_status():
        """Admin: update order status and send WhatsApp notification"""
        if "admin_id" not in session:
            return jsonify({"success": False, "message": "Admin not logged in"}), 401

        data = request.get_json(silent=True) or {}
        order_id = data.get("order_id")
        new_status = data.get("status", "").strip()

        VALID_STATUSES = {"Processing", "Shipped", "Delivered", "Cancelled"}
        if not order_id or new_status not in VALID_STATUSES:
            return jsonify({
                "success": False,
                "message": f"Provide order_id and status. Valid: {VALID_STATUSES}",
            }), 400

        # Update database
        db_config = {
            "host":     os.environ.get("DB_HOST", "switchyard.proxy.rlwy.net"),
            "user":     os.environ.get("DB_USER", "root"),
            "password": os.environ.get("DB_PASSWORD", "uxnLFmmHCnLVblKklWKEGxJFrcgqxUcu"),
            "database": os.environ.get("DB_NAME", "railway"),
            "port":     int(os.environ.get("DB_PORT", 26497)),
        }
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE ORDERS SET status = %s WHERE order_id = %s",
                (new_status, order_id),
            )
            conn.commit()
        except Error as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            cur.close()
            conn.close()

        # Send WhatsApp notification
        wa_sent = notify_order_status_change(order_id, new_status)

        return jsonify({
            "success": True,
            "message": f"Order {order_id} updated to '{new_status}'.",
            "whatsapp_notified": wa_sent,
        }), 200