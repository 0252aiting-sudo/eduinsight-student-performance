# EduInsight – Student Analytics System

## Overview

EduInsight is a Python-based student analytics system developed to analyze student academic performance using the UCI Student Performance Dataset.

The system provides both a console-based interface and a graphical user interface (GUI) built with PyWebView. It helps users search student information, analyze academic results, visualize performance data, generate reports, and obtain AI-based performance comments.

## Features

- **Student Information Search** – Search and view student academic information.
- **Academic Performance Analysis** – Calculate average, highest, and lowest grades, as well as pass and fail statistics.
- **Performance Factor Analysis** – Analyze factors such as previous failures, study time, absences, and health.
- **Data Visualization** – Display student performance through charts.
- **Student Report Generation** – Generate academic performance reports in text format.
- **AI Performance Comments** – Generate student performance comments using Ollama, with rule-based fallback analysis.
- **Console Interface** – Run the system through the terminal.
- **Graphical User Interface** – Use the desktop application built with PyWebView.

## Technologies Used

- Python
- Pandas
- Matplotlib
- PyWebView
- Requests
- Ollama
- HTML
- CSS
- JavaScript

## Installation

1. Clone this repository:

   ```bash
   git clone YOUR_REPOSITORY_URL
   ```

2. Open the project folder:

   ```bash
   cd YOUR_REPOSITORY_FOLDER
   ```

3. Install the required libraries:

   ```bash
   pip install -r requirements.txt
   ```

## Run the Application

**GUI Version:**

```bash
python gui.py
```

**Console Version:**

```bash
python main.py
```

Ollama is used for AI-based performance comments when the service is available. The system also provides rule-based fallback comments when Ollama is unavailable.

## Dataset

This project uses the Student Performance Dataset from the UCI Machine Learning Repository.

Dataset: https://archive.ics.uci.edu/dataset/320/student+performance

## Project Structure

```text
asss/
├── web/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── ai_comment.py
├── analyzer.py
├── gui.py
├── main.py
├── report.py
├── requirements.txt
├── student-mat.csv
├── student.py
├── visualization.py
├── GUI_EXPLANATION_CN.md
├── Student_Report.txt
├── README.md
└── .gitignore
```

## Project Background

This project was developed as a final assignment for TCKA213 Introduction to Python Programming at New Era University College.

The project demonstrates Python programming concepts, including functions, conditional statements, loops, exception handling, file handling, data structures, and Object-Oriented Programming (OOP).
