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


class OutputName(Component):
    """An OutputName component.
Handles and gets the output EXSCLAIM file name inputted by the user.

Keyword arguments:

- outputName (string; optional):
    The name of the search's output."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'OutputName'


    def __init__(
        self,
        outputName: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['outputName']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['outputName']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(OutputName, self).__init__(**args)

setattr(OutputName, "__init__", _explicitize_args(OutputName.__init__))
