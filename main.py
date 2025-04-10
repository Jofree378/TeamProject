from config import DATABASE, PASSWORD, USER, SUBD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import create_tables, create_users_parameters, UsersParameters, update_users_parameters

if __name__ == '__main__':

    DNS = f'{SUBD}://{USER}:{PASSWORD}@localhost:5432/{DATABASE}'
    engine = create_engine(DNS)

    Session = sessionmaker(bind=engine)
    session = Session()

    # create_tables(engine)

    # create_users_parameters(session, 567, 22, 'Спб', 'men')
    # update_users_parameters(session, 567, 22, age_max=24, city='Спб')

    

    session.close()