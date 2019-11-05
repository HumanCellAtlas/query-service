from connexion import ProblemException


class DCPQueryError(ProblemException):
    pass


class DatabaseError(DCPQueryError):
    pass


class QueryTimeoutError(DatabaseError):
    pass


class QuerySizeError(DatabaseError):
    pass


class DCPFileNotFoundError(ProblemException):
    pass
