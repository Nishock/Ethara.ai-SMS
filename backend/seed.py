import sys
from app.database import SessionLocal, Base, engine
from app.seed_helper import run_seed

# Ensure tables are created
# Base.metadata.create_all(bind=engine)


def seed_db():
    db = SessionLocal()
    try:
        msg = run_seed(db)
        print(msg)
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

