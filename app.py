import streamlit as st
import pandas as pd
from io import BytesIO
import datetime

# Set page config
st.set_page_config(page_title="Recipe Cost Calculator", layout="wide")

# Pre-saved ingredient prices (can be extended or replaced by user)
default_prices = {
    "Rice": 50,
    "Wheat Flour": 45,
    "Milk": 60,
    "Sugar": 42,
    "Salt": 20,
    "Butter": 500,
    "Oil": 120,
    "Eggs": 6
}

units_conversion = {
    "g": 0.001,  # 1 gram = 0.001 kg
    "kg": 1,
    "ml": 0.001, # 1 ml = 0.001 liter
    "l": 1,
    "unit": 1
}

st.markdown("## 🍽️ Recipe Cost Calculator")
st.markdown("Use this tool to create recipes, calculate ingredient costs, and export your recipe book!")

st.markdown("---")

# --- Input Form ---
with st.form("recipe_form", clear_on_submit=False):
    st.subheader("📝 Recipe Details")

    col1, col2 = st.columns(2)
    with col1:
        dish_name = st.text_input("Dish Name", "")
    with col2:
        servings = st.number_input("Number of People", min_value=1, step=1, value=1)

    st.markdown("### 🧂 Ingredients")

    num_ingredients = st.number_input("How many ingredients?", min_value=1, max_value=50, step=1, value=3)

    ingredients_data = []

    for i in range(int(num_ingredients)):
        st.markdown(f"**Ingredient {i+1}**")
        cols = st.columns([2, 1, 1, 1, 1])
        name = cols[0].text_input(f"Name", key=f"name_{i}")
        qty = cols[1].number_input(f"Qty", min_value=0.0, step=0.1, key=f"qty_{i}")
        unit = cols[2].selectbox("Unit", ["g", "kg", "ml", "l", "unit"], key=f"unit_{i}")
        price = cols[3].number_input(f"Price/kg or l (₹)", min_value=0.0, step=0.1, value=float(default_prices.get(name, 0)), key=f"price_{i}")
        
        ingredients_data.append({
            "name": name,
            "quantity": qty,
            "unit": unit,
            "price_per_kg_l": price
        })

    submitted = st.form_submit_button("Calculate Recipe Cost 💰")

# --- Process and Display ---
if submitted:
    st.success(f"Cost breakdown for **{dish_name}** serving **{servings}** people:")
    result_data = []
    total_cost = 0.0

    for item in ingredients_data:
        qty_kg_or_l = item['quantity'] * units_conversion.get(item['unit'], 1)
        cost = qty_kg_or_l * item['price_per_kg_l']
        total_cost += cost

        result_data.append({
            "Ingredient": item['name'],
            "Quantity": item['quantity'],
            "Unit": item['unit'],
            "Price per kg/l": item['price_per_kg_l'],
            "Cost (₹)": round(cost, 2)
        })

    df = pd.DataFrame(result_data)
    df.loc[len(df.index)] = ["", "", "", "Total", round(total_cost, 2)]
    st.dataframe(df, use_container_width=True)

    st.markdown(f"### 🧾 Total Cost: ₹{round(total_cost,2)}")
    st.markdown(f"### 👤 Cost Per Person: ₹{round(total_cost / servings, 2)}")

    # Save recipe to session state
    if "recipe_book" not in st.session_state:
        st.session_state.recipe_book = []

    st.session_state.recipe_book.append({
        "Dish Name": dish_name,
        "Servings": servings,
        "Total Cost": round(total_cost, 2),
        "Cost per Person": round(total_cost / servings, 2),
        "Date": datetime.date.today().isoformat()
    })

    # Download Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Recipe')
            writer.save()
        return output.getvalue()

    excel_data = to_excel(df)
    st.download_button(
        label="📥 Download This Recipe as Excel",
        data=excel_data,
        file_name=f"{dish_name.replace(' ', '_')}_cost.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Master Recipe Book ---
if "recipe_book" in st.session_state and st.session_state.recipe_book:
    st.markdown("---")
    st.subheader("📚 Your Recipe Book")
    book_df = pd.DataFrame(st.session_state.recipe_book)
    st.dataframe(book_df, use_container_width=True)

    # Download full recipe book
    def to_excel_book(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='RecipeBook')
            writer.save()
        return output.getvalue()

    excel_book = to_excel_book(book_df)
    st.download_button(
        label="📕 Download Master Recipe Book",
        data=excel_book,
        file_name="recipe_book.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
