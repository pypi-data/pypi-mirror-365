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


class Header(Component):
    """A Header component.
The header of the app, introduces the user to the EXSCLAIM UI and how to use it

Keyword arguments:

- id (string; default "header"):
    The id of the header.

- alert (boolean; optional):
    If the alert should be shown to the user."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'Header'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        alert: typing.Optional[bool] = None,
        setAlert: typing.Optional[typing.Any] = None,
        setAlertContent: typing.Optional[typing.Any] = None,
        setAlertSeverity: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'alert']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'alert']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Header, self).__init__(**args)

setattr(Header, "__init__", _explicitize_args(Header.__init__))
