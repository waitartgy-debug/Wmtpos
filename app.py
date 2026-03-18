import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Page Configuration ---
st.set_page_config(page_title="WMT Mobile POS Pro", layout="wide", page_icon="📱")

# --- Database Files ---
STOCK_FILE = "wmt_stock_v2.csv"
SALES_FILE = "wmt_sales_v2.csv"

# ဖိုင်မရှိသေးရင် Header နဲ့တကွ တစ်ခါတည်း ဆောက်ပေးခြင်း
for file, cols in zip([STOCK_FILE, SALES_FILE], 
                     [['barcode', 'item_name', 'category', 'stock_qty', 'cost', 'sell'],
                      ['id', 'customer', 'item_name', 'barcode', 'qty', 'cost', 'sell', 'total', 'profit', 'date', 'time', 'staff', 'payment']]):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file, index=False)

def load_data(file): 
    return pd.read_csv(file, dtype={'barcode': str})

def save_data(file, df): 
    df.to_csv(file, index=False)

# --- Session State ---
if 'auth' not in st.session_state: 
    st.session_state.update({'auth': False, 'user': None, 'role': None, 'cart': [], 'last_receipt': None})

# --- Logo & Branding ---
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
            else: st.error("❌ Username သို့မဟုတ် Password မှားယွင်းနေပါသည်။")
    st.stop()

# --- Sidebar ---
st.sidebar.image(LOGO_URL, width=80)
st.sidebar.markdown(f"👤 **{st.session_state.user}**")
menu = st.sidebar.radio("Main Menu", ["📊 Dashboard", "📦 ပစ္စည်းစာရင်းသွင်းရန် (Inventory)", "🛒 အရောင်းဖွင့်ရန် (POS)", "📋 အရောင်းမှတ်တမ်း"])

