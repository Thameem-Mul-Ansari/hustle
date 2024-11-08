# app.py

import streamlit as st
import pdfplumber
from groq import Groq

# Initialize the Groq client
client = Groq(api_key="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")

# Streamlit app configuration
st.set_page_config(page_title="Med Lingo", layout="wide")

# Sidebar for file upload and instructions
st.sidebar.title("Upload Your PDF Report")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
st.sidebar.markdown("""
### How to use:
1. Upload a blood test report PDF.
2. Input your custom Boolean query (e.g., 'blood glucose AND HbA1c OR cholesterol NOT creatinine').
3. The tool will analyze the report and display relevant sections.
""")

# Main title and description
st.title("Med Lingo🩺")
st.markdown("""
This tool helps you search your blood test report by analyzing custom Boolean expressions.
Enter your query using `AND`, `OR`, `NOT` to find specific information within your report.
""")

# Container for user input and query display
user_input_container = st.container()
extracted_text_container = st.container()
query_display_container = st.container()
query_result_container = st.container()

# User input for Boolean query
with user_input_container:
    boolean_query = st.text_input(
        "Enter your custom Boolean query (e.g., 'blood glucose AND HbA1c OR cholesterol NOT creatinine'):",
        placeholder="Type your Boolean query here"
    )

if uploaded_file and boolean_query:
    # Extract text from the uploaded PDF
    with pdfplumber.open(uploaded_file) as pdf:
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text() + "\n"
    
    # Display extracted text in a collapsible container
    with extracted_text_container:
        st.subheader("Extracted Text from PDF")
        st.expander("View Extracted PDF Content").write(pdf_text)

    # Display the custom Boolean query
    with query_display_container:
        st.subheader("AI Generated Boolean Query")
        st.code(boolean_query, language="text")

    # Send extracted text to Groq for processing
    if boolean_query:
        with st.spinner("Analyzing the report..."):
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": f"Search this text for: ({boolean_query})\n\n{pdf_text}"}
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )

        # Collect and display results
        result = ""
        for chunk in completion:
            result += chunk.choices[0].delta.content or ""

        with query_result_container:
            st.subheader("Query Results")
            st.expander("View Search Results").write(result)
    else:
        st.error("Please enter a valid Boolean query.")

else:
    st.info("Upload a PDF file and enter a Boolean query to start.")

# Footer
st.sidebar.markdown("Developed by Lingo")
