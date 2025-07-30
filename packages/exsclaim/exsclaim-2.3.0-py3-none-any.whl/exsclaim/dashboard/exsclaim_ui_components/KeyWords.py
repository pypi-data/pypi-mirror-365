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


class KeyWords(Component):
    """A KeyWords component.
Gets what keywords should be contained in/related to the subfigures.

Keyword arguments:

- allSubFigures (list; optional)

- articles (list; optional)

- keywordType (string; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'KeyWords'


    def __init__(
        self,
        keywordType: typing.Optional[str] = None,
        allSubFigures: typing.Optional[typing.Sequence] = None,
        articles: typing.Optional[typing.Sequence] = None,
        **kwargs
    ):
        self._prop_names = ['allSubFigures', 'articles', 'keywordType']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['allSubFigures', 'articles', 'keywordType']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(KeyWords, self).__init__(**args)

setattr(KeyWords, "__init__", _explicitize_args(KeyWords.__init__))
