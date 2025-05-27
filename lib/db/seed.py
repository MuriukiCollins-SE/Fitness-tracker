from lib.db.models import Session, init_db, Workout, Exercise
from lib.helpers import validate_positive_int, validate_float, print_table
from datetime import datetime

def main_menu():
    print("\nFitness Tracker CLI")
    print("1. Manage Workouts")
    print("2. Manage Exercises")
    print("3. Exit")

def workout_menu():
    print("\nWorkout Menu")
    print("1. Create Workout")
    print("2. Delete Workout")
    print("3. List All Workouts")
    print("4. Find Workout by ID")
    print("5. View Exercises for Workout")
    print("6. Update Workout")
    print("7. Back")

def exercise_menu():
    print("\nExercise Menu")
    print("1. Create Exercise")
    print("2. Delete Exercise")
    print("3. List All Exercises")
    print("4. Find Exercise by ID")
    print("5. Filter Exercises by Category")
    print("6. Update Exercise")
    print("7. Back")

def main():
    init_db()
    session = Session()

    while True:
        main_menu()
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            while True:
                workout_menu()
                w_choice = input("Enter choice (1-7): ").strip()
                
                if w_choice == '1':
                    try:
                        duration = validate_positive_int(input("Enter duration (minutes): "), "duration")
                        notes = input("Enter notes (optional): ").strip() or None
                        workout = Workout.create(session, duration, notes)
                        print(f"Created workout ID {workout.id}")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif w_choice == '2':
                    try:
                        workout_id = validate_positive_int(input("Enter workout ID to delete: "), "workout ID")
                        if Workout.delete(session, workout_id):
                            print("Workout deleted successfully")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif w_choice == '3':
                    workouts = Workout.get_all(session)
                    if workouts:
                        # Sort workouts by date (newest first)
                        workouts = sorted(workouts, key=lambda w: w.date, reverse=True)
                        # Format date as YYYY-MM-DD HH:MM
                        table = [[w.id, w.date.strftime("%Y-%m-%d %H:%M"), w.duration, w.notes or ""] for w in workouts]
                        print(f"\nAll Workouts ({len(workouts)} total)")
                        print_table(table, ["ID", "Date", "Duration (min)", "Notes"])
                    else:
                        print("No workouts found")
                
                elif w_choice == '4':
                    try:
                        workout_id = validate_positive_int(input("Enter workout ID: "), "workout ID")
                        workout = Workout.find_by_id(session, workout_id)
                        if workout:
                            print(f"ID: {workout.id}, Date: {workout.date.strftime('%Y-%m-%d %H:%M')}, Duration: {workout.duration} min, Notes: {workout.notes or ''}")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif w_choice == '5':
                    try:
                        workout_id = validate_positive_int(input("Enter workout ID: "), "workout ID")
                        workout = Workout.find_by_id(session, workout_id)
                        if workout:
                            exercises = workout.exercises
                            if exercises:
                                table = [[e.id, e.name, e.category, e.reps, e.sets, e.weight or "N/A"] for e in exercises]
                                print_table(table, ["ID", "Name", "Category", "Reps", "Sets", "Weight"])
                            else:
                                print("No exercises for this workout")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif w_choice == '6':
                    try:
                        workout_id = validate_positive_int(input("Enter workout ID to update: "), "workout ID")
                        workout = Workout.find_by_id(session, workout_id)
                        if workout:
                            duration = input(f"Enter new duration (current: {workout.duration}, press enter to keep): ").strip()
                            if duration:
                                workout.duration = validate_positive_int(duration, "duration")
                            notes = input(f"Enter new notes (current: {workout.notes or 'None'}, press enter to keep): ").strip()
                            if notes:
                                workout.notes = notes or None
                            session.commit()
                            print(f"Updated workout ID {workout.id}")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif w_choice == '7':
                    break
                else:
                    print("Invalid choice")
        
        elif choice == '2':
            while True:
                exercise_menu()
                e_choice = input("Enter choice (1-7): ").strip()
                
                if e_choice == '1':
                    try:
                        name = input("Enter exercise name: ").strip()
                        if not name:
                            raise ValueError("Name cannot be empty")
                        category = input("Enter category (Strength/Cardio/Flexibility): ").strip()
                        reps = validate_positive_int(input("Enter reps: "), "reps")
                        sets = validate_positive_int(input("Enter sets: "), "sets")
                        weight = input("Enter weight (optional, press enter to skip): ").strip()
                        weight = validate_float(weight, "weight") if weight else None
                        workout_id = validate_positive_int(input("Enter workout ID: "), "workout ID")
                        if not Workout.find_by_id(session, workout_id):
                            raise ValueError("Workout not found")
                        exercise = Exercise.create(session, name, category, reps, sets, weight, workout_id)
                        print(f"Created exercise ID {exercise.id}")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif e_choice == '2':
                    try:
                        exercise_id = validate_positive_int(input("Enter exercise ID to delete: "), "exercise ID")
                        if Exercise.delete(session, exercise_id):
                            print("Exercise deleted successfully")
                        else:
                            print("Exercise not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif e_choice == '3':
                    exercises = Exercise.get_all(session)
                    if exercises:
                        table = [[e.id, e.name, e.category, e.reps, e.sets, e.weight or "N/A", e.workout_id] for e in exercises]
                        print_table(table, ["ID", "Name", "Category", "Reps", "Sets", "Weight", "Workout ID"])
                    else:
                        print("No exercises found")
                
                elif e_choice == '4':
                    try:
                        exercise_id = validate_positive_int(input("Enter exercise ID: "), "exercise ID")
                        exercise = Exercise.find_by_id(session, exercise_id)
                        if exercise:
                            print(f"ID: {exercise.id}, Name: {exercise.name}, Category: {exercise.category}, Reps: {exercise.reps}, Sets: {exercise.sets}, Weight: {exercise.weight or 'N/A'}, Workout ID: {exercise.workout_id}")
                        else:
                            print("Exercise not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif e_choice == '5':
                    try:
                        category = input("Enter category to filter (Strength/Cardio/Flexibility): ").strip()
                        valid_categories = ['Strength', 'Cardio', 'Flexibility']
                        if category not in valid_categories:
                            raise ValueError(f"Category must be one of {valid_categories}")
                        exercises = session.query(Exercise).filter(Exercise.category == category).all()
                        if exercises:
                            table = [[e.id, e.name, e.category, e.reps, e.sets, e.weight or "N/A", e.workout_id] for e in exercises]
                            print_table(table, ["ID", "Name", "Category", "Reps", "Sets", "Weight", "Workout ID"])
                        else:
                            print(f"No exercises found for category {category}")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif e_choice == '6':
                    try:
                        exercise_id = validate_positive_int(input("Enter exercise ID to update: "), "exercise ID")
                        exercise = Exercise.find_by_id(session, exercise_id)
                        if exercise:
                            name = input(f"Enter new name (current: {exercise.name}, press enter to keep): ").strip()
                            if name:
                                exercise.name = name
                            category = input(f"Enter new category (current: {exercise.category}, press enter to keep): ").strip()
                            if category:
                                exercise.category = category
                            reps = input(f"Enter new reps (current: {exercise.reps}, press enter to keep): ").strip()
                            if reps:
                                exercise.reps = validate_positive_int(reps, "reps")
                            sets = input(f"Enter new sets (current: {exercise.sets}, press enter to keep): ").strip()
                            if sets:
                                exercise.sets = validate_positive_int(sets, "sets")
                            weight = input(f"Enter new weight (current: {exercise.weight or 'N/A'}, press enter to keep): ").strip()
                            if weight:
                                exercise.weight = validate_float(weight, "weight")
                            workout_id = input(f"Enter new workout ID (current: {exercise.workout_id}, press enter to keep): ").strip()
                            if workout_id:
                                workout_id = validate_positive_int(workout_id, "workout ID")
                                if not Workout.find_by_id(session, workout_id):
                                    raise ValueError("Workout not found")
                                exercise.workout_id = workout_id
                            session.commit()
                            print(f"Updated exercise ID {exercise.id}")
                        else:
                            print("Exercise not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                
                elif e_choice == '7':
                    break
                else:
                    print("Invalid choice")
        
        elif choice == '3':
            print("Exiting Fitness Tracker CLI")
            break
        else:
            print("Invalid choice")

    session.close()

if __name__ == "__main__":
    main()