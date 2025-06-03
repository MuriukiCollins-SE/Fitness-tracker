# Existing imports and setup
from lib.db.models import Trainer, Trainee, Workout, Exercise, create_db, get_sessionmaker
import random
from datetime import datetime, timedelta

def seed_database():
    engine = create_db()
    Session = get_sessionmaker(engine)
    session = Session()

    try:
        # Clear existing data
        session.query(Exercise).delete()
        session.query(Workout).delete()
        session.query(Trainee).delete()
        session.query(Trainer).delete()
        session.commit()

        # Seed trainers
        trainer_names = ["Alex Smith", "Bob Johnson", "Cathy Lee", "Dana Brown"]
        trainers = [Trainer(name=name) for name in trainer_names]
        session.add_all(trainers)
        session.commit()
        print(f"Debug: Committed {len(trainers)} trainers: {[t.name for t in trainers]}")

        # Seed trainees
        trainee_names = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Sophia", "Jackson", "Lucas", "Mia", "Ethan"]
        trainees = [Trainee(name=name, trainer_id=random.choice(trainers).id) for name in trainee_names]
        session.add_all(trainees)
        session.commit()

        # Seed workouts
        workouts = []
        for trainee in trainees:
            for _ in range(random.randint(5, 15)):
                date = datetime.now() - timedelta(days=random.randint(0, 30))
                duration = random.randint(30, 120)
                notes = random.choice([None, "Morning run", "Gym session", "Yoga class"])
                workouts.append(Workout(date=date, duration=duration, notes=notes, trainee_id=trainee.id))
        session.add_all(workouts)
        session.commit()

        # Seed exercises
        exercise_names = [
            ("Push-ups", "Strength"), ("Running", "Cardio"), ("Squats", "Strength"),
            ("Plank", "Strength"), ("Yoga", "Flexibility"), ("Cycling", "Cardio")
        ]
        exercises = []
        for workout in workouts:
            for _ in range(random.randint(1, 5)):
                name, category = random.choice(exercise_names)
                reps = random.randint(5, 20)
                sets = random.randint(1, 5)
                weight = random.uniform(0, 100) if random.choice([True, False]) else None
                exercises.append(Exercise(name=name, category=category, reps=reps, sets=sets, weight=weight, workout_id=workout.id))
        session.add_all(exercises)
        session.commit()

        print("Database seeded successfully")
    except Exception as e:
        print(f"Error seeding database: {e}")
        session.rollback()
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    seed_database()