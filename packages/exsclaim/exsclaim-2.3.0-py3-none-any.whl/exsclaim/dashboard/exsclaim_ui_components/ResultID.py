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


class ResultID(Component):
    """A ResultID component.
The input box that holds the current run ID.
If the value is changed, the results from the new run ID will be added to the screen (alongside the previous values).

Keyword arguments:

- resultsID (string; optional):
    The ID of the run who's results are being looked at."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'ResultID'


    def __init__(
        self,
        resultsID: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['resultsID']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['resultsID']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(ResultID, self).__init__(**args)

setattr(ResultID, "__init__", _explicitize_args(ResultID.__init__))
