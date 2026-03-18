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
    .main { background-color: #f4f7f6; }
    .reportview-container .main .block-container{ padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- Authentication (admin/staff) ---
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user_role': None, 'username': None, 'cart': [], 'last_receipt': None})

def login_form():
    st.title("🔐 WMT POS - ဆိုင်ဝင်ရန်")
    user_type = st.radio("အကောင့်အမျိုးအစား", ["Admin (ဆိုင်ရှင်)", "Staff (ဝန်ထမ်း)"])
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Login စကားဝှက်များကို ဒီမှာ သတ်မှတ်ပါ
        if user_type == "Admin (ဆိုင်ရှင်)" and user == "admin" and pw == "wmtadmin123":
            st.session_state.update({'auth': True, 'user_role': 'admin', 'username': 'Admin'})
            st.rerun()
        elif user_type == "Staff (ဝန်ထမ်း)" and user == "staff1" and pw == "wmtstaff456":
            st.session_state.update({'auth': True, 'user_role': 'staff', 'username': 'Staff 1'})
            st.rerun()
        else:
            st.error("အသုံးပြုသူအမည် သို့မဟုတ် လျှို့ဝှက်နံပါတ် မှားယွင်းနေပါသည်။")

if not st.session_state.auth:
    login_form()
    st.stop()

# --- Navigation ---
st.sidebar.title(f"WMT Mobile POS")
st.sidebar.write(f"🧑‍💼 **{st.session_state.username}** ({st.session_state.user_role})")

if st.session_state.user_role == 'admin':
    menu = ["🏠 Dashboard", "🛒 အရောင်းဖွင့်ရန်", "📋 စာရင်းမှတ်တမ်း", "📦 ပစ္စည်းစာရင်း"]
else:
    menu = ["🏠 Dashboard", "🛒 အရောင်းဖွင့်ရန်"]

choice = st.sidebar.radio("သွားရောက်လိုသည့်နေရာ", menu)

# --- Functions ---
def generate_voucher_text(transaction_id, df_cart):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    v = f"--- WMT Phone & Service ---\n"
    v += f"Address: Your Shop Address Here\n"
    v += f"Phone: Your Phone Number\n"
    v += f"--------------------------\n"
    v += f"Voucher ID: {transaction_id}\n"
    v += f"Date: {now}\n"
    v += f"Staff: {st.session_state.username}\n"
    v += f"--------------------------\n"
    v += f"{'Item':<16} {'Qty':<3} {'Price':>8}\n"
    v += f"--------------------------\n"
    
    total = 0
    for _, row in df_cart.iterrows():
        name = row['item_name'][:15]
        v += f"{name:<16} {row['qty']:<3} {row['sell_price']:>8,.0f}\n"
        total += row['sell_price'] * row['qty']
        
    v += f"--------------------------\n"
    v += f"{'Grand Total':<19} {total:>8,.0f}\n"
    v += f"--------------------------\n"
    v += f"*** Thank You! ***\n"
    return v

# --- 1. Dashboard ---
if choice == "🏠 Dashboard":
    st.header("🏠 ယနေ့ လုပ်ငန်းအခြေအနေ")
    df = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # ယနေ့ဒေတာများ
    today_df = df[df['date'] == today]
    
    c1, c2, c3 = st.columns(3)
    
    if st.session_state.user_role == 'admin':
        total_sales = today_df['total_amount'].sum()
        total_profit = today_df['profit'].sum()
        
        c1.metric("ယနေ့ရောင်းရငွေ", f"{total_sales:,.0f} ကျပ်")
        c2.metric("ယနေ့အမြတ်", f"{total_profit:,.0f} ကျပ်", delta=f"{total_profit:,.0f}")
        c3.metric("စုစုပေါင်း မှတ်တမ်း", f"{len(df)} ခု")
    else:
        # Staff အတွက် အမြတ်မပြပါ
        total_sales = today_df['total_amount'].sum()
        c1.metric("ယနေ့ရောင်းရငွေ", f"{total_sales:,.0f} ကျပ်")
        c2.metric("စုစုပေါင်း မှတ်တမ်း", f"{len(df)} ခု")
        c3.empty()

    st.write("### လတ်တလော အရောင်းမှတ်တမ်း")
    display_cols = ['id', 'item_name', 'qty', 'total_amount', 'date', 'staff']
    if st.session_state.user_role == 'admin': display_cols.append('profit')
    
    st.dataframe(df[display_cols].tail(10), use_container_width=True)

# --- 2. Sales & Voucher ---
elif choice == "🛒 အရောင်းဖွင့်ရန်":
    st.header("🛒 အရောင်းနှင့် ဝန်ဆောင်မှု")
    
    # -- Cart Section --
    st.subheader("🛒 ခြင်းတောင်း")
    col1, col2 = st.columns(2)
    
    # ပစ္စည်းထည့်ရန် (Barcode/QR စကန်ဖတ်ရန် ဤနေရာတွင် Text input သုံးပါ)
    # (ဖုန်းကင်မရာနှင့် စကန်ဖတ်ရန် Streamlit တွင် direct native support မရှိပါ၊ Barcode Scanner device သုံးပါ သို့မဟုတ် manual ရိုက်ထည့်ပါ)
    barcode = st.text_input("ပစ္စည်းအမည် သို့မဟုတ် Barcode", placeholder="ဥပမာ- iPhone 15, Barcode Scan ဖတ်ပါ")
    qty = st.number_input("အရေအတွက်", min_value=1, value=1)
    
    # 🛒 ခြင်းတောင်းထဲထည့်ရန် Button
    if st.button("ခြင်းတောင်းထဲထည့်မည်"):
        if barcode:
            # လောလောဆယ် manual စျေးနှုန်းသတ်မှတ်ချက် (နောက်ပိုင်း inventory database နှင့် ချိတ်ဆက်ရန်)
            new_item = {
                'item_name': barcode,
                'qty': qty,
                'cost_price': 0,  # အမြတ်တွက်ရန် ရောင်းစျေးကိုပဲ သုံးပါ
                'sell_price': 0,
            }
            st.session_state.cart.append(new_item)
            st.rerun()
        else:
            st.error("ပစ္စည်းအမည် ထည့်သွင်းပါ။")

    # -- Display Cart --
    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.write("#### ခြင်းတောင်းထဲရှိ ပစ္စည်းများ")
        
        # စျေးနှုန်းသတ်မှတ်ရန်
        for i, row in df_cart.iterrows():
            st.write(f"--- {row['item_name']} ---")
            c1, c2 = st.columns(2)
            row_sell_price = c1.number_input(f"ရောင်းစျေး (ကျပ်) - {row['item_name']}", min_value=0, value=0, key=f"sell_{i}")
            
            # Admin သာ အရင်းထည့်ခွင့်ရှိပြီး အမြတ်တွက်မည်
            row_cost_price = 0
            if st.session_state.user_role == 'admin':
                row_cost_price = c2.number_input(f"အရင်းစျေး (ကျပ်) - {row['item_name']}", min_value=0, value=0, key=f"cost_{i}")
            
            # Update dataframe
            df_cart.at[i, 'sell_price'] = row_sell_price
            df_cart.at[i, 'cost_price'] = row_cost_price

        grand_total = (df_cart['sell_price'] * df_cart['qty']).sum()
        st.write(f"### Сုစုပေါင်းကျသင့်ငွေ: **{grand_total:,.0f} MMK**")
        
        # -- Checkout Button --
        if st.button("ရောင်းမည် (Voucher ထုတ်မည်)"):
            if grand_total > 0:
                transaction_id = f"WMT{datetime.now().strftime('%Y%m%d%H%M%S')}"
                today = datetime.now().strftime("%Y-%m-%d")
                
                final_sales = []
                for _, row in df_cart.iterrows():
                    cost = row['cost_price'] if row['cost_price'] > 0 else 0
                    profit = (row['sell_price'] - cost) * row['qty']
                    
                    final_sales.append({
                        'id': transaction_id,
                        'type': 'အရောင်း',
                        'item_name': row['item_name'],
                        'qty': row['qty'],
                        'cost_price': cost,
                        'sell_price': row['sell_price'],
                        'total_amount': row['sell_price'] * row['qty'],
                        'profit': profit,
                        'date': today,
                        'staff': st.session_state.username
                    })
                
                save_data(final_sales)
                st.session_state.last_receipt = generate_voucher_text(transaction_id, df_cart)
                st.session_state.cart = [] # ခြင်းတောင်းရှင်းပါ
                st.success("ရောင်းချမှု အောင်မြင်ပါသည်။")
                st.rerun()
            else:
                st.error("စျေးနှုန်းသတ်မှတ်ပေးပါ။")

    # -- Voucher Display & Download --
    if st.session_state.last_receipt:
        st.write("#### နောက်ဆုံး ဘောင်ချာ (Voucher)")
        st.text(st.session_state.last_receipt)
        
        # Voucher ကို Text ဖိုင်အနေနဲ့ Download လုပ်ရန်
        receipt_io = io.BytesIO()
        receipt_io.write(st.session_state.last_receipt.encode())
        st.download_button(
            label="📥 ဘောင်ချာ Download ဆွဲမည် (Voucher)",
            data=receipt_io.getvalue(),
            file_name=f"wmt_receipt_{datetime.now().strftime('%H%M%S')}.txt",
            mime="text/plain"
        )
        if st.button("ဘောင်ချာပိတ်မည်"):
            st.session_state.last_receipt = None
            st.rerun()

# --- 3. Logs (Admin Only) ---
elif choice == "📋 စာရင်းမှတ်တမ်း":
    st.header("📋 စုစုပေါင်း အရောင်းမှတ်တမ်း")
    df = load_data()
    st.dataframe(df, use_container_width=True)
    
    # Excel ဖိုင်ထုတ်ရန်
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Download Excel (CSV)",
            data=csv,
            file_name=f'wmt_all_sales_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )

# --- 4. Inventory (Admin Only) ---
elif choice == "📦 ပစ္စည်းစာရင်း":
    st.header("📦 ပစ္စည်းစာရင်း (လောလောဆယ် သရုပ်ပြရန်သာ)")
    st.info("နောက်ပိုင်းတွင် ပစ္စည်းစာရင်းသွင်းရန်နှင့် စကန်ဖတ်ရန် Feature ကို ဤနေရာတွင် ထည့်သွင်းနိုင်ပါသည်။")
    st.write("လတ်တလောတွင် '🛒 အရောင်းဖွင့်ရန်' ၌ ပစ္စည်းအမည်ကို manual ရိုက်ထည့်ခြင်း သို့မဟုတ် Barcode Device ဖြင့် စကန်ဖတ်ခြင်း
