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


class Classification(Component):
    """A Classification component.
Gets what type the subfigure results should be.

Keyword arguments:

- classes (list of strings; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'Classification'


    def __init__(
        self,
        classes: typing.Optional[typing.Sequence[str]] = None,
        **kwargs
    ):
        self._prop_names = ['classes']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['classes']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Classification, self).__init__(**args)

setattr(Classification, "__init__", _explicitize_args(Classification.__init__))
