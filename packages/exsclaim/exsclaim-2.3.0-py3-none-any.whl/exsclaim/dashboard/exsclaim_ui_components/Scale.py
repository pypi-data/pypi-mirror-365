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


class Scale(Component):
    """A Scale component.
Gets the scale and size of the subfigure results should be.

Keyword arguments:

- id (string; default "scale-grid")

- scales (list; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'Scale'


    def __init__(
        self,
        scales: typing.Optional[typing.Sequence] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'scales']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'scales']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Scale, self).__init__(**args)

setattr(Scale, "__init__", _explicitize_args(Scale.__init__))
