import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page Config ---
st.set_page_config(page_title="WMT Mobile POS Pro", layout="wide", page_icon="📱")

# --- Database Files ---
STOCK_FILE = "wmt_stock_v1.csv"
SALES_FILE = "wmt_sales_v1.csv"

# ဖိုင်မရှိသေးရင် အသစ်ဆောက်ပေးခြင်း
for file, cols in zip([STOCK_FILE, SALES_FILE], 
                     [['barcode', 'item_name', 'category', 'stock_qty', 'cost', 'sell'],
                      ['id', 'customer', 'item_name', 'barcode', 'qty', 'cost', 'sell', 'total', 'profit', 'date', 'time', 'staff', 'payment']]):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)

def load_data(file): return pd.read_csv(file)
def save_data(file, df): df.to_csv(file, index=False)

# --- Session State ---
if 'auth' not in st.session_state: st.session_state.update({'auth': False, 'user': None, 'role': None, 'cart': []})

# --- Logo & Styling ---
LOGO_URL = "https://drive.google.com/thumbnail?id=1S-ga29FKEi5ekqDAeJ2F1dDENWUTxUvP&sz=w500"

# --- Login System ---
if not st.session_state.auth:
    st.image(LOGO_URL, width=120)
    st.title("WMT Mobile POS Login")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("ဝင်မည်"):
            if u == "admin" and p == "wmtadmin123":
                st.session_state.update({'auth': True, 'role': 'admin', 'user': 'Wai Min Tar'})
                st.rerun()
            elif u == "staff1" and p == "wmtstaff456":
                st.session_state.update({'auth': True, 'role': 'staff', 'user': 'Staff-01'})
                st.rerun()
    st.stop()

# --- Navigation ---
st.sidebar.image(LOGO_URL, width=80)
st.sidebar.markdown(f"👤 **{st.session_state.user}**")
menu = st.sidebar.radio("Main Menu", ["📊 Dashboard", "📦 ပစ္စည်းစာရင်းသွင်းရန်", "🛒 အရောင်းဖွင့်ရန်", "📋 အရောင်းမှတ်တမ်း"])

# --- 1. Dashboard ---
if menu == "📊 Dashboard":
    st.header("📊 ယနေ့ လုပ်ငန်းအခြေအနေ")
    sdf = load_data(SALES_FILE)
    stdf = load_data(STOCK_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    tdf = sdf[sdf['date'] == today]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 ယနေ့ရောင်းရငွေ", f"{tdf['total'].sum():,.0f} MMK")
    if st.session_state.role == 'admin':
        c2.metric("📈 ယနေ့အမြတ်", f"{tdf['profit'].sum():,.0f} MMK")
    c3.metric("⚠️ လက်ကျန်နည်းသောပစ္စည်း", len(stdf[stdf['stock_qty'] < 3]))
    
    st.subheader("📦 လက်ရှိပစ္စည်းစာရင်း (Stock List)")
    st.dataframe(stdf, use_container_width=True)

# --- 2. Inventory (ပစ္စည်းစာရင်းသွင်းရန်) ---
elif menu == "📦 ပစ္စည်းစာရင်းသွင်းရန်":
    st.header("📦 ပစ္စည်းအသစ်ထည့်ခြင်း / Stock ဖြည့်ခြင်း")
    stdf = load_data(STOCK_FILE)
    
    with st.form("inventory_form"):
        col1, col2 = st.columns(2)
        b_code = col1.text_input("🔍 Barcode Scan ဖတ်ပါ")
        i_name = col2.text_input("📦 ပစ္စည်းအမည်")
        cat = st.selectbox("📁 အမျိုးအစား", ["Handset", "Accessory", "Service", "Software"])
        
        c3, c4, c5 = st.columns(3)
        s_qty = c3.number_input("🔢 အရေအတွက်သွင်းရန်", min_value=1, value=1)
        c_price = c4.number_input("📉 အရင်းစျေး (၁ ခုစာ)", min_value=0)
        s_price = c5.number_input("💵 ရောင်းစျေး (၁ ခုစာ)", min_value=0)
        
        if st.form_submit_button("✅ စာရင်းသွင်းမည်"):
            if not b_code or not i_name:
                st.error("Barcode နှင့် ပစ္စည်းအမည် ထည့်ပေးပါ")
            else:
                if b_code in stdf['barcode'].astype(str).values:
                    # ရှိပြီးသားဆိုရင် stock ပဲတိုးမယ်
                    stdf.loc[stdf['barcode'].astype(str) == b_code, 'stock_qty'] += s_qty
                    stdf.loc[stdf['barcode'].astype(str) == b_code, 'cost'] = c_price
                    stdf.loc[stdf['barcode'].astype(str) == b_code, 'sell'] = s_price
                    st.info("ရှိပြီးသားပစ္စည်းတွင် အရေအတွက် တိုးလိုက်ပါပြီ။")
                else:
                    # အသစ်ဆိုရင် အသစ်ထည့်မယ်
                    new_item = pd.DataFrame([{'barcode': b_code, 'item_name': i_name, 'category': cat, 'stock_qty': s_qty, 'cost': c_price, 'sell': s_price}])
                    stdf = pd.concat([stdf, new_item], ignore_index=True)
                    st.success("ပစ္စည်းအသစ် ထည့်သွင်းပြီးပါပြီ။")
                save_data(STOCK_FILE, stdf)

# --- 3. POS (အရောင်းဖွင့်ရန်) ---
elif menu == "🛒 အရောင်းဖွင့်ရန်":
    st.header("🛒 အရောင်းဘောင်ချာ")
    stdf = load_data(STOCK_FILE)
    
    cus = st.text_input("👤 ဝယ်သူအမည်", value="Guest")
    scan = st.text_input("🔍 Scan Barcode (ပစ္စည်းရောင်းရန်)")
    
    if scan:
        item = stdf[stdf['barcode'].astype(str) == scan]
        if not item.empty:
            i_row = item.iloc[0]
            st.success(f"တွေ့ရှိသည်: {i_row['item_name']} (လက်ကျန်: {i_row['stock_qty']})")
            
            with st.container():
                c1, c2, c3 = st.columns(3)
                s_price = c1.number_input("ရောင်းစျေး", value=float(i_row['sell']))
                qty_to_sell = c2.number_input("အရေအတွက်", min_value=1, max_value=int(i_row['stock_qty']), value=1)
                pay_method = c3.selectbox("ငွေချေမှု", ["Cash", "KPay", "Wave"])
                
                if st.button("➕ ခြင်းတောင်းထဲထည့်မည်"):
                    st.session_state.cart.append({
                        'customer': cus, 'item_name': i_row['item_name'], 'barcode': scan, 
                        'qty': qty_to_sell, 'cost': i_row['cost'], 'sell': s_price, 'payment': pay_method
                    })
                    st.rerun()
        else:
            st.error("❌ ဤ Barcode မှာ Stock စာရင်းထဲတွင် မရှိသေးပါ။ အရင်စာရင်းသွင်းပါ။")

    if st.session_state.cart:
        st.write("---")
        cdf = pd.DataFrame(st.session_state.cart)
        st.table(cdf
