const ChatbotWidget = {
    messages: [],
    isOpen: false,

    init() {
        this.injectHTML();
        this.cacheDOM();
        this.bindEvents();
    },

    injectHTML() {
        const widgetHTML = `
            <div id="adminChatbotToggle" class="chatbot-toggle" style="bottom: 20px; right: 20px; z-index: 10000; display: flex; align-items: center; justify-content: center; width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #0066cc 0%, #0099ff 100%); color: white; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.5); position: fixed; font-size: 24px;">
                💬
            </div>
            <div id="adminChatbot" class="chatbot" style="width: 350px; height: 500px; bottom: 90px; right: 20px; z-index: 10000; border-radius: 12px; display: none; flex-direction: column; background: #1a1f3a; border: 1px solid #2a3f5f; position: fixed; box-shadow: 0 4px 20px rgba(0,0,0,0.5); overflow: hidden;">
                <div class="chatbot-header" style="background: linear-gradient(135deg, #0066cc 0%, #0099ff 100%); color: white; padding: 15px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 20px;">🤖</span>
                        <div>
                            <div style="font-weight: bold; font-size: 16px;">TechMart Assistant</div>
                            <div style="font-size: 12px; opacity: 0.8;">Online</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 5px;">
                        <a href="https://wa.me/7978685519?text=Hi%20TechMart%20Support," target="_blank" title="Chat on WhatsApp" style="background: #25D366; color: white; text-decoration: none; font-size: 13px; font-weight: 600; padding: 6px 12px; border-radius: 20px; display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 10px rgba(37,211,102,0.3);">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg"><path d="M17.498 14.382c-.301-.15-1.767-.867-2.04-.966-.273-.101-.473-.15-.673.15-.197.295-.771.964-.944 1.162-.175.195-.349.21-.646.06-.301-.151-1.258-.46-2.396-1.474-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>
                            Let's connect on WhatsApp
                        </a>
                        <button id="adminChatbotClose" style="background: none; border: none; color: white; cursor: pointer; font-size: 18px; padding: 5px;">✖</button>
                    </div>
                </div>
                
                <div id="adminChatbotBody" class="chatbot-body" style="flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 12px; background: #0f1419;">
                </div>
                
                <div id="adminChatbotTyping" style="display: none; padding: 10px 15px; background: #0f1419; color: #4a9eff; font-size: 13px; font-style: italic;">
                    Assistant is typing <span class="typing-dots">...</span>
                </div>

                <div class="chatbot-input" style="display: flex; gap: 10px; padding: 15px; border-top: 1px solid #2a3f5f; background: #1a1f3a;">
                    <input type="text" id="adminChatbotInput" placeholder="Ask about products..." style="flex: 1; padding: 10px 15px; border-radius: 20px; border: 1px solid #2a3f5f; background: #0f1419; color: white; outline: none;">
                    <button id="adminChatbotSend" style="padding: 10px 20px; border-radius: 20px; background: linear-gradient(135deg, #0066cc 0%, #0099ff 100%); color: white; border: none; cursor: pointer; font-weight: bold;">Send</button>
                </div>
            </div>
            <style>
                @keyframes blink { 0% { opacity: 0.2; } 20% { opacity: 1; } 100% { opacity: 0.2; } }
                .typing-dots { display: inline-block; }
                .typing-dots span { animation: blink 1.4s infinite reverse; animation-fill-mode: both; }
                .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
                .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
                
                .msg-bubble { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.4; word-wrap: break-word; }
                .msg-user { background: #0066cc; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
                .msg-bot { background: #2a3f5f; color: white; align-self: flex-start; border-bottom-left-radius: 4px; border: 1px solid #3d5682; }
                
                .suggested-questions { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
                .suggested-btn { background: rgba(0, 102, 204, 0.2); border: 1px solid #0066cc; color: #4a9eff; padding: 8px 12px; border-radius: 15px; font-size: 13px; cursor: pointer; text-align: left; transition: all 0.2s; }
                .suggested-btn:hover { background: #0066cc; color: white; }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    },

    cacheDOM() {
        this.toggleBtn = document.getElementById('adminChatbotToggle');
        this.chatbotWin = document.getElementById('adminChatbot');
        this.closeBtn = document.getElementById('adminChatbotClose');
        this.chatBody = document.getElementById('adminChatbotBody');
        this.chatInput = document.getElementById('adminChatbotInput');
        this.sendBtn = document.getElementById('adminChatbotSend');
        this.typingIndicator = document.getElementById('adminChatbotTyping');

        // Setup typing dots animation content
        this.typingIndicator.querySelector('.typing-dots').innerHTML = '<span>.</span><span>.</span><span>.</span>';
    },

    bindEvents() {
        this.toggleBtn.addEventListener('click', () => this.toggleChat());
        this.closeBtn.addEventListener('click', () => this.closeChat());
        this.sendBtn.addEventListener('click', () => this.handleSend());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSend();
        });
    },

    toggleChat() {
        if (!this.isOpen) {
            this.openChat();
        } else {
            this.closeChat();
        }
    },

    openChat() {
        this.isOpen = true;
        this.chatbotWin.style.display = 'flex';
        this.toggleBtn.style.display = 'none';

        // Reset chat if empty
        if (this.messages.length === 0) {
            this.chatBody.innerHTML = '';
            this.addBotMessage("Hi! 👋 I'm your TechMart assistant. How can I help you today?");
            this.addSuggestions([
                "What products do you sell?",
                "How do I track my order?",
                "What is your return policy?"
            ]);
        }

        setTimeout(() => this.chatInput.focus(), 100);
    },

    closeChat() {
        this.isOpen = false;
        this.chatbotWin.style.display = 'none';
        this.toggleBtn.style.display = 'flex';

        // Clear chat history on close as requested
        this.messages = [];
        this.chatBody.innerHTML = '';
    },

    addMessage(text, isUser) {
        // Save to context
        this.messages.push({ role: isUser ? 'user' : 'assistant', content: text });

        // Keep only last 10 messages for context (5 pairs)
        if (this.messages.length > 10) {
            this.messages = this.messages.slice(-10);
        }

        // Better markdown parsing:
        let formattedText = text
            // 1. Convert **text** to <strong>text</strong>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // 2. Convert bullet points: * or - followed by space
            .replace(/^\s*[\*\-]\s+(.+)$/gm, '<li>$1</li>')
            // 3. Convert numbered lists: 1. followed by space
            .replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>')
            // 4. Wrap lists in <ul>
            .replace(/(<li>.*?<\/li>)/gs, '<ul style="margin: 5px 0 5px 20px; padding: 0;">$1</ul>')
            // 5. Convert remaining newlines to <br>
            .replace(/\n/g, '<br/>');

        const msgDiv = document.createElement('div');
        msgDiv.className = `msg-bubble ${isUser ? 'msg-user' : 'msg-bot'}`;
        msgDiv.innerHTML = formattedText;

        this.chatBody.appendChild(msgDiv);
        this.scrollToBottom();
    },

    addBotMessage(text) {
        this.addMessage(text, false);
    },

    addUserMessage(text) {
        this.addMessage(text, true);
    },

    addSuggestions(questions) {
        const containerDiv = document.createElement('div');
        containerDiv.className = 'suggested-questions';

        questions.forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'suggested-btn';
            btn.textContent = q;
            btn.onclick = () => {
                containerDiv.remove();
                this.chatInput.value = q;
                this.handleSend();
            };
            containerDiv.appendChild(btn);
        });

        this.chatBody.appendChild(containerDiv);
        this.scrollToBottom();
    },

    scrollToBottom() {
        this.chatBody.scrollTop = this.chatBody.scrollHeight;
    },

    async handleSend() {
        const text = this.chatInput.value.trim();
        if (!text) return;

        // Remove any existing suggestion buttons
        const suggestions = this.chatBody.querySelector('.suggested-questions');
        if (suggestions) suggestions.remove();

        this.chatInput.value = '';
        this.addUserMessage(text);

        this.setLoading(true);

        try {
            // Build context string from the last 10 messages but exclude the very last one (which is the current text)
            const previousMessages = this.messages.slice(0, -1);
            let fullMessage = text;

            if (previousMessages.length > 0) {
                const contextString = previousMessages.map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`).join('\\n');
                fullMessage = `Here is the conversation history:\\n${contextString}\\n\\nNow answer this new message from the user based on history:\\n${text}`;
            }

            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                // Send the context-injected message to the existing endpoint
                body: JSON.stringify({ message: fullMessage })
            });

            const data = await response.json();

            if (data.success) {
                this.addBotMessage(data.response);
            } else {
                this.addBotMessage("Sorry, I encountered an error providing a response.");
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.addBotMessage("Sorry, I could not connect to the server. Please try again later.");
        } finally {
            this.setLoading(false);
        }
    },

    setLoading(isLoading) {
        this.chatInput.disabled = isLoading;
        this.sendBtn.disabled = isLoading;
        this.typingIndicator.style.display = isLoading ? 'block' : 'none';
        if (isLoading) {
            this.scrollToBottom();
        } else {
            setTimeout(() => this.chatInput.focus(), 10);
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ChatbotWidget.init());
} else {
    ChatbotWidget.init();
}
