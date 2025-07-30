import pkgutil

def get_p(name):
    data = pkgutil.get_data(__name__, f'p/{name}')
    return data.decode('utf-8') if data else None
