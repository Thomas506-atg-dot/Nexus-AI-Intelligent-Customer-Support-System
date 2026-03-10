"""
AI Customer Service Bot - PREMIUM EDITION
Final Year Project - Intelligent Customer Support System
"""

import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import time
import hashlib

# ============== PAGE CONFIG ==============

st.set_page_config(
    page_title="Nexus AI | Intelligent Customer Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'customer_id' not in st.session_state:
    st.session_state.customer_id = f"CUST-{datetime.now().strftime('%H%M%S')}"

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
    st.session_state.admin_username = None

# ============== CUSTOM MODULES ==============

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

load_css_animations()
init_sample_orders()

# ============== AUTHENTICATION ==============

ADMIN_CREDENTIALS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "manager": hashlib.sha256("manager456".encode()).hexdigest()
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_admin_auth():
    return st.session_state.admin_logged_in

def login_admin(username, password):
    if username in ADMIN_CREDENTIALS:
        if hash_password(password) == ADMIN_CREDENTIALS[username]:
            st.session_state.admin_logged_in = True
            st.session_state.admin_username = username
            return True
    return False

def logout_admin():
    st.session_state.admin_logged_in = False
    st.session_state.admin_username = None

def show_login_form():
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
    </div>
    """, unsafe_allow_html=True)

# ============== AI CLIENT ==============

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

@st.cache_resource
def get_groq_client():
    """Get Groq client - works locally AND on Streamlit Cloud"""
    try:
        from groq import Groq
        
        api_key = None
        
        # Try Streamlit Cloud Secrets first
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except:
            pass
        
        # Fallback to local .env file
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            return None
        
        # Clean the key
        api_key = api_key.strip().strip('"').strip("'")
        
        return Groq(api_key=api_key)
        
    except Exception:
        return None

def process_message(customer_id, message, client):
    """Process message with AI"""
    if client is None:
        return "⚠️ AI service not available. Please configure GROQ_API_KEY.", {'label': 'NEUTRAL', 'severity': 5, 'intent': 'GENERAL'}, False
    
    try:
        analysis = analyzer.analyze(message)
        
        # Check escalation
        if analyzer.should_escalate(analysis):
            ticket_id, response = escalation_manager.escalate(customer_id, message, analysis)
            save_conversation(customer_id, message, response, analysis['label'], 
                             analysis['severity'], analysis['intent'], True, ticket_id)
            return response, analysis, True
        
        # Prepare messages
        system_msg = CUSTOMER_SERVICE_PROMPT
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": message}
        ]
        
        # Call Groq API
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
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
        
    except Exception as e:
        error_msg = f"I apologize, but I'm having trouble right now. ({str(e)})"
        return error_msg, {'label': 'NEUTRAL', 'severity': 5, 'intent': 'GENERAL'}, False

# ============== SIDEBAR ==============

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</div>
        <h2 style="color: #333; margin: 0; font-weight: 700;">NEXUS AI</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    user_mode = st.radio("Select Mode", ["🧑‍💼 Customer", "🔐 Admin"], key="user_mode")
    is_admin_mode = (user_mode == "🔐 Admin")
    
    if is_admin_mode:
        if not check_admin_auth():
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
        page = "💬 Live Support"
    
    # Status indicator
    client = get_groq_client()
    if client:
        st.success("✅ AI Online")
    else:
        st.error("❌ AI Offline - Check API Key")

# ============== MAIN PAGES ==============

if is_admin_mode and not check_admin_auth():
    show_login_form()
    st.stop()

if page == "💬 Live Support" or page == "💬 Live Support (Test)":
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 class="animated-header">Nexus AI Support</h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        customer_id = st.text_input("Customer ID", value=st.session_state.customer_id, 
                                   key="cust_id", label_visibility="collapsed")
    
    # Chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg['role'], avatar="🧑‍💼" if msg['role'] == 'user' else "🤖"):
            st.markdown(msg['content'])
            if msg['role'] == 'assistant' and 'analysis' in msg:
                cols = st.columns([1, 1, 1, 2])
                with cols[0]:
                    sentiment = msg['analysis']['label']
                    emoji = "😊" if sentiment == "POSITIVE" else "😠" if sentiment == "NEGATIVE" else "😐"
                    st.markdown(f"{emoji} {sentiment}")
                with cols[1]:
                    render_severity_badge(msg['analysis']['severity'])
    
    # Input
    if client := get_groq_client():
        if prompt := st.chat_input("How can Nexus AI assist you today?"):
            st.session_state.chat_history.append({'role': 'user', 'content': prompt})
            
            with st.chat_message('user', avatar="🧑‍💼"):
                st.markdown(prompt)
            
            with st.chat_message('assistant', avatar="🤖"):
                with st.spinner("🤖 Nexus AI is typing..."):
                    response, analysis, escalated = process_message(customer_id, prompt, client)
                
                if escalated:
                    st.error("🚨 Priority Escalation")
                st.markdown(response)
                
                cols = st.columns([1, 1, 1, 2])
                with cols[0]:
                    sentiment = analysis['label']
                    emoji = "😊" if sentiment == "POSITIVE" else "😠" if sentiment == "NEGATIVE" else "😐"
                    st.markdown(f"{emoji} {sentiment}")
                with cols[1]:
                    render_severity_badge(analysis['severity'])
                
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'analysis': analysis,
                    'escalated': escalated
                })
    else:
        st.error("⚠️ Cannot connect to AI service")
        st.info("1. Get API key from console.groq.com")
        st.info("2. Add to Streamlit Cloud: Settings → Secrets → GROQ_API_KEY")

elif page == "📊 Command Center":
    st.markdown('<h1 class="animated-header">📊 Command Center</h1>', unsafe_allow_html=True)
    
    metrics = get_analytics()
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("Sentiment Distribution")
        if metrics['sentiment_distribution']:
            try:
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
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.info("Install plotly for charts")
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
                            padding: 1rem; margin-bottom: 0.5rem; 
                            border-left: 4px solid {'#e74c3c' if row['escalated'] else '#27ae60'};">
                    <span style="color: white;">{emoji} {row['customer_id']}</span>
                    <p style="color: rgba(255,255,255,0.7); margin: 0.5rem 0 0 0;">
                        {str(row['message'])[:50]}...
                    </p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "🚨 Priority Queue":
    st.markdown('<h1 class="animated-header">🚨 Priority Queue</h1>', unsafe_allow_html=True)
    
    escalated = get_escalated_conversations()
    
    if escalated.empty:
        st.success("✅ No escalations - all customers handled smoothly")
    else:
        for _, row in escalated.iterrows():
            with st.expander(f"🚨 Ticket {row['ticket_id']} | {row['customer_id']} | Severity {row['severity']}/10"):
                st.markdown(f"""
                <div style="background: rgba(231, 76, 60, 0.1); border-radius: 16px; padding: 1.5rem;">
                    <p style="color: white;"><b>Message:</b> {row['message']}</p>
                    <p style="color: rgba(255,255,255,0.8);"><b>Response:</b> {row['response']}</p>
                </div>
                """, unsafe_allow_html=True)

elif page == "📋 Conversation Log":
    st.markdown('<h1 class="animated-header">📋 Conversation Log</h1>', unsafe_allow_html=True)
    
    df = get_all_conversations()
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_filter = st.selectbox("Sentiment", ["All"] + list(df['sentiment'].unique()))
        with col2:
            intent_filter = st.selectbox("Intent", ["All"] + list(df['intent'].unique()))
        with col3:
            escalated_filter = st.selectbox("Status", ["All", "Escalated", "Resolved"])
        
        filtered = df
        if sentiment_filter != "All":
            filtered = filtered[filtered['sentiment'] == sentiment_filter]
        if intent_filter != "All":
            filtered = filtered[filtered['intent'] == intent_filter]
        if escalated_filter == "Escalated":
            filtered = filtered[filtered['escalated'] == True]
        elif escalated_filter == "Resolved":
            filtered = filtered[filtered['escalated'] == False]
        
        st.dataframe(
            filtered[['timestamp', 'customer_id', 'sentiment', 'severity', 'intent', 'escalated', 'message']],
            use_container_width=True,
            hide_index=True
        )
        
        csv = filtered.to_csv(index=False)
        st.download_button("📥 Export Data", csv, "nexus_conversations.csv", "text/csv")
    else:
        st.info("No conversations recorded yet")
