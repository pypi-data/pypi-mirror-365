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


class License(Component):
    """A License component.
Gets whether the subfigure should come from an open-source project or not.

Keyword arguments:

- license (boolean; optional):
    If the subfigure's license should be open-source (True) or not
    (False)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'License'


    def __init__(
        self,
        license: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['license']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['license']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(License, self).__init__(**args)

setattr(License, "__init__", _explicitize_args(License.__init__))
