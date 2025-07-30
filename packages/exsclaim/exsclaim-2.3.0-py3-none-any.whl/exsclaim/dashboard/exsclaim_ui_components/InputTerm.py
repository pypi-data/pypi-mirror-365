# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class InputTerm(Component):
    """An InputTerm component.
Gets the main search term to be used in EXSCLAIM

Keyword arguments:

- term (string; optional):
    The input term to search for."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'InputTerm'


    def __init__(
        self,
        term: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['term']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['term']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(InputTerm, self).__init__(**args)

setattr(InputTerm, "__init__", _explicitize_args(InputTerm.__init__))
