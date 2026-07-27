import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import pandas as pd

from student import Student, ExcellentStudent
from analyzer import PerformanceAnalyzer
from visualization import Visualization
from ai_comment import OllamaAI
from report import ReportGenerator

# ==========================
# CustomTkinter Settings
# ==========================

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class EduInsightGUI(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("EduInsight Student Analytics System")
        self.geometry("1200x700")

        # ------------------------
        # Load Dataset
        # ------------------------

        self.data = pd.read_csv("student-mat.csv", sep=";")

        self.analyzer = PerformanceAnalyzer(self.data)
        self.visual = Visualization(self.data)
        self.report = ReportGenerator(self.data)
        self.ai = OllamaAI()

        # ------------------------
        # Sidebar
        # ------------------------

        self.sidebar = ctk.CTkFrame(
            self,
            width=220
            )

        self.sidebar.pack(side="left",fill="y")

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="EduInsight",
            font=("Arial",28,"bold")
        )

        self.logo.pack(pady=30)

        self.btn_dashboard = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=self.dashboard_page
        )

        self.btn_dashboard.pack(pady=10,padx=20)

        self.btn_search = ctk.CTkButton(
            self.sidebar,
            text="Search Student",
            command=self.search_page
        )

        self.btn_search.pack(pady=10,padx=20)

        self.btn_analytics = ctk.CTkButton(
            self.sidebar,
            text="Analytics",
            command=self.analytics_page
        )

        self.btn_analytics.pack(pady=10,padx=20)

        self.btn_report = ctk.CTkButton(
            self.sidebar,
            text="Generate Report",
            command=self.report_page
        )

        self.btn_report.pack(pady=10,padx=20)

        self.btn_exit = ctk.CTkButton(
            self.sidebar,
            text="Exit",
            fg_color="red",
            command=self.destroy
        )

        self.btn_exit.pack(side="bottom",pady=20)

        # ------------------------
        # Main Frame
        # ------------------------

        self.main = ctk.CTkFrame(self)

        self.main.pack(fill="both",expand=True,padx=20,pady=20)

        self.dashboard_page()

    # =====================================
    # Clear Main Frame
    # =====================================

    def clear_main(self):

        for widget in self.main.winfo_children():
            widget.destroy()


    # =====================================
    # Dashboard
    # =====================================

    def dashboard_page(self):

        self.clear_main()

        dashboard_scroll = ctk.CTkScrollableFrame(
            self.main
        )

        dashboard_scroll.pack(
            fill="both",
            expand=True
        )

        title = ctk.CTkLabel(
            dashboard_scroll,
            text="EduInsight Dashboard",
            font=("Arial",28,"bold")
        )

        title.pack(pady=20)

        subtitle = ctk.CTkLabel(
            dashboard_scroll,
            text="Student Academic Performance Analytics System",
            font=("Arial",16)
        )

        subtitle.pack(pady=5)

        # ===========================
        # Statistics Frame
        # ===========================

        stats = ctk.CTkFrame(dashboard_scroll)

        stats.pack(fill="x",padx=30,pady=20)

        total = len(self.data)
        average = self.analyzer.average_grade()
        highest = self.analyzer.highest_grade()
        pass_student = self.analyzer.pass_students()
        fail_student = self.analyzer.fail_students()
        excellent = len(self.data[self.data["G3"] >= 18])

        labels = [

            ("Total Students", total),

            ("Average Grade", round(average,2)),

            ("Highest Grade", highest),

            ("Pass Students", pass_student),

            ("Fail Students", fail_student),

            ("Excellent Students", excellent)

        ]

        for text,value in labels:

            card = ctk.CTkFrame(stats)

            card.pack(fill="x",padx=15,pady=10)

            left = ctk.CTkLabel(
                card,
                text=text,
                font=("Arial",16,"bold")
            )

            left.pack(side="left",padx=20,pady=15)

            right = ctk.CTkLabel(
                card,
                text=str(value),
                font=("Arial",18)
            )

            right.pack(side="right",padx=20)

        # ===========================
        # Feature Box
        # ===========================

        feature = ctk.CTkFrame(dashboard_scroll)

        feature.pack(fill="both",expand=True,padx=30,pady=10)

        ctk.CTkLabel(
            feature,
            text="System Features",
            font=("Arial",20,"bold")
        ).pack(anchor="w",padx=20,pady=15)

        text = """
    ✓ Search Student Information

    ✓ Performance Factors Analysis

    ✓ AI Performance Comment

    ✓ Student Statistics

    ✓ Data Visualization

    ✓ Generate Report
    """

        textbox = ctk.CTkTextbox(
            feature,
            height=180
        )

        textbox.pack(fill="both",expand=True,padx=20,pady=15)

        textbox.insert("1.0",text)

        textbox.configure(state="disabled")

    # =====================================
    # Search Student Page
    # =====================================

    def search_page(self):

        self.clear_main()

        title = ctk.CTkLabel(
            self.main,
            text="Student Search",
            font=("Arial",28,"bold")
        )

        title.pack(pady=15)

        search_frame = ctk.CTkFrame(self.main)

        search_frame.pack(fill="x",padx=20,pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Student ID"
        ).pack(side="left",padx=15)

        self.entry_id = ctk.CTkEntry(
            search_frame,
            width=200
        )

        self.entry_id.pack(side="left",padx=10)

        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_student
        ).pack(side="left",padx=10)

        ctk.CTkButton(
            search_frame,
            text="New Search",
            command=self.new_search
        ).pack(side="left",padx=10)

        # ===========================
        # Student Information
        # ===========================

        self.info_box = ctk.CTkTextbox(
            self.main,
            height=180
        )

        self.info_box.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # ===========================
        # Performance Factors
        # ===========================

        self.factor_box = ctk.CTkTextbox(
            self.main,
            height=180
        )

        self.factor_box.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # ===========================
        # AI Comment
        # ===========================

        self.ai_box = ctk.CTkTextbox(
            self.main,
            height=180
        )

        self.ai_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

    def new_search(self):

        self.entry_id.delete(
            0,
            "end"
        )

        self.info_box.delete(
            "1.0",
            "end"
        )

        self.factor_box.delete(
            "1.0",
            "end"
        )

        self.ai_box.delete(
            "1.0",
            "end"
        )

        self.entry_id.focus()

    def search_student(self):

        self.info_box.delete("1.0","end")
        self.factor_box.delete("1.0","end")
        self.ai_box.delete("1.0","end")

        try:

            student_id = int(self.entry_id.get())

        except:

            messagebox.showerror(
                "Error",
                "Please enter a valid Student ID."
            )

            return

        if student_id < 1 or student_id > len(self.data):

            messagebox.showerror(
                "Error",
                "Student ID not found."
            )

            return

        row = self.data.iloc[student_id-1]

        info = f"""
Student Information

Student ID : {student_id}

School : {row['school']}

Age : {row['age']}

Gender : {row['sex']}

Final Grade : {row['G3']}

Previous Failures : {row['failures']}

Study Time : {row['studytime']}

Absences : {row['absences']}

Health : {row['health']}
"""

        self.info_box.insert(
            "1.0",
            info
        )

        factors = self.analyzer.analyze_performance_factors(row)

        text = "Performance Factors\n\n"

        for factor in factors:

            text += f"""
    {factor['factor']}

    Importance : {factor['importance']}%

    Analysis :
    {factor['analysis']}

    Recommendation :
    {factor['recommendation']}

    --------------------------
    """

        self.factor_box.insert(
            "1.0",
            text
        )

        student_data = {

            "student_id":student_id,

            "G3":row["G3"],

            "failures":row["failures"],

            "studytime":row["studytime"],

            "absences":row["absences"],

            "health":row["health"]

        }

        ai = self.ai.generate_performance_analysis(
            student_data,
            factors
        )

        self.ai_box.insert(
            "1.0",
               ai
        )

    # =====================================
    # Analytics Page
    # =====================================

    def analytics_page(self):

        self.clear_main()

        title = ctk.CTkLabel(
            self.main,
            text="Student Analytics",
            font=("Arial",28,"bold")
        )

        title.pack(pady=15)

        body = ctk.CTkFrame(self.main)

        body.pack(fill="both",expand=True,padx=20,pady=10)

        # -------------------------
        # Left Panel
        # -------------------------

        left = ctk.CTkFrame(body,width=300)

        left.pack(side="left",fill="y",padx=10)

        average = round(self.analyzer.average_grade(),2)
        highest = self.analyzer.highest_grade()
        lowest = self.analyzer.lowest_grade()
        passed = self.analyzer.pass_students()
        failed = self.analyzer.fail_students()

        excellent = len(
            self.data[self.data["G3"]>=18]
        )

        info = f"""
    Total Students : {len(self.data)}

    Average Grade : {average}

    Highest Grade : {highest}

    Lowest Grade : {lowest}

    Pass Students : {passed}

    Fail Students : {failed}

    Excellent Students : {excellent}
    """

        textbox = ctk.CTkTextbox(
            left,
            width=250,
            height=280
        )

        textbox.pack(padx=15,pady=20)

        textbox.insert("1.0",info)

        textbox.configure(state="disabled")

        # -------------------------
        # Chart Buttons
        # -------------------------

        ctk.CTkButton(
            left,
            text="Pass vs Fail",
            command=self.show_pass_chart
        ).pack(fill="x",padx=15,pady=5)

        ctk.CTkButton(
            left,
            text="Grade Distribution",
            command=self.show_histogram
        ).pack(fill="x",padx=15,pady=5)

        ctk.CTkButton(
            left,
            text="Study Time",
            command=self.show_study_chart
        ).pack(fill="x",padx=15,pady=5)

        # -------------------------
        # Right Panel
        # -------------------------

        self.chart_frame = ctk.CTkFrame(body)

        self.chart_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=10
        )

        self.after(
            100,
        )

    def clear_chart(self):

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

    def show_pass_chart(self):

        self.clear_chart()

        passed = self.analyzer.pass_students()
        failed = self.analyzer.fail_students()

        fig = plt.Figure(figsize=(6,4))

        ax = fig.add_subplot(111)

        ax.bar(
            ["Pass","Fail"],
            [passed,failed]
        )

        ax.set_title("Pass vs Fail")

        self.canvas = FigureCanvasTkAgg(
            fig,
            master=self.chart_frame
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def show_histogram(self):

        self.clear_chart()

        fig = plt.Figure(figsize=(6,4))

        ax = fig.add_subplot(111)

        ax.hist(
            self.data["G3"],
            bins=10
        )

        ax.set_title("Grade Distribution")

        ax.set_xlabel("Grade")

        ax.set_ylabel("Students")

        self.canvas = FigureCanvasTkAgg(
            fig,
            master=self.chart_frame
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def show_study_chart(self):

        self.clear_chart()

        avg = self.data.groupby(
            "studytime"
        )["G3"].mean()

        fig = plt.Figure(figsize=(6,4))

        ax = fig.add_subplot(111)

        ax.plot(
            avg.index,
            avg.values,
            marker="o"
        )

        ax.set_title("Study Time vs Average Grade")

        ax.set_xlabel("Study Time")

        ax.set_ylabel("Average Grade")

        self.canvas = FigureCanvasTkAgg(
            fig,
            master=self.chart_frame
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    # =====================================
    # Report Page
    # =====================================

    def report_page(self):

        self.clear_main()

        title = ctk.CTkLabel(
            self.main,
            text="Report Generator",
            font=("Arial",28,"bold")
        )

        title.pack(pady=20)

        ctk.CTkLabel(
            self.main,
            text="Generate student performance report."
        ).pack()

        self.report_status = ctk.CTkLabel(
            self.main,
            text="Status : Ready",
            font=("Arial",16)
        )

        self.report_status.pack(pady=20)

        ctk.CTkButton(
            self.main,
            text="Generate Report",
            width=220,
            height=40,
            command=self.generate_report
        ).pack(pady=10)

        ctk.CTkButton(
            self.main,
            text="Open Report",
            width=220,
            height=40,
            command=self.open_report
        ).pack(pady=10)

    def generate_report(self):

        self.report.generate_report()

        self.report_status.configure(
            text="Status : Report Generated Successfully"
        )

        messagebox.showinfo(
            "Success",
            "Student_Report.txt has been generated."
        )

    def open_report(self):

        import os

        try:

            os.startfile("Student_Report.txt")

        except:

            messagebox.showerror(
                "Error",
                "Report not found.\nPlease generate the report first."
            )

if __name__ == "__main__":

    app = EduInsightGUI()

    app.mainloop()        