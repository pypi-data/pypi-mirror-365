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


class Layout(Component):
    """A Layout component.
One big container containing the UI results page. It is divided into two parts: left side menu, right side figures.

Keyword arguments:

- id (string; default "layout"):
    The id of the layout.

- loadResults (boolean; optional):
    If the results page should be loaded (True) or the query page
    (False).

- queryResultsId (string; optional):
    The ID for the results that were submitted from the Query page."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'Layout'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        loadResults: typing.Optional[bool] = None,
        queryResultsId: typing.Optional[str] = None,
        setLoadResults: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'loadResults', 'queryResultsId']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'loadResults', 'queryResultsId']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Layout, self).__init__(**args)

setattr(Layout, "__init__", _explicitize_args(Layout.__init__))
