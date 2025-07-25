import streamlit as st
import pandas as pd
import io

# Page configuration
st.set_page_config(page_title="Recipe Cost Calculator", layout="wide")
st.title("🍽️ Recipe Cost Calculator (Editable)")

# File uploader
uploaded_file = st.file_uploader("📤 Upload your Excel file with recipe ingredients", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read uploaded Excel file
        df = pd.read_excel(uploaded_file)

        st.success("✅ File uploaded successfully! You can now edit the values below.")

        # Editable table
        st.subheader("✏️ Edit your recipe details below:")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

        # Calculate 'Total' column if the necessary columns exist
        if "Quantity" in edited_df.columns and "Unit Price" in edited_df.columns:
            edited_df["Total"] = edited_df["Quantity"] * edited_df["Unit Price"]
        else:
            st.warning("⚠️ Please ensure your file includes 'Quantity' and 'Unit Price' columns.")

        # Display the updated table
        st.subheader("📊 Updated Table:")
        st.dataframe(edited_df, use_container_width=True)

        # Calculate and show grand total
        if "Total" in edited_df.columns:
            total_cost = edited_df["Total"].sum()
            st.markdown(f"### 🧾 Grand Total: ₹ {total_cost:,.2f}")

        # Prepare file for download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            edited_df.to_excel(writer, index=False, sheet_name="Updated Recipe")
            writer.close()
            processed_data = output.getvalue()

        # Download button
        st.download_button(
            label="📥 Download Updated Excel",
            data=processed_data,
            file_name="updated_recipe.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

else:
    st.info("📄 Please upload an Excel (.xlsx) file to begin.")
