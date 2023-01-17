from typing import Callable, Mapping, Type, TypeVar

from game import state

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
TDispatcher = Mapping[Type[T], Callable[[T, V], T]]


def _copy_list(t: list[T], dispatch: TDispatcher) -> list[T]:
    ret = t.copy()
    for idx, item in enumerate(ret):
        cp = dispatch.get(type(item))
        if cp is not None:
            ret[idx] = cp(item, dispatch)
    return ret


def _copy_dict(d: dict[K, V], dispatch: TDispatcher) -> dict[K, V]:
    ret = d.copy()
    for key, value in ret.items():
        cp = dispatch.get(type(value))
        if cp is not None:
            ret[key] = cp(value, dispatch)

    return ret


def _copy_player(d: state.PlayerState, dispatch: TDispatcher) -> state.PlayerState:
    # Start with a shallow copy.
    ret = state.PlayerState.shallow()
    for key in state.PlayerState.__slots__:
        value = getattr(d, key)
        cp = dispatch.get(type(value))
        if cp is not None:
            value = cp(value, dispatch)
        setattr(ret, key, value)
    return ret


def _copy_game(d: state.GameState, dispatch: TDispatcher) -> state.GameState:
    # Start with a shallow copy.
    ret = state.GameState.shallow()
    for key in state.GameState.__slots__:
        value = getattr(d, key)
        if key == "player_names":
            # Shallow copy player names since they never change.
            setattr(ret, key, value)
        cp = dispatch.get(type(value))
        if cp is not None:
            value = cp(value, dispatch)
        setattr(ret, key, value)
    return ret


def _copy_tile_bag(d: state.TileBag, dispatch: TDispatcher) -> state.TileBag:
    # Start with a shallow copy.
    ret = state.TileBag.shallow()
    for key in state.TileBag.__slots__:
        value = getattr(d, key)
        if key == "draw_order":
            # This is a list, but we shallow copy to share across instances.
            setattr(ret, key, value)
        cp = dispatch.get(type(value))
        if cp is not None:
            value = cp(value, dispatch)
        setattr(ret, key, value)
    return ret


_dispatcher: TDispatcher = {
    list: _copy_list,
    dict: _copy_dict,
    state.GameState: _copy_game,
    state.PlayerState: _copy_player,
    state.TileBag: _copy_tile_bag,
}


def deepcopy(sth: T) -> T:
    cp = _dispatcher.get(type(sth))
    if cp is None:
        return sth
    else:
        return cp(sth, _dispatcher)
