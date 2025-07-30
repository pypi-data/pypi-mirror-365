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


class InputSynonyms(Component):
    """An InputSynonyms component.
Gets the alternative search terms (synonyms) to be used in EXSCLAIM!

Keyword arguments:

- synonyms (list of strings; optional):
    Any synonyms that are related to the search term."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'InputSynonyms'


    def __init__(
        self,
        synonyms: typing.Optional[typing.Sequence[str]] = None,
        **kwargs
    ):
        self._prop_names = ['synonyms']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['synonyms']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(InputSynonyms, self).__init__(**args)

setattr(InputSynonyms, "__init__", _explicitize_args(InputSynonyms.__init__))
