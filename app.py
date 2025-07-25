import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- Pre-saved ingredients with cost per standard unit ---
ingredient_prices = {
    "Tomato": {"unit": "kg", "price": 30},
    "Onion": {"unit": "kg", "price": 25},
    "Oil": {"unit": "L", "price": 120},
    "Salt": {"unit": "kg", "price": 10},
    "Milk": {"unit": "L", "price": 60},
    "Chicken": {"unit": "kg", "price": 200},
    "Rice": {"unit": "kg", "price": 50},
}

unit_conversion = {
    "g": 0.001,
    "kg": 1,
    "ml": 0.001,
    "L": 1,
}

# Initialize session state for storing recipes
if "recipes" not in st.session_state:
    st.session_state.recipes = []

st.title("📘 Recipe Cost Calculator & Master Sheet Creator")

with st.form("recipe_form"):
    st.subheader("🍲 Enter New Recipe")

    dish_name = st.text_input("Dish Name")
    servings = st.number_input("Number of Servings", min_value=1, value=1)

    st.markdown("### 🧾 Add Ingredients")
    ingredient_data = []
    num_ingredients = st.number_input("How many ingredients?", min_value=1, value=3)

    for i in range(num_ingredients):
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            name = st.text_input(f"Ingredient #{i+1}", key=f"name_{i}")
        with cols[1]:
            qty = st.number_input(f"Qty", min_value=0.0, key=f"qty_{i}")
        with cols[2]:
            unit = st.selectbox("Unit", ["g", "kg", "ml", "L"], key=f"unit_{i}")
        with cols[3]:
            price = ingredient_prices.get(name, {}).get("price", 0)
            price_unit = ingredient_prices.get(name, {}).get("unit", "kg")
            st.write(f"{price} ₹/{price_unit}")
        ingredient_data.append((name, qty, unit))

    submitted = st.form_submit_button("Calculate Cost & Save")
    if submitted:
        total_cost = 0
        ingredients_final = []

        for name, qty, unit in ingredient_data:
            if name not in ingredient_prices:
                st.warning(f"No price found for {name}. Skipped.")
                continue

            price_info = ingredient_prices[name]
            price_per_unit = price_info["price"]
            standard_unit = price_info["unit"]

            # Convert qty to standard unit
            qty_kg_or_L = qty * unit_conversion[unit]
            if standard_unit != unit and standard_unit in unit_conversion:
                qty_kg_or_L = qty * unit_conversion[unit] / unit_conversion[standard_unit]

            cost = qty_kg_or_L * price_per_unit
            total_cost += cost

            ingredients_final.append({
                "Ingredient": name,
                "Quantity": qty,
                "Unit": unit,
                "Converted Qty": round(qty_kg_or_L, 3),
                "Cost (₹)": round(cost, 2)
            })

        recipe_entry = {
            "Dish Name": dish_name,
            "Servings": servings,
            "Total Cost (₹)": round(total_cost, 2),
            "Ingredients": ingredients_final,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        st.session_state.recipes.append(recipe_entry)
        st.success(f"Recipe '{dish_name}' added successfully! Total Cost: ₹{round(total_cost, 2)}")

# --- Display Saved Recipes ---
if st.session_state.recipes:
    st.header("📒 Master Recipe Sheet")

    for idx, recipe in enumerate(st.session_state.recipes):
        with st.expander(f"{idx+1}. {recipe['Dish Name']} - ₹{recipe['Total Cost (₹)']}"):
            st.write(f"👥 Servings: {recipe['Servings']} | 🕒 {recipe['Date']}")
            df = pd.DataFrame(recipe["Ingredients"])
            st.dataframe(df)

    # Download Excel file
    if st.button("📥 Download Master Sheet (Excel)"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for recipe in st.session_state.recipes:
                sheet_name = recipe["Dish Name"][:31]  # Excel sheet name limit
                df = pd.DataFrame(recipe["Ingredients"])
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                worksheet.write(len(df)+2, 0, "Total Cost")
                worksheet.write(len(df)+2, 1, recipe["Total Cost (₹)"])

        st.download_button(
            label="Download Excel File",
            data=output.getvalue(),
            file_name="Master_Recipe_Sheet.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
