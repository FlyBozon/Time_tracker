import sys
import time
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QLineEdit, QMessageBox, QComboBox, QHBoxLayout
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
TASKS_SHEET = CLIENT.open("TaskTracking").worksheet("Tasks")
TRACKING_SHEET = CLIENT.open("TaskTracking").worksheet("TaskTracking")

try:
    STATISTICS_SHEET = CLIENT.open("TaskTracking").worksheet("Statistics")
except gspread.exceptions.WorksheetNotFound:
    STATISTICS_SHEET = CLIENT.open("TaskTracking").add_worksheet(title="Statistics", rows="100", cols="30")


class TaskTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Time Tracker")
        self.resize(400, 500)

        self.tasks = []
        self.load_tasks()
        self.start_time = None
        self.selected_task = None
        self.on_break = False

        layout = QVBoxLayout()

        self.label = QLabel("Select a task:")
        layout.addWidget(self.label)

#show all tasks
        # self.list_widget = QListWidget()
        # self.list_widget.addItems([task["name"] for task in self.tasks])
        # layout.addWidget(self.list_widget)

#only active tasks
        self.list_widget = QListWidget()
        self.list_widget.addItems([task["name"] for task in self.tasks if task.get("active", "").lower() == "yes"])
        layout.addWidget(self.list_widget)

        self.add_task_input = QLineEdit()
        self.add_task_input.setPlaceholderText("Add new task...")
        layout.addWidget(self.add_task_input)

        self.add_description_input = QLineEdit()
        self.add_description_input.setPlaceholderText("Add description...")
        layout.addWidget(self.add_description_input)

        combo_layout = QHBoxLayout()

        combo_layout.addWidget(QLabel("Project:"))
        self.project_combo = QComboBox()
        self.project_combo.addItems(np.unique([task["project"] for task in self.tasks]))
        self.project_combo.setFixedWidth(150)
        combo_layout.addWidget(self.project_combo)

        combo_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(np.unique([task["category"] for task in self.tasks]))
        self.category_combo.setFixedWidth(150)
        combo_layout.addWidget(self.category_combo)

        layout.addLayout(combo_layout)

        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_task_button)

        self.start_button = QPushButton("Start Tracking")
        self.start_button.clicked.connect(self.start_tracking)
        layout.addWidget(self.start_button)

        self.break_button = QPushButton("Break")
        self.break_button.clicked.connect(self.break_time)
        layout.addWidget(self.break_button)

        self.stop_button = QPushButton("Stop & Save")
        self.stop_button.clicked.connect(self.stop_and_save)
        layout.addWidget(self.stop_button)

        self.analyze_button = QPushButton("Analyze Time")
        self.analyze_button.clicked.connect(self.analyze_time)
        layout.addWidget(self.analyze_button)

        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_tasks(self):
        self.tasks = []
        try:
            records = TASKS_SHEET.get_all_records(expected_headers=["Is active?", "Task Name", "Description", "Project", "Category"])
            for row in records:
                self.tasks.append({"active":row["Is active?"], "name": row["Task Name"], "description": row["Description"], "project": row["Project"], "category": row["Category"]})
        except gspread.exceptions.GSpreadException as e:
            QMessageBox.critical(self, "Error", f"Failed to load tasks: {str(e)}")

    def add_task(self):
        task_name = self.add_task_input.text().strip()
        task_description = self.add_description_input.text().strip()
        project_name = self.project_combo.currentText().strip()
        category_name = self.category_combo.currentText().strip()
        if task_name:
            TASKS_SHEET.append_row([task_name, task_description, project_name, category_name])
            self.tasks.append({"name": task_name, "description": task_description})
            self.list_widget.addItem(task_name)
            self.add_task_input.clear()
            self.add_description_input.clear()
            project_name = self.project_combo.clear()
            category_name = self.category_combo.clear()
            QMessageBox.information(self, "Task Added", f"Task '{task_name}' added.")
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid task name.")


    def start_tracking(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a task.")
            return
        self.selected_task = selected_items[0].text()
        self.start_time = time.time()
        self.status_label.setText(f"Tracking: {self.selected_task}")

    def break_time(self):
        if (not self.start_time) and (not self.on_break):
            QMessageBox.warning(self, "Error", "You are not doing anything.")
            return
        self.on_break = not self.on_break
        if self.on_break:
            duration = int(time.time() - self.start_time)
            self.start_time = time.time()
            self.status_label.setText("Status: Break")
            self.save_to_google_sheets(self.selected_task, duration)
            QMessageBox.information(self, "Break", f"Saved {duration} seconds for '{self.selected_task}'. Have a nice break and come back later!")
            self.selected_task = "Break"
            self.start_time = time.time()
        else:
            selected_items = self.list_widget.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Error", "Please select a task.")
                return
            self.selected_task = selected_items[0].text()
            self.start_time = time.time()
            self.status_label.setText(f"Tracking: {self.selected_task}")

    def stop_and_save(self):
        if self.start_time is None or self.selected_task is None:
            QMessageBox.warning(self, "Error", "No active tracking session.")
            return
        duration = int(time.time() - self.start_time)
        self.start_time = None
        self.status_label.setText("Status: Idle")
        self.save_to_google_sheets(self.selected_task, duration)
        QMessageBox.information(self, "Saved", f"Saved {duration} seconds for '{self.selected_task}'.")

    def save_to_google_sheets(self, task, duration):
        TRACKING_SHEET.append_row([task, duration, time.strftime('%Y-%m-%d %H:%M:%S')])

    def analyze_time(self):
        data = TRACKING_SHEET.get_all_records()
        if not data:
            QMessageBox.warning(self, "No Data", "No new records to analyze.")
            return

        today = datetime.today()
        monday = today - timedelta(days=today.weekday())
        week_dates = [(monday + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

        task_totals = {date: defaultdict(int) for date in week_dates}
        task_names = set()
        archive_rows = []

        for row in data:
            task = row["Task"]
            duration = int(row["Duration"])
            date_str = row["Timestamp"][:10]

            if date_str in week_dates:
                task_totals[date_str][task] += duration
                task_names.add(task)

            archive_rows.append([row["Task"], row["Duration"], row["Timestamp"]])

        stats_data = STATISTICS_SHEET.get_all_values()
        if not stats_data:
            QMessageBox.warning(self, "Error", "Statistics sheet is empty or missing headers.")
            return

        header = stats_data[0]
        existing_stats = {}
        sum_row_index = None

        for i, row in enumerate(stats_data[1:], start=1):
            task_name = row[0].strip()
            values = [int(x) if x.strip().isdigit() else 0 for x in row[1:]]

            if task_name.lower() == "sum":
                sum_row_index = i + 1
            else:
                existing_stats[task_name.lower()] = (task_name, values)

        for task in task_names:
            task_key = task.lower()
            if task_key not in existing_stats:
                existing_stats[task_key] = (task, [0] * (len(week_dates) + 1))

            task_name, values = existing_stats[task_key]
            for i, date in enumerate(week_dates):
                values[i] += task_totals[date].get(task, 0)
            values[-1] = sum(values[:-1])

        sum_row = ["Sum"] + [sum(existing_stats[task][1][i] for task in existing_stats) for i in range(len(week_dates))]
        sum_row.append(sum(sum_row[1:]))

        STATISTICS_SHEET.clear()
        STATISTICS_SHEET.append_row(header)

        if sum_row_index:
            STATISTICS_SHEET.update(f'A{sum_row_index}', [sum_row])
        else:
            STATISTICS_SHEET.append_row(sum_row)

        for task, values in existing_stats.values():
            STATISTICS_SHEET.append_row([task] + values)

        ARCHIVE_SHEET = CLIENT.open("TaskTracking").worksheet("Archive")
        for row in archive_rows:
            ARCHIVE_SHEET.append_row(row)

        TRACKING_SHEET.clear()
        TRACKING_SHEET.append_row(["Task", "Duration", "Timestamp"])

        QMessageBox.information(self, "Analysis Complete", "Statistics updated and records moved to Archive.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tracker = TaskTracker()
    tracker.show()
    sys.exit(app.exec_())
