
import streamlit as st
import pandas as pd
import fitz
from adobe_api import*
from data_finder import*
st.set_page_config(page_title="Document AI")

st.markdown("Document AI")
st.sidebar.title("Upload Files")
pdf_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
container=st.sidebar.empty()
st.sidebar.markdown('---')
csv_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

option = st.selectbox("Find specific detail", ["Date", "Judges Name", "Case Number", "Case Name"])


if csv_file:
    data_panda=pd.read_csv(csv_file)
    data_panda=unwanted_data_removal(data_panda)   
    if st.button("Find"):
        if option == "Date" and csv_file:
            decided_on=find_decided_on_date(data_panda)
            st.write(decided_on)
            # Function to find date in PDF file
            pass
        elif option == "Judges Name" and csv_file:
            judges=find_judges(data_panda)
            st.write(judges)
                
            pass
        elif option == "Case Number" and csv_file:
            case_number=find_case_number(data_panda)
            st.write(case_number)
            # Function to find case number in CSV file
            pass
        elif option == "Case Name" and csv_file:
            # Function to find case name in CSV file
            case_name=find_case_name_text(data_panda)
            st.write(case_name)
            pass
               
if pdf_file:
    print("this is pdf: ",pdf_file.name)
    if container.button("Send to Adobe"):
        print("button clicked")
        # doc = fitz.open(pdf_file.name)
        print(pdf_file)
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        json_data=json_manage(pdf_file)
        data_panda=json_to_dataframe(json_data)
        st.write(data_panda)
    
if pdf_file:
    st.write(f"PDF file uploaded: {pdf_file.name}")