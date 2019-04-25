from connexion import ProblemException


class DCPQueryError(ProblemException):
    pass


class DatabaseError(DCPQueryError):
    pass


class QueryTimeoutError(DatabaseError):
    pass


class QuerySizeError(DatabaseError):
    pass
