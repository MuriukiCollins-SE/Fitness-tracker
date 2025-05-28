# Fitness Tracker CLI

A simple command-line app to track workouts and exercises. Data is saved in a SQLite database. Trainers and trainees can log and manage workouts easily.

---

## Features

- Add, delete, or update workouts
- Add, delete, or update exercises (e.g., push-ups, running)
- Group exercises by type: **Strength**, **Cardio**, **Flexibility**
- Track trainees and their assigned trainers
- Show workout summaries with reps, sets, and weights
- All data saved in `fitness_tracker.db`

---

## Installation

### Requirements

- Python 3.8.13 (other 3.8 versions may work)
- Linux, macOS, or Windows
- [SQLAlchemy](https://www.sqlalchemy.org/)

### Setup Steps

1. **Get the Project**

   - Using Git:
     ```sh
     git clone git@github.com:MuriukiCollins-SE/Fitness-tracker.git
     cd fitness-tracker
     ```
   - Or download and unzip the project files.

2. **Set Up a Virtual Environment**

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate  
   ```

3. **Install Dependencies**

   - Create a `requirements.txt` file with:
     ```
     sqlalchemy==2.0.35
     ```
   - Then install:
     ```sh
     pip install -r requirements.txt
     ```

4. **Check Project Structure**

   ```
   Fitness-Tracker/
   ├── lib/
   │   ├── db/
   │   │   ├── models.py
   │   │   └── seed.py
   │   ├── helpers.py
   │   └── tracker.py
   ├── cli.py
   ├── fitness_tracker.db  
   ├── Pipfile
   ├── Pipfile.lock
   └── README.md
   ```

5. **Start the Database**

   - The app creates `fitness_tracker.db` automatically when you run it.
   - Trainers are seeded automatically if needed.

---

## Usage

### Start the App

1. Activate the virtual environment:
   ```sh
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Run the app:
   ```sh
   python -m lib.tracker
   ```

### Main Menu

You will see the following options:

```
Fitness Tracker CLI
1. View Trainer Menu
2. Track Trainee Progress
3. View Workouts
4. Exercise Menu
5. Exit
```

Type a number (1-5) to choose an option.

### Example: Add a Workout and Exercises

1. Choose **3. View Workouts**.
2. Pick **1. Create Workout**.
3. Answer the prompts:
   ```
   How many workouts to create (1-4)? 1
   Enter trainee ID: 3
   Enter details for Workout 1:
   Enter duration (minutes): 20
   Enter notes (optional): Afternoon workout
   How many exercises for Workout ID 103 (0-4)? 2
   ```
4. Enter exercise details:
   ```
   Enter details for Exercise 1:
   Exercise name: Push-ups
   Category (Strength/Cardio/Flexibility): Strength
   Reps: 15
   Sets: 3
   Weight (optional, press enter to skip): 
   
   Enter details for Exercise 2:
   Exercise name: Running
   Category (Strength/Cardio/Flexibility): Cardio
   Reps: 30
   Sets: 1
   Weight (optional, press enter to skip): 
   ```
5. You will see a confirmation like:
   ```
   Created workout ID 103 with exercise IDs: 104, 105
   ```

### Check exercises:

1. Choose **5. View Exercises for Workout**.
2. Type **103** to see Push-ups and Running.

### Example: See All Workouts

1. Choose **3. View Workouts**.
2. Then select **3. List All Workouts**.
3. You will see a table of all workouts, for example:

```
All Workouts (1 total)
+----+--------------------+--------------+-------+--------------+--------------+
| ID | Date               | Duration (min) | Notes | Trainee Name | Trainee ID   |
+----+--------------------+--------------+-------+--------------+--------------+
| 103| 2025-05-28 00:00:01| 20           | Afternoon workout | Emma | 3         |
+----+--------------------+--------------+-------+--------------+--------------+
```

---

## Files and Folders

- `lib/`: Contains the app’s code.
- `db/models.py`: Sets up data structure for workouts and exercises.
- `helpers.py`: Provides utility functions to check inputs and display tables.
- `tracker.py`: The main application file you run.

- `fitness_tracker.db`: The database file where all data is saved (created when you run the app).
- `requirements.txt`: Lists the required Python packages (like SQLAlchemy).

---

## Database Info

- **File**: `fitness_tracker.db` in the project folder.
- **Tables**:
  - `trainers`: ID, name.
  - `trainees`: ID, name, trainer ID.
  - `workouts`: ID, date, duration, notes, trainee ID.
  - `exercises`: ID, name, category, reps, sets, weight, workout ID.

### Rules:

- Exercises must be linked to a workout.
- Workouts must be linked to a trainee.
- Deleting a workout will remove its associated exercises.

> **Tip**: To make deleting easier, ask the project owner to update the database rules.

---

## How to Help

1. **Copy the project** (fork it on GitHub).
2. **Make a new branch**:
   ```sh
   git checkout -b my-new-feature
   ```
3. **Save your changes**:
   ```sh
   git commit -m "Added my feature"
   ```
4. **Send your changes**:
   ```sh
   git push origin my-new-feature
   ```
5. **Create a Pull Request** on GitHub to merge your changes.

- Use clear and descriptive code.
- Add comments to explain any new features or changes.

---

## License

This project uses the MIT License. You can use or change it freely. Check the LICENSE.txt file for more details.

---

## Contact

For help, suggestions, or issues:

- **Email**: your.email@example.com
- **GitHub**: [yourusername/fitness-tracker](https://github.com/yourusername/fitness-tracker/issues)

