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
# Streamlit UI
# -----------------------------
st.title("🍽️ Recipe Cost Calculator")

dish_name = st.text_input("Enter Dish Name")
num_people = st.number_input("Number of People", min_value=1, value=1)

st.subheader("Add Ingredients")
num_ingredients = st.number_input("How many ingredients?", min_value=1, value=3)

ingredients = []
for i in range(num_ingredients):
    st.markdown(f"### Ingredient {i+1}")
    use_saved = st.checkbox(f"Use pre-saved ingredient for item {i+1}?", key=f"use_saved_{i}")
    
    if use_saved:
        selected = st.selectbox(f"Select ingredient {i+1}", pre_saved_ingredients['Ingredient'], key=f"sel_{i}")
        row = pre_saved_ingredients[pre_saved_ingredients['Ingredient'] == selected].iloc[0]
        name = selected
        unit = row['Unit']
        price_per_unit = row['Price_per_unit']
    else:
        name = st.text_input(f"Ingredient name {i+1}", key=f"name_{i}")
        unit = st.text_input(f"Unit (e.g., gram, kg, ml) for {name}", key=f"unit_{i}")
        price_per_unit = st.number_input(f"Price per {unit} for {name}", min_value=0.0, key=f"price_{i}")
    
    quantity = st.number_input(f"Quantity of {name}", min_value=0.0, key=f"qty_{i}")
    convert_to_unit = st.text_input(f"Convert {unit} to (leave blank to skip)", key=f"conv_unit_{i}")
    
    if convert_to_unit:
        try:
            converted_qty = convert_unit(quantity, unit, convert_to_unit)
            st.write(f"Converted Quantity: {converted_qty:.2f} {convert_to_unit}")
            unit = convert_to_unit
            quantity = converted_qty
        except:
            st.error("Conversion failed. Please check units.")

    cost = quantity * price_per_unit
    ingredients.append({
        'Ingredient': name,
        'Quantity': quantity,
        'Unit': unit,
        'Price_per_unit': price_per_unit,
        'Cost': cost
    })

# -----------------------------
# Display Recipe Summary
# -----------------------------
df = pd.DataFrame(ingredients)
df['Cost'] = df['Cost'].round(2)
total_cost = df['Cost'].sum()

st.subheader("📋 Recipe Summary")
st.write(f"Dish: **{dish_name}**")
st.write(f"Serves: **{num_people}** people")
st.dataframe(df)
st.write(f"### 🧾 Total Cost: ₹{total_cost:.2f}")

# -----------------------------
# Export to Excel
# -----------------------------
output = BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Recipe')
    worksheet = writer.sheets['Recipe']
    worksheet.write(len(df)+2, 0, 'Total Cost')
    worksheet.write(len(df)+2, 1, total_cost)

excel_data = output.getvalue()
b64 = base64.b64encode(excel_data).decode()
href = f'<a href="data:application/octet-stream;base64,{b64}" download="recipe_cost.xlsx">📥 Download Excel File</a>'
st.markdown(href, unsafe_allow_html=True)
