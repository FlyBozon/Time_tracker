# Task Time Tracker

This is a **Task Time Tracking Application** built with **Python and PyQt5**, using **Google Sheets** for data storage.  
It allows users to track task durations, analyze weekly statistics, and archive completed tasks.

## **Features**
- **Track task durations** with Start and Stop functionality.
- **Analyze weekly statistics** and update a Google Sheet.
- **Automatically move processed records** to an archive.
- **Prevents duplicate "Sum" rows** in statistics.
- **Ensures case-insensitive task matching.**

---

## **Setup Instructions**

### **1. Install Required Dependencies**
Ensure you have Python 3 installed, then run:
```bash
pip install -r requirements.txt
```
If you don't have a requirements.txt file, install dependencies manually:

```bash
pip install PyQt5 gspread oauth2client
```
### **2. Google Credentials Setup**
This project uses Google Sheets API and Google Drive API to store and retrieve data. You need to create API credentials for authentication.

#### What Are Google Credentials?
Google credentials allow your Python script to access Google Sheets securely.
The credentials come in a JSON file that contains authentication keys, including:

Client ID & Client Secret → Identifies the app to Google.
Project ID → Links the credentials to a specific Google Cloud project.
Private Key → Used for authentication.
Service Account Email → This acts as a virtual user with permission to modify your spreadsheet.
#### Step 1: Create a Google Cloud Project
Go to Google Cloud Console.
Click "Create Project" and give it a name (e.g., TaskTimeTracker).
Navigate to "APIs & Services" > "Library".
Search for Google Sheets API and enable it.
Search for Google Drive API and enable it.
#### Step 2: Create Service Account & Download Credentials
Go to "APIs & Services" > "Credentials".
Click "Create Credentials" > "Service Account".
Give it a name (e.g., TaskTrackerService).
Click "Create", then go to the "Keys" tab.
Click "Add Key" > "JSON", and it will download a file (e.g., credentials.json).
#### Step 3: Share Your Google Sheets with the Service Account
Open Google Sheets.
Create a new spreadsheet and rename it (e.g., "TaskTracking").
Click "Share" and add the email from your credentials.json
(it looks like task-tracker@your-project.iam.gserviceaccount.com).
Give it Editor permissions.
### 3. Configure Google Sheets in Code
Place your downloaded credentials.json file in the project directory.
Ensure the file is named exactly as credentials.json, or update the code in time.py:
``` python
CREDS = ServiceAccountCredentials.from_json_keyfile_name("your_credentials_file.json", SCOPE)
```
The app will now have access to the Google Sheets you shared.
Running the Application
Start the tracker by running:

``` bash
python time.py
```
This will launch the PyQt5 UI.

### Google Sheets Structure
The app interacts with three sheets:

Tasks → Stores the list of tasks.
TaskTracking → Stores ongoing task tracking data.
Statistics → Stores weekly reports and totals.
Once tasks are analyzed, they are moved to "Archive" and cleared from the tracking sheet.
Contributing
If you want to contribute:

Fork the repo.
Create a feature branch (git checkout -b feature-branch).
Commit your changes (git commit -m "Add new feature").
Push the branch (git push origin feature-branch).
Open a Pull Request.
License
This project is licensed under the MIT License.

### Troubleshooting
1. Permission Denied on Google Sheets?
Ensure the service account email has Editor access to your Google Sheet.
Try re-sharing the sheet with the correct email.
2. Application crashes on startup?
Check if credentials.json is present and correctly named.
3. Statistics are duplicated?
Ensure you are using the latest script version, which prevents duplicate "Sum" rows.


## Author
Developed by FlyBozon

For questions or issues, open a GitHub Issue.
