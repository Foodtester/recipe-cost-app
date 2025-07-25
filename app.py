import pandas as pd
import streamlit as st
from io import BytesIO
import base64

# -----------------------------
# Pre-saved Ingredients with Prices
# -----------------------------
pre_saved_ingredients = pd.DataFrame({
    'Ingredient': ['Flour', 'Sugar', 'Milk', 'Butter'],
    'Unit': ['kg', 'kg', 'litre', 'gram'],
    'Price_per_unit': [40, 50, 60, 5]
})

# -----------------------------
# Unit Conversion Dictionary
# -----------------------------
unit_conversion = {
    ('gram', 'kg'): 0.001,
    ('kg', 'gram'): 1000,
    ('ml', 'litre'): 0.001,
    ('litre', 'ml'): 1000,
    ('ounce', 'gram'): 28.35,
    ('gram', 'ounce'): 1 / 28.35,
}

def convert_unit(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    return value * unit_conversion.get((from_unit, to_unit), 1)

# -----------------------------
# UI: Title & Dish Details
# -----------------------------
st.markdown("<h1 style='text-align: center;'>🍽️ Recipe Cost Calculator</h1>", unsafe_allow_html=True)
st.markdown("Easily estimate the cost of your custom dishes by entering ingredients and quantities.")

with st.expander("📝 Enter Dish Information"):
    col1, col2 = st.columns(2)
    with col1:
        dish_name = st.text_input("🍲 Dish Name", placeholder="e.g., Vegetable Biryani")
    with col2:
        num_people = st.number_input("👥 Number of People", min_value=1, value=1)

# -----------------------------
# UI: Ingredients Section
# -----------------------------
st.markdown("### 🧂 Add Ingredients")
num_ingredients = st.number_input("How many ingredients?", min_value=1, value=3)

ingredients = []

for i in range(num_ingredients):
    with st.expander(f"📦 Ingredient {i+1}"):
        use_saved = st.checkbox(f"🔖 Use pre-saved ingredient?", key=f"use_saved_{i}")
        
        if use_saved:
            selected = st.selectbox("Select Ingredient", pre_saved_ingredients['Ingredient'], key=f"sel_{i}")
            row = pre_saved_ingredients[pre_saved_ingredients['Ingredient'] == selected].iloc[0]
            name = selected
            unit = row['Unit']
            price_per_unit = row['Price_per_unit']
        else:
            name = st.text_input("Ingredient Name", key=f"name_{i}", placeholder="e.g., Tomato")
            unit = st.text_input("Measurement Unit (e.g., gram, ml, kg)", key=f"unit_{i}")
            price_per_unit = st.number_input(f"💰 Price per {unit}", min_value=0.0, key=f"price_{i}")
        
        quantity = st.number_input("📏 Quantity", min_value=0.0, key=f"qty_{i}")
        convert_to_unit = st.text_input("🔄 Convert unit to (optional)", key=f"conv_unit_{i}")
        
        if convert_to_unit:
            try:
                converted_qty = convert_unit(quantity, unit, convert_to_unit)
                st.success(f"Converted: {quantity} {unit} = {converted_qty:.2f} {convert_to_unit}")
                unit = convert_to_unit
                quantity = converted_qty
            except:
                st.error("⚠️ Conversion failed. Check unit names.")
        
        cost = quantity * price_per_unit
        ingredients.append({
            'Ingredient': name,
            'Quantity': quantity,
            'Unit': unit,
            'Price_per_unit': price_per_unit,
            'Cost': cost
        })

# -----------------------------
# Results Table
# -----------------------------
st.markdown("## 📊 Recipe Summary")
df = pd.DataFrame(ingredients)
df['Cost'] = df['Cost'].round(2)
total_cost = df['Cost'].sum()

st.markdown(f"**🍽️ Dish:** {dish_name} | **👥 Serves:** {num_people} people")
st.dataframe(df.style.format({"Price_per_unit": "₹{:.2f}", "Cost": "₹{:.2f}"}), height=300)

st.markdown(f"""
<div style='background-color:#f9f9f9;padding:15px;border-radius:10px;margin-top:20px'>
<h3 style='text-align:center;color:#2E8B57;'>🧾 Total Recipe Cost: ₹{total_cost:.2f}</h3>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Export to Excel Button
# -----------------------------
output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Recipe')
    worksheet = writer.sheets['Recipe']
    worksheet.write(len(df)+2, 0, 'Total Cost')
    worksheet.write(len(df)+2, 1, total_cost)

excel_data = output.getvalue()
b64 = base64.b64encode(excel_data).decode()
href = f'<a href="data:application/octet-stream;base64,{b64}" download="recipe_cost.xlsx"><button style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-size:16px;">📥 Download Excel File</button></a>'
st.markdown(href, unsafe_allow_html=True)
