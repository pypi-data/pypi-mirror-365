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


class JournalFamily(Component):
    """A JournalFamily component.
Gets the journal family where EXSCLAIM! will parse through

Keyword arguments:

- id (string; optional):
    The id of the JournalFamily box.

- journalFamilies (list of strings; optional):
    The list of available journal families to search through.

- journalFamily (string; optional):
    The journal family that will be searched through."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'exsclaim_ui_components'
    _type = 'JournalFamily'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        journalFamily: typing.Optional[str] = None,
        journalFamilies: typing.Optional[typing.Sequence[str]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'journalFamilies', 'journalFamily']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'journalFamilies', 'journalFamily']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(JournalFamily, self).__init__(**args)

setattr(JournalFamily, "__init__", _explicitize_args(JournalFamily.__init__))
