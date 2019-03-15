from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from query.lib.logger import logger

from query.lib.database.tables import Base


class Database:
    def __init__(self, db_string):
        # The echo flag is a shortcut to setting up SQLAlchemy
        # logging, which is accomplished via Python’s standard logging
        # module. With it enabled, we’ll see all the generated SQL
        # produced. I
        self.db = create_engine(db_string, echo=True)

        # Bind the engine to the metadata of the Base class so that
        # the declaratives can be accessed through a DBSession
        # instance
        Base.metadata.bind = self.db
        self.session = sessionmaker(bind=self.db)

    def init_db(self):
        Base.metadata.create_all(self.db)

    def insert_one(self, data_object):
        # A DBSession() instance establishes all conversations with the database
        # and represents a "staging zone" for all the objects loaded into the
        # database session object. Any change made against the objects in the
        # session won't be persisted into the database until you call
        # session.commit(). If you're not happy about the changes, you can
        # revert all of them back to the last commit by calling
        # session.rollback()
        session = self.session()
        try:
            session.add(data_object)
            session.commit()
        except Exception as e:
            logger.warning(f"Something went wrong adding: {data_object} to the db. Exception: {e}")
            session.rollback()

    def insert_many(self, data_object_list):
        session = self.session()
        try:
            session.add_all(data_object_list)
            session.commit()
        except Exception as e:
            logger.warning(f"Something went wrong adding: {data_object_list} to the db. Exception: {e}")
            session.rollback()
