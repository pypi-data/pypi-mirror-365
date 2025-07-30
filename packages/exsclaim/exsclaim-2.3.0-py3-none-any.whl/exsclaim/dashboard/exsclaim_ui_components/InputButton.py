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


class InputButton(Component):
    """An InputButton component.
Submits the user query to the API, which then runs EXSCLAIM.
After the subfigure results are loaded, the user is taken to the results page (Layout.js)

Keyword arguments:

- id (string; default "submit-query"):
    The id of the button.

- access (boolean; optional):
    If the articles should be open access or not.

- fast_api_url (string; optional):
    The API's URL.

- journalFamily (string; optional):
    The journal family that will be searched through.

- model (string; optional):
    The name of the LLM model.

- modelKey (string; optional):
    The API Key needed to run the given LLM.

- numArticles (number; optional):
    The maximum number of articles to search through.

- outputName (string; optional):
    The name of the output.

- queryId (string; optional):
    The id for the most recently submitted query.

- sort (string; optional):
    How the articles should be sorted.

- synonyms (list of strings; optional):
    Any synonyms that are related to the search term.

- term (string; optional):
    The input term to search for."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'InputButton'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        outputName: typing.Optional[str] = None,
        journalFamily: typing.Optional[str] = None,
        numArticles: typing.Optional[NumberType] = None,
        sort: typing.Optional[str] = None,
        term: typing.Optional[str] = None,
        synonyms: typing.Optional[typing.Sequence[str]] = None,
        access: typing.Optional[bool] = None,
        model: typing.Optional[str] = None,
        modelKey: typing.Optional[str] = None,
        fast_api_url: typing.Optional[str] = None,
        queryId: typing.Optional[str] = None,
        setAlert: typing.Optional[typing.Any] = None,
        setAlertContent: typing.Optional[typing.Any] = None,
        setAlertSeverity: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'access', 'fast_api_url', 'journalFamily', 'model', 'modelKey', 'numArticles', 'outputName', 'queryId', 'sort', 'synonyms', 'term']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'access', 'fast_api_url', 'journalFamily', 'model', 'modelKey', 'numArticles', 'outputName', 'queryId', 'sort', 'synonyms', 'term']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(InputButton, self).__init__(**args)

setattr(InputButton, "__init__", _explicitize_args(InputButton.__init__))
