from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, validates, declarative_base
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///fitness_tracker.db', echo=False)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

class Workout(Base):
    __tablename__ = 'workouts'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    duration = Column(Integer, nullable=False)  # in minutes
    notes = Column(String)
    exercises = relationship("Exercise", back_populates="workout", cascade="all, delete-orphan")

    @validates('duration')
    def validate_duration(self, key, value):
        if value <= 0:
            raise ValueError("Duration must be positive")
        return value

    @classmethod
    def create(cls, session, duration, notes=None):
        workout = cls(duration=duration, notes=notes)
        session.add(workout)
        session.commit()
        return workout

    @classmethod
    def delete(cls, session, workout_id):
        workout = session.query(cls).get(workout_id)
        if workout:
            session.delete(workout)
            session.commit()
            return True
        return False

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def find_by_id(cls, session, workout_id):
        return session.query(cls).get(workout_id)

    def __repr__(self):
        return f"<Workout(id={self.id}, date={self.date}, duration={self.duration} min)>"

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    reps = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'), nullable=False)
    workout = relationship("Workout", back_populates="exercises")

    @validates('reps', 'sets')
    def validate_positive(self, key, value):
        if value <= 0:
            raise ValueError(f"{key} must be positive")
        return value

    @validates('weight')
    def validate_weight(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Weight cannot be negative")
        return value

    @validates('category')
    def validate_category(self, key, value):
        valid_categories = ['Strength', 'Cardio', 'Flexibility']
        if value not in valid_categories:
            raise ValueError(f"Category must be one of {valid_categories}")
        return value

    @classmethod
    def create(cls, session, name, category, reps, sets, weight, workout_id):
        exercise = cls(name=name, category=category, reps=reps, sets=sets, weight=weight, workout_id=workout_id)
        session.add(exercise)
        session.commit()
        return exercise

    @classmethod
    def delete(cls, session, exercise_id):
        exercise = session.query(cls).get(exercise_id)
        if exercise:
            session.delete(exercise)
            session.commit()
            return True
        return False

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def find_by_id(cls, session, exercise_id):
        return session.query(cls).get(exercise_id)

    def __repr__(self):
        return f"<Exercise(id={self.id}, name={self.name}, category={self.category})>"