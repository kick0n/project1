#imports zips.csv into locations table

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
    f = open("zips.csv")
    reader = csv.reader(f)
    for zipcode, city, state, lat, longi, population in reader:
        db.execute("INSERT INTO locations (zipcode, city, state,lat, longi, population) VALUES (:zipcode, :city, :state, :lat, :longi, :population)",
                    {"zipcode": zipcode, "city": city, "state": state, "lat": lat, "longi": longi, "population": population})
        print(f"Added {city}, {state} {zipcode} to database")
    db.commit()

if __name__ == "__main__":
    main()