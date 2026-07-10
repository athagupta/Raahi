cd ..import streamlit as st
import json
import os

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Raahi", page_icon="🧭", layout="centered")

st.markdown("<h1 style='text-align: center; color: #4EA8DE;'>Raahi: Travel & Expense Companion</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7A6F7D;'>Track group expenses and explore destinations seamlessly.</p>", unsafe_allow_html=True)

# --- TRACK TRAVELERS GLOBALLY ---
if "members" not in st.session_state:
    st.session_state["members"] = []

# --- COMPARTMENTALIZED EXPENSES ---
if "expenses" not in st.session_state:
    st.session_state["expenses"] = {}

# --- DYNAMICALLY LOAD DESTINATIONS FROM EXTERNAL JSON ---
@st.cache_data
def load_travel_guide():
    file_path = "destinations.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Default fallback matching the updated nested JSON structure
    return {
        "Goa (India)": {
            "country": "India",
            "currency_code": "INR",
            "inr_exchange_rate": 1.0,
            "attractions": [{"name": "Default Spot", "desc": "Please ensure destinations.json exists."}]
        }
    }

TRAVEL_GUIDE = load_travel_guide()

# --- SIDEBAR: COMPARTMENT MANAGEMENT ---
st.sidebar.markdown("<h2 style='color: #4EA8DE;'>Trip Settings</h2>", unsafe_allow_html=True)

destination_list = sorted(list(TRAVEL_GUIDE.keys()))
destination = st.sidebar.selectbox("Choose Destination Compartment", options=destination_list, index=0)

# Extract city-specific metadata from the updated nested dictionary structure
city_metadata = TRAVEL_GUIDE.get(destination, {"currency_code": "INR", "inr_exchange_rate": 1.0})
local_currency = city_metadata.get("currency_code", "INR")
exchange_rate = city_metadata.get("inr_exchange_rate", 1.0)

# Initialize a private folder for the selected city if it doesn't exist yet
if destination not in st.session_state["expenses"]:
    st.session_state["expenses"][destination] = []

st.sidebar.write("---")
st.sidebar.markdown("<h3 style='color: #4EA8DE;'>Travelers</h3>", unsafe_allow_html=True)
new_member = st.sidebar.text_input("Add traveler name:")
if st.sidebar.button("Add Traveler"):
    if new_member and new_member not in st.session_state["members"]:
        st.session_state["members"].append(new_member)
        st.sidebar.success(f"Added {new_member}")

if st.session_state["members"]:
    for m in st.session_state["members"]:
        st.sidebar.text(f"• {m}")

# --- TABS INTERFACE ---
tab1, tab2 = st.tabs(["Expense Tracker", "Destination Guide"])

with tab1:
    st.markdown(f"<h2 style='color: #4EA8DE;'>Log an Expense for {destination}</h2>", unsafe_allow_html=True)

    if not st.session_state["members"]:
        st.info("Please add travelers in the sidebar to begin tracking expenses.")
    else:
        expense_desc = st.text_input("Expense Description", placeholder="e.g., Fuel, Hotel, Dinner")
        # Dynamic label showing current country's currency unit
        amount = st.number_input(f"Total Amount ({local_currency})", min_value=0.0, step=10.0)
        payer = st.selectbox("Paid By", options=st.session_state["members"])
        
        if st.button("Log Expense"):
            if expense_desc and amount > 0:
                num_people = len(st.session_state["members"])
                
                # 1. Split locally in original currency units
                local_share = round(amount / num_people, 2)
                
                # 2. Convert total and individual splits to INR
                amount_inr = round(amount * exchange_rate, 2)
                share_inr = round(local_share * exchange_rate, 2)
                
                # Save data with both original data and native INR translations
                st.session_state["expenses"][destination].append({
                    "desc": expense_desc, 
                    "amount_local": amount, 
                    "currency_code": local_currency,
                    "amount_inr": amount_inr, 
                    "payer": payer, 
                    "share_inr": share_inr
                })
                st.success(f"Logged '{expense_desc}' inside the {destination} folder!")

    st.write("---")
    st.markdown(f"<h2 style='color: #4EA8DE;'>Balances & Settlement (INR Base)</h2>", unsafe_allow_html=True)

    current_city_expenses = st.session_state["expenses"][destination]

    if current_city_expenses:
        for exp in current_city_expenses:
            # Display itemization showing both local price spent and its conversion price
            st.write(f"**{exp['payer']}** paid **{exp['amount_local']} {exp['currency_code']}** (~₹{exp['amount_inr']}) for *'{exp['desc']}'*")
            
        # Running balances tracking exclusively tracking normalized INR units
        balances = {name: 0.0 for name in st.session_state["members"]}
        for exp in current_city_expenses:
            balances[exp["payer"]] += exp["amount_inr"]
            for member in st.session_state["members"]:
                balances[member] -= exp["share_inr"]
                
        st.write("### Net Balances (in Rupees):")
        for member, bal in balances.items():
            if bal > 0:
                st.write(f"🟢 **{member}** is owed: **`₹{round(bal, 2)}`**")
            elif bal < 0:
                st.write(f"🔴 **{member}** owes: **`₹{abs(round(bal, 2))}`**")
            else:
                st.write(f"⚪ **{member}** is completely even.")
                
        st.write("---")
        st.markdown("<h3 style='color: #4EA8DE;'>💡 How to Settle Up</h3>", unsafe_allow_html=True)
        
        debtors = [[name, bal] for name, bal in balances.items() if bal < 0]
        creditors = [[name, bal] for name, bal in balances.items() if bal > 0]
        
        settlements_found = False
        
        for d in debtors:
            for c in creditors:
                if d[1] == 0 or c[1] == 0:
                    continue
                    
                owes_amount = abs(d[1])
                is_owed_amount = c[1]
                
                payment = min(owes_amount, is_owed_amount)
                payment = round(payment, 2)
                
                if payment > 0:
                    st.info(f"👉 **{d[0]}** pays **₹{payment}** to **{c[0]}**")
                    settlements_found = True
                    
                    d[1] += payment
                    c[1] -= payment
                    
        if not settlements_found:
            st.caption("No payments required to settle up!")
    else:
        st.caption(f"No expenses recorded yet for {destination}. This folder is clean!")

with tab2:
    st.markdown(f"<h2 style='color: #4EA8DE;'>Points of Interest in {destination}</h2>", unsafe_allow_html=True)
    st.write("Top curated locations and local highlights:")
    st.write("")

    # Point to the nested "attractions" property array inside the modified json layout
    if destination in TRAVEL_GUIDE and "attractions" in TRAVEL_GUIDE[destination]:
        spots = TRAVEL_GUIDE[destination]["attractions"]
        for spot in spots:
            st.markdown(f"### {spot['name']}")
            st.write(spot['desc'])
            st.markdown("<hr style='border:0.5px solid #E0E0E0'>", unsafe_allow_html=True)