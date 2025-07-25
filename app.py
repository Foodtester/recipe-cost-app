import streamlit as st
import pandas as pd
import base64
from io import BytesIO

# ------------------ Custom CSS ------------------
custom_css = """
<style>
html, body, [class*="css"]  {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f7f7f7;
    color: #333333;
}
h1, h2, h3, h4 {
    color: #2c3e50;
    font-weight: 600;
    text-align: center;
}
.stForm {
    background-color: #ffffff;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
}
.stDataFrame, .stTable {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.stExpander {
    border-radius: 8px !important;
    border: 1px solid #dcdcdc !important;
    background-color: #ffffff !important;
    margin-top: 1rem;
}
button[kind="primary"] {
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    margin-top: 1rem;
}
button[kind="primary"]:hover {
    background-color: #45a049;
}
input, select {
    border-radius: 6px !important;
    border: 1px solid #cccccc !important;
    padding: 0.5rem !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ------------------ Pre-saved Ingredients ------------------
default_prices = {
    "Onion": 20,  # per kg
    "Tomato": 30,
    "Chicken": 200,
    "Milk": 60,
    "Oil": 150,
    "Salt": 10,
    "Sugar": 40
}

unit_conversion = {
    "g": 0.001, "kg": 1,
    "ml": 0.001, "l": 1,
    "oz": 0.02835, "lb": 0.4536
}

# ------------------ App Title ------------------
st.title("🍲 Recipe Cost Calculator")

# ------------------ Form ------------------
with st.form("recipe_form"):
    recipe_name = st.text_input("Enter recipe name:")
    servings = st.number_input("How many people will eat this?", min_value=1, step=1)
    num_ingredients = st.number_input("Number of ingredients:", min_value=1, max_value=30, step=1)

    ingredients = []
    for i in range(int(num_ingredients)):
        st.markdown(f"**Ingredient {i+1}**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            name = st.text_input(f"Name {i+1}", key=f"name_{i}")
        with col2:
            qty = st.number_input(f"Quantity {i+1}", min_value=0.0, step=0.1, key=f"qty_{i}")
        with col3:
            unit = st.selectbox(f"Unit {i+1}", ["g", "kg", "ml", "l", "oz", "lb"], key=f"unit_{i}")
        with col4:
            price = st.number_input(f"Price/kg or l (₹) {i+1}", min_value=0.0, step=0.1, value=float(default_prices.get(name, 0)), key=f"price_{i}")
        ingredients.append({
            "Ingredient": name,
            "Quantity": qty,
            "Unit": unit,
            "PricePerKgOrL": price
        })

    submitted = st.form_submit_button("Calculate")

# ------------------ Processing ------------------
if submitted:
    data = []
    total_cost = 0

    for item in ingredients:
        name = item["Ingredient"]
        qty = item["Quantity"]
        unit = item["Unit"]
        price = item["PricePerKgOrL"]

        # Convert to kg or liters
        qty_in_kg_or_l = qty * unit_conversion.get(unit, 1)
        cost = qty_in_kg_or_l * price
        total_cost += cost

        data.append({
            "Ingredient": name,
            "Quantity": qty,
            "Unit": unit,
            "Converted Qty (kg/l)": round(qty_in_kg_or_l, 3),
            "Price per Kg/L (₹)": price,
            "Cost (₹)": round(cost, 2)
        })

    df = pd.DataFrame(data)
    df_total = pd.DataFrame({
        "Total Cost (₹)": [round(total_cost, 2)],
        "Cost Per Serving (₹)": [round(total_cost / servings, 2) if servings else 0]
    })

    st.success("✅ Calculation Complete!")
    st.subheader("📋 Recipe Summary")
    st.dataframe(df, use_container_width=True)
    st.subheader("💰 Total Cost")
    st.table(df_total)

    # Save to session state master list
    if "all_recipes" not in st.session_state:
        st.session_state["all_recipes"] = []

    st.session_state["all_recipes"].append({
        "Recipe": recipe_name,
        "Servings": servings,
        "Ingredients": df,
        "Summary": df_total
    })

    # ------------------ Export Section ------------------
    def download_excel(recipes):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for r in recipes:
                sheet_name = r["Recipe"][:31] or "Sheet"
                r["Ingredients"].to_excel(writer, sheet_name=sheet_name, index=False)
                r["Summary"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(r["Ingredients"]) + 2)
        output.seek(0)
        return output

    if st.session_state["all_recipes"]:
        st.subheader("📘 Download Recipe Book (Excel)")
        excel_data = download_excel(st.session_state["all_recipes"])
        b64 = base64.b64encode(excel_data.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="recipe_book.xlsx">📥 Download Recipe Book</a>'
        st.markdown(href, unsafe_allow_html=True)
