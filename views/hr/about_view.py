import streamlit as st
import json
import os
from utils.ml_pipeline import METADATA_PATH

def render_about_view():
    st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <h2 style="color: #1e3a8a; margin: 0;">ℹ️ About AttritionSense AI</h2>
            <p style="color: #64748b; margin: 0.2rem 0 0 0;">Architecture, Machine Learning specifications, and ethical AI governance</p>
        </div>
    """, unsafe_allow_html=True)
    
    metadata = {}
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            metadata = json.load(f)
            
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🧠 Machine Learning Model Specifications")
        st.markdown("""
            - **Algorithm:** Random Forest Classifier (`RandomForestClassifier`)
            - **Ensemble Size:** 250 Estimators (Decision Trees)
            - **Tree Depth:** Max Depth 12, Min Samples Split 6, Min Samples Leaf 2
            - **Class Weighting:** Balanced (to mitigate historical attrition imbalance)
            - **Preprocessing:** One-Hot Encoding for categorical features; Standard Scaling for numerical features
            - **Pipeline Validation:** Stratified 80/20 train-test validation
        """)
        
        if metadata and "metrics" in metadata:
            st.markdown("#### 🎯 Verified Test Performance")
            m = metadata["metrics"]
            st.write(f"- **Accuracy:** `{m.get('accuracy', 0):.2%}`")
            st.write(f"- **ROC-AUC Score:** `{m.get('roc_auc', 0):.4f}`")
            st.write(f"- **F1 Score:** `{m.get('f1_score', 0):.4f}`")
            st.write(f"- **Precision:** `{m.get('precision', 0):.4f}`")
            st.write(f"- **Recall:** `{m.get('recall', 0):.4f}`")

    with col2:
        st.markdown("### 🛡️ Ethical AI & Privacy Safeguards")
        st.markdown("""
            AttritionSense AI is designed with strict human-in-the-loop ethical principles:
            
            1. **Strict Role Separation:** Employees cannot view HR analytics or other employee records; HR cannot view private BuddyBot chat messages.
            2. **No Punitive Automation:** Risk scores are diagnostic indicators to help leadership support and retain talent, never to automate terminations or adverse actions.
            3. **Zero Manual ML Bias:** Features are drawn directly from objective organizational records; HR does not manually manipulate inputs to alter predictions.
            4. **Confidential Feedback:** Employees have an explicit choice to submit feedback with complete anonymity.
            5. **Decoupled Wellness:** Game play and relaxation activities are completely voluntary and decoupled from attrition risk.
        """)
