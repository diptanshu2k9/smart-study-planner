import os
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

os.environ["TK_SILENCE_DEPRECATION"] = "1"


class SmartStudyPlanner:
    BG_MAIN = "#111827"
    BG_CARD = "#1f2937"
    BG_INPUT = "#374151"
    TEXT_WHITE = "#ffffff"
    TEXT_MUTED = "#9ca3af"

    COLOR_TOTAL = "#818cf8"
    COLOR_PENDING = "#f87171"
    COLOR_COMPLETED = "#34d399"

    BTN_ADD = "#6366f1"
    BTN_UPDATE = "#2563eb"
    BTN_TOGGLE = "#059669"
    BTN_DELETE = "#dc2626"
    BTN_CLEAR = "#4b5563"

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Study Planner")
        self.root.geometry("1020x720")
        self.root.minsize(920, 640)

        try:
            self.root.tk.call("tk::unsupported::MacWindowStyle", "appearance", self.root._w, "aqua")
        except Exception:
            pass

        self.root.configure(bg=self.BG_MAIN)

        self.init_db()
        self.configure_styles()
        self.build_ui()
        self.load_tasks()
        self.root.update_idletasks()

    def init_db(self):
        self.conn = sqlite3.connect("smart_study_planner.db")
        self.cur = self.conn.cursor()

        try:
            self.cur.execute("PRAGMA table_info(study_tasks)")
            cols = [col[1] for col in self.cur.fetchall()]
            if cols and "deadline" not in cols:
                self.cur.execute("DROP TABLE study_tasks")
        except Exception:
            pass

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS study_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                deadline TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        """)
        self.conn.commit()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure(
            "Custom.Treeview",
            background="#1e293b",
            foreground="#f8fafc",
            fieldbackground="#1e293b",
            rowheight=30,
            font=("Helvetica", 10),
            borderwidth=0,
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#0f172a",
            foreground="#ffffff",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padding=(8, 8),
        )
        self.style.map(
            "Custom.Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "#ffffff")],
        )
        self.style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#1e293b")],
        )

        self.style.configure(
            "Custom.TCombobox",
            fieldbackground=self.BG_INPUT,
            background=self.BG_INPUT,
            foreground="#ffffff",
            arrowcolor="#ffffff",
            padding=5,
        )

    def create_color_btn(self, parent, text, bg_color, command):
        btn = tk.Label(
            parent,
            text=text,
            bg=bg_color,
            fg="white",
            font=("Helvetica", 10, "bold"),
            padx=14,
            pady=7,
            cursor="hand2",
            relief="flat",
        )
        btn.pack(side=tk.LEFT, padx=(0, 8))

        def on_enter(e):
            btn.config(relief="groove")

        def on_leave(e):
            btn.config(relief="flat")

        def on_press(e):
            btn.config(relief="sunken")

        def on_release(e):
            btn.config(relief="flat")
            try:
                command()
            except Exception as ex:
                messagebox.showerror("Error", f"Action failed: {ex}")

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        return btn

    def build_ui(self):
        self.container = tk.Frame(self.root, bg=self.BG_MAIN)
        self.container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        self._build_header()
        self._build_stat_cards()
        self._build_progress_bar()
        self._build_form()
        self._build_search_and_table()
        self._build_footer()

    def _build_header(self):
        hdr = tk.Frame(self.container, bg=self.BG_MAIN)
        hdr.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            hdr,
            text="SMART STUDY PLANNER",
            font=("Helvetica", 20, "bold"),
            bg=self.BG_MAIN,
            fg=self.TEXT_WHITE,
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Organize your study tasks. Achieve your goals.",
            font=("Helvetica", 10),
            bg=self.BG_MAIN,
            fg=self.TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

    def _build_stat_cards(self):
        cards_frame = tk.Frame(self.container, bg=self.BG_MAIN)
        cards_frame.pack(fill=tk.X, pady=(0, 15))

        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)

        card_configs = [
            ("TOTAL TASKS", self.COLOR_TOTAL, "total"),
            ("PENDING", self.COLOR_PENDING, "pending"),
            ("COMPLETED", self.COLOR_COMPLETED, "completed"),
        ]

        self.stat_labels = {}
        for idx, (title, color, key) in enumerate(card_configs):
            card = tk.Frame(
                cards_frame,
                bg=self.BG_CARD,
                highlightbackground="#2d3748",
                highlightthickness=1,
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=6 if idx == 1 else (0, 6) if idx == 0 else (6, 0))

            tk.Label(
                card,
                text=title,
                font=("Helvetica", 9, "bold"),
                bg=self.BG_CARD,
                fg=self.TEXT_MUTED,
            ).pack(anchor="w", padx=16, pady=(12, 4))

            lbl_val = tk.Label(
                card,
                text="0",
                font=("Helvetica", 22, "bold"),
                bg=self.BG_CARD,
                fg=color,
            )
            lbl_val.pack(anchor="w", padx=16, pady=(0, 12))
            self.stat_labels[key] = lbl_val

    def _build_progress_bar(self):
        p_frame = tk.Frame(self.container, bg=self.BG_MAIN)
        p_frame.pack(fill=tk.X, pady=(0, 15))

        self.lbl_progress = tk.Label(
            p_frame,
            text="Study Progress: 0%",
            font=("Helvetica", 10, "bold"),
            bg=self.BG_MAIN,
            fg=self.TEXT_WHITE,
        )
        self.lbl_progress.pack(anchor="w", pady=(0, 6))

        self.bar_bg = tk.Frame(p_frame, bg=self.BG_CARD, height=12)
        self.bar_bg.pack(fill=tk.X)
        self.bar_bg.pack_propagate(False)

        self.bar_fill = tk.Frame(self.bar_bg, bg=self.COLOR_COMPLETED, height=12)
        self.bar_fill.place(x=0, y=0, relwidth=0.0, relheight=1.0)

    def _build_form(self):
        f_frame = tk.Frame(self.container, bg=self.BG_MAIN)
        f_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            f_frame,
            text="Manage Your Study Tasks",
            font=("Helvetica", 13, "bold"),
            bg=self.BG_MAIN,
            fg=self.TEXT_WHITE,
        ).pack(anchor="w", pady=(0, 8))

        input_row = tk.Frame(f_frame, bg=self.BG_MAIN)
        input_row.pack(fill=tk.X)

        col1 = tk.Frame(input_row, bg=self.BG_MAIN)
        col1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(col1, text="Subject", font=("Helvetica", 9), bg=self.BG_MAIN, fg=self.TEXT_MUTED).pack(anchor="w")
        self.ent_subject = tk.Entry(
            col1, bg=self.BG_INPUT, fg=self.TEXT_WHITE, font=("Helvetica", 10),
            insertbackground="white", relief="flat", bd=5
        )
        self.ent_subject.pack(fill=tk.X, pady=(2, 0))

        col2 = tk.Frame(input_row, bg=self.BG_MAIN)
        col2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(col2, text="Study Task", font=("Helvetica", 9), bg=self.BG_MAIN, fg=self.TEXT_MUTED).pack(anchor="w")
        self.ent_task = tk.Entry(
            col2, bg=self.BG_INPUT, fg=self.TEXT_WHITE, font=("Helvetica", 10),
            insertbackground="white", relief="flat", bd=5
        )
        self.ent_task.pack(fill=tk.X, pady=(2, 0))

        col3 = tk.Frame(input_row, bg=self.BG_MAIN)
        col3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(col3, text="Deadline (YYYY-MM-DD)", font=("Helvetica", 9), bg=self.BG_MAIN, fg=self.TEXT_MUTED).pack(anchor="w")
        self.ent_deadline = tk.Entry(
            col3, bg=self.BG_INPUT, fg=self.TEXT_WHITE, font=("Helvetica", 10),
            insertbackground="white", relief="flat", bd=5
        )
        self.ent_deadline.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_deadline.pack(fill=tk.X, pady=(2, 0))

        col4 = tk.Frame(input_row, bg=self.BG_MAIN)
        col4.pack(side=tk.LEFT, fill=tk.X, expand=False, padx=(0, 0))
        tk.Label(col4, text="Priority", font=("Helvetica", 9), bg=self.BG_MAIN, fg=self.TEXT_MUTED).pack(anchor="w")
        self.priority_var = tk.StringVar(value="Medium")
        self.combo_priority = ttk.Combobox(
            col4, textvariable=self.priority_var, values=["High", "Medium", "Low"],
            state="readonly", width=12, style="Custom.TCombobox", font=("Helvetica", 10)
        )
        self.combo_priority.pack(fill=tk.X, pady=(3, 0))

        btn_row = tk.Frame(f_frame, bg=self.BG_MAIN)
        btn_row.pack(fill=tk.X, pady=(12, 0))

        self.create_color_btn(btn_row, "+ Add Task", self.BTN_ADD, self.add_task)
        self.create_color_btn(btn_row, "Update", self.BTN_UPDATE, self.update_task)
        self.create_color_btn(btn_row, "Mark Complete / Pending", self.BTN_TOGGLE, self.toggle_status)
        self.create_color_btn(btn_row, "Delete", self.BTN_DELETE, self.delete_task)
        self.create_color_btn(btn_row, "Clear", self.BTN_CLEAR, self.clear_fields)

    def _build_search_and_table(self):
        s_frame = tk.Frame(self.container, bg=self.BG_MAIN)
        s_frame.pack(fill=tk.X, pady=(10, 8))

        tk.Label(
            s_frame, text="Search:", font=("Helvetica", 10, "bold"),
            bg=self.BG_MAIN, fg=self.TEXT_MUTED
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.filter_tasks())

        self.ent_search = tk.Entry(
            s_frame, textvariable=self.search_var, bg=self.BG_INPUT,
            fg=self.TEXT_WHITE, font=("Helvetica", 10),
            insertbackground="white", relief="flat", bd=5
        )
        self.ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True)

        t_frame = tk.Frame(self.container, bg=self.BG_MAIN)
        t_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Subject", "Task", "Deadline", "Priority", "Status")
        self.tree = ttk.Treeview(
            t_frame, columns=columns, show="headings",
            style="Custom.Treeview", selectmode="browse"
        )

        col_widths = {"ID": 50, "Subject": 160, "Task": 260, "Deadline": 130, "Priority": 100, "Status": 110}
        for col, width in col_widths.items():
            self.tree.heading(col, text=col)
            align = "center" if col in ("ID", "Priority", "Status", "Deadline") else "w"
            self.tree.column(col, width=width, anchor=align)

        scrollbar = ttk.Scrollbar(t_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def _build_footer(self):
        footer = tk.Frame(self.container, bg=self.BG_MAIN)
        footer.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            footer,
            text="Made By Diptanshu Kumar",
            font=("Helvetica", 10),
            bg=self.BG_MAIN,
            fg=self.TEXT_MUTED,
        ).pack(anchor="center")

    def _update_stats(self, rows):
        total = len(rows)
        completed = sum(1 for r in rows if r[5] == "Completed")
        pending = total - completed
        pct = int((completed / total) * 100) if total > 0 else 0

        self.stat_labels["total"].config(text=str(total))
        self.stat_labels["pending"].config(text=str(pending))
        self.stat_labels["completed"].config(text=str(completed))

        self.lbl_progress.config(text=f"Study Progress: {pct}%")
        self.bar_fill.place(x=0, y=0, relwidth=pct / 100.0, relheight=1.0)

    def load_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cur.execute("SELECT * FROM study_tasks")
        rows = self.cur.fetchall()
        for r in rows:
            self.tree.insert("", tk.END, values=r)

        self._update_stats(rows)

    def filter_tasks(self):
        q = self.search_var.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.cur.execute("SELECT * FROM study_tasks")
        rows = self.cur.fetchall()
        for r in rows:
            if not q or any(q in str(v).lower() for v in r):
                self.tree.insert("", tk.END, values=r)

    def on_row_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        row = self.tree.item(sel[0])["values"]
        self.ent_subject.delete(0, tk.END)
        self.ent_subject.insert(0, row[1])

        self.ent_task.delete(0, tk.END)
        self.ent_task.insert(0, row[2])

        self.ent_deadline.delete(0, tk.END)
        self.ent_deadline.insert(0, row[3])

        self.priority_var.set(row[4])

    def clear_fields(self):
        self.ent_subject.delete(0, tk.END)
        self.ent_task.delete(0, tk.END)
        self.ent_deadline.delete(0, tk.END)
        self.ent_deadline.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.priority_var.set("Medium")
        self.search_var.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def add_task(self):
        sub = self.ent_subject.get().strip()
        task = self.ent_task.get().strip()
        due = self.ent_deadline.get().strip()
        pri = self.priority_var.get()

        if not sub or not task or not due:
            messagebox.showerror("Error", "Please fill in Subject, Task, and Deadline!")
            return

        try:
            self.cur.execute(
                "INSERT INTO study_tasks (subject, topic, deadline, priority, status) VALUES (?, ?, ?, ?, ?)",
                (sub, task, due, pri, "Pending"),
            )
            self.conn.commit()
            self.clear_fields()
            self.load_tasks()
            messagebox.showinfo("Success", "Study task added successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add task: {e}")

    def update_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a task from the table to update.")
            return

        task_id = self.tree.item(sel[0])["values"][0]
        sub = self.ent_subject.get().strip()
        task = self.ent_task.get().strip()
        due = self.ent_deadline.get().strip()
        pri = self.priority_var.get()

        if not sub or not task or not due:
            messagebox.showerror("Error", "All fields are required for updating!")
            return

        try:
            self.cur.execute(
                "UPDATE study_tasks SET subject = ?, topic = ?, deadline = ?, priority = ? WHERE id = ?",
                (sub, task, due, pri, task_id),
            )
            self.conn.commit()
            self.load_tasks()
            messagebox.showinfo("Updated", "Task updated successfully!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not update task: {e}")

    def toggle_status(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a task to toggle status.")
            return

        task_id = self.tree.item(sel[0])["values"][0]
        cur_status = self.tree.item(sel[0])["values"][5]
        new_status = "Completed" if cur_status == "Pending" else "Pending"

        try:
            self.cur.execute(
                "UPDATE study_tasks SET status = ? WHERE id = ?",
                (new_status, task_id),
            )
            self.conn.commit()
            self.load_tasks()
            messagebox.showinfo("Status Updated", f"Task marked as {new_status}!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not update status: {e}")

    def delete_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return

        task_id = self.tree.item(sel[0])["values"][0]
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this task?")
        if confirm:
            try:
                self.cur.execute("DELETE FROM study_tasks WHERE id = ?", (task_id,))
                self.conn.commit()
                self.clear_fields()
                self.load_tasks()
                messagebox.showinfo("Deleted", "Task deleted successfully!")
            except Exception as e:
                messagebox.showerror("Database Error", f"Could not delete task: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SmartStudyPlanner(root)
    root.mainloop()
