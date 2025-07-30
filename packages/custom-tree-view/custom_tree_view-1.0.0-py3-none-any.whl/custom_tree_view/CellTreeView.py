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


class CellTreeView(Component):
    """A CellTreeView component.
CellTreeView is a custom TreeView component for hierarchically grouping cell types.
It displays cell types in a hierarchical structure (Major → Minor → Sub) and allows
users to create groups, rename them, and reorganize the hierarchy via drag & drop.
Data is provided as CSV-formatted strings with columns: celltype_major, celltype_minor, celltype_sub.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- groupedData (string; optional):
    Grouped cell hierarchy data as CSV string with columns:
    celltype_major, celltype_minor, celltype_sub.

- initialData (string; optional):
    Initial cell hierarchy data as CSV string with columns:
    celltype_major, celltype_minor, celltype_sub.

- searchTerm (string; default ''):
    Search term to filter the tree.

- selectedItems (list of strings; optional):
    Array of selected item IDs.

- selectionMode (a value equal to: 'multi', 'single', 'none'; default 'multi'):
    Selection mode: 'multi' (default), 'single', or 'none'."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'custom_tree_view'
    _type = 'CellTreeView'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        initialData: typing.Optional[str] = None,
        groupedData: typing.Optional[str] = None,
        selectedItems: typing.Optional[typing.Sequence[str]] = None,
        searchTerm: typing.Optional[str] = None,
        selectionMode: typing.Optional[Literal["multi", "single", "none"]] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'groupedData', 'initialData', 'searchTerm', 'selectedItems', 'selectionMode']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'groupedData', 'initialData', 'searchTerm', 'selectedItems', 'selectionMode']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(CellTreeView, self).__init__(**args)

setattr(CellTreeView, "__init__", _explicitize_args(CellTreeView.__init__))
