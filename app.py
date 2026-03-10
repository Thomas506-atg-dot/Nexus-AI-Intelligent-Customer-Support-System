"""
AI Customer Service Bot - PREMIUM EDITION
Modern, Animated, Professional UI
Final Year Project - Intelligent Customer Support System
"""

import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import time
import hashlib

# Import custom modules
from database import (
    save_conversation, get_all_conversations, get_escalated_conversations,
    get_analytics, init_sample_orders, get_order_status
)
from sentiment_analyzer import analyzer
from escalation import escalation_manager
from animations import (
    load_css_animations, render_typing_indicator, render_severity_badge,
    render_metric_card, render_glass_card
)

load_dotenv()

# ============== AUTHENTICATION SYSTEM ==============

# Simple admin credentials (in production, use database)
ADMIN_CREDENTIALS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "manager": hashlib.sha256("manager456".encode()).hexdigest()
}

def hash_password(password):
    """Hash password for secure comparison"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_admin_auth():
    """Check if admin is authenticated"""
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
        st.session_state.admin_username = None
    
    return st.session_state.admin_logged_in

def login_admin(username, password):
    """Authenticate admin"""
    if username in ADMIN_CREDENTIALS:
        if hash_password(password) == ADMIN_CREDENTIALS[username]:
            st.session_state.admin_logged_in = True
            st.session_state.admin_username = username
            return True
    return False

def logout_admin():
    """Logout admin"""
    st.session_state.admin_logged_in = False
    st.session_state.admin_username = None

def show_login_form():
    """Display admin login form"""
    st.markdown("""
    <div style="max-width: 400px; margin: 0 auto; padding: 2rem; 
                background: rgba(255,255,255,0.05); border-radius: 20px; 
                border: 1px solid rgba(255,255,255,0.1);">
        <h2 style="text-align: center; color: white; margin-bottom: 2rem;">🔐 Admin Login</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("admin_login"):
        username = st.text_input("Username", placeholder="Enter admin username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            if login_admin(username, password):
                st.success("✅ Login successful!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: rgba(255,255,255,0.5);">
        <p>Default credentials:</p>
        <p>Username: <b>admin</b> | Password: <b>admin123</b></p>
        <p>Username: <b>manager</b> | Password: <b>manager456</b></p>
    </div>
    """, unsafe_allow_html=True)

# ============== PAGE CONFIG ==============

st.set_page_config(
    page_title="Nexus AI | Intelligent Customer Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css_animations()

# Customer Service System Prompt
CUSTOMER_SERVICE_PROMPT = """You are Nexus AI, an elite Customer Service Assistant for a premium e-commerce platform.

Your capabilities:
• Process orders, tracking, returns instantly
• Detect customer emotions and respond empathetically  
• Escalate complex issues to human specialists
• Maintain professional, solution-oriented tone

Guidelines:
- Always acknowledge customer emotions before solving
- For complaints: Apologize sincerely, offer concrete solutions
- Be concise but thorough
- Never fabricate order information
"""

init_sample_orders()

# ============== FUNCTIONS ==============

def get_groq_client():
    from groq import Groq
    import streamlit as st

    api_key = st.secrets["GROQ_API_KEY"]
    return Groq(api_key=api_key)

def process_message(customer_id, message, client):
    analysis = analyzer.analyze(message)
    
    order_info = None
    if analysis['intent'] == 'ORDER':
        import re
        order_match = re.search(r'ORD-\d+', message.upper())
        if order_match:
            order_info = get_order_status(order_match.group(), customer_id)
    
    should_escalate = analyzer.should_escalate(analysis)
    
    if should_escalate:
        ticket_id, response = escalation_manager.escalate(customer_id, message, analysis)
        save_conversation(customer_id, message, response, analysis['label'], 
                         analysis['severity'], analysis['intent'], True, ticket_id)
        return response, analysis, True
    
    system_msg = CUSTOMER_SERVICE_PROMPT
    if order_info:
        system_msg += f"\n\nOrder Context: {order_info}"
    
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": message}
    ]
    
    response_text = ""
    stream = client.chat.completions.create(
      import streamlit as st

# Get the model from secrets (or default)
model = st.secrets.get("GROQ_MODEL", "llama-3.3-70b-versatile")

response_text = ""
stream = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0.7,
    max_tokens=1024,
    stream=True
)
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content
    
    save_conversation(customer_id, message, response_text, analysis['label'],
                     analysis['severity'], analysis['intent'], False)
    
    return response_text, analysis, False

# ============== SIDEBAR NAVIGATION ==============

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</div>
        <h2 style="color: #333; margin: 0; font-weight: 700;">NEXUS AI</h2>
        <p style="color: rgba(0,0,0,0.6); font-size: 0.9rem;">Intelligent Support</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mode selection
    user_mode = st.radio("Select Mode", ["🧑‍💼 Customer", "🔐 Admin"], key="user_mode")
    
    is_admin_mode = (user_mode == "🔐 Admin")
    
    # If admin mode, check authentication
    if is_admin_mode:
        if not check_admin_auth():
            st.warning("Please login to access admin panel")
            page = "login"
        else:
            st.success(f"Welcome, {st.session_state.admin_username}!")
            if st.button("🚪 Logout", use_container_width=True):
                logout_admin()
                st.rerun()
            
            page = st.radio("Admin Panel", [
                "📊 Command Center", 
                "🚨 Priority Queue",
                "📋 Conversation Log",
                "💬 Live Support (Test)"
            ])
    else:
        # Customer mode - only chat
        page = "💬 Live Support"
        st.info("👋 Welcome! How can we help you today?")
    
    st.markdown("---")
    
    # System status
    status_color = "#27ae60" if check_admin_auth() or not is_admin_mode else "#e74c3c"
    status_text = "Admin Online" if check_admin_auth() else "System Online"
    
    st.markdown(f"""
    <div style="background: rgba(39, 174, 96, 0.1); border: 1px solid rgba(39, 174, 96, 0.3); 
                border-radius: 12px; padding: 1rem; text-align: center;">
        <span style="color: {status_color}; font-weight: 600;">● {status_text}</span>
        <p style="color: rgba(0,0,0,0.5); font-size: 0.8rem; margin: 0.5rem 0 0 0;">
            All services operational
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============== MAIN CONTENT ==============

# Show login form if admin mode but not logged in
if is_admin_mode and not check_admin_auth():
    show_login_form()
    st.stop()

# ============== CUSTOMER CHAT PAGE ==============

if page == "💬 Live Support" or page == "💬 Live Support (Test)":
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 class="animated-header float">Nexus AI Support</h1>
        <p style="color: rgba(255,255,255,0.6); font-size: 1.1rem; margin-top: 1rem;">
            Experience the future of customer service with emotional intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Customer ID
    if 'customer_id' not in st.session_state:
        st.session_state.customer_id = f"CUST-{datetime.now().strftime('%H%M%S')}"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        customer_id = st.text_input("Customer ID", value=st.session_state.customer_id, 
                                   key="cust_id", label_visibility="collapsed",
                                   placeholder="Enter Customer ID...")
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display messages
    for i, msg in enumerate(st.session_state.chat_history):
        with st.chat_message(msg['role'], avatar="🧑‍💼" if msg['role'] == 'user' else "🤖"):
            st.markdown(f'<div class="chat-message-enter" style="animation-delay: {i*0.1}s">', 
                       unsafe_allow_html=True)
            st.markdown(msg['content'])
            
            if msg['role'] == 'assistant' and 'analysis' in msg:
                cols = st.columns([1, 1, 1, 2])
                with cols[0]:
                    sentiment = msg['analysis']['label']
                    emoji = "😊" if sentiment == "POSITIVE" else "😠" if sentiment == "NEGATIVE" else "😐"
                    st.markdown(f"<span style='color: rgba(255,255,255,0.7);'>{emoji} {sentiment}</span>", 
                               unsafe_allow_html=True)
                with cols[1]:
                    render_severity_badge(msg['analysis']['severity'])
                with cols[2]:
                    st.markdown(f"<span style='color: rgba(255,255,255,0.7); font-size: 0.85rem;'>"
                               f"🎯 {msg['analysis']['intent']}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input
    client = get_groq_client()
    if client:
        if prompt := st.chat_input("How can Nexus AI assist you today?", key="chat_input"):
            st.session_state.chat_history.append({'role': 'user', 'content': prompt})
            
            with st.chat_message('user', avatar="🧑‍💼"):
                st.markdown(prompt)
            
            with st.chat_message('assistant', avatar="🤖"):
                typing_placeholder = st.empty()
                with typing_placeholder:
                    render_typing_indicator()
                
                time.sleep(0.5)
                response, analysis, escalated = process_message(customer_id, prompt, client)
                
                typing_placeholder.empty()
                
                if escalated:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(231, 76, 60, 0.2), rgba(192, 57, 43, 0.3));
                                border: 1px solid rgba(231, 76, 60, 0.5);
                                border-radius: 16px; padding: 1.5rem;
                                animation: pulse 2s infinite;">
                        <h3 style="color: #e74c3c; margin: 0 0 1rem 0;">🚨 Priority Escalation</h3>
                        <p style="color: white; margin: 0; line-height: 1.6;">{response}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(response)
                
                cols = st.columns([1, 1, 1, 2])
                with cols[0]:
                    sentiment = analysis['label']
                    emoji = "😊" if sentiment == "POSITIVE" else "😠" if sentiment == "NEGATIVE" else "😐"
                    st.markdown(f"<span style='color: rgba(255,255,255,0.7);'>{emoji} {sentiment}</span>", 
                               unsafe_allow_html=True)
                with cols[1]:
                    render_severity_badge(analysis['severity'])
                with cols[2]:
                    st.markdown(f"<span style='color: rgba(255,255,255,0.7); font-size: 0.85rem;'>"
                               f"🎯 {analysis['intent']}</span>", unsafe_allow_html=True)
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'analysis': analysis,
                    'escalated': escalated
                })

