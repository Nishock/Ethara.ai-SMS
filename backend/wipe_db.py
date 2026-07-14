from app.database import Base, engine

def wipe():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables cleanly...")
    Base.metadata.create_all(bind=engine)
    print("Wipe and recreate complete!")

if __name__ == "__main__":
    wipe()
