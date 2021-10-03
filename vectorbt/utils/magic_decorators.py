# Copyright (c) 2021 Oleg Polakow. All rights reserved.
# This code is licensed under Apache 2.0 with Commons Clause license (see LICENSE.md for details)

"""Class decorators for adding magic methods."""

import numpy as np

from vectorbt import _typing as tp
from vectorbt.utils.config import Config

WrapperFuncT = tp.Callable[[tp.Type[tp.T]], tp.Type[tp.T]]

__pdoc__ = {}

binary_magic_config = Config(
    {
        '__eq__': dict(func=np.equal),
        '__ne__': dict(func=np.not_equal),
        '__lt__': dict(func=np.less),
        '__gt__': dict(func=np.greater),
        '__le__': dict(func=np.less_equal),
        '__ge__': dict(func=np.greater_equal),
        # arithmetic ops
        '__add__': dict(func=np.add),
        '__sub__': dict(func=np.subtract),
        '__mul__': dict(func=np.multiply),
        '__pow__': dict(func=np.power),
        '__mod__': dict(func=np.mod),
        '__floordiv__': dict(func=np.floor_divide),
        '__truediv__': dict(func=np.true_divide),
        '__radd__': dict(func=lambda x, y: np.add(y, x)),
        '__rsub__': dict(func=lambda x, y: np.subtract(y, x)),
        '__rmul__': dict(func=lambda x, y: np.multiply(y, x)),
        '__rpow__': dict(func=lambda x, y: np.power(y, x)),
        '__rmod__': dict(func=lambda x, y: np.mod(y, x)),
        '__rfloordiv__': dict(func=lambda x, y: np.floor_divide(y, x)),
        '__rtruediv__': dict(func=lambda x, y: np.true_divide(y, x)),
        # mask ops
        '__and__': dict(func=np.bitwise_and),
        '__or__': dict(func=np.bitwise_or),
        '__xor__': dict(func=np.bitwise_xor),
        '__rand__': dict(func=lambda x, y: np.bitwise_and(y, x)),
        '__ror__': dict(func=lambda x, y: np.bitwise_or(y, x)),
        '__rxor__': dict(func=lambda x, y: np.bitwise_xor(y, x))
    },
    readonly=True,
    as_attrs=False
)
"""_"""

__pdoc__['binary_magic_config'] = f"""Config of binary magic methods to be added to a class.

```json
{binary_magic_config.to_doc()}
```
"""

BinaryTranslateFuncT = tp.Callable[[tp.Any, tp.Any, tp.Callable], tp.Any]


def attach_binary_magic_methods(translate_func: BinaryTranslateFuncT,
                                config: tp.Optional[Config] = None) -> WrapperFuncT:
    """Class decorator to add binary magic methods to a class.

    `translate_func` must

    * take `self`, `other`, and unary function,
    * perform computation, and
    * return the result.

    `config` defaults to `binary_magic_config` and must contain target method names (keys)
    and dictionaries (values) with the following keys:

    * `func`: Function that combines two array-like objects.
    """
    if config is None:
        config = binary_magic_config

    def wrapper(cls: tp.Type[tp.T]) -> tp.Type[tp.T]:
        for target_name, settings in config.items():
            func = settings['func']

            def new_method(self,
                           other: tp.Any,
                           _translate_func: BinaryTranslateFuncT = translate_func,
                           _func: tp.Callable = func) -> tp.SeriesFrame:
                return _translate_func(self, other, _func)

            new_method.__qualname__ = f"{cls.__name__}.{target_name}"
            new_method.__name__ = target_name
            setattr(cls, target_name, new_method)
        return cls

    return wrapper


unary_magic_config = Config(
    {
        '__neg__': dict(func=np.negative),
        '__pos__': dict(func=np.positive),
        '__abs__': dict(func=np.absolute),
        '__invert__': dict(func=np.invert)
    },
    readonly=True,
    as_attrs=False
)
"""_"""

__pdoc__['unary_magic_config'] = f"""Config of unary magic methods to be added to a class.

```json
{unary_magic_config.to_doc()}
```
"""

UnaryTranslateFuncT = tp.Callable[[tp.Any, tp.Callable], tp.Any]


def attach_unary_magic_methods(translate_func: UnaryTranslateFuncT,
                               config: tp.Optional[Config] = None) -> WrapperFuncT:
    """Class decorator to add unary magic methods to a class.

    `translate_func` must

    * take `self` and unary function,
    * perform computation, and
    * return the result.

    `config` defaults to `unary_magic_config` and must contain target method names (keys)
    and dictionaries (values) with the following keys:

    * `func`: Function that transforms one array-like object.
    """
    if config is None:
        config = unary_magic_config

    def wrapper(cls: tp.Type[tp.T]) -> tp.Type[tp.T]:
        for target_name, settings in config.items():
            func = settings['func']

            def new_method(self,
                           _translate_func: UnaryTranslateFuncT = translate_func,
                           _func: tp.Callable = func) -> tp.SeriesFrame:
                return _translate_func(self, _func)

            new_method.__qualname__ = f"{cls.__name__}.{target_name}"
            new_method.__name__ = target_name
            setattr(cls, target_name, new_method)
        return cls

    return wrapper