import streamlit as st

def load_css_animations():
    """Inject premium CSS animations"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { 
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* White text for main content on dark background */
    .main .stMarkdown p,
    .main .stMarkdown h1,
    .main .stMarkdown h2,
    .main .stMarkdown h3,
    .main .stMarkdown h4,
    .main .stMarkdown h5,
    .main .stMarkdown h6,
    .main .stMarkdown span,
    .main .stMarkdown div,
    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span {
        color: white !important;
    }
    
    /* Dark text for light backgrounds (sidebar, inputs, buttons) */
    .stSidebar .stMarkdown p,
    .stSidebar .stMarkdown div,
    .stSidebar .stRadio label,
    .stSidebar span,
    .stTextInput label,
    .stSelectbox label,
    .stButton button,
    .stTextInput input,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #333333 !important;
    }
    
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    /* Input fields - dark text on light background */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        color: #333333 !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Buttons - dark text */
    .stButton > button {
        color: #333333 !important;
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .animated-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        width: fit-content;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: typingBounce 1.4s ease-in-out infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingBounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }
    
    .severity-low {
        background: rgba(39, 174, 96, 0.2);
        color: #27ae60 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .severity-medium {
        background: rgba(243, 156, 18, 0.2);
        color: #f39c12 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .severity-high {
        background: rgba(231, 76, 60, 0.2);
        color: #e74c3c !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea !important;
    }
    
    .metric-label {
        color: rgba(255,255,255,0.8) !important;
    }
    
    /* Dataframe - dark text on light background */
    .stDataFrame {
        color: #333333 !important;
    }
    
    /* Ensure chat input text is visible */
    .stChatInput input {
        color: #333333 !important;
        background: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_typing_indicator():
    """Render animated typing indicator"""
    st.markdown("""
    <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    """, unsafe_allow_html=True)

def render_severity_badge(severity):
    """Render animated severity badge"""
    level = "low" if severity < 4 else "medium" if severity < 7 else "high"
    emoji = "✅" if level == "low" else "⚠️" if level == "medium" else "🚨"
    
    st.markdown(f"""
    <span class="severity-{level}">
        {emoji} Severity {severity}/10
    </span>
    """, unsafe_allow_html=True)

def render_metric_card(value, label, icon="📊"):
    """Render animated metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_glass_card(content):
    """Render glassmorphism card"""
    st.markdown(f"""
    <div class="glass-card">
        {content}
    </div>
    """, unsafe_allow_html=True)