from lib.db.models import Workout, Exercise, Trainer, Trainee, create_db, get_sessionmaker
from lib.helpers import print_table
from datetime import datetime
import os

def seed_database(session):
    from lib.db.seed import seed_database as seed
    seed()
    print("Database seeded successfully")

def debug_database():
    # Initialize database
    engine = create_db()
    Session = get_sessionmaker(engine)
    session = Session()

    # Check if database is empty
    if not Trainer.get_all(session) and not os.getenv("SKIP_SEED"):
        print("Database is empty. Would you like to seed it? (y/n)")
        if input().strip().lower() == 'y':
            seed_database(session)
            session = Session()  # Recreate session after seeding

    # List Trainers
    trainers = Trainer.get_all(session)
    if trainers:
        print("\nTrainers:")
        table = [[t.id, t.name] for t in trainers]
        print_table(table, ["ID", "Name"])
    else:
        print("\nNo trainers found")

    # List Trainees
    trainees = Trainee.get_all(session)
    if trainees:
        print("\nTrainees:")
        table = [[t.id, t.name, t.trainer_id or "None"] for t in trainees]
        print_table(table, ["ID", "Name", "Trainer ID"])
    else:
        print("\nNo trainees found")

    # List Trainee Summaries
    if trainees:
        print("\nTrainee Summaries:")
        for trainee in trainees:
            trainer = trainee.trainer
            table = []
            for w in trainee.workouts:
                for e in w.exercises:
                    table.append([trainee.id, trainee.name, w.id, w.date.strftime("%Y-%m-%d %H:%M"), w.duration, w.notes or "", e.id, e.name, e.category, e.reps, e.sets, e.weight or "N/A", trainer.name if trainer else "None"])
                if not w.exercises:
                    table.append([trainee.id, trainee.name, w.id, w.date.strftime("%Y-%m-%d %H:%M"), w.duration, w.notes or "", "", "", "", "", "", "", trainer.name if trainer else "None"])
            if not trainee.workouts:
                table.append([trainee.id, trainee.name, "", "", "", "", "", "", "", "", "", "", trainer.name if trainer else "None"])
            print(f"\nTrainee: {trainee.name} (ID: {trainee.id})")
            print_table(table, ["Trainee ID", "Trainee Name", "Workout ID", "Workout Date", "Duration (min)", "Notes", "Exercise ID", "Exercise Name", "Category", "Reps", "Sets", "Weight", "Trainer"])
    else:
        print("\nNo trainee summaries available")

    # List Workouts
    workouts = Workout.get_all(session)
    if workouts:
        print(f"\nWorkouts ({len(workouts)} total):")
        table = [[w.id, w.date.strftime("%Y-%m-%d %H:%M"), w.duration, w.notes or "", w.trainee_id] for w in workouts]
        print_table(table, ["ID", "Date", "Duration (min)", "Notes", "Trainee ID"])
    else:
        print("\nNo workouts found")

    # List Exercises
    exercises = Exercise.get_all(session)
    if exercises:
        print(f"\nExercises ({len(exercises)} total):")
        table = [[e.id, e.name, e.category, e.reps, e.sets, e.weight or "N/A", e.workout_id] for e in exercises]
        print_table(table, ["ID", "Name", "Category", "Reps", "Sets", "Weight", "Workout ID"])
    else:
        print("\nNo exercises found")

    session.close()

if __name__ == "__main__":
    debug_database()