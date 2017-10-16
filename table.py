"""
    Table
    =====

    The :class:`Table` widget is an advanced data table layout.

    Features
    --------

        * Vertical and horizonal scrolling utilizing `RecycleView` for fast rendering.

        * Fixed header of column titles when scrolling vertically.

        * Fixed first column when scrolling horizontally.

        * Tooltip on mouse-over when text is shortened to fit cell dimensions.

        * Selectable rows by clicking on the value in the first column.

    Notes
    -----

        * An app crash can be triggered with rapid scrolling and quick window resizing.
          See this post regarding max recursion errors. The issue with data misplacement
          mentioned in the post has been solved.

          https://stackoverflow.com/q/44573674

    Usage
    =====

    Requirements
    ------------

        * `tooltip` module

    Parameters
    ----------

        `list_dicts` : list of `collections.OrderedDict`
            Required. This is the data to be displayed.

        `pre_selected_rows` : list of int
            Optional. A list of indexes of rows that will be in the `selected` state
            on initialization.

        `selectable` : bool
            Defaults to `False`. If `True`, allows for selection behavior. Otherwise,
            that behavior is ignored.

    Events
    ------

    `on_selected_rows`:
        Fired when the attribute `selected_rows` changes. This can be bound to by the
        caller to cross-reference the indexes of selected rows with the list of
        `OrderedDict`s.

    Example
    -------::

        if __name__ == '__main__':
            from kivy.app import App
            from kivy.lang import Builder

            from random import sample
            from collections import OrderedDict

            Builder.load_file("tooltip.kv")

            class TableApp(App):
                def build(self):
                    Window.size = (960, 640)
                    data = []
                    pre_selected_rows = sample(range(30), 10)

                    rand_row = sample(range(30), 10)
                    rand_col = sample(range(15), 5)

                    keys = ["Title Col: {}".format(i) for i in range(15)]

                    for nrow in range(30):
                        row = OrderedDict.fromkeys(keys)
                        for ncol, key in enumerate(keys):
                            row[key] = "row: {}, col: {}".format(nrow, ncol)

                            if nrow in rand_row and ncol in rand_col:
                                row[key] = row[key] + "; Extra long text."

                        data.append(row)

                    return Table(list_dicts=data, selectable=True, pre_selected_rows=pre_selected_rows)

            TableApp().run()
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.properties import BooleanProperty, ListProperty
from kivy.core.window import Window

from tooltip import ToolTipLabel, ToolTip


class Cell(ToolTipLabel):
    """Defines the class for a table cell widget.

        The `Cell` class inherits from ToolTipLabel to provide a hover effect with a tooltip
        for text that has been shortened inorder to display the full text of the cell.

        Attributes
        ----------

        `is_even` : BooleanProperty
            When `Table` is passed a list of dicts, where each dict represents a row,
            `is_even` is assigned True/False if it's index in the list is even/odd.
            This is used to determine the background color of the row. If the row is
            the table header, the is_even remains `None` and is assigned it's own
            background color.

        `selected : BooleanProperty
            If the first column is composed of `SelectableDataCell`s, this property is used to
            visually indicate that the row has been selected.
    """

    is_even = BooleanProperty(None, allownone=True)
    selected = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(Cell, self).__init__(*args, **kwargs)

    def on_pos(self, instance, value):
        for child in Window.children:
            if type(child) == ToolTip:
                Window.remove_widget(child)


class SelectableDataCell(RecycleDataViewBehavior, Cell):
    """A class that adds selection behavior to `Cell`.

        It is necessary to combine this class with `SelectableRecycleGridLayout`
        to implement this behavior.

        Attributes
        ----------

        index : int
            The index of instance derived from RecycleView's `data` list attribute.

        selected : BooleanProperty
            Set to `True` is selected, otherwise `False`.
    """

    index = None

    def __init__(self, *args, **kwargs):
        super(SelectableDataCell, self).__init__(*args, **kwargs)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes.

            With RecycleViews, the view is not always up to date with the data.
            This method syncs the view's attributtes with the corresponding values
            in `data`

            Parameters
            ----------
            rv : RecycleView

            index : int
                The index location in `data` that corresponds to `self`.

            data : AliasProperty : list of dict
                This is a list of dicts whose keys map to the corresponding property
                names of the viewclass.
        """
        self.index = index

        # Need to set self.selected before the rv.data is sent to the view and
        # adds the node to super's self.selected_nodes via select_node(self.index)
        if data['selected'] is True:
            setattr(self, 'selected', True)
            rv.grid.select_node(self.index)

        return super(SelectableDataCell, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        """Adds selection on touch down.

            For more information see:
            -------------------------

            https://kivy.org/docs/api-kivy.input.motionevent.html
            https://kivy.org/docs/api-kivy.uix.behaviors.compoundselection.html

            Parameters
            ----------
            `touch` : MouseMotionEvent
                Description of 'param'
        """
        if super(SelectableDataCell, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to a selection in the view.

            This method syncs the RecycleView `data` with the view and updates the list
            storing the indexes of selected rows.

            It is required to update rv.data list of dicts because rv.data is not bound
            to the attributes rv sets initially.

            Because LayoutSelectionBehavior, which inherits from CompoundSelectionBehavior,
            only adds nodes to select_nodes when the SelectableDataCell comes into 'view'
            (if it is pre-selected), LayoutSelectionBehavior.selected_nodes does not
            accurately reflect the cells that are selected only the ones visible on widget
            load.

            Parameters
            ----------
            rv : RecycleView

            index : int

            is_selected : BooleanProperty
        """

        self.selected = is_selected
        rv.data[index]['selected'] = self.selected
        rv.selected_cells = [i for i, row in enumerate(rv.data) if row['selected'] is True]


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    """This class adds focus and selection behavior to RecycleGridLayout."""

    def __init__(self, *args, **kwargs):
        super(SelectableRecycleGridLayout, self).__init__(*args, **kwargs)
        self.fbind('children', self.hover_on_scroll)

    def hover_on_scroll(self, instance, children):
        """This method updates the hover property when the mouse is not
            moving but the scrollview is.
        """

        for ch in children:
            if ch.collide_point(*ch.to_widget(*Window.mouse_pos)):
                ch.hover = True
            else:
                ch.hover = False


class FirstColRv(RecycleView):
    """A RecycleView based class that adds the attribute:

        selected_cells : ListProperty
            A kivy property that can respond to changes with a callback.
    """
    selected_cells = ListProperty([])


class Table(GridLayout):
    """This is the top level widget returned from this module.

        See module documentation at the top of this file for more
        information on how to use this module.

        Attributes
        ----------

            `selected_rows` : ListProperty
                A kivy property storing a list of indexes that have been selected. It is
                initialized with `pre_selected_rows`.

            `pre_selected_rows` : ListProperty
                A list of indexes of rows that will be in the `selected` state on `Table`
                instantiation.

            `first_col_header` : StringProperty
                A Kivy property bound to the first column header's text property found in `table.kv`

            `first_col_rv` : ObjectProperty
                A Kivy property referencing the `FirstColRv` object instantiated by `Table`.

            `table_header_scrlv` : ObjectProperty
                A kivy property referencing the `TableHeaderScrlv` object instantiated by `Table`.
                The `TableHeaderScrlv` layout object is defined in `table.kv`.

            `main_table_rv` : ObjectProperty
                A kivy property referencing the `MainTableRv` object instantiated by `Table`.
                The `MainTableRv` layout object is defined in `table.kv`.
    """

    selected_rows = ListProperty([])
    pre_selected_rows = ListProperty([])

    first_col_header = StringProperty("")
    first_col_rv = ObjectProperty(None)

    table_header_scrlv = ObjectProperty(None)
    main_table_rv = ObjectProperty(None)

    def __init__(self, list_dicts=[], selectable=False, pre_selected_rows=[], *args, **kwargs):
        self.selectable = selectable
        super(Table, self).__init__(*args, **kwargs)

        self.list_dicts = list_dicts
        self.pre_selected_rows = pre_selected_rows

        if list_dicts:
            self.first_col_header = list_dicts[0].items()[0][0]
            self.set_first_col_data(list_dicts)
            self.set_table_headers(list_dicts)
            self.set_main_table_data(list_dicts)

            # Bind self.selected_rows to first_col_rv.selected_cells
            self.first_col_rv.bind(selected_cells=self.setter('selected_rows'))

            # Bind scroll behaviors of header, first column and table.
            self.main_table_rv.fbind('scroll_x', self.scroll_with_header)
            self.first_col_rv.fbind('scroll_y', self.scroll_with_first_col)
            self.main_table_rv.fbind('scroll_y', self.scroll_with_data)

    def set_first_col_data(self, list_dicts):
        """Appends values to the `data` property of the `first_col_rv` object."""

        for row_num, dct in enumerate(list_dicts):
            text = dct.values()[0]

            self.first_col_rv.data.append(
                {'text': text if text is not None else " ",
                 'is_even': True if row_num % 2 is 0 else False,
                 'selected': row_num in self.pre_selected_rows, }
            )

    def set_table_headers(self, list_dicts):
        """Adds `Cell` widgets to the `GridLayout` child of `table_header_scrlv`."""

        # Less the first column key.
        for title in list_dicts[0].keys()[1:]:
            self.table_header_scrlv.grid.add_widget(Cell(text=title))

    def set_main_table_data(self, list_dicts):
        """Appends values to the `data` property of the `main_table_rv` object."""

        self.main_table_rv.grid.cols = len(list_dicts[0]) - 1

        for row_num, ord_dict in enumerate(list_dicts):

            for text in ord_dict.values()[1:]:
                self.main_table_rv.data.append(
                    {'text': text if text is not None else " ",
                     'is_even': True if row_num % 2 is 0 else False,
                     "selected": False,
                     "row": row_num, }
                )

    def scroll_with_header(self, obj, value):
        self.table_header_scrlv.scroll_x = value

    def scroll_with_data(self, obj, value):
        self.first_col_rv.scroll_y = value

    def scroll_with_first_col(self, obj, value):
        self.main_table_rv.scroll_y = value

    def on_selected_rows(self, instance, row_nums):
        """Synx main_table_rv cells' selected state with self.selected_rows."""

        # could probable keep track of the previous list of indexes, get the diff with new list of
        # indexes and set accordingly instead of looping through the whole data set
        for d in self.main_table_rv.data:
            if d["row"] in row_nums:
                d["selected"] = True
            else:
                d["selected"] = False

        self.main_table_rv.refresh_from_data()


if __name__ == '__main__':
    from kivy.app import App
    from kivy.lang import Builder
    from random import sample
    from collections import OrderedDict

    Builder.load_file("tooltip.kv")

    class TableApp(App):
        def build(self):
            Window.size = (960, 640)
            data = []
            pre_selected_rows = sample(range(30), 10)

            rand_row = sample(range(30), 10)
            rand_col = sample(range(15), 5)

            keys = ["Title Col: {}".format(i) for i in range(15)]

            for nrow in range(30):
                row = OrderedDict.fromkeys(keys)
                for ncol, key in enumerate(keys):
                    row[key] = "row: {}, col: {}".format(nrow, ncol)

                    if nrow in rand_row and ncol in rand_col:
                        row[key] = row[key] + "; Extra long text."

                data.append(row)

            return Table(list_dicts=data, selectable=True, pre_selected_rows=pre_selected_rows)

    TableApp().run()
