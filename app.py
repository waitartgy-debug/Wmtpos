import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('wmt_pro_pos.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY, brand TEXT, model TEXT, imei TEXT UNIQUE, buy_price REAL, sell_price REAL, status TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, type TEXT, customer TEXT, detail TEXT, 
                  total_amount REAL, cost_price REAL, profit REAL, date TEXT, staff_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="WMT Phone & Service Pro", layout="wide")

# --- Authentication System ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.role = None

def login():
    st.sidebar.title("🔐 Login Area")
    user = st.sidebar.text_input("Username")
    pw = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if user == "admin" and pw == "admin123":
            st.session_state.auth = True
            st.session_state.role = "Owner"
        elif user == "staff" and pw == "staff123":
            st.session_state.auth = True
            st.session_state.role = "Staff"
        else:
            st.sidebar.error("Invalid credentials")

if not st.session_state.auth:
    login()
    st.info("System ကို အသုံးပြုရန် Login အရင်ဝင်ပါ။")
    st.stop()

# --- Sidebar Menu ---
st.sidebar.write(f"Logged in as: **{st.session_state.role}**")
if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

menu = ["🛒 အရောင်းနှင့် ဝန်ဆောင်မှု", "📦 Stock စာရင်း"]
if st.session_state.role == "Owner":
    menu.append("📊 စာရင်းချုပ် (Owner Only)")

choice = st.sidebar.radio("Main Menu", menu)
conn = sqlite3.connect('wmt_pro_pos.db')

# --- 1. အရောင်းနှင့် ဝန်ဆောင်မှု ---
if choice == "🛒 အရောင်းနှင့် ဝန်ဆောင်မှု":
    st.title("Sale & Service Point")
    scanned_input = st.text_input("Scan IMEI / Barcode...", placeholder="ဖုန်း IMEI ကို scan ဖတ်ပါ")

    if scanned_input:
        action_type = st.radio("Type:", ["Sale", "Service"], horizontal=True)
        
        if action_type == "Sale":
            phone = pd.read_sql(f"SELECT * FROM inventory WHERE imei='{scanned_input}' AND status='Available'", conn)
            if not phone.empty:
                st.success(f"Model: {phone['brand'].iloc[0]} {phone['model'].iloc[0]}")
                cust = st.text_input("Customer Name")
                price = st.number_input("ရောင်းစျေး (MMK)", value=float(phone['sell_price'].iloc[0]))
                
                if st.button("Confirm Sale"):
                    cost = phone['buy_price'].iloc[0]
                    profit = price - cost
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c = conn.cursor()
                    c.execute("INSERT INTO transactions (type, customer, detail, total_amount, cost_price, profit, date, staff_name) VALUES (?,?,?,?,?,?,?,?)",
                              ("Sale", cust, f"{phone['model'].iloc[0]} ({scanned_input})", price, cost, profit, now, "Staff_1"))
                    c.execute("UPDATE inventory SET status='Sold' WHERE imei=?", (scanned_input,))
                    conn.commit()
                    st.success("ရောင်းချမှု အောင်မြင်ပါသည်။")
            else:
                st.error("Stock မရှိပါ။")

        elif action_type == "Service":
            st.subheader("🔧 Repair Service")
            cust = st.text_input("Customer Name")
            service_type = st.selectbox("ပြုပြင်သည့် အမျိုးအစား", ["Touch + LCD လဲလှယ်ခြင်း", "အသံချို့ယွင်းမှုပြုပြင်ခြင်း", "ဖုန်း အင်တာနာ ပြုပြင်ခြင်း", "အားသွင်းပေါက်ပြုပြင်ခြင်း", "အခြား"])
            
            col1, col2 = st.columns(2)
            # ဝန်ထမ်းတွေအတွက် 'အရင်း' ကို 'Parts Cost' လို့ပဲ ပြပေးထားပါတယ်
            cost = col1.number_input("ပစ္စည်း အရင်းနှီးစရိတ် (Parts Cost)", min_value=0.0)
            total = col2.number_input("ကျသင့်ငွေ စုစုပေါင်း (Total Bill)", min_value=0.0)
            
            if st.button("Save Service"):
                profit = total - cost
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c = conn.cursor()
                c.execute("INSERT INTO transactions (type, customer, detail, total_amount, cost_price, profit, date, staff_name) VALUES (?,?,?,?,?,?,?,?)",
                          ("Service", cust, f"{service_type} ({scanned_input})", total, cost, profit, now, "Staff_1"))
                conn.commit()
                st.success("Service မှတ်တမ်း တည်ဆောက်ပြီးပါပြီ။")

# --- 2. Stock စာရင်း (Staff မြင်ရမည့်ပုံစံတွင် အရင်းဖျောက်ထားသည်) ---
elif choice == "📦 Stock စာရင်း":
    st.title("Inventory List")
    if st.session_state.role == "Owner":
        with st.expander("Add Stock (အရင်းထည့်ရန်)"):
            b, m, im = st.columns(3)
            brand = b.text_input("Brand")
            model = m.text_input("Model")
            imei = im.text_input("IMEI")
            bp = b.number_input("Buy Price (အရင်း)", min_value=0.0)
            sp = m.number_input("Sell Price (ရောင်းစျေး)", min_value=0.0)
            if st.button("Save Inventory"):
                c = conn.cursor()
                c.execute("INSERT INTO inventory (brand, model, imei, buy_price, sell_price, status) VALUES (?,?,?,?,?,'Available')", (brand, model, imei, bp, sp))
                conn.commit()
                st.success("Stored!")

    # View Table
    query = "SELECT brand, model, imei, sell_price, status FROM inventory" if st.session_state.role == "Staff" else "SELECT * FROM inventory"
    df_inv = pd.read_sql(query, conn)
    st.dataframe(df_inv, use_container_width=True)

# --- 3. စာရင်းချုပ် (Owner Only) ---
elif choice == "📊 စာရင်းချုပ် (Owner Only)":
    st.title
