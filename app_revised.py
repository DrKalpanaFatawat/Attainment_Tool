import streamlit as st
import os
import pandas as pd
from calculation import calculate_mt
from co_revised_split import split_co_marks
#from co_split import split_co_marks
from excel_writer import generate_workbook
from validation import validate_data
st.markdown("""
<h1 style='
text-align:center;
color:whiteblack;
background:#1565C0;
padding:15px;
border-radius:10px;
box-shadow:2px 2px 8px rgba(0,0,0,0.3);
'>
🎓 Attainment Generator
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<style>

.stButton > button {
    background-color: #1565C0;
    color: whiteblack;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
}

.stButton > button:hover {
    background-color: #0D47A1;
    color: whiteblack;
}

</style>
""", unsafe_allow_html=True)

subject_code = st.text_input("Subject Code")

# template_folder = "input_templates"

# template_files = sorted([
#     f for f in os.listdir(template_folder)
#     if f.endswith(".xlsx")
# ])

# selected_template = st.selectbox(
#     "📄 Select Input Template file",
#     template_files
# )

input_template = "Input_Template.xlsx"

with open(f"input_templates/{input_template}", "rb") as file:

    st.download_button(
        label="📥 Download Student Marks Template",
        data=file,
        file_name=input_template,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# with open(f"input_templates/{selected_template}", "rb") as file:
#     st.download_button(
#         label="📥 Download selected Template File",
#         data=file,
#         file_name=selected_template,
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

    st.info("""
📌 Instructions

1. Download the sample marks template.
2. Do not change the column names.
3. Enter roll no., name, and marks in the respective columns.
4. Save the file as .xlsx.
5. Upload it below.
""")
uploaded_file = st.file_uploader(
    "Upload Student Marks File",
    type=["xlsx"]
)

if uploaded_file:

    # Read Excel
    df = pd.read_excel(uploaded_file)
    
    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", " ", regex=False)
    )

    st.success("File uploaded successfully")
    st.write("Total Students:", len(df))
    st.subheader("Detected Columns")
    st.write(df.columns.tolist())
    st.subheader("Original Data")
    st.dataframe(df.head())
    # Column Detection
    roll_col = df.columns[0]
    name_col = df.columns[1]
    endterm_col = df.columns[2]
    sessional_col = df.columns[3]
    # Calculations
    
    calc_df = df.copy()
    
    student_count = len(calc_df)

    if student_count > len(calc_df):
        st.warning(f"More students found than expected: {student_count}")

    elif student_count < len(calc_df):
        st.warning(f"Fewer students found than expected: {student_count}")

    else:
        st.success(f"Correct number of students found: {student_count}")
    
    calc_df = calculate_mt(calc_df, sessional_col)
    calc_df = split_co_marks(calc_df)
    errors = validate_data(calc_df)
    errors = validate_data(calc_df)

    if errors:

        st.error("Validation Failed!")

        st.write("The following business rules failed:")

        for err in errors:
            st.write("•", err)

        st.stop()

    st.success("All validations passed successfully!")
    template_map = {
    22: "Template_22.xlsx",    
    60: "Template_60.xlsx",
    176: "Template_176.xlsx",
    179: "Template_179.xlsx",
    212: "Template_212.xlsx",
    250: "Template_250.xlsx"
        }
    selected_template = template_map.get(student_count)

    if selected_template is None:
        st.error(
            f"No template available for {student_count} students."
        )
        st.stop()

    st.subheader("Calculated Marks with CO Split")
    st.dataframe(
    calc_df,
    use_container_width=True,
    height=600
    )
    if st.button("Generate Attainment Sheet"):

        output_file = generate_workbook(
        calc_df,
        subject_code,
        roll_col,
        name_col,
        endterm_col,
        sessional_col,
        selected_template,
            )

        st.success("Workbook Generated Successfully!")

        with open(output_file, "rb") as file:

            st.download_button(
                label="Download Workbook",
                data=file,
                file_name=f"{subject_code}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )