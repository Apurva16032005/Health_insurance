import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

# --- CONFIGURATION ---
API_URL = "http://localhost:8000"
st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLING & HEADER ---
def render_header(show_logout=False):
    st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
        }
        .main-header {
            background: linear-gradient(to right, #1e3c72, #2a5298);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        /* Status Badges */
        .badge-high { background-color: #ffebee; color: #c62828; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #ef9a9a; }
        .badge-med { background-color: #fff3e0; color: #ef6c00; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #ffcc80; }
        .badge-low { background-color: #e8f5e9; color: #2e7d32; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #a5d6a7; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown("""
        <div class="main-header">
            <h1 style="margin:0; font-family: 'Segoe UI', sans-serif;">🛡️ FraudShield AI</h1>
            <p style="margin:0; opacity: 0.8; font-weight: 300;">Enterprise-Grade Insurance Verification System</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if show_logout:
            st.write("")
            st.write("")
            if st.button("🚪 Logout"):
                st.session_state['role'] = None
                st.rerun()

# --- PAGE: LOGIN ---
def login_page():
    render_header(show_logout=False)
    
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.container(border=True):
            st.subheader("🔐 Secure Access Portal")
            
            role = st.radio("Select User Role:", ["Policyholder", "Claims Officer"], horizontal=True)
            st.markdown("---")
            
            if role == "Policyholder":
                st.markdown("#### 👤 Policyholder Login")
                email = st.text_input("Email Address", placeholder="user@example.com")
                password = st.text_input("Password", type="password")
                
                if st.button("Login", type="primary"):
                    if email and password:
                        with st.spinner("Authenticating..."):
                            time.sleep(1)
                            st.session_state['role'] = "User"
                            st.session_state['user_email'] = email
                            st.success("Login Successful!")
                            st.rerun()
                    else:
                        st.error("Please enter both Email and Password.")

            elif role == "Claims Officer":
                st.markdown("#### 👮‍♂️ Officer Login")
                officer_id = st.text_input("Officer ID", placeholder="EMP-8821")
                email = st.text_input("Official Email", placeholder="officer@insurance.com")
                password = st.text_input("Password", type="password")
                
                if st.button("Access Dashboard", type="primary"):
                    if officer_id and email and password == "admin123":
                        with st.spinner("Verifying Credentials..."):
                            time.sleep(1)
                            st.session_state['role'] = "Officer"
                            st.success("Access Granted")
                            st.rerun()
                    elif not (officer_id and email and password):
                        st.warning("All fields are required.")
                    else:
                        st.error("Invalid Credentials. (Hint: Pass is 'admin123')")

# --- PAGE: USER DASHBOARD ---
def user_dashboard():
    render_header(show_logout=True)
    
    st.info(f"👤 Logged in as: {st.session_state.get('user_email', 'User')}")

    st.subheader("📄 Submit New Claims")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Patient Name")
            hospital = st.text_input("Hospital Name")
        with col2:
            amount = st.number_input("Total Claim Amount (₹)", min_value=0)
            desc = st.text_area("Treatment Description", height=100)
            
        files = st.file_uploader(
            "Upload Documents (Bills, Reports, etc.)", 
            type=["jpg", "png", "jpeg", "pdf"], 
            accept_multiple_files=True 
        )
        
        if st.button("🚀 Submit All Claims", type="primary"):
            if files and amount > 0:
                for file in files:
                    with st.status(f"Processing {file.name}...", expanded=True) as status:
                        st.write("📤 Uploading secure data...")
                        time.sleep(0.5)
                        st.write("🔍 Running OCR & Text Extraction...")
                        st.write("🖼️ Performing CNN Forgery Detection...")
                        st.write("🧠 Analyzing Medical Context...")
                        
                        try:
                            file.seek(0)
                            files_payload = {"file": (file.name, file.getvalue(), file.type)}
                            data_payload = {"amount": amount, "user_id": 101, "description": desc}
                            
                            res = requests.post(f"{API_URL}/upload-claim", files=files_payload, data=data_payload)
                            
                            if res.status_code == 200:
                                json_res = res.json()
                                status.update(label=f"✅ {file.name} - Analysis Complete", state="complete", expanded=False)
                                
                                risk = json_res['fraud_score']
                                color = "red" if risk > 0.7 else "orange" if risk > 0.4 else "green"
                                label = "High Risk" if risk > 0.7 else "Review" if risk > 0.4 else "Low Risk"
                                
                                st.markdown(f"""
                                <div style="border-left: 5px solid {color}; padding: 10px; background: #f0f2f6; border-radius: 5px; margin-bottom: 10px;">
                                    <strong>File:</strong> {file.name}<br>
                                    <strong>Claim ID:</strong> {json_res['claim_id']}<br>
                                    <strong>AI Assessment:</strong> <span style="color:{color}; font-weight:bold;">{label} ({risk*100:.1f}%)</span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                status.update(label="❌ Error", state="error")
                                st.error(f"Server Error for {file.name}")
                        except Exception as e:
                            st.error(f"Could not connect for {file.name}. Is backend running?")
                            
                st.success("Batch processing finished!")
            else:
                st.warning("Please upload at least one file and enter a valid amount.")

# --- ANALYTICS COMPONENT (Native Python) ---
def render_analytics():
    st.subheader("📊 Executive Risk Overview")
    st.markdown("Real-time insights from the **FraudShield Data Warehouse**.")
    
    try:
        # 1. Fetch live data from Backend
        claims = requests.get(f"{API_URL}/get-pending-claims").json()
        
        if not claims:
            st.info("Waiting for data... Submit some claims to see analytics!")
            return

        # 2. Process Data into a Table (DataFrame)
        df = pd.DataFrame(claims)
        
        # Extract values from the nested JSON structure
        df['Claim ID'] = df['claim_id']
        df['Amount'] = df['input_data'].apply(lambda x: x['amount_claimed'])
        df['Hospital'] = df['input_data'].apply(lambda x: x['hospital_name'])
        df['Risk Score'] = df['scores'].apply(lambda x: x['final_fraud_score'])
        df['Risk Level'] = df['details'].apply(lambda x: x.get('risk_label', 'Unknown'))
        df['Date'] = pd.to_datetime(df['created_at'])

        # 3. TOP METRICS ROW
        total_val = df['Amount'].sum()
        avg_risk = df['Risk Score'].mean() * 100
        critical = df[df['Risk Score'] > 0.7].shape[0]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Claims Processed", len(df))
        m2.metric("Total Value at Risk", f"₹{total_val:,.0f}")
        m3.metric("Average Fraud Risk", f"{avg_risk:.1f}%")
        m4.metric("Critical Flags", critical, delta_color="inverse")
        
        st.divider()

        # 4. CHARTS ROW
        c1, c2 = st.columns(2)
        
        with c1:
            # Pie Chart: Risk Distribution
            st.markdown("##### ⚠️ Risk Classification")
            fig_pie = px.pie(df, names='Risk Level', values='Amount', hole=0.4,
                             color='Risk Level',
                             color_discrete_map={'High':'#ef5350', 'Medium':'#ffa726', 'Low':'#66bb6a'})
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            # Bar Chart: Fraud by Hospital
            st.markdown("##### 🏥 Hospital Watchlist")
            # Calculate average risk per hospital
            hosp_risk = df.groupby('Hospital')['Risk Score'].mean().reset_index()
            fig_bar = px.bar(hosp_risk, x='Risk Score', y='Hospital', orientation='h',
                             color='Risk Score', range_x=[0,1],
                             color_continuous_scale=['green', 'yellow', 'red'])
            st.plotly_chart(fig_bar, use_container_width=True)

    except Exception as e:
        st.error(f"Analytics Error: {e}")

# --- PAGE: OFFICER DASHBOARD ---
def officer_dashboard():
    render_header(show_logout=True)
    st.success("👮‍♂️ Officer Dashboard: Active")
    
    tab1, tab2 = st.tabs(["📥 Pending Claims", "📊 Executive Analytics"])
    
    with tab1:
        st.subheader("📥 Pending Claims Queue")
        try:
            claims = requests.get(f"{API_URL}/get-pending-claims").json()
            if not claims:
                st.info("No pending claims found. System clear.")
            else:
                for c in claims:
                    risk_score = c['scores']['final_fraud_score']
                    if risk_score > 0.75:
                        emoji = "🔴"
                        risk_text = "CRITICAL RISK"
                    elif risk_score > 0.4:
                        emoji = "🟠"
                        risk_text = "MODERATE RISK"
                    else:
                        emoji = "🟢"
                        risk_text = "SAFE"

                    with st.expander(f"{emoji} Claim #{c['claim_id']} | {c['input_data']['hospital_name']} | {risk_text} ({risk_score:.2f})"):
                        
                        c1, c2 = st.columns([1, 1.5])
                        with c1:
                            st.image(f"{API_URL}{c['input_data']['file_url']}", caption="Submitted Document", use_container_width=True)
                        
                        with c2:
                            st.markdown("### 📊 AI Analysis Report")
                            st.write(f"**Claim Amount:** ₹{c['input_data']['amount_claimed']}")
                            st.write(f"**Tamper Score:** {c['scores']['cnn_score']:.2f}")
                            st.info(f"**🤖 Explainable AI (XAI):** {c['xai_explanation']}")
                            
                            report_url = f"{API_URL}/reports/Fraud_Report_{c['claim_id']}.pdf"
                            st.link_button("📥 Download Full Report (PDF)", report_url)
                            
                            st.divider()
                            col_a, col_b = st.columns(2)
                            if col_a.button("✅ Approve", key=f"app_{c['claim_id']}", use_container_width=True):
                                requests.post(f"{API_URL}/update-decision", json={"claim_id": c['claim_id'], "status": "Approved", "remarks": "Officer Verified"})
                                st.success("Approved!")
                                time.sleep(1)
                                st.rerun()
                            if col_b.button("🚫 Reject", key=f"rej_{c['claim_id']}", use_container_width=True):
                                requests.post(f"{API_URL}/update-decision", json={"claim_id": c['claim_id'], "status": "Rejected", "remarks": "Officer Rejected"})
                                st.error("Rejected!")
                                time.sleep(1)
                                st.rerun()
        except Exception as e:
            st.error(f"Unable to fetch data. Ensure Backend is running. Error: {e}")

    with tab2:
        render_analytics()

# --- ROUTER ---
if 'role' not in st.session_state:
    st.session_state['role'] = None

if st.session_state['role'] == 'User':
    user_dashboard()
elif st.session_state['role'] == 'Officer':
    officer_dashboard()
else:
    login_page()