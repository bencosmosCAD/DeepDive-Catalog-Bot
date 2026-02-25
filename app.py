import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import os
import time

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="DeepDive Catalog Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS - underwater theme + bubbles
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&family=Open+Sans:wght@300;400&display=swap');
.stApp{background:radial-gradient(circle at center,#1e293b 0%,#0f172a 100%);font-family:'Open Sans',sans-serif;color:#e2e8f0;overflow-x:hidden}
h1,h2,h3{font-family:'Montserrat',sans-serif;color:#fff;position:relative;z-index:1}
h1{background:linear-gradient(120deg,#67e8f9,#2563eb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800}
.stButton>button{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);color:#fff;backdrop-filter:blur(5px);transition:.3s}
.stButton>button:hover{background:rgba(6,182,212,.2);border-color:#06b6d4;transform:translateY(-3px);box-shadow:0 5px 15px rgba(6,182,212,.2)}
.stChatMessage{background-color:rgba(15,23,42,.85);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.1);z-index:1;position:relative}
.brand-card{background:rgba(255,255,255,.03);border-radius:12px;padding:15px;text-align:center;border:1px solid rgba(255,255,255,.05);transition:.3s;backdrop-filter:blur(4px)}
.brand-card:hover{background:rgba(255,255,255,.1);border-color:#22d3ee}
.brand-name{font-weight:600;color:#bae6fd;font-size:1.1em;font-family:'Montserrat',sans-serif}
.bubble{position:fixed;bottom:-100px;background:rgba(255,255,255,.08);border-radius:50%;animation:rise 10s infinite ease-in;z-index:0;pointer-events:none}
@keyframes rise{0%{bottom:-100px;transform:translateX(0)}50%{transform:translateX(80px)}100%{bottom:110vh;transform:translateX(-120px)}}
</style>
<script>
!function(){function b(){var d=document.createElement('div');d.className='bubble';var s=Math.random()*50+15+'px';d.style.width=s;d.style.height=s;d.style.left=Math.random()*100+'vw';d.style.animationDuration=Math.random()*6+6+'s';d.style.opacity=Math.random()*.25;document.body.appendChild(d);setTimeout(function(){d.remove()},12000)}setInterval(b,800)}();
</script>
""", unsafe_allow_html=True)

# ============================================================
# API + MODEL CONFIG
# ============================================================
API_KEY = "AIzaSyDnK1HyjCbkpn7FJTgpKXAbr479hQAwNHE"
genai.configure(api_key=API_KEY)

MODEL_CANDIDATES = [
    "gemini-2.5-flash-lite",   # Higher free-tier quota
    "gemini-flash-latest",     # Confirmed working
    "gemini-2.5-flash",        # Best quality but low free quota
    "gemini-2.0-flash",
]
MAX_CONTEXT_CHARS = 120_000      # ~30k tokens, safe for speed

# ============================================================
# BRAND MAPPING
# ============================================================
BRAND_MAP = {
    "Suunto": "Suunto", "Oceanic": "Oceanic", "Atomic": "Atomic Aquatics",
    "Hollis": "Hollis", "Ocean Hunter": "Ocean Hunter", "Rob Allen": "Rob Allen",
    "Salvimar": "Salvimar", "Zeagle": "Zeagle", "Bare": "Bare",
    "Stahlsac": "Stahlsac", "Princeton": "Princeton Tec",
    "Enth Degree": "Enth Degree", "Gear Aid": "Gear Aid", "Oceanpro": "Oceanpro",
}

def _brand(filename):
    stem = filename.replace(".pdf", "")
    for key, val in BRAND_MAP.items():
        if key in stem:
            return val
    return stem

# ============================================================
# KNOWLEDGE BASE - local text extraction (cached)
# ============================================================
@st.cache_data(show_spinner=False)
def load_catalog_text():
    data_dir = "data"
    if not os.path.isdir(data_dir):
        return "", 0, []

    pdfs = sorted(f for f in os.listdir(data_dir) if f.lower().endswith(".pdf"))
    if not pdfs:
        return "", 0, []

    chunks = []
    brands = []
    total_chars = 0

    for f in pdfs:
        path = os.path.join(data_dir, f)
        brand = _brand(f)
        if brand not in brands:
            brands.append(brand)
        try:
            doc = fitz.open(path)
            file_text = ""
            for page in doc:
                file_text += page.get_text()
            doc.close()

            remaining = MAX_CONTEXT_CHARS - total_chars
            if remaining <= 0:
                break
            trimmed = file_text[:remaining]
            chunks.append(f"\n--- {brand} Catalog ---\n{trimmed}")
            total_chars += len(trimmed)
        except Exception:
            pass

    return "\n".join(chunks), len(pdfs), sorted(brands)


CATALOG_TEXT, FILE_COUNT, BRANDS = load_catalog_text()

# ============================================================
# ANSWER GENERATION - with retry for rate limits
# ============================================================
def generate_answer(user_prompt):
    """Generate answer with catalog context. Returns (response_stream, error_msg)."""
    
    full_prompt = (
        "You are DeepDive Intelligence, a specialist AI for underwater diving equipment.\n"
        "Answer using ONLY the catalog data below. Be specific with product names, prices, specs.\n"
        "Format tables with Markdown. If info is not in catalogs, say so.\n\n"
        "=== CATALOG DATA ===\n"
        + CATALOG_TEXT +
        "\n=== END CATALOG DATA ===\n\n"
        "USER QUESTION: " + user_prompt
    )

    # Try each model candidate
    for model_name in MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt, stream=True)
            return response, None
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                continue  # Rate limited, try next model
            elif "404" in error_str:
                continue  # Model not found, try next
            else:
                continue  # Any other error, try next
    
    return None, "All models are currently busy. Please wait 30 seconds and try again."


# ============================================================
# SESSION STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "on_landing" not in st.session_state:
    st.session_state.on_landing = True

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.caption("DeepDive Intelligence v3.1")
    if FILE_COUNT:
        st.success(f"{FILE_COUNT} catalogs indexed")
    if st.button("New Search"):
        st.session_state.messages = []
        st.session_state.on_landing = True
        st.rerun()

# ============================================================
# HELPER
# ============================================================
def _submit(query):
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.on_landing = False
    st.rerun()

# ============================================================
# LANDING PAGE
# ============================================================
if st.session_state.on_landing:
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align:center;font-size:3.8em;margin-bottom:8px'>"
        "DeepDive Intelligence</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;color:#bae6fd;font-size:1.3em;"
        "font-weight:300;margin-bottom:50px'>"
        "The advanced AI for your entire product ecosystem.</p>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Wetsuits under $300"):
            _submit("List all wetsuits under $300 in a table with brand, model, and price.")
    with c2:
        if st.button("Compare Dive Computers"):
            _submit("Compare the Suunto and Oceanic dive computers side by side.")
    with c3:
        if st.button("Best Tech Lights"):
            _submit("What are the best value primary lights for technical diving?")

    st.markdown(
        "<h3 style='text-align:center;margin-top:50px;margin-bottom:25px;"
        "color:#94a3b8;font-weight:300'>INDEXED CATALOGS</h3>",
        unsafe_allow_html=True,
    )
    display_brands = BRANDS if BRANDS else ["No catalogs found"]
    cols_per_row = 4
    for i in range(0, len(display_brands), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(display_brands):
                col.markdown(
                    f'<div class="brand-card"><div class="brand-name">'
                    f'{display_brands[idx]}</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)
    if user_input := st.chat_input("Ask about any product..."):
        _submit(user_input)

# ============================================================
# CHAT PAGE
# ============================================================
else:
    st.title("DeepDive Intelligence")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if (
        st.session_state.messages
        and st.session_state.messages[-1]["role"] == "user"
    ):
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Searching catalogs...")

            response, error = generate_answer(
                st.session_state.messages[-1]["content"]
            )

            if error:
                placeholder.markdown(f"**{error}**")
                st.session_state.messages.append(
                    {"role": "assistant", "content": error}
                )
            else:
                full = ""
                try:
                    for chunk in response:
                        if chunk.text:
                            full += chunk.text
                            placeholder.markdown(full + " |")
                except Exception as exc:
                    if not full:
                        full = f"Connection interrupted: {exc}"
                    else:
                        full += f"\n\n(Stream interrupted: {exc})"

                placeholder.markdown(full)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full}
                )

    if follow_up := st.chat_input("Ask a follow-up..."):
        _submit(follow_up)