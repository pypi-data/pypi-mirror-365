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


class CropImage(Component):
    """A CropImage component.
Returns the cropped image from the given data.

Keyword arguments:

- data (dict; required):
    The data about this image from EXSCLAIM.

- url (string; required):
    The url to the image."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'CropImage'


    def __init__(
        self,
        url: typing.Optional[str] = None,
        data: typing.Optional[dict] = None,
        **kwargs
    ):
        self._prop_names = ['data', 'url']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['data', 'url']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['data', 'url']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(CropImage, self).__init__(**args)

setattr(CropImage, "__init__", _explicitize_args(CropImage.__init__))
