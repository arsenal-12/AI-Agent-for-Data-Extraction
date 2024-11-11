import os
import streamlit as st
import pandas as pd
import requests
from dotenv import load_dotenv
import re
import gspread
from google.oauth2.service_account import Credentials
from sklearn.feature_extraction.text import CountVectorizer

# Load environment variables from .env file
load_dotenv()

# Set up Google Sheets API credentials
def get_gspread_client():
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON')
    if not creds_path:
        st.error("Google Sheets credentials JSON file path is missing. Please set the GOOGLE_SHEETS_CREDENTIALS_JSON environment variable.")
        st.stop()
    creds = Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return gspread.authorize(creds)

# Function to get the SERPAPI key from environment variables
def get_serpapi_key():
    return os.getenv('SERPAPI_KEY')

def get_sheet_data_dynamic_headers(sheet_url):
    client = get_gspread_client()
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(0)  # Assuming data is in the first sheet

    try:
        # Fetch the actual headers from the sheet
        headers = worksheet.row_values(1)  # The first row is assumed to be the header row
        normalized_headers = [header.strip().lower() for header in headers]
        
        # Display the headers dynamically
        st.write(f"### Dynamic Headers in Google Sheet: {normalized_headers}")
        
        # Get all the records with dynamic headers
        sheet_data = worksheet.get_all_records()
        return sheet_data

    except gspread.GSpreadException as e:
        st.error(f"Error getting sheet data: {e}")
        return None

# Function to perform web search using SerpAPI
def web_search(query):
    api_key = get_serpapi_key()
    if not api_key:
        raise ValueError("API key is missing. Please set your SERPAPI_KEY environment variable.")
    
    search_url = f"https://serpapi.com/search?q={query}&api_key={api_key}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Search failed: {e}")
        return {"error": "Failed to fetch search results"}

# Function to extract structured information from SerpAPI results
def extract_info_from_serpapi(query, search_result):
    try:
        search_data = search_result.get("organic_results", [])
        extracted_data = []

        for result in search_data:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            extracted_data.append([title, link, snippet])
        
        if not extracted_data:
            st.error("No relevant data found in search results.")
            return []

        return extracted_data

    except Exception as e:
        st.error(f"Error extracting information: {e}")
        return []

# Function to extract keywords as column headers
def extract_keywords(query):
    vectorizer = CountVectorizer(max_features=3, stop_words="english")
    vectorizer.fit([query])
    return vectorizer.get_feature_names_out()

# Function to display data from Google Sheets (after writing)
def display_sheet_data(sheet_url):
    try:
        client = get_gspread_client()
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)  # Assuming data is in the first sheet
        sheet_data = worksheet.get_all_records()  # Get all records
        st.write("### Current Data in Google Sheet:")
        st.write(sheet_data)
    except Exception as e:
        st.error(f"Failed to display sheet data: {e}")

def write_to_google_sheet(sheet_url, data_frame, confirm_overwrite):
    try:
        # Check if confirm_overwrite is True
        if not confirm_overwrite:
            st.warning("Overwrite option not confirmed. Please check the box to confirm.")
            return

        if sheet_url == "":
            st.error("No Google Sheets URL provided.")
            return

        if data_frame is None or data_frame.empty:
            st.error("No data to write to Google Sheets.")
            return

        # Display the DataFrame before writing for debugging purposes
        st.write("### Writing DataFrame to Google Sheets:")
        st.write(data_frame)

        # Initialize the Google Sheets client
        client = get_gspread_client()

        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)  # Assuming the first worksheet is the one to update
        worksheet.clear()  # Clear existing data before writing

        # Write the data frame to Google Sheets
        worksheet.update([data_frame.columns.values.tolist()] + data_frame.values.tolist())

        # Success message
        st.success("Data successfully written to Google Sheets!")

        # Optionally, display the first few rows from the Google Sheet to confirm it worked
        display_sheet_data(sheet_url)

    except Exception as e:
        st.error(f"Failed to write data to Google Sheets: {e}")

