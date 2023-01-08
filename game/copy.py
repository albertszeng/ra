import copy

from game import state


def _copy_list(l, dispatch):
    ret = l.copy()
    for idx, item in enumerate(ret):
        cp = dispatch.get(type(item))
        if cp is not None:
            ret[idx] = cp(item, dispatch)
    return ret


def _copy_dict(d, dispatch):
    ret = d.copy()
    for key, value in ret.items():
        cp = dispatch.get(type(value))
        if cp is not None:
            ret[key] = cp(value, dispatch)

    return ret


def _copy_object(d, dispatch):
    # Start with a shallow copy.
    ret = copy.copy(d)
    for key, value in vars(d).items():
        cp = dispatch.get(type(value))
        if cp is not None:
            setattr(ret, key, cp(value, dispatch))
    return ret


_dispatcher = {
    list: _copy_list,
    dict: _copy_dict,
    state.GameState: _copy_object,
    state.PlayerState: _copy_object,
    state.TileBag: _copy_object,
}


def deepcopy(sth):
    cp = _dispatcher.get(type(sth))
    if cp is None:
        return sth
    else:
        return cp(sth, _dispatcher)
