import streamlit as st

st.set_page_config(page_title="Privacy Policy")

st.title("Privacy Policy")
st.write("""
Last updated: 10 May 2026

## 1. Information We Collect
SellSmart AI collects minimal data necessary to operate the Service, including:
- text you input into the generator  
- usage counts (free vs premium)  
- payment confirmation from Stripe (no card details)  

## 2. How We Use Your Data
We use your data to:
- generate listings  
- manage free‑use limits  
- verify premium access  

## 3. Data Sharing
We do not sell or share your data with third parties except:
- Stripe (for payment processing)  
- Streamlit (for hosting)  

## 4. Data Retention
We retain minimal operational data only as long as necessary.

## 5. Security
We use industry‑standard security measures but cannot guarantee absolute protection.

## 6. Your Rights (UK GDPR)
You have the right to:
- request deletion  
- request access  
- request correction  

## 7. Contact
privacy@sellsmartai.app
""")
