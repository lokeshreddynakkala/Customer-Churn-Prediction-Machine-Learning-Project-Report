import streamlit as st
import pandas as pd
import joblib
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="ChurnGuard | Customer Retention Tool",
    page_icon="📊",
    layout="wide"
)

# --- Custom CSS for Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Metric text color styling */
    [data-testid="stMetricValue"] {
        color: #1c4966; /* Deep Blue */
    }
    [data-testid="stMetricLabel"] {
        color: #000000; /* Black */
    }
    </style>
    """, unsafe_allow_html=True)

# --- Load Model ---
@st.cache_resource
def load_model():
    # Note: Ensure the path is correct
    return joblib.load('Chun_prediction_model.h5')

try:
    model = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3121/3121768.png", width=100)
    st.title("ChurnGuard AI")
    st.info("This tool uses machine learning to predict the likelihood of a customer leaving the bank.")
    st.markdown("---")
    st.markdown("### Model Info")
    st.text("Type: Gradient Boosting Classifier")

# --- Main Interface ---
st.title('📈 Customer Churn Analytics')
st.markdown("Fill in the customer profile below to generate a retention risk assessment.")

# Use Columns to organize inputs
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👤 Demographics")
    Geography = st.selectbox('Geography', ['France', 'Spain', 'Germany'])
    Gender = st.selectbox('Gender', ['Male', 'Female'])
    Age = st.number_input('Age', min_value=18, max_value=100, value=35)
    Tenure = st.slider('Tenure (Years)', 0, 10, 5)

with col2:
    st.subheader("💳 Financial Profile")
    CreditScore = st.number_input('Credit Score', 300, 850, 650)
    Balance = st.number_input('Account Balance ($)', min_value=0.0, value=50000.0, step=500.0)
    EstimatedSalary = st.number_input('Estimated Salary ($)', min_value=0.0, value=75000.0, step=500.0)

with col3:
    st.subheader("📱 Product Usage")
    NumOfProducts = st.selectbox('Number of Products', [1, 2, 3, 4])
    HasCrCard = st.radio('Has Credit Card?', ['Yes', 'No'], horizontal=True)
    IsActiveMember = st.radio('Is Active Member?', ['Yes', 'No'], horizontal=True)

# --- Data Transformation ---
# Mapping Logic
gender_map = {'Male': [1, 0], 'Female': [0, 1]}
g_m, g_f = gender_map[Gender]

geo_map = {'France': [1, 0], 'Germany': [0, 1], 'Spain': [0, 0]}
geo_f, geo_g = geo_map[Geography]

input_df = pd.DataFrame({
    'CreditScore': [CreditScore],
    'Age': [Age],
    'Tenure': [Tenure],
    'Balance': [Balance],
    'NumOfProducts': [NumOfProducts],
    'EstimatedSalary': [EstimatedSalary],
    'HasCrCard': [1 if HasCrCard == 'Yes' else 0],
    'IsActiveMember': [1 if IsActiveMember == 'Yes' else 0],
    'Gender_Male': [g_m],
    'Gender_Female': [g_f],
    'Geography_France': [geo_f],
    'Geography_Germany': [geo_g]
})

# --- Prediction Logic ---
st.markdown("---")
if st.button('Analyze Retention Risk'):
    prediction = model.predict(input_df)
    prediction_proba = model.predict_proba(input_df)[0][1]
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.subheader("Risk Assessment")
        if prediction[0] == 0:
            st.success("### LOW RISK", icon="✅")
            st.write("This customer is likely to stay with the bank.")
        else:
            st.warning("### HIGH RISK", icon="⚠️")
            st.write("This customer shows high probability of churning.")

    with res_col2:
        st.subheader("Churn Probability")
        # Custom HTML card for better visual appearance
        churn_percentage = prediction_proba * 100
        st.markdown(f"""
            <div style="
                background-color: #e1effe; 
                padding: 20px; 
                border-radius: 10px; 
                border-left: 5px solid #1c4966;
                text-align: center;">
                <p style="color: #1c4966; font-size: 18px; margin-bottom: 5px; font-weight: bold;">
                    Calculated Churn Risk
                </p>
                <h2 style="color: #000000; margin-top: 0px;">
                    {churn_percentage:.2f}%
                </h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar for visual representation
        st.progress(prediction_proba)

#
