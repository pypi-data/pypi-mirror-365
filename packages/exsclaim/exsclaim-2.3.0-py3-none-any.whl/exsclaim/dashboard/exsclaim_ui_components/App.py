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


class App(Component):
    """An App component.
Layout of app should be:
NavigationBar / Header
Menu and Results
Footer

Keyword arguments:

- id (string; default "exsclaim-app"):
    The id of the main app.

- alert (boolean; default False):
    If the alert should be shown to the user.

- alertContent (string; default ""):
    The content of the alert that is shown to the user.

- alertSeverity (string; default "success"):
    How severe the alert is.

- available_llms (list of dicts; default ["llama3.2"]):
    The list of available LLMs. The syntax should match LLM.models().

- fast_api_url (string; default "https://exsclaim.materialeyes.org"):
    The API's URL.

- journalFamilies (list of strings; default ["Nature"]):
    The list of available journal families to search through.

- loadResults (boolean; optional):
    If the results page should be loaded (True) or the query page
    (False).

- queryResultsId (string; optional):
    The ID for the results that were submitted from the Query page."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'App'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        loadResults: typing.Optional[bool] = None,
        queryResultsId: typing.Optional[str] = None,
        fast_api_url: typing.Optional[str] = None,
        available_llms: typing.Optional[typing.Sequence[dict]] = None,
        alert: typing.Optional[bool] = None,
        setAlert: typing.Optional[typing.Any] = None,
        alertContent: typing.Optional[str] = None,
        setAlertContent: typing.Optional[typing.Any] = None,
        alertSeverity: typing.Optional[str] = None,
        setAlertSeverity: typing.Optional[typing.Any] = None,
        journalFamilies: typing.Optional[typing.Sequence[str]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'alert', 'alertContent', 'alertSeverity', 'available_llms', 'fast_api_url', 'journalFamilies', 'loadResults', 'queryResultsId']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'alert', 'alertContent', 'alertSeverity', 'available_llms', 'fast_api_url', 'journalFamilies', 'loadResults', 'queryResultsId']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(App, self).__init__(**args)

setattr(App, "__init__", _explicitize_args(App.__init__))