# --- 1. Dashboard ---
if menu == "📊 Dashboard":
    st.header("📊 ယနေ့ လုပ်ငန်းအခြေအနေ")
    sdf, stdf = load_data(SALES_FILE), load_data(STOCK_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    tdf = sdf[sdf['date'] == today]
    
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 ယနေ့ရောင်းရငွေ", f"{tdf['total'].sum():,.0f} MMK")
    if st.session_state.role == 'admin':
        c2.metric("📈 ယနေ့အမြတ်", f"{tdf['profit'].sum():,.0f} MMK")
    c3.metric("⚠️ လက်ကျန်နည်းပစ္စည်း", len(stdf[stdf['stock_qty'] < 3]))
    
    st.subheader("📦 လက်ကျန်ပစ္စည်းစာရင်း")
    st.dataframe(stdf, use_container_width=True)

# --- 2. Inventory (ပစ္စည်းစာရင်းသွင်းရန်) ---
elif menu == "📦 ပစ္စည်းစာရင်းသွင်းရန် (Inventory)":
    st.header("📦 ပစ္စည်းအသစ်ထည့်ခြင်း / Stock ဖြည့်ခြင်း")
    stdf = load_data(STOCK_FILE)
    
    with st.form("inventory_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        b_code = col1.text_input("🔍 Barcode Scan ဖတ်ပါ (သို့မဟုတ်) ရိုက်ထည့်ပါ")
        i_name = col2.text_input("📦 ပစ္စည်းအမည်")
        cat = st.selectbox("📁 အမျိုးအစား", ["Handset", "Accessory", "Service", "Software"])
        
        c3, c4, c5 = st.columns(3)
        s_qty = c3.number_input("🔢 အရေအတွက်သွင်းရန်", min_value=1, value=1)
        c_price = c4.number_input("📉 အရင်းစျေး (၁ ခုစာ)", min_value=0)
        s_price = c5.number_input("💵 ရောင်းစျေး (၁ ခုစာ)", min_value=0)
        
        if st.form_submit_button("✅ စာရင်းသွင်းမည်"):
            if b_code and i_name:
                if b_code in stdf['barcode'].values:
                    stdf.loc[stdf['barcode'] == b_code, 'stock_qty'] += s_qty
                    stdf.loc[stdf['barcode'] == b_code, 'cost'] = c_price
                    stdf.loc[stdf['barcode'] == b_code, 'sell'] = s_price
                    st.success(f"✅ {i_name} ၏ လက်ကျန်ကို တိုးလိုက်ပါပြီ။")
                else:
                    new_item = pd.DataFrame([{'barcode': b_code, 'item_name': i_name, 'category': cat, 'stock_qty': s_qty, 'cost': c_price, 'sell': s_price}])
                    stdf = pd.concat([stdf, new_item], ignore_index=True)
                    st.success(f"✅ ပစ္စည်းအသစ် {i_name} ကို စာရင်းသွင်းပြီးပါပြီ။")
                save_data(STOCK_FILE, stdf)
            else: st.warning("⚠️ Barcode နှင့် ပစ္စည်းအမည်ကို ဖြည့်စွက်ပေးပါ။")

# --- 3. POS (အရောင်းဖွင့်ရန်) ---
elif menu == "🛒 အရောင်းဖွင့်ရန် (POS)":
    st.header("🛒 အရောင်းဘောင်ချာ")
    stdf = load_data(STOCK_FILE)
    
    cus = st.text_input("👤 ဝယ်သူအမည်", value="Guest")
    scan = st.text_input("🔍 Barcode Scan ဖတ်ရန်", placeholder="Barcode ကို ဤနေရာတွင် Scan ဖတ်ပါ")
    
    if scan:
        item = stdf[stdf['barcode'] == scan]
        if not item.empty:
            i_row = item.iloc[0]
            st.info(f"ပစ္စည်း: {i_row['item_name']} (လက်ကျန်: {i_row['stock_qty']})")
            
            with st.container():
                c1, c2, c3 = st.columns(3)
                s_price = c1.number_input("ရောင်းစျေး", value=float(i_row['sell']))
                qty_sale = c2.number_input("အရေအတွက်", min_value=1, max_value=int(i_row['stock_qty']), value=1)
                pay_type = c3.selectbox("ငွေပေးချေမှု", ["Cash", "KPay", "Wave"])
                
                if st.button("➕ ခြင်းတောင်းထဲထည့်မည်"):
                    st.session_state.cart.append({
                        'customer': cus, 'item_name': i_row['item_name'], 'barcode': scan, 
                        'qty': qty_sale, 'cost': i_row['cost'], 'sell': s_price, 'payment': pay_type
                    })
                    st.rerun()
        else: st.error("❌ ဤ Barcode မှာ Stock စာရင်းထဲတွင် မရှိသေးပါ။")

    if st.session_state.cart:
        st.write("---")
        cdf = pd.DataFrame(st.session_state.cart)
        st.table(cdf[['item_name', 'qty', 'sell', 'payment']])
        
        total_bill = (cdf['sell'] * cdf['qty']).sum()
        st.subheader(f"💵 စုစုပေါင်း: {total_bill:,.0f} MMK")
        
        if st.button("✅ စာရင်းသိမ်းမည်"):
            sales_df = load_data(SALES_FILE)
            tid = f"WMT{datetime.now().strftime('%y%m%d%H%M%S')}"
            dt, tm = datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%I:%M %p")
            
            receipt_text = f"WMT Mobile POS\n{dt} {tm}\n------------------\n"
            for r in st.session_state.cart:
                # Stock နှုတ်ခြင်း
                stdf.loc[stdf['barcode'] == r['barcode'], 'stock_qty'] -= r['qty']
                # Sales သွင်းခြင်း
                new_row = {'id': tid, 'customer': r['customer'], 'item_name': r['item_name'], 'barcode': r['barcode'], 'qty': r['qty'], 'cost': r['cost'], 'sell': r['sell'], 'total': r['sell']*r['qty'], 'profit': (r['sell']-r['cost'])*r['qty'], 'date': dt, 'time': tm, 'staff': st.session_state.user, 'payment': r['payment']}
                sales_df = pd.concat([sales_df, pd.DataFrame([new_row])], ignore_index=True)
                receipt_text += f"{r['item_name']} x {r['qty']} = {r['sell']*r['qty']:,}\n"
            
            save_data(STOCK_FILE, stdf)
            save_data(SALES_FILE, sales_df)
            receipt_text += f"------------------\nTOTAL: {total_bill:,} MMK\nကျေးဇူးတင်ပါသည်"
            st.session_state.last_receipt = receipt_text
            st.session_state.cart = []
            st.success("✅ စာရင်းသိမ်းပြီးပါပြီ")
            st.rerun()

    if st.session_state.last_receipt:
        st.text_area("Voucher Preview", st.session_state.last_receipt, height=200)
        if st.button("🔄 ဘောင်ချာအသစ်ဖွင့်ရန်"):
            st.session_state.last_receipt = None
            st.rerun()

# --- 4. Records ---
elif menu == "📋 အရောင်းမှတ်တမ်း":
    st.header("📋 အရောင်းမှတ်တမ်းအပြည့်အစုံ")
    st.dataframe(load_data(SALES_FILE), use_container_width=True)

if st.sidebar.button("🚪 Logout"):
    st.session_state.auth = False
    st.rerun()
