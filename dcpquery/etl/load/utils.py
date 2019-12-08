def check_data(f=None):
    def wrapper(data, **kwargs):
        if data is None:
            return None
        else:
            return f(data=data, **kwargs)
    return wrapper