import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

st.set_page_config(page_title="WMT Mobile POS Pro", layout="wide")

# --- Database Setup ---
DATA_FILE = "wmt_pos_data.csv"
COLUMNS = ['id', 'type', 'item_name', 'qty', 'cost_price', 'sell_price', 'total_amount', 'profit', 'date', 'staff']

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(new_data):
    df = load_data()
    df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- UI Styling ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; background-color: #28a745; color: white; height: 3em; }
    .stHeader { color: #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- Authentication ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user_role': None, 'username': None, 'cart': [], 'last_receipt': None})

if not st.session_state.auth:
    st.title("🔐 WMT POS - ဆိုင်ဝင်ရန်")
    user_type = st.radio("အကောင့်အမျိုးအစား", ["Admin (ဆိုင်ရှင်)", "Staff (ဝန်ထမ်း)"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if user_type == "Admin (ဆိုင်ရှင်)" and user == "admin" and pw == "wmtadmin123":
            st.session_state.update({'auth': True, 'user_role': 'admin', 'username': 'Admin'})
            st.rerun()
        elif user_type == "Staff (ဝန်ထမ်း)" and user == "staff1" and pw == "wmtstaff456":
            st.session_state.update({'auth': True, 'user_role': 'staff', 'username': 'Staff 1'})
            st.rerun()
        else:
            st.error("Username သို့မဟုတ် Password မှားနေပါသည်။")
    st.stop()

# --- Sidebar Navigation ---
st.sidebar.title(f"WMT Mobile POS")
st.sidebar.write(f"🧑‍💼 **{st.session_state.username}**")

menu = ["🏠 Dashboard", "🛒 အရောင်းဖွင့်ရန်"]
if st.session_state.user_role == 'admin':
    menu.append("📋 စာရင်းမှတ်တမ်း")

choice = st.sidebar.radio("Menu", menu)

# --- Voucher Generator ---
def generate_voucher_text(tid, df_cart):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    v = "      WMT Phone & Service\n"
    v += "    ------------------------\n"
    v += f"  ID: {tid}\n"
    v += f"  Date: {now}\n"
    v += f"  Staff: {st.session_state.username}\n"
    v += "  --------------------------\n"
    v += f"{'Item':<15} {'Qty':<3} {'Price':>7}\n"
    total = 0
    for _, row in df_cart.iterrows():
        v += f"{row['item_name'][:14]:<15} {row['qty']:<3} {row['sell_price']:>7,.0f}\n"
        total += row['sell_price'] * row['qty']
    v += "  --------------------------\n"
    v += f"  Total:      {total:>10,.0f} MMK\n"
    v += "  --------------------------\n"
    v += "   ကျေးဇူးတင်ပါသည် (WMT)\n"
    return v

# --- 1. Dashboard ---
if choice == "🏠 Dashboard":
    st.header("🏠 ယနေ့ လုပ်ငန်းအခြေအနေ")
    df = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    tdf = df[df['date'] == today]
    
    c1, c2 = st.columns(2)
    c1.metric("ယနေ့ရောင်းရငွေ", f"{tdf['total_amount'].sum():,.0f} MMK")
    if st.session_state.user_role == 'admin':
        c2.metric("ယနေ့အမြတ်", f"{tdf['profit'].sum():,.0f} MMK")
    
    st.write("### လတ်တလော အရောင်း")
    st.dataframe(df.tail(10), use_container_width=True)

# --- 2. Sales & POS ---
elif choice == "🛒 အရောင်းဖွင့်ရန်":
    st.header("🛒 POS အရောင်းဘောင်ချာ")
    
    # QR/Barcode Scanner အတွက် input
    barcode = st.text_input("ပစ္စည်းအမည် သို့မဟုတ် Barcode စကန်ဖတ်ပါ", key="scan")
    col1, col2 = st.columns(2)
    s_price = col1.number_input("ရောင်းစျေး", min_value=0)
    c_price = col2.number_input("အရင်းစျေး (Admin သာ)", min_value=0) if st.session_state.user_role == 'admin' else 0
    qty = st.number_input("အရေအတွက်", min_value=1, value=1)

    if st.button("ခြင်းတောင်းထဲထည့်မည်"):
        if barcode and s_price > 0:
            st.session_state.cart.append({
                'item_name': barcode, 'qty': qty, 
                'cost_price': c_price, 'sell_price': s_price
            })
            st.rerun()

    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.table(df_cart)
        
        if st.button("ဘောင်ချာထုတ်ပြီး စာရင်းသွင်းမည်"):
            tid = f"WMT{datetime.now().strftime('%m%d%H%M%S')}"
            final_data = []
            for _, r in df_cart.iterrows():
                final_data.append({
                    'id': tid, 'type': 'Sale', 'item_name': r['item_name'],
                    'qty': r['qty'], 'cost_price': r['cost_price'],
                    'sell_price': r['sell_price'], 'total_amount': r['sell_price'] * r['qty'],
                    'profit': (r['sell_price'] - r['cost_price']) * r['qty'],
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'staff': st.session_state.username
                })
            save_data(final_data)
            st.session_state.last_receipt = generate_voucher_text(tid, df_cart)
            st.session_state.cart = []
            st.success("စာရင်းသွင်းပြီးပါပြီ")
            st.rerun()

    if st.session_state.last_receipt:
        st.text_area("Voucher Preview", st.session_state.last_receipt, height=300)
        st.download_button("📥 Voucher Download", st.session_state.last_receipt, "voucher.txt")
        if st.button("ဘောင်ချာအသစ်ဖွင့်ရန်"):
            st.session_state.last_receipt = None
            st.rerun()

# --- 3. Logs (Admin Only) ---
elif choice == "📋 စာရင်းမှတ်တမ်း":
    st.header("📋 အရောင်းမှတ်တမ်းအပြည့်အစုံ")
    df = load_data()
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Excel ထုတ်ယူရန်", csv, "wmt_sales.csv", "text/csv")

if st.sidebar.button("Log out"):
    st.session_state.update({'auth': False, 'user_role': None, 'username': None, 'cart': [], 'last_receipt': None})
    st.rerun()
