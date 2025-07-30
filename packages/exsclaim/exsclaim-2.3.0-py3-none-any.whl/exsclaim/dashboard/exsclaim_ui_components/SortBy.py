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


class SortBy(Component):
    """A SortBy component.
Gets the type of sort that EXSCLAIM will use

Keyword arguments:

- sort (string; optional):
    How the articles should be sorted."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'SortBy'


    def __init__(
        self,
        sort: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['sort']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['sort']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(SortBy, self).__init__(**args)

setattr(SortBy, "__init__", _explicitize_args(SortBy.__init__))
