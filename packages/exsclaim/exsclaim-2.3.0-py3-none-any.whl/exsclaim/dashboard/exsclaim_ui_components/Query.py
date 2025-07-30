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


class Query(Component):
    """A Query component.
One big container with the input query menu for the user to run EXSCLAIM

Keyword arguments:

- id (string; default "query"):
    The id of the query object.

- fast_api_url (string; optional):
    The API's URL.

- journalFamilies (list of strings; optional):
    The list of available journal families to search through.

- loadResults (boolean; optional):
    If the query page should be loaded (False) or the results page
    (True)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'Query'


    def __init__(
        self,
        loadResults: typing.Optional[bool] = None,
        setLoadResults: typing.Optional[typing.Any] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        fast_api_url: typing.Optional[str] = None,
        setAlert: typing.Optional[typing.Any] = None,
        setAlertContent: typing.Optional[typing.Any] = None,
        setAlertSeverity: typing.Optional[typing.Any] = None,
        journalFamilies: typing.Optional[typing.Sequence[str]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'fast_api_url', 'journalFamilies', 'loadResults']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'fast_api_url', 'journalFamilies', 'loadResults']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Query, self).__init__(**args)

setattr(Query, "__init__", _explicitize_args(Query.__init__))
