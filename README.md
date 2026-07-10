# 🧭 Raahi - Global Expense Splitter

Raahi is an interactive, multi-currency travel expense splitter built using Python and Streamlit. Designed for international group trips, it allows users to log expenses in local currencies based on their travel destination and automatically calculates final settlements converted back to Indian Rupees (INR).

## 🚀 Live Link
Check out the live application here: [raahiweb.streamlit.app](https://raahiweb.streamlit.app)

## ✨ Features
* **Dynamic Location Tracking:** Select destinations like Dubai, Paris, or Tokyo to automatically adapt the app's currency theme.
* **Local Currency Logging:** Input expenses natively using local currency symbols (e.g., AED, EUR, USD, JPY).
* **Smart Math Engine:** Computes total trip costs and individual fair shares dynamically.
* **Automated INR Conversion:** Instantly breaks down final balances and dues back into Indian Rupees (INR) using a built-in static exchange matrix.

## 🛠️ Tech Stack
* **Frontend/Backend:** Python & Streamlit Cloud
* **Data Storage:** JSON (for destination configurations and exchange rates)

## 💻 How to Run Locally

1. Clone this repository or download the source files.
2. Install the required dependencies:
   ```bash
   python -m pip install streamlit
