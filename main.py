from config import DATABASE, PASSWORD, USER, SUBD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import create_tables

if __name__ == '__main__':

    DNS = f'{SUBD}://{USER}:{PASSWORD}@localhost:5432/{DATABASE}'
    engine = create_engine(DNS)

    Session = sessionmaker(bind=engine)
    session = Session()

    create_tables(engine)

    session.close()