# Streamlit UI
st.set_page_config(page_title="AI Agent for Data Extraction", layout="wide")
st.title("AI Agent for Data Extraction with SerpApi")
st.markdown("""
    This tool helps you perform web searches using the **SerpApi** and extract relevant information 
    from the results to populate Google Sheets. You can upload CSV files or directly link to Google Sheets.
""")

# Option to rewrite the data in Google Sheets
data_source = st.radio("Choose Data Source", ["Upload CSV", "Google Sheets URL"], key="data_source", help="Select the source for data extraction.")

# Initialize variables
df = None
sheet_url = ""
query_input = ""

# Step 2: Handle CSV upload
if data_source == "Upload CSV":
    uploaded_file = st.file_uploader("Upload CSV file", type="csv", label_visibility="collapsed")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
        st.write("### Preview of the uploaded file:")
        st.write(df.head())
        
        # Enter Query
        query_input = st.text_area("Enter your query (e.g., 'What is the contact email of {company}?')")

# Step 3: Handle Google Sheets URL
elif data_source == "Google Sheets URL":
    sheet_url = st.text_input("Enter Google Sheets URL", placeholder="Paste your Google Sheets URL here")
    if sheet_url:
        # Use dynamic header fetching function
        sheet_data = get_sheet_data_dynamic_headers(sheet_url)
        if sheet_data:
            df = pd.DataFrame(sheet_data)
            st.write("### Preview of the Google Sheet data:")
            st.write(df.head())
        
        # Enter Query
        query_input = st.text_area("Enter your query (e.g., 'What is the contact email of {company}?')")

# Check if query_input and placeholder are valid
if query_input:
    placeholder_match = re.search(r"\{(\w+)\}", query_input)
    if placeholder_match:
        placeholder = placeholder_match.group(1)
        
        # Verify if the detected placeholder has a matching column
        if df is not None and placeholder in df.columns:
            column_name = placeholder
            st.write(f"Using '{column_name}' column for searches based on query placeholder.")
        else:
            st.error(f"No matching column for placeholder '{placeholder}' found in uploaded file.")
            st.stop()
    else:
        st.error("Please provide a valid query with a placeholder in curly braces, e.g., '{company}'.")
        st.stop()

# Initialize results in session state if not already present
if 'results' not in st.session_state:
    st.session_state['results'] = {}

# Step 4: Perform Searches and Store Results
if st.button("Run Search", key="search_button"):
    st.session_state['results'] = {}  # Clear previous results
    for item in df[column_name]:
        query = query_input.replace(f"{{{placeholder}}}", str(item))
        search_result = web_search(query)
        if "error" not in search_result:
            st.session_state['results'][item] = search_result
    st.success("Search results stored. Now click 'Extract Info' to display.")

# Step 5: Extract Information from SerpApi on Button Click
if st.button("Extract Info", key="extract_button") and 'results' in st.session_state and st.session_state['results']:
    extracted_data = []

    for entity, search_result in st.session_state['results'].items():
        if isinstance(search_result, dict) and 'error' not in search_result:
            try:
                current_query = query_input.replace(f"{{{placeholder}}}", entity)
                st.write(f"### Extracting info for {entity} with query: {current_query}")

                extracted_info = extract_info_from_serpapi(current_query, search_result)

                if extracted_info:
                    for info in extracted_info:
                        extracted_data.append(info)

            except Exception as e:
                st.error(f"Error extracting info for {entity}: {e}")

    if extracted_data:
        # Save the DataFrame to session state
        st.session_state.extracted_df = pd.DataFrame(extracted_data, columns=["Title", "Link", "Snippet"])
        st.write("### Extracted Information:")
        st.write(st.session_state.extracted_df)
    else:
        st.warning("No data extracted.")

# Step 6: Write to Google Sheets button only when "Google Sheets URL" is selected
if data_source == "Google Sheets URL" and 'extracted_df' in st.session_state:
    confirm_overwrite = st.checkbox("Confirm Overwrite Data in Google Sheet", key="overwrite_checkbox")
    if confirm_overwrite:
        write_to_google_sheet(sheet_url, st.session_state.extracted_df, confirm_overwrite)

