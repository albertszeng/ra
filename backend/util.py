from backend import routes


def use_token(data: routes.LoginRequest) -> bool:
    """Use token only if 'token' is the only param specified."""
    nonEmptyKeys = [key for key, val in data.items() if val]
    return nonEmptyKeys == ["token"]
