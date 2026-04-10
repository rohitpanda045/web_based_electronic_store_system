from flask import Blueprint, request, jsonify
from extensions import db
from models import Product

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chatbot', methods=['POST'])
def chatbot():
    import urllib.request
    import json
    
    data = request.get_json()
    user_message = data.get('message', '').lower().strip()
    
    if not user_message:
        return jsonify({'success': True, 'response': 'Please ask me something!'}), 200
        
    try:
        import os
        api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyC00mW6wb_oGuht1mD8ln3SA6S1OPeQZGo")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        products = Product.query.all()
        product_info = ""
        for p in products:
            product_info += f"{p.p_name} - ₹{p.price}. Category: {p.category}. Features: {p.features}. Warranty: {p.warranty}\\n"
            
        prompt = f"You are a helpful AI assistant for TechMart, an online electronic store. Help customers choose products, explain specifications, prices, and offers. Be friendly and professional.\\n\\nCRITICAL RULES FOR YOUR RESPONSES:\\n1. ALWAYS provide your answers in a concise format.\\n2. NEVER write long, lengthy paragraphs. Keep it short and scannable.\\n3. DO NOT use asterisks (**) for bolding or any other purpose. Use plain text or other markers if needed.\\n4. Provide step-by-step or bulleted lists WITHOUT using asterisks as bullets.\\n\\nAvailable products in our store:\\n{product_info}\\n\\nCustomer message: {user_message}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        ai_response = result['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify({'success': True, 'response': ai_response}), 200
    except Exception as e:
        print(f"Chatbot API error: {e}")
        # Local fallback logic parsing the user message
        msg = user_message.lower()
        if 'hello' in msg or 'hi ' in msg or msg == 'hi':
            return jsonify({'success': True, 'response': 'Hello! I am your TechMart assistant. How can I help you today?'}), 200
        
        products = Product.query.all()
        
        if 'price' in msg or 'cost' in msg:
            for p in products:
                # Check if any main word from product name is in the user's message
                name_words = p.p_name.lower().split()
                if any(word in msg for word in name_words if len(word) > 2) or p.category.lower() in msg:
                    return jsonify({'success': True, 'response': f'The price of {p.p_name} is ₹{p.price}. (Discount: {p.discount}%)'}), 200
            return jsonify({'success': True, 'response': 'Please specify which product you want the price for (e.g. iPhone, Samsung, MacBook).'}), 200
            
        elif 'warranty' in msg:
            for p in products:
                name_words = p.p_name.lower().split()
                if any(word in msg for word in name_words if len(word) > 2) or p.category.lower() in msg:
                    return jsonify({'success': True, 'response': f'The {p.p_name} comes with a {p.warranty}.'}), 200
            return jsonify({'success': True, 'response': 'Please specify which product you need warranty details for.'}), 200
            
        elif 'features' in msg or 'specs' in msg or 'what is' in msg:
            for p in products:
                name_words = p.p_name.lower().split()
                if any(word in msg for word in name_words if len(word) > 2) or p.category.lower() in msg:
                    return jsonify({'success': True, 'response': f'Features of {p.p_name}: {p.features}.'}), 200
            return jsonify({'success': True, 'response': 'Please specify which product you need features for.'}), 200
            
        elif 'products' in msg or 'buy' in msg or 'have' in msg:
            return jsonify({'success': True, 'response': 'We currently have Smartphones, Laptops, Tablets, and Accessories. Please browse our Products page to see the catalog!'}), 200
            
        # Catch just the product name being mentioned without a specific intent
        for p in products:
            name_words = p.p_name.lower().split()
            if any(word in msg for word in name_words if len(word) > 2) or p.category.lower() in msg:
                return jsonify({'success': True, 'response': f'{p.p_name} is available for ₹{p.price}. Features include: {p.features}. Warranty: {p.warranty}.'}), 200

        return jsonify({'success': True, 'response': 'I am currently operating in offline mode. I can answer questions about Prices, Features, and Warranties. Try asking "What is the price of iPhone?" or "What are the features of MacBook?"'}), 200
