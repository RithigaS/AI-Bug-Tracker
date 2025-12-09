import streamlit as st
import os
from utils.redaction import redact_sensitive_data
from utils.hashing import generate_log_hash
from database import init_db, insert_log, get_log_by_hash, get_all_logs
from ai_engine import analyze_log_content
import json

# Page Config
st.set_page_config(
    page_title="AI Bug Tracker",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize DB
init_db()

# 🌙 DARK THEME CSS
st.markdown("""
    <style>
    /* GLOBAL THEME */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Segoe UI', sans-serif;
    }

    /* HEADER */
    .main-header {
        font-size: 2.8rem;
        color: #79c0ff;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        text-shadow: 0 0 15px rgba(121,192,255,0.4);
        letter-spacing: 1px;
    }

    /* GLASS CARD */
    .log-card {
        background: rgba(22, 27, 34, 0.65);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid rgba(121,192,255,0.1);
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        backdrop-filter: blur(10px);
        transition: transform 0.15s ease-in-out;
    }
    .log-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.55);
    }

    /* SEVERITY COLORS */
    .severity-high {
        color: #ff7b72;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(255,80,80,0.4);
    }
    .severity-medium {
        color: #f0ad4e;
        font-weight: bold;
    }
    .severity-low {
        color: #4ae3b5;
        font-weight: bold;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
        padding: 15px;
    }

    /* SIDEBAR BUTTONS */
    .stSidebar button {
        background-color: #21262d !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #e6edf3 !important;
        transition: 0.2s ease-in-out;
        padding: 8px !important;
    }
    .stSidebar button:hover {
        background-color: #30363d !important;
        border-color: #58a6ff !important;
        color: #58a6ff !important;
    }

    /* FILE UPLOADER */
    .stFileUploader {
        background-color: #161b22 !important;
        border-radius: 12px;
        padding: 15px;
        border: 1px dashed #30363d !important;
    }

    /* PRIMARY BUTTON */
    button[kind="primary"] {
        background: linear-gradient(90deg, #238636, #2ea043) !important;
        border: none !important;
        color: white !important;
        padding: 0.6rem 1rem !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 0 10px rgba(35,134,54,0.4);
        transition: 0.2s ease-in-out;
    }
    button[kind="primary"]:hover {
        transform: scale(1.02);
        box-shadow: 0 0 18px rgba(35,134,54,0.6);
    }

    /* EXPANDER */
    .streamlit-expanderHeader {
        background-color: #161b22 !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: 1px solid #30363d !important;
    }

    .streamlit-expanderContent {
        background-color: #0d1117 !important;
        border-radius: 8px !important;
        border: 1px solid #30363d !important;
        max-height: 500px !important;
        overflow-y: auto !important;
    }

    /* CODE BLOCKS */
    pre, code {
        background-color: #0d1117 !important;
        border-radius: 10px !important;
        border: 1px solid #30363d !important;
        padding: 12px !important;
        color: #c9d1d9 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-x: auto !important;
    }
    
    /* LOG CONTENT CONTAINER */
    .log-content-box {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #c9d1d9;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    </style>
""", unsafe_allow_html=True)




def main():
    st.markdown('<h1 class="main-header">🐞 AI Bug Tracker & Smart Debugger</h1>', unsafe_allow_html=True)

    # Sidebar - History
    st.sidebar.title("📜 Upload History")
    history_logs = get_all_logs()
    
    selected_history_log = None
    if history_logs:
        for log in history_logs:
            # Create a button for each log entry
            label = f"{log['filename']} ({log['upload_time'][:16]})"
            if st.sidebar.button(label, key=log['id']):
                selected_history_log = log
    else:
        st.sidebar.info("No logs uploaded yet.")

    # Main Content Area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Log File")
        uploaded_file = st.file_uploader("Drag and drop .log, .txt, or .json files", type=['log', 'txt', 'json'])

        if uploaded_file is not None:
            file_content = uploaded_file.read().decode("utf-8")
            file_size = uploaded_file.size
            filename = uploaded_file.name
            
            st.info(f"File: {filename} | Size: {file_size/1024:.2f} KB")
            
            with st.expander("📄 View Raw Log Content", expanded=False):
                st.markdown(f'<div class="log-content-box">{file_content}</div>', unsafe_allow_html=True)

            if st.button("🔍 Analyze Log", type="primary"):
                with st.spinner("Processing log..."):
                    # 1. Redaction
                    redacted_content = redact_sensitive_data(file_content)
                    
                    # 2. Hashing & Deduplication
                    file_hash = generate_log_hash(redacted_content)
                    
                    existing_log = get_log_by_hash(file_hash)
                    
                    if existing_log:
                        st.success("✨ Duplicate log detected! Fetching cached analysis.")
                        result = json.loads(existing_log['analysis_json'])
                        display_results(result, redacted_content)
                    else:
                        # 3. AI Analysis
                        st.text("🤖 Sending to AI for analysis...")
                        analysis_result = analyze_log_content(redacted_content)
                        
                        # 4. Save to DB ONLY if analysis was successful
                        if analysis_result.get('issue_type') != "Analysis Failed":
                            insert_log(
                                file_hash=file_hash,
                                filename=filename,
                                file_size=file_size,
                                analysis=analysis_result,
                                severity=analysis_result.get('severity', 'Unknown')
                            )
                        
                        st.success("✅ Analysis Complete!")
                        display_results(analysis_result, redacted_content)
                        if analysis_result.get('issue_type') != "Analysis Failed":
                            st.rerun() # Rerun to update sidebar history

    with col2:
        if selected_history_log:
            st.subheader("📜 Historical Analysis")
            st.info(f"Viewing analysis for: {selected_history_log['filename']}")
            result = json.loads(selected_history_log['analysis_json'])
            display_results(result, None)
        elif not uploaded_file:
            st.info("👈 Upload a file or select from history to view analysis.")



def highlight_redacted(text: str) -> str:
    """Highlights redacted tags with HTML/CSS."""
    tags = {
        "[REDACTED_IP]": "#ff6b6b",
        "[REDACTED_EMAIL]": "#f0ad4e",
        "[REDACTED_SECRET]": "#ff4757",
        "[REDACTED_PATH]": "#4ae3b5"
    }
    
    for tag, color in tags.items():
        # Replace tag with a styled span
        text = text.replace(tag, f'<span style="background-color: {color}33; color: {color}; padding: 3px 8px; border-radius: 4px; border: 1px solid {color}; font-weight: bold; display: inline-block; margin: 2px;">{tag}</span>')
    
    # Preserve newlines for markdown
    text = text.replace("\n", "<br>")
    return f'<div class="log-content-box">{text}</div>'

def display_results(analysis: dict, redacted_content: str = None):
    """Helper to display structured analysis results."""
    
    # Severity Badge
    severity = analysis.get('severity', 'Unknown').upper()
    color_class = "severity-low"
    if "HIGH" in severity or "CRITICAL" in severity:
        color_class = "severity-high"
    elif "MEDIUM" in severity:
        color_class = "severity-medium"
        
    st.markdown(f"""
        <div class="log-card">
            <h3>🛡️ Analysis Report</h3>
            <p><strong>Severity:</strong> <span class="{color_class}">{severity}</span></p>
            <p><strong>Issue Type:</strong> {analysis.get('issue_type', 'N/A')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧐 Root Cause")
    st.write(analysis.get('root_cause', 'No explanation provided.'))
    
    st.markdown("### 🛠️ Suggested Fix")
    suggested_fix = analysis.get('suggested_fix', 'No fix provided.')
    st.markdown(f'<div class="log-content-box" style="max-height: 300px;">{suggested_fix}</div>', unsafe_allow_html=True)

    if redacted_content:
        with st.expander("👀 View Redacted Content (Sent to AI)"):
            st.markdown(highlight_redacted(redacted_content), unsafe_allow_html=True)



if __name__ == "__main__":
    main()
