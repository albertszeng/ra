from backend import routes


def use_token(data: routes.LoginOrRegisterRequest) -> bool:
    """Use token only if 'token' is the only param specified."""
    nonEmptyKeys = [key for key, val in data.items() if val]
    return nonEmptyKeys == ["token"]
