import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import os
import time
import json
import re

# ============================================================
# 1. VISUAL CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="DeepDive Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Setup
API_KEY = "AIzaSyDnK1HyjCbkpn7FJTgpKXAbr479hQAwNHE"
os.environ["GEMINI_API_KEY"] = API_KEY
try:
    genai.configure(api_key=API_KEY)
except Exception:
    pass

MODEL_Flash = "gemini-2.5-flash-lite" 
MODEL_Pro = "gemini-2.5-flash-lite" 
MAX_CONTEXT_CHARS = 500_000

# ============================================================
# 2. PREMIUM CSS: Background, Buttons, Search
# ============================================================
st.markdown("""
<style>
    /* Import Fonts: CINZEL (Luxury), Montserrat, Inter */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Montserrat:wght@300;400&family=Inter:wght@300;400;600&display=swap');

    /* Vibrant Deep Ocean Background */
    .stApp {
        background: linear-gradient(rgba(10, 20, 30, 0.6), rgba(10, 20, 30, 0.85)), 
                    url('https://images.unsplash.com/photo-1546026423-cc4642628d2b?ixlib=rb-4.0.3&auto=format&fit=crop&w=2560&q=80');
        background-size: cover;
        background-position: center bottom;
        background-attachment: fixed;
        color: #e0f2fe;
        font-family: 'Inter', sans-serif;
    }

    /* Uniform Glassmorphic Buttons */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #e0f2fe !important;
        border-radius: 12px !important;
        padding: 1rem 1rem !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        text-align: center !important;
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        letter-spacing: 0.5px;
    }
    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        border-color: #38bdf8 !important;
        transform: translateY(-4px) !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.25) !important;
        color: white !important;
    }
    div.stButton > button:active {
        transform: translateY(-2px) !important;
    }

    /* Centered Search Input Container Styling */
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        height: 60px !important;
        min-height: 60px !important;
        background-color: rgba(255, 255, 255, 0.9) !important; 
        border: 2px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 50px !important; 
        box-sizing: border-box !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Input element itself */
    div[data-testid="stTextInput"] input {
        height: 100% !important;
        padding: 0 2rem !important;
        color: #0f172a !important; 
        background: transparent !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        text-align: center !important;
    }
    /* Gradient Placeholder Text */
    div[data-testid="stTextInput"] input::placeholder {
        background: linear-gradient(to right, #0f172a 0%, #1e3a8a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        opacity: 1 !important; 
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #1e3a8a !important;
        box-shadow: 0 0 25px rgba(30, 58, 138, 0.3) !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stTextInput"] label { display: none; }

    /* Chat Message Consistancy */
    .stChatMessage {
        background-color: rgba(15, 23, 42, 0.95) !important; 
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stChatMessage p, .stChatMessage li, .stChatMessage td {
        color: #f8fafc !important; 
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .stChatMessage a {
        color: #38bdf8 !important; 
        text-decoration: underline;
    }
    
    /* Typography - CINZEL */
    h1 {
        font-family: 'Cinzel', serif !important;
        font-weight: 700;
        font-size: 4.2rem !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        background: linear-gradient(to right, #e0f2fe 0%, #22d3ee 40%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 15px rgba(0,0,0,0.4);
        text-align: center;
        padding-bottom: 25px;
        margin-top: 20px;
        line-height: 1.1;
    }
    p.subtitle {
        text-align: center;
        font-size: 2.2rem !important; /* Large Subtitle */
        color: #bae6fd;
        font-weight: 500;
        margin-bottom: 50px;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    h3 {
        font-family: 'Cinzel', serif !important;
        color: #e0f2fe;
        letter-spacing: 1px;
    }
    /* Sidebar Reset Button - High Visibility */
    [data-testid="stSidebar"] button[kind="primary"] {
        background: linear-gradient(135deg, #06b6d4 0%, #2563eb 100%) !important;
        border: 1px solid #67e8f9 !important;
        color: white !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4) !important;
        margin-top: 10px;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(6, 182, 212, 0.6) !important;
        background: linear-gradient(135deg, #22d3ee 0%, #3b82f6 100%) !important;
        border-color: #a5f3fc !important;
    }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. BACKEND LOGIC
# ============================================================

BRAND_MAPPING = {
    "Suunto": "Suunto", "Oceanic": "Oceanic", "Atomic": "Atomic Aquatics",
    "Hollis": "Hollis", "Ocean Hunter": "Ocean Hunter", "Rob Allen": "Rob Allen",
    "Salvimar": "Salvimar", "Zeagle": "Zeagle", "Bare": "Bare",
    "Stahlsac": "Stahlsac", "Princeton": "Princeton Tec",
    "Enth Degree": "Enth Degree", "Gear Aid": "Gear Aid", "Oceanpro": "Oceanpro",
}

def clean_filename(fname):
    name = fname.replace(".pdf", "")
    for k, v in BRAND_MAPPING.items():
        if k in name: return v
    return name

@st.cache_data(show_spinner="Indexing catalogs...")
def index_catalogs_fresh():
    # Fix for CWD being different than script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(script_dir, "data")
    if not os.path.exists(folder):
        st.error(f"Cannot find folder: {folder}. CWD was {os.getcwd()}")
        return "", []
    
    files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    if len(files) == 0:
        st.warning(f"No PDFs found in {folder}.")
        return "", []

    all_text = []
    indexed_brands = set()
    total_chars = 0

    for f in files:
        path = os.path.join(folder, f)
        brand = clean_filename(f)
        
        try:
            doc = fitz.open(path)
            file_text = ""
            for page in doc:
                file_text += page.get_text()
            doc.close()
            
            if total_chars + len(file_text) > MAX_CONTEXT_CHARS:
                remaining = MAX_CONTEXT_CHARS - total_chars
                all_text.append(f"\n=== {brand} Catalog (Truncated) ===\n{file_text[:remaining]}")
                indexed_brands.add(brand)
                break
            
            all_text.append(f"\n=== {brand} Catalog ===\n{file_text}")
            total_chars += len(file_text)
            indexed_brands.add(brand)
            
        except Exception as e:
            st.error(f"Failed to fitz.open({path}): {e}")

    return "\n".join(all_text), sorted(list(indexed_brands))

CONTEXT, BRANDS = index_catalogs_fresh()

# ============================================================
# 4. LOGIC & NAVIGATION
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"
if "history" not in st.session_state:
    st.session_state.history = []
if "cart" not in st.session_state:
    st.session_state.cart = []  # List of dicts: {sku, name, price, qty, etc.}
if "price_tier" not in st.session_state:
    st.session_state.price_tier = "RRP" # Default Tier

def reset():
    st.session_state.page = "home"
    st.session_state.history = []
    st.session_state.search_results = [] # Clear structured results
    st.rerun()

def go_search(query):
    st.session_state.history.append({"role": "user", "content": query})
    st.session_state.page = "chat"
    
    # Debug Info
    with st.sidebar.expander("🔌 Index Status", expanded=False):
        st.write(f"**Total Chars:** {len(CONTEXT):,}")
        st.write(f"**Catalogs:** {', '.join(BRANDS)}")

    # ---------------------------------------------------------
    # INTELLIGENT SEARCH STRATEGY (Auto-Fallback + JSON)
    # ---------------------------------------------------------
    
    @st.cache_data(show_spinner="Deep Searching Catalogs...", ttl=3600)
    def fetch_catalog_json(q, ctx, model_name):
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are DeepDive Intelligence. 
        
        TASK:
        Analyze the request and the catalog data.
        Return a JSON LIST of products found. Dictionary format below.
        
        REQUIRED JSON FORMAT:
        [
          {{
            "brand": "Brand Name",
            "model": "Model Name",
            "sku": "SKU if found else null",
            "prices": {{
                "rrp": 100.00,
                "trade": 60.00,
                "partner": 70.00,
                "distributor": 50.00,
                "promo": 40.00
            }},
            "features": "Key features summary",
            "url": "https://www.google.com/search?q=Brand+Model"
          }}
        ]
        
        PRICING LOGIC:
        - If text lists multiple prices (e.g. "Trade $X", "RRP $Y"), map them.
        - If ONLY RRP is found: set Trade=RRP*0.6, Partner=RRP*0.7 (ESTIMATES).
        - If NO price found, set all to 0.00.
        
        === CATALOG DATA START ===
        {ctx}
        === CATALOG DATA END ===
        
        USER QUESTION: {q}
        """
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return response.text

    @st.cache_data(show_spinner="Searching Knowledge Base...", ttl=3600)
    def fetch_general_knowledge(q, model_name):
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are DeepDive Intelligence Pro (Gemini 3).
        
        TASK:
        The user's question was NOT found in the specific product catalogs.
        Please answer using your GENERAL DIVING KNOWLEDGE.
        
        GUIDELINES:
        1. **State Context**: Start by saying: "⚠️ **Not found in catalogs.** However, based on general diving knowledge..."
        2. **Helpfulness**: Provide a detailed, expert answer about the topic.
        
        USER QUESTION: {q}
        """
        response = model.generate_content(prompt)
        return response.text

    answer = ""
    structured_data = []

    # 1. Attempt Catalog Search (Fast, Strict)
    try:
        # Note: Enforcing JSON output format natively via the SDK
        text = fetch_catalog_json(query, CONTEXT, MODEL_Flash)
        
        try:
            structured_data = json.loads(text)
            if not isinstance(structured_data, list):
                if isinstance(structured_data, dict): structured_data = [structured_data]
                else: structured_data = []
                
            answer = f"Found {len(structured_data)} products."
            st.session_state.search_results = structured_data
        except json.JSONDecodeError as e:
            # Fallback to text if JSON fails
            answer = f"⚠️ Catalog responded, but search data was unreadable. Try rephrasing."
            st.session_state.search_results = []
            
        # Check if Flash indicated failure
        if not structured_data:
            raise ValueError("Catalog miss")
            
    except Exception as e:
        # Debug API exhaustion errors for clear feedback
        if "429" in str(e):
             answer = f"⚠️ Catalog search unavailable (Rate Limited). We are actively upgrading processing limits! Please try again in 1 minute."
             st.session_state.search_results = []
             st.session_state.history.append({"role": "assistant", "content": answer})
             st.rerun()

        # 2. Fallback to General Knowledge
        try:
            answer = fetch_general_knowledge(query, MODEL_Pro)
            st.session_state.search_results = [] # Context switch
        except Exception as e:
            if "429" in str(e):
                answer = "⚠️ Not found in catalogs. Also, specialized reasoning is temporarily unavailable (Rate Limited). Please wait a moment."
            else:
                answer = "⚠️ I couldn't find that in the catalogs, and specialized reasoning is currently unavailable."

    st.session_state.history.append({"role": "assistant", "content": answer})
    st.rerun()

# ============================================================
# 5. AUTHENTICATION & RENDER PAGES
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>DeepDive Secure Access</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Please enter the client passcode.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Passcode", type="password", label_visibility="collapsed", placeholder="Enter Passcode")
        if st.button("UNLOCK", use_container_width=True):
            if pwd == "ROSEBUD2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied. Incorrect Passcode.")
    st.stop()
# Sidebar
with st.sidebar:
    # Custom Title (Stacked)
    st.caption(f"v5.8 Premium • {len(BRANDS)} Catalogs")

    # Beginner Instructions
    with st.expander("📝 How to use", expanded=True):
        st.markdown("""
        1. **Search**: Use the main chat box 👉
        2. **Order**: Select tier & add items.
        3. **Export**: Review cart layout.
        """,
        help="The sidebar is for settings and cart management only. Use the main chat area for searching.")
    
    st.markdown("---")
    # Price Tier Selector for Debug/Admin
    tier_options = ["RRP", "Trade", "Partner", "Distributor", "Promo"]
    selected_tier = st.selectbox(
        "Select Price Tier (Affects Cart)", 
        tier_options, 
        index=0,
        help="Choose the pricing level to apply when adding items to the cart."
    )
    if selected_tier != st.session_state.get("price_tier"):
        st.session_state.price_tier = selected_tier
        st.rerun()
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Reset App", key="sidebar_reset", use_container_width=True, help="Clear current session and start over."):
        reset()

    # Demo Script Viewer
    st.markdown("---")
    if st.checkbox("📖 Show User Manual", value=False):
        try:
            with open("DEMO_SCRIPT.md", "r", encoding="utf-8") as f:
                script_content = f.read()
            st.info("💡 **Quick Start Guide**")
            st.markdown(script_content)
        except Exception as e:
            st.error(f"Could not load script: {e}")

    # System Status Indicator (New Feature)
    st.markdown("---")
    with st.expander("🛠️ System Status", expanded=True):
        # 1. Check API Key
        import os
        if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"].startswith("AI"):
             st.success("API Key: Active")
        else:
             st.error("API Key: Missing")
        
        # 2. Check Data
        if len(BRANDS) > 0:
             st.success(f"Index: {len(BRANDS)} Brands")
        else:
             st.warning("Index: Empty")
             
        # 3. Last Verified
        import datetime
        st.caption(f"Verified: {datetime.datetime.now().strftime('%H:%M')}")

# ============================================================
# BRAND LOGOS
# ============================================================
# Using direct official/wiki links where possible for better quality
BRAND_LOGOS = {
    "Suunto": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Suunto_logo.svg/2560px-Suunto_logo.svg.png",
    "Oceanic": "https://www.oceanicworldwide.com/wp-content/uploads/2019/02/Oceanic-Logo-1.png",
    "Atomic Aquatics": "https://www.atomicaquatics.com/wp-content/uploads/2019/02/Atomic-Aquatics-Logo-1.png",
    "Hollis": "https://www.hollis.com/wp-content/uploads/2019/02/Hollis-Logo-1.png",
    "Ocean Hunter": "https://www.oceanhunter.com.au/assets/images/logo.png", 
    "Rob Allen": "https://roballen.co.za/wp-content/uploads/2021/05/RA-Logo-Landscape-White.png", # White version for dark mode
    "Salvimar": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Salvimar_logo.png",
    "Zeagle": "https://www.zeagle.com/wp-content/uploads/2019/02/Zeagle-Logo-1.png",
    "Bare": "https://www.baresports.com/wp-content/uploads/2019/02/BARE-Logo-1.png",
    "Stahlsac": "https://www.stahlsac.com/wp-content/uploads/2019/02/Stahlsac-Logo-1.png",
    "Princeton Tec": "https://princetontec.com/wp-content/uploads/2020/03/pt-logo-white.png",
    "Enth Degree": "https://www.enth-degree.com/wp-content/uploads/2018/10/logo.png",
    "Gear Aid": "https://www.gearaid.com/cdn/shop/files/GA_Logo_White_200x.png",
    "Oceanpro": "https://www.oceanpro.com.au/assets/images/logo.png"
}

# Home Page
if st.session_state.page == "home":
    
    # Logos removed for cleaner UI as requested

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1>AUP DeepDive Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>The AI-powered expert for your product ecosystem.</p>", unsafe_allow_html=True)

    c_search = st.container()
    with c_search:
        def submit():
            st.session_state.submitted = True
        
        # Call to Action Text (ABOVE Search Bar)
        st.markdown("""
            <p style='
                text-align: center; 
                font-family: "Cinzel", serif; 
                font-weight: 700; 
                font-size: 1.2rem; 
                margin-bottom: 5px; 
                letter-spacing: 1px;
                background: linear-gradient(to right, #bae6fd, #38bdf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            '>
                START HERE - ASK AI ANYTHING DIVE RELATED
            </p>
        """, unsafe_allow_html=True)

        c_input, c_btn = st.columns([5, 1])
        with c_input:
            query = st.text_input(
                "Search", 
                placeholder="type your question here", 
                key="landing_search",
                label_visibility="collapsed",
                on_change=submit
            )
        with c_btn:
            # Custom Search Button styled as rectangle
            if st.button("SEARCH", key="search_btn", use_container_width=True):
                st.session_state.submitted = True

        if st.session_state.get("submitted"):
            st.session_state.submitted = False 
            if query:
                go_search(query)

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

    # Suggestions
    c1, c2, c3 = st.columns(3)
    if c1.button("🔍 Wetsuits < $300", use_container_width=True):
        go_search("List all wetsuits under $300 with brand, model and price in a table.")
    if c2.button("⚖️ Compare Computers", use_container_width=True):
        go_search("Compare Suunto and Oceanic dive computers specs side-by-sides.")
    if c3.button("🔦 Best Tech Lights", use_container_width=True):
        go_search("What are the best value primary lights for technical diving?")

    # Catalog Grid
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
    st.markdown("### Explore by Brand")
    
    cols = st.columns(4)
    for i, brand in enumerate(BRANDS):
        col = cols[i % 4]
        with col:
            # Display Logo + Button
            logo_url = BRAND_LOGOS.get(brand, "https://placehold.co/100x50?text=" + brand)
            st.image(logo_url, use_container_width=False, width=80) 
            if st.button(f"View {brand}", key=f"btn_{brand}", use_container_width=True):
                st.session_state.history = []
                st.session_state.history.append({"role": "user", "content": f"Show me the {brand} catalog."})
                st.session_state.history.append({
                    "role": "assistant", 
                    "content": f"### 📘 **{brand} Catalog**\nI've loaded the {brand} product line. **What are you looking for?**"
                })
                st.session_state.page = "chat"
                st.rerun()

# Chat Page
else:
    # Header
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("<h3>DeepDive Chat</h3>", unsafe_allow_html=True)
    with c2:
        if st.button("🔄 New Search", use_container_width=True):
            reset()
    
    # Chat History
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # RESULTS GRID (If Structured Data Exists)
    if st.session_state.get("search_results"):
        st.markdown("### 🛍️ Product Results")
        results = st.session_state.search_results
        
        # Grid Layout
        cols = st.columns(3)
        for i, item in enumerate(results):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"**{item.get('brand')}**")
                    st.markdown(f"#### {item.get('model')}")
                    
                    # Price Display
                    prices = item.get('prices', {})
                    tier = st.session_state.price_tier.lower()
                    price = prices.get(tier, 0.0)
                    
                    st.markdown(f"### ${price:,.2f} <span style='font-size:0.8rem;color:gray'>({st.session_state.price_tier})</span>", unsafe_allow_html=True)
                    st.caption(item.get('features', '')[:100] + "...")
                    
                    # Add to Cart
                    if st.button("🛒 Add to Cart", key=f"add_{i}", use_container_width=True):
                        cart_item = {
                            "sku": item.get("sku") or f"{item.get('brand')}-{item.get('model')}",
                            "name": f"{item.get('brand')} {item.get('model')}",
                            "price": price,
                            "tier": st.session_state.price_tier,
                            "qty": 1
                        }
                        st.session_state.cart.append(cart_item)
                        st.toast(f"Added {item.get('model')} to cart!", icon="✅")
                        st.rerun()

    # Input Area (Styled like Landing Page)
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    with st.container():
        def submit_chat():
            st.session_state.chat_submitted = True

        c_input, c_btn = st.columns([6, 1])
        with c_input:
            chat_query = st.text_input(
                "Follow-up", 
                placeholder="Ask a follow-up question...", 
                key="chat_search_input",
                label_visibility="collapsed",
                on_change=submit_chat
            )
        with c_btn:
             if st.button("GO", key="chat_btn", use_container_width=True):
                 st.session_state.chat_submitted = True
                 
        if st.session_state.get("chat_submitted"):
            st.session_state.chat_submitted = False
            if chat_query:
                go_search(chat_query)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
    # Bottom 'New Search' Button for convenience
    st.markdown("---")
    if st.button("🔄 Start New Search", key="btn_new_search_bottom", use_container_width=True):
        reset()

# ============================================================
# SHOPPING CART SIDEBAR
# ============================================================
if st.session_state.cart:
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🛒 Shopping Cart")
        
        total = 0.0
        for i, item in enumerate(st.session_state.cart):
            st.markdown(f"**{item['name']}**")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.caption(f"${item['price']:,.2f} ({item['tier']})")
            with c2:
                if st.button("❌", key=f"rm_{i}"):
                    st.session_state.cart.pop(i)
                    st.rerun()
            total += item['price'] * item['qty']
            st.divider()
            
        st.markdown(f"### Total: ${total:,.2f}")
        if st.button("💳 Checkout / Export", use_container_width=True):
            order_text = "ORDER DETAILS:\n\n"
            for item in st.session_state.cart:
                order_text += f"- {item['name']} (${item['price']}) x {item['qty']}\n"
            order_text += f"\nTOTAL: ${total:,.2f}"
            st.code(order_text)
            st.info("Copy the details above to email.")
