from lib.db.models import Workout, Exercise, Trainer, Trainee, create_db, get_sessionmaker
from lib.helpers import validate_positive_int, validate_float, print_table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
import random
import os

def main_menu():
    print("\nFitness Tracker CLI")
    print("1. View Trainer Menu")
    print("2. View Trainee Menu")
    print("3. Workout Menu")
    print("4. Exercise Menu")
    print("5. Exit")

def trainer_menu():
    print("\nTrainer Menu")
    print("1. View Assigned Trainees")
    print("2. View Trainee Details")
    print("3. Delete Trainee")
    print("4. Back to Main Menu")

def workout_menu():
    print("\nWorkout Menu")
    print("1. Create Workout")
    print("2. Delete Workout")
    print("3. List All Workouts")
    print("4. Find Workout by ID")
    print("5. View Exercises for Workout")
    print("6. Update Workout")
    print("7. Back to Main Menu")

def exercise_menu():
    print("\nExercise Menu")
    print("1. Create Exercise")
    print("2. Delete Exercise")
    print("3. List All Exercises")
    print("4. Find Exercise by ID")
    print("5. Filter Exercises by Category")
    print("6. Update Exercise")
    print("7. Back to Menu")

def seed_database(engine):
    from lib.db.seed import seed_database
    Session = get_sessionmaker(engine)
    session = Session()
    try:
        seed_database()
        print("Debug: Seed started")
        session.commit()
        trainers = session.query(Trainer).all()
        print(f"Debug: Seeded and committed {len(trainers)} trainers: {[(t.id, t.name) for t in trainers]}")
        return trainers
    except Exception as e:
        print(f"Error seeding database: {e}")
        session.rollback()
        return []
    finally:
        session.close()

