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


class Model(Component):
    """A Model component.
Gets what kind of LLM (Large Langauge Model) EXSCLAIM! will use.

Keyword arguments:

- available_llms (list of dicts; optional):
    A dictionary of available models, and if they need an API key or
    not.

- model (string; required):
    The name of the LLM model.

- modelKey (string; optional):
    The API Key needed to run the given LLM."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'Model'


    def __init__(
        self,
        model: typing.Optional[str] = None,
        modelKey: typing.Optional[str] = None,
        available_llms: typing.Optional[typing.Sequence[dict]] = None,
        **kwargs
    ):
        self._prop_names = ['available_llms', 'model', 'modelKey']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['available_llms', 'model', 'modelKey']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['model']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Model, self).__init__(**args)

setattr(Model, "__init__", _explicitize_args(Model.__init__))
