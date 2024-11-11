# AI Agent for Data Extraction with SerpApi

## **Overview**

This project is an **AI agent** that performs **web searches** using the **SerpApi** and extracts relevant information from the results. The extracted data is then populated into **Google Sheets**. It allows users to upload a **CSV file** or directly provide a **Google Sheets URL**. The agent uses **dynamic headers** for data extraction and allows users to customize queries based on their needs.

## **Features**

- **Dynamic Header Fetching**: Automatically retrieves headers from the provided Google Sheet and allows users to customize queries using these headers.
- **Web Search**: Utilizes **SerpApi** for web searches, extracting titles, links, and snippets from search results.
- **Data Extraction**: Extracts specific information from the **SerpApi** results based on user-defined queries.
- **Google Sheets Integration**: Writes extracted data back to a Google Sheet after confirmation.

## **Installation**

To get started with this project, follow these steps:

1. Clone this repository:
   ```bash
   git clone <repository_url>
2. Install the required dependencies:
pip install -r requirements.txt

3.Set up the environment variables in a .env file:
GOOGLE_SHEETS_CREDENTIALS_JSON: Path to your Google Sheets API credentials.
SERPAPI_KEY: Your SerpApi API key.

## Usage
# Choose Data Source:
Select either "Upload CSV" or "Google Sheets URL" as your data source.

# Upload CSV:
Upload a CSV file to the application.
Enter a query with a placeholder (e.g., What is the contact email of {company}?).

# Google Sheets URL:
Paste the Google Sheets URL into the input field.
The agent will automatically fetch the data and display the dynamic headers.

# Perform Search:
Click on "Run Search" to perform a search for each item in the selected column of your dataset.

# Extract Info:
Once the search results are stored, click "Extract Info" to extract relevant information from SerpApi results.

# Write to Google Sheets:
After extraction, click "Write to Google Sheets" to save the extracted data back to the provided Google Sheets.

# Environment Variables
-GOOGLE_SHEETS_CREDENTIALS_JSON: Path to the Google Sheets API credentials JSON file.
-SERPAPI_KEY: Your SerpApi API key for web searches.
 ## Dependencies
-pandas
-requests
-gspread
-google-auth
-sklearn
-streamlit
-python-dotenv

## Future Improvements
Error Handling: Improve error handling for Google Sheets and SerpApi integration.
Batch Processing: Add support for processing multiple queries in a batch.
UI Enhancements: Improve the Streamlit UI for a better user experience.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
