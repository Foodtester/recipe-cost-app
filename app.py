import streamlit as st
import pandas as pd
import io

# Sample data
data = {
    "Ingredient": ["Flour", "Sugar", "Butter", "Eggs"],
    "Quantity": [1000, 500, 250, 10],
    "Measurement": ["grams (g)", "grams (g)", "grams (g)", "pieces"],
    "Unit Cost": [1.5, 1.2, 2.5, 0.3],
    "Total Cost": [1.5, 0.6, 0.625, 3.0]
}
df = pd.DataFrame(data)

# Create a summary
summary_df = pd.DataFrame({
    "Sheet Name": ["Recipe1", "Recipe2", "Recipe3"],
    "Total Cost": [sum(df["Total Cost"])] * 3
})

# Excel in memory
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    for sheet in summary_df["Sheet Name"]:
        df.to_excel(writer, sheet_name=sheet, index=False)
    summary_df.to_excel(writer, sheet_name="Summary", index=False)
output.seek(0)

# Streamlit UI
st.title("📋 Recipe Cost Calculator")

st.subheader("Ingredients")
st.dataframe(df)

st.subheader("Download Excel")
st.download_button(
    label="📥 Download Excel File",
    data=output,
    file_name="Food_Cost_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