# ============== ADMIN PAGES ==============

elif page == "📊 Command Center":
    st.markdown('<h1 class="animated-header">📊 Command Center</h1>', unsafe_allow_html=True)
    
    metrics = get_analytics()
    
    # Metrics row
    cols = st.columns(4)
    metric_data = [
        (metrics['total_chats'], "Total Conversations", "💬"),
        (metrics['escalated'], "Escalated Issues", "🚨"),
        (f"{metrics['escalation_rate']:.1f}%", "Escalation Rate", "📈"),
        (f"{metrics['avg_severity']}/10", "Avg Severity", "⚡")
    ]
    
    for col, (val, label, icon) in zip(cols, metric_data):
        with col:
            render_metric_card(val, label, icon)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Sentiment Distribution")
        if metrics['sentiment_distribution']:
            import plotly.express as px
            colors = ['#27ae60', '#e74c3c', '#f39c12']
            fig = px.pie(
                values=list(metrics['sentiment_distribution'].values()),
                names=list(metrics['sentiment_distribution'].keys()),
                hole=0.6,
                color_discrete_sequence=colors
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1)
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Recent Activity")
        recent = get_all_conversations().tail(5)
        if not recent.empty:
            for _, row in recent.iterrows():
                emoji = "😊" if row['sentiment'] == 'POSITIVE' else "😠" if row['sentiment'] == 'NEGATIVE' else "😐"
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border-radius: 12px; 
                            padding: 1rem; margin-bottom: 0.5rem; border-left: 4px solid {'#e74c3c' if row['escalated'] else '#27ae60'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: white; font-weight: 500;">{emoji} {row['customer_id']}</span>
                        <span style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">{row['timestamp']}</span>
                    </div>
                    <p style="color: rgba(255,255,255,0.7); margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                        {row['message'][:50]}...
                    </p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "🚨 Priority Queue":
    st.markdown('<h1 class="animated-header">🚨 Priority Queue</h1>', unsafe_allow_html=True)
    
    escalated = get_escalated_conversations()
    
    if escalated.empty:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">✅</div>
            <h3 style="color: white; margin: 0;">No Escalations</h3>
            <p style="color: rgba(255,255,255,0.6);">All customers are being handled smoothly</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for _, row in escalated.iterrows():
            with st.expander(f"🚨 Ticket {row['ticket_id']} | {row['customer_id']} | Severity {row['severity']}/10"):
                st.markdown(f"""
                <div style="background: rgba(231, 76, 60, 0.1); border-radius: 16px; padding: 1.5rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                        <div>
                            <p style="color: rgba(255,255,255,0.5); margin: 0; font-size: 0.85rem;">Timestamp</p>
                            <p style="color: white; margin: 0.25rem 0 0 0; font-weight: 500;">{row['timestamp']}</p>
                        </div>
                        <div>
                            <p style="color: rgba(255,255,255,0.5); margin: 0; font-size: 0.85rem;">Intent</p>
                            <p style="color: white; margin: 0.25rem 0 0 0; font-weight: 500;">{row['intent']}</p>
                        </div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <p style="color: rgba(255,255,255,0.5); margin: 0; font-size: 0.85rem;">Customer Message</p>
                        <p style="color: white; margin: 0.5rem 0 0 0; padding: 1rem; 
                                  background: rgba(0,0,0,0.3); border-radius: 8px;">{row['message']}</p>
                    </div>
                    <div>
                        <p style="color: rgba(255,255,255,0.5); margin: 0; font-size: 0.85rem;">AI Response</p>
                        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;">{row['response']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif page == "📋 Conversation Log":
    st.markdown('<h1 class="animated-header">📋 Conversation Log</h1>', unsafe_allow_html=True)
    
    df = get_all_conversations()
    
    if not df.empty:
        # Filters
        st.markdown('<div class="glass-card" style="margin-bottom: 1rem;">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_filter = st.selectbox("Sentiment", ["All"] + list(df['sentiment'].unique()))
        with col2:
            intent_filter = st.selectbox("Intent", ["All"] + list(df['intent'].unique()))
        with col3:
            escalated_filter = st.selectbox("Status", ["All", "Escalated", "Resolved"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters
        filtered = df
        if sentiment_filter != "All":
            filtered = filtered[filtered['sentiment'] == sentiment_filter]
        if intent_filter != "All":
            filtered = filtered[filtered['intent'] == intent_filter]
        if escalated_filter == "Escalated":
            filtered = filtered[filtered['escalated'] == True]
        elif escalated_filter == "Resolved":
            filtered = filtered[filtered['escalated'] == False]
        
        # Styled dataframe
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(
            filtered[['timestamp', 'customer_id', 'sentiment', 'severity', 'intent', 'escalated', 'message']],
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export
        csv = filtered.to_csv(index=False)
        st.download_button(
            "📥 Export Data",
            csv,
            "nexus_conversations.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.info("No conversations recorded yet")
