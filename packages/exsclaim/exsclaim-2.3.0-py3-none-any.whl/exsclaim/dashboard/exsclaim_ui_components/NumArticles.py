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


class NumArticles(Component):
    """A NumArticles component.
Gets the number of articles EXSCLAIM will parse through.

Keyword arguments:

- numArticles (number; optional):
    The maximum number of articles to search through."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'NumArticles'


    def __init__(
        self,
        numArticles: typing.Optional[NumberType] = None,
        **kwargs
    ):
        self._prop_names = ['numArticles']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['numArticles']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(NumArticles, self).__init__(**args)

setattr(NumArticles, "__init__", _explicitize_args(NumArticles.__init__))
