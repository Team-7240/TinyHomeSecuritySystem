from db import Options, get_session


def remove_options(target):
    session = get_session()
    session.query(Options).filter(Options.id == target or Options.name == target).delete()
    session.commit()
    session.close()
    return True


def get_options_by_name(name):
    session = get_session()
    result = session.query(Options).filter(Options.name == name).first().value
    session.close()
    return result


def set_option(name, value):
    session = get_session()
    session.query(Options).filter(Options.name == name).update({"value": value})
    session.commit()
    session.close()
    return True


def add_option(name, value):
    session = get_session()

    query = session.query(Options).filter(Options.name == name).all()
    if len(query):
        return False

    session.add(Options(name=name, value=value))
    session.commit()
    session.close()
    return True