def trainee_workflow(session):
    print("\n=== Trainee Workflow ===")
    try:
        # Collect Trainee Name and Check Validity
        name = input("Enter trainee name: ").strip()
        if not name:
            print("Error: Name cannot be empty.")
            return
        if len(name) > 50:
            print("Error: Name too long (max 50 characters).")
            return
        existing_trainee = session.query(Trainee).filter_by(name=name).first()
        if existing_trainee:
            print(f"Error: Trainee '{name}' already exists (ID: {existing_trainee.id}). Please use a unique name.")
            return

       
        num_workouts = input("How many workouts to add (0-4)? ").strip()
        num_workouts = validate_positive_int(num_workouts, "0-4")
        if num_workouts > 4:
            print("Error: Number of workouts cannot exceed 4.")
            return
        workouts_data = []
        for i in range(num_workouts):
            print(f"\nEnter details for Workout {i + 1}:")
            duration = input("Enter duration (minutes): ").strip()
            duration = validate_positive_int(duration, "duration")
            notes = input("Enter notes (optional): ").strip() or None
            num_exercises = input(f"How many exercises for Workout {i} (0-4)? ").strip()
            num_exercises = validate_positive_int(num_exercises, "0-4")
            if num_exercises > 4:
                print("Error: Number of exercises cannot exceed 4.")
                return
            exercises_data = []
            for j in range(num_exercises):
                print(f"\nEnter details for Exercise {j + 1}:")
                ex_name = input("Exercise name: ").strip()
                if not ex_name:
                    print("Error: Exercise name cannot be empty")
                    return
                category = input("Category (Strength/Cardio/Flexibility): ").strip().capitalize()
                if category not in ["Strength", "Cardio", "Flexibility"]:
                    print("Error: Invalid category")
                    return
                reps = input("Reps: ").strip()
                reps = validate_positive_int(reps, "reps")
                sets = input("Sets: ").strip()
                sets = validate_positive_int(sets, "sets")
                weight = input("Weight (optional, press enter to skip): ").strip()
                weight = validate_float(weight, "weight") if weight else None
                exercises_data.append({
                    "name": ex_name,
                    "category": category,
                    "reps": reps,
                    "sets": sets,
                    "weight": weight
                })
            workouts_data.append({
                "duration": duration,
                "notes": notes,
                "exercises": exercises_data
            })

        # Assign Trainer and Save Records
        trainers = session.query(Trainer).all()
        if not trainers:
            print("Error: No trainers available. Please contact support to seed trainers.")
            return
        trainer = random.choice(trainers)
        trainee = Trainee(name=name, trainer_id=trainer.id)
        session.add(trainee)
        session.flush()
        trainee_id = trainee.id
        print(f"Debug: Created trainee ID {trainee_id}, name: {name}, trainer_id: {trainer.id}")

        for w in workouts_data:
            workout = Workout(duration=w["duration"], notes=w["notes"], trainee_id=trainee_id)
            session.add(workout)
            session.flush()
            for e in w["exercises"]:
                exercise = Exercise(
                    name=e["name"],
                    category=e["category"],
                    reps=e["reps"],
                    sets=e["sets"],
                    weight=e["weight"],
                    workout_id=workout.id
                )
                session.add(exercise)
                session.flush()

    
        trainee = session.query(Trainee).filter_by(id=trainee_id).first()
        if not trainee:
            print("Error: Trainee record lost before commit. Please re-register.")
            session.rollback()
            return
        session.commit()
        print("Records added successfully")

        
        trainee = session.query(Trainee).options(
            joinedload(Trainee.workouts).joinedload(Workout.exercises),
            joinedload(Trainee.trainer)
        ).filter_by(id=trainee_id).first()
        if not trainee:
            print("Error: Trainee not found after commit. Please re-register to continue.")
            return
        trainee_id = trainee.id

        print(f"\nSummary for Trainee: {trainee.name} (ID: {trainee.id})")
        table = []
        seen_entries = set()
        for w in trainee.workouts:
            exercise_dict = {}
            for e in w.exercises:
                key = (e.name, e.category)
                if key not in exercise_dict:
                    exercise_dict[key] = {"reps": [], "sets": [], "weights": [], "id": e.id}
                exercise_dict[key]["reps"].append(e.reps)
                exercise_dict[key]["sets"].append(e.sets)
                if e.weight is not None:
                    exercise_dict[key]["weights"].append(str(e.weight))
            for (ex_name, category), data in exercise_dict.items():
                entry_key = (trainee.id, w.id, data["id"])
                if entry_key not in seen_entries:
                    table.append([
                        trainee.id, trainee.name, w.id, w.date.strftime("%Y-%m-%d %H:%M:%S"),
                        w.duration, w.notes or "None", data["id"], ex_name, category,
                        sum(data["reps"]), sum(data["sets"]), ",".join(data["weights"]) or "None", trainee.trainer.name
                    ])
                    seen_entries.add(entry_key)
            if not w.exercises:
                entry_key = (trainee.id, w.id, 0)
                if entry_key not in seen_entries:
                    table.append([
                        trainee.id, trainee.name, w.id, w.date.strftime("%Y-%m-%d %H:%M:%S"),
                        w.duration, w.notes or "None", "", "", "", "", "", "", trainee.trainer.name
                    ])
                    seen_entries.add(entry_key)
        if not trainee.workouts:
            entry_key = (trainee.id, 0, 0)
            if entry_key not in seen_entries:
                table.append([
                    trainee.id, trainee.name, "", "", "", "", "", "", "", "", "", "", trainee.trainer.name
                ])
                seen_entries.add(entry_key)
        print_table(table, [
            "Trainee ID", "Trainee Name", "Workout ID", "Workout Date", "Duration (min)",
            "Notes", "Exercise ID", "Exercise Name", "Category", "Total Reps", "Total Sets", "Weights", "Trainer"
        ])

    except ValueError as e:
        print(f"Input Error: {e}")
        session.rollback()
    except IntegrityError as e:
        print(f"Database Error: Failed to save records: {e}")
        session.rollback()
    except Exception as e:
        print(f"Unexpected Error: {e}")
        session.rollback()

