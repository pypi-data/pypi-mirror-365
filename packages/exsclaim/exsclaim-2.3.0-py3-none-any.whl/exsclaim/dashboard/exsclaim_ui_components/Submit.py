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


class Submit(Component):
    """A Submit component.
Submit user's query for filtered subfigures

Keyword arguments:

- allSubFigures (list; optional)

- articles (list; optional)

- classes (list; optional)

- figures (list; optional)

- keyword (string; optional)

- keywordType (string; optional)

- license (boolean; optional)

- scales (list; optional)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'Submit'


    def __init__(
        self,
        allSubFigures: typing.Optional[typing.Sequence] = None,
        articles: typing.Optional[typing.Sequence] = None,
        classes: typing.Optional[typing.Sequence] = None,
        figures: typing.Optional[typing.Sequence] = None,
        keyword: typing.Optional[str] = None,
        keywordType: typing.Optional[str] = None,
        license: typing.Optional[bool] = None,
        scales: typing.Optional[typing.Sequence] = None,
        id = None,
        **kwargs
    ):
        self._prop_names = ['allSubFigures', 'articles', 'classes', 'figures', 'keyword', 'keywordType', 'license', 'scales']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['allSubFigures', 'articles', 'classes', 'figures', 'keyword', 'keywordType', 'license', 'scales']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Submit, self).__init__(**args)

setattr(Submit, "__init__", _explicitize_args(Submit.__init__))
