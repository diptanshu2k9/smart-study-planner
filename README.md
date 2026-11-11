# Smart Study Planner

A modern desktop study task manager and schedule tracker built with Python, Tkinter, and SQLite. Designed to help students organize study subjects, set deadlines, track pending assignments, and visualize completion progress in real time.

---

## Features

- **Dark-Themed Dashboard**: Clean interface built with modern colors and responsive controls.
- **Real-Time Statistics**: Instant metric cards tracking Total Tasks, Pending Tasks, and Completed Tasks.
- **Dynamic Study Progress Bar**: Automatically calculates and displays your completion percentage as tasks get finished.
- **Task Management (CRUD)**:
  - Add tasks with Subject, Task Description, Deadline date picker/field, and Priority (High, Medium, Low).
  - Update existing task details with one click.
  - Quick toggle button to flip tasks between `Pending` and `Completed`.
  - Delete completed or outdated tasks.
- **Instant Search Filter**: Live table search filtering across subjects, task names, dates, and priorities.
- **Persistent Local Database**: Built-in SQLite database (`smart_study_planner.db`) saves your study tasks automatically across sessions.

---

## Tech Stack

- **Language**: Python 3
- **GUI Toolkit**: Tkinter & TTK
- **Database**: SQLite3
- **Platform**: Cross-platform (macOS, Windows, Linux)

---

## Getting Started

### Prerequisites

Ensure Python 3 is installed on your computer.

On macOS (using Homebrew):
```bash
brew install python-tk
```

### Installation & Running

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/smart-study-planner.git
   cd smart-study-planner
   ```

2. Run the application:
   ```bash
   python3 SmartStudy.py
   ```

---

## Author

**Diptanshu Kumar**

