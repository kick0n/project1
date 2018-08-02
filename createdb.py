import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE checkins (id SERIAL PRIMARY KEY, location_id INTEGER REFERENCES locations, user_id INTEGER REFERENCES users, note TEXT)")
    db.commit()

if __name__ == "__main__":
    main()