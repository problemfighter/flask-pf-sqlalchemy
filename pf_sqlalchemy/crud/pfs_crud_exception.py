from sqlalchemy.exc import IntegrityError


def parse_integrity_error(exception: IntegrityError):
    try:
        if exception.orig and exception.orig.args and exception.orig.args[1]:
            return str(exception.orig.args[1])
    except:
        pass
    return str(exception.orig)
