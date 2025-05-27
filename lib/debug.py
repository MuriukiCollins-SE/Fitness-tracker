from lib.db.models import Session, Workout, Exercise
from lib.helpers import print_table

def inspect_database():
    session = Session()
    
    print("\nWorkouts in Database:")
    workouts = Workout.get_all(session)
    if workouts:
        table = [[w.id, w.date, w.duration, w.notes or ""] for w in workouts]
        print_table(table, ["ID", "Date", "Duration (min)", "Notes"])
    else:
        print("No workouts found")
    
    print("\nExercises in Database:")
    exercises = Exercise.get_all(session)
    if exercises:
        table = [[e.id, e.name, e.category, e.reps, e.sets, e.weight or "N/A", e.workout_id] for e in exercises]
        print_table(table, ["ID", "Name", "Category", "Reps", "Sets", "Weight", "Workout ID"])
    else:
        print("No exercises found")
    
    session.close()

if __name__ == "__main__":
    inspect_database()