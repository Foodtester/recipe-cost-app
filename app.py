import streamlit as st
import pandas as pd
from io import BytesIO
import base64

st.set_page_config(page_title="Recipe Cost Calculator", layout="wide")

st.title("👨‍🍳 Recipe Cost Calculator & Master Book Creator")

# -----------------------------
# Form Inputs
# -----------------------------
st.subheader("🔧 Enter Recipe Details")

dish_name = st.text_input("🍽️ Dish Name")
num_people = st.number_input("👥 Number of People", min_value=1, value=1)

st.markdown("### 🧂 Ingredients")

ingredient_count = st.number_input("Number of Ingredients", min_value=1, max_value=50, value=3)

ingredient_data = []

unit_conversion = {
    "grams": 0.001,
    "kilograms": 1,
    "ml": 0.001,
    "litres": 1,
    "ounce": 0.0283495,
    "pound": 0.453592,
    "cup": 0.24,  # assuming 1 cup = 240ml
    "tablespoon": 0.015,
    "teaspoon": 0.005
}

with st.form("ingredients_form"):
    for i in range(int(ingredient_count)):
        cols = st.columns([3, 2, 2, 2])
        name = cols[0].text_input(f"Ingredient {i+1} Name", key=f"name_{i}")
        quantity = cols[1].number_input("Quantity", key=f"qty_{i}", step=0.1)
        unit = cols[2].selectbox("Unit", options=list(unit_conversion.keys()), key=f"unit_{i}")
        price_per_base = cols[3].number_input("Price per base unit (kg/litre)", key=f"price_{i}", step=0.1)
        ingredient_data.append({
            "Ingredient": name,
            "Quantity": quantity,
            "Unit": unit,
            "Price per unit (kg/litre)": price_per_base
        })

    submitted = st.form_submit_button("✅ Calculate Recipe Cost")

# -----------------------------
# Cost Calculation
# -----------------------------
if submitted:
    df = pd.DataFrame(ingredient_data)
    df["Qty (kg/litre)"] = df.apply(lambda row: row["Quantity"] * unit_conversion[row["Unit"]], axis=1)
    df["Cost"] = df["Qty (kg/litre)"] * df["Price per unit (kg/litre)"]
    total_cost = df["Cost"].sum()

    st.markdown("### 🧾 Recipe Cost Breakdown")
    st.dataframe(df[["Ingredient", "Quantity", "Unit", "Price per unit (kg/litre)", "Cost"]], use_container_width=True)

    st.success(f"💰 **Total Cost for {num_people} people**: ₹ {total_cost:.2f}")
    st.info(f"🧍 Cost per person: ₹ {total_cost / num_people:.2f}")

    # -----------------------------
    # Export Single Recipe as Excel
    # -----------------------------
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=dish_name[:31])
        worksheet = writer.sheets[dish_name[:31]]
        worksheet.write(len(df)+2, 0, "Total Cost")
        worksheet.write(len(df)+2, 1, total_cost)
        worksheet.write(len(df)+3, 0, "Number of People")
        worksheet.write(len(df)+3, 1, num_people)

    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    st.markdown(f'''
        <a href="data:application/octet-stream;base64,{b64}" download="{dish_name}_Recipe.xlsx">
            <button style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:5px;">📥 Download This Recipe as Excel</button>
        </a>
    ''', unsafe_allow_html=True)

    # -----------------------------
    # Add to Master Book
    # -----------------------------
    if 'book' not in st.session_state:
        st.session_state.book = {}

    if st.button("📚 Add This Recipe to Master Book"):
        if dish_name.strip() == "":
            st.warning("Please enter a dish name before adding.")
        else:
            st.session_state.book[dish_name] = {
                'Data': df,
                'Total Cost': total_cost,
                'Serves': num_people
            }
            st.success(f"✅ '{dish_name}' added to master book!")

# -----------------------------
# Download Master Book
# -----------------------------
if "book" in st.session_state and st.session_state.book:
    st.markdown("---")
    st.markdown("## 📘 Download Master Recipe Book")

    book_output = BytesIO()
    with pd.ExcelWriter(book_output, engine='xlsxwriter') as writer:
        for dish, details in st.session_state.book.items():
            df_recipe = details['Data'].copy()
            df_recipe.to_excel(writer, index=False, sheet_name=dish[:31])
            ws = writer.sheets[dish[:31]]
            ws.write(len(df_recipe)+2, 0, "Total Cost")
            ws.write(len(df_recipe)+2, 1, details["Total Cost"])
            ws.write(len(df_recipe)+3, 0, "Serves")
            ws.write(len(df_recipe)+3, 1, details["Serves"])

    master_excel = book_output.getvalue()
    b64_master = base64.b64encode(master_excel).decode()
    st.markdown(f'''
        <a href="data:application/octet-stream;base64,{b64_master}" download="Master_Recipe_Book.xlsx">
            <button style="background-color:#1E90FF;color:white;padding:10px 20px;border:none;border-radius:5px;">📥 Download Master Book</button>
        </a>
    ''', unsafe_allow_html=True)
