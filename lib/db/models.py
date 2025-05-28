from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Trainer(Base):
    __tablename__ = 'trainers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    trainees = relationship("Trainee", back_populates="trainer")

class Trainee(Base):
    __tablename__ = 'trainees'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id'))
    trainer = relationship("Trainer", back_populates="trainees")
    workouts = relationship("Workout", back_populates="trainee")

class Workout(Base):
    __tablename__ = 'workouts'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer)
    notes = Column(String)
    trainee_id = Column(Integer, ForeignKey('trainees.id', ondelete='SET NULL'), nullable=False)
    trainee = relationship("Trainee", back_populates="workouts")
    exercises = relationship("Exercise", back_populates="workout")

    @classmethod
    def delete(cls, session, workout_id):
        try:
            workout = session.query(cls).filter_by(id=workout_id).first()
            if not workout:
                return False
            
            exercises = session.query(Exercise).filter_by(workout_id=workout_id).all()
            for exercise in exercises:
                session.delete(exercise)
            session.delete(workout)
            session.commit()
            return True
        except IntegrityError as e:
            session.rollback()
            print(f"Database Error: Failed to delete workout: {e}")
            return False
        except Exception as e:
            session.rollback()
            print(f"Unexpected Error: {e}")
            return False

class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    category = Column(String(20))
    reps = Column(Integer)
    sets = Column(Integer)
    weight = Column(Float)
    workout_id = Column(Integer, ForeignKey('workouts.id', ondelete='SET NULL'), nullable=False)
    workout = relationship("Workout", back_populates="exercises")

    @classmethod
    def delete(cls, session, exercise_id):
        try:
            exercise = session.query(cls).filter_by(id=exercise_id).first()
            if not exercise:
                return False
            session.delete(exercise)
            session.commit()
            return True
        except IntegrityError as e:
            session.rollback()
            print(f"Database Error: Failed to delete exercise: {e}")
            return False
        except Exception as e:
            session.rollback()
            print(f"Unexpected Error: {e}")
            return False

def create_db():
    db_path = os.path.abspath("fitness_tracker.db")
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_sessionmaker(engine):
    return sessionmaker(bind=engine)