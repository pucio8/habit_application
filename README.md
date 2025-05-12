# Habit Tracker Application

This is a Django-based web application for tracking and managing user-defined habits. Users can create habits, track their progress, and monitor their streaks of completion.

## Features

- **User Authentication**: Each user can create and manage their own habits.
- **Habit Creation**: Users can define their habits with a name, description, color, and duration.
- **Habit Tracking**: Users can mark habits as completed on specific days and track their progress.
- **Streak Tracking**: The app tracks consecutive days of habit completion, showing the current streak of completed days.
- **Completion Score**: Users can see a percentage score showing how much of their habit they have completed.

## Models

### Habit
The `Habit` model represents a habit created by the user.

- **user**: The user who created the habit (ForeignKey to CustomUser).
- **name**: The name of the habit (max length: 200).
- **description**: A brief description of the habit (optional, max length: 200).
- **color**: The UI color associated with the habit, selected from predefined colors (choices include "Bright Blue", "Tomato", "Gold", etc.).
- **created_at**: Timestamp of when the habit was created.
- **updated_at**: Timestamp of when the habit was last updated.

Methods:
- `score()`: Calculates the completion percentage of the habit between the first and last status entries.
- `current_streak()`: Returns the number of consecutive days the habit has been completed.
- `best_streak()`: Returns the longest streak (consecutive days) the habit has been completed.

### HabitStatus
The HabitStatus model tracks whether a habit was completed on a specific day for a given user.

- **user**: The user who marked the habit as done.
- **habit**: The habit being tracked.
- **date**: The date the habit was completed (or not completed).
- **done**: A boolean indicating whether the habit was completed on the given day.

This model ensures that a user can only have one entry per habit per day.

## Setup

### Prerequisites

1. Python 3.x
2. Django 5.x

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/pucio8/habits_application.git
   cd habits_application
   
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   
4. Apply database migrations:
   ```bash
   python manage.py migrate
   
5. Create a superuser to access the Django admin:
   ```bash
   python manage.py createsuperuser
   
7. Start the development server:
   ```bash
   python manage.py runserver
   
8. You can log in to the admin interface at:
   ```bash
   http://127.0.0.1:8000/admin

9. Access the application in your web browser at:
   ```bash
   http://127.0.0.1:8000/admin
   
## Usage
After logging in, you can:

Create and manage your own habits.
Mark habits as completed each day.
View your habit completion scores and streaks.

## Contributing

Thank you for considering contributing to this project! Here are the guidelines for submitting contributions:

### How to contribute:

1. **Fork the repository**:
   - Click the "Fork" button on the top right of this repository to create your own copy of the project.

2. **Create a new branch**:
   - After forking, create a new branch for your changes:
     ```bash
     git checkout -b feature-name
     ```

3. **Make your changes**:
   - Implement the new feature or bug fix you'd like to contribute.

4. **Commit your changes**:
   - Commit your changes to your branch with a clear and descriptive message:
     ```bash
     git commit -am 'Add feature-name'
     ```

5. **Push your changes**:
   - Push your changes to your fork:
     ```bash
     git push origin feature-name
     ```

6. **Open a pull request**:
   - Once your changes are pushed to your fork, go to the repository's main page and click on "New pull request".
   - Make sure to target the `contribution` branch and not `main`.

### Important Notes:
- **Only push to the `contribution` branch**: Pull requests to the `main` branch will be rejected.
- **Pull requests will be reviewed manually**: Contributions submitted to the `contribution` branch will be reviewed before being considered for merging into the `main` branch.
- **Do not merge into `main`**: We do not accept direct commits or pull requests to the `main` branch.

### Why the `contribution` branch?
We have created a dedicated `contribution` branch to handle feature additions, bug fixes, and improvements. This ensures that all contributions are reviewed and tested before being merged into the main project. We prefer to keep `main` stable and free of unverified changes.

Thank you again for your interest in contributing!