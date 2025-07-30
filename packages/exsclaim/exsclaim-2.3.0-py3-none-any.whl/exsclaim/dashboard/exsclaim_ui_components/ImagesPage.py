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


class ImagesPage(Component):
    """An ImagesPage component.
Displays the subfigure results of the user's input in the subfigure results menu and the query menu.

Keyword arguments:

- articles (list; optional):
    The list of articles scraped by EXSCLAIM!.

- figures (list; optional):
    The list of figures scraped by EXSCLAIM!.

- subFigures (list; optional):
    The list of subfigures discovered by EXSCLAIM!."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'ImagesPage'


    def __init__(
        self,
        articles: typing.Optional[typing.Sequence] = None,
        figures: typing.Optional[typing.Sequence] = None,
        subFigures: typing.Optional[typing.Sequence] = None,
        **kwargs
    ):
        self._prop_names = ['articles', 'figures', 'subFigures']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['articles', 'figures', 'subFigures']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(ImagesPage, self).__init__(**args)

setattr(ImagesPage, "__init__", _explicitize_args(ImagesPage.__init__))