def main():
    db_path = os.path.abspath("fitness_tracker.db")
    print(f"Debug: Database at {db_path}")
    engine = create_db()
    Session = get_sessionmaker(engine)
    session = Session()

    try:
        trainers = session.query(Trainer).all()
        print(f"Debug: Found {len(trainers)} trainers: {[(t.id, t.name) for t in trainers]}")
        if not trainers:
            print("No trainers. Seeding database...")
            trainers = seed_database(engine)
            session.close()
            session = Session()
            trainers = session.query(Trainer).all()
            print(f"Debug: Post-seeding found {len(trainers)} trainers: {[(t.id, t.name) for t in trainers]}")
            if not trainers:
                raise RuntimeError("Failed to seed database.")
    except Exception as e:
        print(f"Error initializing: {e}")
        session.close()
        engine.dispose()
        return

    while True:
        main_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            while True:
                trainer_menu()
                t_choice = input("Enter choice (1-4): ").strip()

                if t_choice == "1":
                    try:
                        trainer_id = input("Enter trainer ID: ").strip()
                        trainer_id = validate_positive_int(trainer_id, "trainer ID")
                        trainer = session.query(Trainer).filter_by(id=trainer_id).first()
                        if trainer:
                            trainees = trainer.trainees
                            if not trainees:
                                print("No trainees assigned")
                            else:
                                print(f"\nAssigned Trainees for {trainer.name}:")
                                table = []
                                seen = set()
                                for t in trainees:
                                    for w in t.workouts:
                                        exercise_dict = {}
                                        for e in w.exercises:
                                            key = (e.name, e.category)
                                            if key not in exercise_dict:
                                                exercise_dict[key] = {"reps": 0, "sets": 0, "weights": [], "id": e.id}
                                            exercise_dict[key]["reps"] += e.reps
                                            exercise_dict[key]["sets"] += e.sets
                                            if e.weight is not None:
                                                exercise_dict[key]["weights"].append(str(e.weight))
                                        for (ex_name, category), data in exercise_dict.items():
                                            entry_key = (t.id, w.id, data["id"])
                                            if entry_key not in seen:
                                                table.append([
                                                    t.id, t.name, w.id, w.date.strftime("%Y-%m-%d %H:%M:%S"),
                                                    data["id"], ex_name, category, data["reps"],
                                                    data["sets"], ",".join(data["weights"]) or "None"
                                                ])
                                                seen.add(entry_key)
                                        if not w.exercises:
                                            entry_key = (t.id, w.id, 0)
                                            if entry_key not in seen:
                                                table.append([
                                                    t.id, t.name, w.id, w.date.strftime("%Y-%m-%d %H:%M:%S"),
                                                    "", "", "", "", "", ""
                                                ])
                                                seen.add(entry_key)
                                    if not t.workouts:
                                        entry_key = (t.id, 0, 0)
                                        if entry_key not in seen:
                                            table.append([t.id, t.name, "", "", "", "", "", "", "", ""])
                                            seen.add(entry_key)
                                print_table(table, [
                                    "Trainee ID", "Trainee Name", "Workout ID", "Workout Date",
                                    "Exercise ID", "Exercise Name", "Category", "Total Reps", "Total Sets", "Weights"
                                ])
                        else:
                            print("Trainer not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif t_choice == "2":
                    try:
                        trainer_id = input("Enter trainer ID: ").strip()
                        trainer_id = validate_positive_int(trainer_id, "trainer ID")
                        trainer = session.query(Trainer).filter_by(id=trainer_id).first()
                        if trainer:
                            trainee_id = input("Enter trainee ID: ").strip()
                            trainee_id = validate_positive_int(trainee_id, "trainee ID")
                            trainee = session.query(Trainee).filter_by(id=trainee_id).first()
                            if trainee and trainee.trainer_id == trainer_id:
                                print(f"\nTrainee: {trainee.name}")
                                print(f"Trainer: {trainer.name}")
                                workouts = trainee.workouts
                                if workouts:
                                    table = [[w.id, w.date.strftime("%Y-%m-%d %H:%M:%S"), w.duration, w.notes or ""] for w in workouts]
                                    print("\nWorkouts:")
                                    print_table(table, ["ID", "Date", "Duration (min)", "Notes"])
                                    for workout in workouts:
                                        exercises = workout.exercises
                                        if exercises:
                                            exercise_dict = {}
                                            for e in exercises:
                                                key = (e.name, e.category)
                                                if key not in exercise_dict:
                                                    exercise_dict[key] = {"reps": 0, "sets": 0, "weights": [], "id": e.id}
                                                exercise_dict[key]["reps"] += e.reps
                                                exercise_dict[key]["sets"] += e.sets
                                                if e.weight is not None:
                                                    exercise_dict[key]["weights"].append(str(e.weight))
                                            table = [[data["id"], ex_name, category, data["reps"], data["sets"], ",".join(data["weights"]) or "None"]
                                                     for (ex_name, category), data in exercise_dict.items()]
                                            print(f"\nExercises for Workout ID {workout.id}:")
                                            print_table(table, ["ID", "Name", "Category", "Total Reps", "Total Sets", "Weights"])
                                        else:
                                            print(f"\nNo exercises for Workout ID {workout.id}")
                                else:
                                    print("No workouts found")
                            else:
                                print("Trainee not found or not assigned to this trainer")
                        else:
                            print("Trainer not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif t_choice == "3":
                    try:
                        trainer_id = input("Enter trainer ID: ").strip()
                        trainer_id = validate_positive_int(trainer_id, "trainer ID")
                        trainer = session.query(Trainer).filter_by(id=trainer_id).first()
                        if not trainer:
                            print("Error: Trainer not found")
                            continue
                        trainee_id = input("Enter trainee ID to delete: ").strip()
                        trainee_id = validate_positive_int(trainee_id, "trainee ID")
                        trainee = session.query(Trainee).filter_by(id=trainee_id).first()
                        if not trainee:
                            print("Error: Trainee not found")
                            continue
                        if trainee.trainer_id != trainer_id:
                            print("Error: Trainee is not assigned to this trainer")
                            continue
                        
                        workouts = session.query(Workout).filter_by(trainee_id=trainee_id).all()
                        for workout in workouts:
                            exercises = session.query(Exercise).filter_by(workout_id=workout.id).all()
                            for exercise in exercises:
                                session.delete(exercise)
                            session.delete(workout)
                        session.delete(trainee)
                        session.commit()
                        print(f"Trainee ID {trainee_id} ({trainee.name}) and associated records deleted successfully")
                    except ValueError as e:
                        print(f"Error: {e}")
                        session.rollback()
                    except IntegrityError as e:
                        print(f"Database Error: Failed to delete trainee: {e}")
                        session.rollback()
                    except Exception as e:
                        print(f"Unexpected Error: {e}")
                        session.rollback()

                elif t_choice == "4":
                    break
                else:
                    print("Invalid choice")

        elif choice == "2":
            trainee_workflow(session)

        elif choice == "3":
            while True:
                workout_menu()
                w_choice = input("Enter choice (1-7): ").strip()

                if w_choice == "1":
                    try:
                        num_workouts = input("How many workouts to create (1-4)? ").strip()
                        num_workouts = validate_positive_int(num_workouts, "1-4")
                        if num_workouts < 1 or num_workouts > 4:
                            print("Error: Number of workouts must be between 1 and 4")
                            continue
                        trainee_id = input("Enter trainee ID: ").strip()
                        trainee_id = validate_positive_int(trainee_id, "trainee ID")
                        if not session.query(Trainee).filter_by(id=trainee_id).first():
                            print("Error: Trainee not found")
                            continue
                        created_ids = []
                        for i in range(num_workouts):
                            print(f"\nEnter details for Workout {i + 1}:")
                            duration = input("Enter duration (minutes): ").strip()
                            duration = validate_positive_int(duration, "duration")
                            notes = input("Enter notes (optional): ").strip() or None
                            workout = Workout(duration=duration, notes=notes, trainee_id=trainee_id)
                            session.add(workout)
                            session.commit()
                            created_ids.append(workout.id)
                        print(f"Created workout(s) with ID(s): {', '.join(map(str, created_ids))}")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif w_choice == "2":
                    try:
                        workout_id = input("Enter workout ID to delete: ").strip()
                        workout_id = validate_positive_int(workout_id, "workout ID")
                        if Workout.delete(session, workout_id):
                            print("Workout deleted successfully")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")
                    except IntegrityError as e:
                        print(f"Database Error: Failed to delete workout: {e}")
                        session.rollback()
                    except Exception as e:
                        print(f"Unexpected Error: {e}")
                        session.rollback()

                elif w_choice == "3":
                    workouts = session.query(Workout).options(
                        joinedload(Workout.trainee).joinedload(Trainee.trainer)
                    ).all()
                    if workouts:
                        workouts = sorted(workouts, key=lambda w: w.date, reverse=True)
                        table = []
                        seen = set()
                        for w in workouts:
                            trainee = w.trainee
                            trainer = trainee.trainer if trainee else None
                            if w.id not in seen:
                                trainee_name = trainee.name if trainee else "Unknown"
                                trainer_name = trainer.name if trainer else "Unknown"
                                print(f"Debug: Workout ID {w.id}, Trainee: {trainee_name}, Trainer: {trainer_name}")
                                table.append([
                                    w.id, w.date.strftime("%Y-%m-%d %H:%M:%S"), w.duration,
                                    w.notes or "", trainee_name, trainer_name
                                ])
                                seen.add(w.id)
                        print(f"\nAll Workouts ({len(workouts)} total)")
                        print_table(table, [
                            "ID", "Date", "Duration (min)", "Notes", "Trainee Name", "Trainer Name"
                        ])
                    else:
                        print("No workouts found")

                elif w_choice == "4":
                    try:
                        workout_id = input("Enter workout ID: ").strip()
                        workout_id = validate_positive_int(workout_id, "workout ID")
                        workout = session.query(Workout).filter_by(id=workout_id).first()
                        if workout:
                            print(f"ID: {workout.id}, Date: {workout.date.strftime('%Y-%m-%d %H:%M:%S')}, Duration: {workout.duration} min, Notes: {workout.notes or ''}, Trainee ID: {workout.trainee_id}")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif w_choice == "5":
                    try:
                        workout_id = input("Enter workout ID: ").strip()
                        workout_id = validate_positive_int(workout_id, "workout ID")
                        workout = session.query(Workout).filter_by(id=workout_id).first()
                        if workout:
                            exercises = workout.exercises
                            if exercises:
                                exercise_dict = {}
                                for e in exercises:
                                    key = (e.name, e.category)
                                    if key not in exercise_dict:
                                        exercise_dict[key] = {"reps": 0, "sets": 0, "weights": [], "id": e.id}
                                    exercise_dict[key]["reps"] += e.reps
                                    exercise_dict[key]["sets"] += e.sets
                                    if e.weight is not None:
                                        exercise_dict[key]["weights"].append(str(e.weight))
                                table = [[data["id"], ex_name, category, data["reps"], data["sets"], ",".join(data["weights"]) or "None"]
                                         for (ex_name, category), data in exercise_dict.items()]
                                print_table(table, ["ID", "Name", "Category", "Total Reps", "Total Sets", "Weights"])
                            else:
                                print("No exercises for this workout")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif w_choice == "6":
                    try:
                        workout_id = input("Enter workout ID to update: ").strip()
                        workout_id = validate_positive_int(workout_id, "workout ID")
                        workout = session.query(Workout).filter_by(id=workout_id).first()
                        if workout:
                            duration = input(f"Enter new duration (current: {workout.duration}, press enter to keep): ").strip()
                            if duration:
                                workout.duration = validate_positive_int(duration, "duration")
                            notes = input(f"Enter new notes (current: {workout.notes or 'None'}, press enter to keep): ").strip()
                            if notes:
                                workout.notes = notes or None
                            trainee_id = input(f"Enter new trainee ID (current: {workout.trainee_id}, press enter to keep): ").strip()
                            if trainee_id:
                                trainee_id = validate_positive_int(trainee_id, "trainee ID")
                                if not session.query(Trainee).filter_by(id=trainee_id).first():
                                    print("Error: Trainee not found")
                                    continue
                                workout.trainee_id = trainee_id
                            session.commit()
                            print(f"Updated workout ID {workout.id}")
                        else:
                            print("Workout not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif w_choice == "7":
                    break
                else:
                    print("Invalid choice")

        elif choice == "4":
            while True:
                exercise_menu()
                e_choice = input("Enter choice (1-7): ").strip()

                if e_choice == "1":
                    try:
                        name = input("Enter exercise name: ").strip()
                        if not name:
                            print("Error: Name cannot be empty")
                            continue
                        category = input("Enter category (Strength/Cardio/Flexibility): ").strip().capitalize()
                        if category not in ["Strength", "Cardio", "Flexibility"]:
                            print("Error: Category must be one of ['Strength', 'Cardio', 'Flexibility']")
                            continue
                        reps = input("Enter reps: ").strip()
                        reps = validate_positive_int(reps, "reps")
                        sets = input("Enter sets: ").strip()
                        sets = validate_positive_int(sets, "sets")
                        weight = input("Enter weight (optional, press enter to skip): ").strip()
                        weight = validate_float(weight, "weight") if weight else None
                        workout_id = input("Enter workout ID: ").strip()
                        workout_id = validate_positive_int(workout_id, "workout ID")
                        if not session.query(Workout).filter_by(id=workout_id).first():
                            print("Error: Workout not found")
                            continue
                        exercise = Exercise(name=name, category=category, reps=reps, sets=sets, weight=weight, workout_id=workout_id)
                        session.add(exercise)
                        session.commit()
                        print(f"Created exercise ID {exercise.id}")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif e_choice == "2":
                    try:
                        exercise_id = input("Enter exercise ID to delete: ").strip()
                        exercise_id = validate_positive_int(exercise_id, "exercise ID")
                        if Exercise.delete(session, exercise_id):
                            print("Exercise deleted successfully")
                        else:
                            print("Exercise not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif e_choice == "3":
                    exercises = session.query(Exercise).all()
                    if exercises:
                        table = [[e.id, e.name, e.category, e.reps, e.sets, e.weight or "None", e.workout_id] for e in exercises]
                        print_table(table, ["ID", "Name", "Category", "Reps", "Sets", "Weight", "Workout ID"])
                    else:
                        print("No exercises found")

                elif e_choice == "4":
                    try:
                        exercise_id = input("Enter exercise ID: ").strip()
                        exercise_id = validate_positive_int(exercise_id, "exercise ID")
                        exercise = session.query(Exercise).filter_by(id=exercise_id).first()
                        if exercise:
                            print(f"Exercise ID: {exercise.id}, Name: {exercise.name}, Category: {exercise.category}, Reps: {exercise.reps}, Sets: {exercise.sets}, Weight: {exercise.weight or 'None'}, Workout ID: {exercise.workout_id}")
                        else:
                            print("Exercise not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif e_choice == "5":
                    try:
                        category = input("Enter category to filter (Strength/Cardio/Flexibility): ").strip().capitalize()
                        valid_categories = ['Strength', 'Cardio', 'Flexibility']
                        if category not in valid_categories:
                            print(f"Error: Category must be one of {valid_categories}")
                            continue
                        exercises = session.query(Exercise).join(Workout, Exercise.workout_id == Workout.id).join(Trainee, Workout.trainee_id == Trainee.id).join(Trainer, Trainee.trainer_id == Trainer.id).filter(Exercise.category == category).all()
                        if exercises:
                            table = []
                            seen = set()
                            for e in exercises:
                                workout = session.query(Workout).filter_by(id=e.workout_id).first()
                                trainee = session.query(Trainee).filter_by(id=workout.trainee_id).first()
                                trainer = session.query(Trainer).filter_by(id=trainee.trainer_id).first()
                                if e.id not in seen:
                                    table.append([
                                        e.id, e.name, e.category, e.reps, e.sets, e.weight or "None",
                                        e.workout_id, trainee.name, trainer.name
                                    ])
                                    seen.add(e.id)
                            print_table(table, [
                                "ID", "Name", "Category", "Reps", "Sets", "Weight", "Workout ID",
                                "Trainee Name", "Trainer Name"
                            ])
                        else:
                            print(f"No exercises found for category {category}")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif e_choice == "6":
                    try:
                        exercise_id = input("Enter exercise ID to update: ").strip()
                        exercise_id = validate_positive_int(exercise_id, "exercise ID")
                        exercise = session.query(Exercise).filter_by(id=exercise_id).first()
                        if exercise:
                            name = input(f"Enter new name (current: {exercise.name}, press enter to keep): ").strip()
                            if name:
                                exercise.name = name
                            category = input(f"Enter new category (current: {exercise.category}, press enter to keep): ").strip().capitalize()
                            if category:
                                if category not in ["Strength", "Cardio", "Flexibility"]:
                                    print("Error: Category must be one of ['Strength', 'Cardio', 'Flexibility']")
                                    continue
                                exercise.category = category
                            reps = input(f"Enter new reps (current: {exercise.reps}, press enter to keep): ").strip()
                            if reps:
                                exercise.reps = validate_positive_int(reps, "reps")
                            sets = input(f"Enter new sets (current: {exercise.sets}, press enter to keep): ").strip()
                            if sets:
                                exercise.sets = validate_positive_int(sets, "sets")
                            weight = input(f"Enter new weight (current: {exercise.weight or 'None'}, press enter to keep): ").strip()
                            if weight:
                                exercise.weight = validate_float(weight, "weight")
                            workout_id = input(f"Enter new workout ID (current: {exercise.workout_id}, press enter to keep): ").strip()
                            if workout_id:
                                workout_id = validate_positive_int(workout_id, "workout ID")
                                if not session.query(Workout).filter_by(id=workout_id).first():
                                    print("Error: Workout not found")
                                    continue
                                exercise.workout_id = workout_id
                            session.commit()
                            print(f"Updated exercise ID {exercise.id}")
                        else:
                            print("Exercise not found")
                    except ValueError as e:
                        print(f"Error: {e}")

                elif e_choice == "7":
                    break
                else:
                    print("Invalid choice")

        elif choice == "5":
            print("Exiting Fitness Tracker CLI")
            break
        else:
            print("Invalid choice")

    session.close()
    engine.dispose()

if __name__ == "__main__":
    main()