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


class OpenAccess(Component):
    """An OpenAccess component.
Toggles if EXSCLAIM should only have open access results

Keyword arguments:

- id (string; default "open-access"):
    The id of the open access box.

- access (boolean; optional):
    If the articles should be open access or not."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'OpenAccess'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        access: typing.Optional[bool] = None,
        setAccess: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'access']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'access']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(OpenAccess, self).__init__(**args)

setattr(OpenAccess, "__init__", _explicitize_args(OpenAccess.__init__))
