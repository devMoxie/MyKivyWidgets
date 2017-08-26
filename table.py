from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.properties import BooleanProperty, ListProperty, ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock

"""
    Table
    =====

    The :class:`Table` widget is an advanced data table layout.

    Notes
    -----

        * An app crash can be triggered with a combination of scrolling and
          window resizing. See this post regarding max recursion errors. The
          issue with data misplacement mentioned in the post has been solved.

          https://stackoverflow.com/q/44573674

        * Tooltip functionality is based on this post:

          https://stackoverflow.com/a/34471497/1880836

    Features
    --------

        * Vertical and horizonal scrolling utilizing `RecycleView` for
          fast rendering.

        * Fixed header of column titles when scrolling vertically.

        * Fixed first column when scrolling horizontally.

        * Tooltip on mouse-over when text is shortened to fit cell dimensions.

        * Selectable rows by clicking on the value in the first column.

    Usage
    =====

    Parameters
    ----------

        `list_dicts` : list of `collections.OrderedDict`
            Required. This is the data to be displayed.

        `pre_selected_rows` : list of int
            Optional. A list of indexes of rows that will be in the `selected` state.

        `selectable` : bool
            Defaults to `False`. If `True`, allows for selection behavior. Otherwise,
            that behavior is ignored.

    Attributes
    ----------

        `selected_rows` : ListProperty
            A kivy property storing a list of indexes that have been selected. It is
            initialized with `pre_selected_rows`.

        `pre_selected_rows` : ListProperty
            A list of indexes of rows that will be in the `selected` state on `Table`
            instantiation.

            TODO: Not sure if this necessary.

    Events
    ------

    `on_selected_rows`:
        Fired when the attribute `selected_rows` changes. This can be bound to by the
        caller to cross-reference the indexes of selected rows with the list of
        `OrderedDict`s.

    Example
    -------::

        from kivy.app import App
        from random import sample
        from collections import OrderedDict

        class TableApp(App):
            def build(self):
                data = []
                pre_selected_rows = sample(range(30), 10)

                keys = ["Title Col: {}".format(i) for i in range(15)]

                for nrow in range(30):
                    row = OrderedDict.fromkeys(keys)
                    for i, key in enumerate(keys):
                        row[key] = "Data col: {}, row: {}".format(i, nrow)

                        if i % 3 == 0:
                            row[key] = row[key] + ". Extra long label. " * 2
                    data.append(row)

                return Table(list_dicts=data, pre_selected_rows=pre_selected_rows, selectable=True)

        TableApp().run()
"""


class ToolTip(Label):
    """Class declaration so that it can be called programmatically and styled in kv"""
    pass


class Cell(Label):
    """Defines the class for a table cell widget.

        The `Cell` class incorporates a hover effect with a tooltip for text that
        has been shortened inorder to display the full text of the cell.

        Attributes
        ----------

        `is_even` : BooleanProperty
            When `Table` is passed a list of dicts, where each dict represents a row,
            `is_even` is assigned True/False if it's index in the list is even/odd.
            This is used to determin the back ground color of the row. If the row is
            the table header, the is_even remains `None` and is assigned it's own
            background color.

        `dark`, `medium`, `light` : ListProperty
            `rgba` color codes to be given to the `canvas.before` property.

        'tooltip' : None
            Initialized in init for clarity. To be reassigned if text is shortend.
    """

    is_even = BooleanProperty(None, allownone=True)
    dark = ListProperty([0.165, 0.165, 0.165, 1])
    medium = ListProperty([0.23, 0.23, 0.23, 1])
    light = ListProperty([0.2, 0.2, 0.2, 1])

    def __init__(self, *args, **kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(Cell, self).__init__(*args, **kwargs)
        self.tooltip = None

    def on_mouse_pos(self, window, pos):
        """A callback called when the mouse position is over the widget.

            If the mouse is within the `Cell`'s bounding box, this method
             schedules `display_tooltip` for the next `Clock` cycle with a
             time delta of 0.6s.

            Parameters
            ----------
            `window` : -
                Unused

            `pos` : tuple of float
                Position of the mouse when the even is triggered.
        """

        if not self.get_root_window() or not self.is_shortened:
            return

        Clock.unschedule(self.display_tooltip)
        self.close_tooltip()

        # to_widget changes coords from window to local coords.
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, .6)

    def close_tooltip(self):
        Window.remove_widget(self.tooltip)

    def display_tooltip(self, *args):
        """Adds tooltip to `Window` relative to the position of `self`."""

        pos = self.to_window(self.pos[0], self.pos[1], relative=False)
        self.tooltip = ToolTip(text=self.text, pos=pos)
        Window.add_widget(self.tooltip)


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
    selected = BooleanProperty(False)

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
            rv.col_one_rgrid.select_node(self.index)

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
        rv.selected_rows = [i for i, row in enumerate(rv.data) if row['selected'] is True]


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    """This class adds focus and selection behavior to RecycleGridLayout."""
    pass


class FirstColRv(RecycleView):
    """A RecycleView based class that adds the attribute:

        selected_rows : ListProperty
            A kivy property that can respond to changes with a callback.
    """
    selected_rows = ListProperty([])


class FirstCol(GridLayout):
    """A widget that composes the first column of a `Table` widget.

        Attributes
        ----------

        first_col_header : ObjectProperty

        rv : ObjectProperty

        col_one_grid : ObjectProperty

        selectable : bool
            If `True`, the `rv.viewclass` is set to "SelectableDataCell" otherwise
            it is set to "Cell".

        Parameters
        ----------

        list_dicts : list of dict
            Required.

        selectable : bool
            Optional. Defaults to False

        pre_selected_rows : list of int
            A list of indexes that are to set as selected on widget initialization.
            Optional. Defaults to an empty list.
    """

    first_col_header = ObjectProperty(None)
    rv = ObjectProperty(None)
    col_one_rgrid = ObjectProperty(None)

    def __init__(self, list_dicts=[], selectable=False, pre_selected_rows=[], *args, **kwargs):
        self.selectable = selectable

        super(FirstCol, self).__init__(*args, **kwargs)

        self.first_col_header.text = list_dicts[0].items()[0][0]

        for i, dct in enumerate(list_dicts):
            text = dct.values()[0]
            is_even = i % 2 == 0
            selected = i in pre_selected_rows
            self.rv.data.append({'text': text,
                                 'is_even': is_even,
                                 'selected': selected})


class TableHeader(ScrollView):
    """This class defines the layout for the table header."""
    pass


class TableData(RecycleView):
    """The `Table` data component right of the first column and below the header.

        This `RecycleView` widget is utilizies `RecycleGridLayout` which
        appends `Cell` instances as children.

        Attributes
        ----------

        ncols : int

        nrows : int

        data : list of dict
            This attribute is inherited from `RecycleView` and must be set.
            `RecycleView` takes in `data` and manages the insantiation of
            `viewclass` widgets and adds them to `RecycleGridLayout`.

        viewclass : str
            The class of the widgets to be attached to the layout. This is
            defined in `<TableData>` definition in `table.kv`.
    """

    def __init__(self, list_dicts=[], *args, **kwargs):
        if list_dicts:
            cols = len(list_dicts[0])
            self.ncols = cols - 1  # less the first column
            self.nrows = len(list_dicts)

            self.data = []

            super(TableData, self).__init__(*args, **kwargs)

            for i, ord_dict in enumerate(list_dicts):
                is_even = i % 2 == 0

                # [1:] less the 1st column value
                for text in ord_dict.values()[1:]:
                    if text is None:
                        text = " "
                    self.data.append({'text': text, 'is_even': is_even})


class Table(GridLayout):
    """This is the top level widget returned from this module.

        Note
        ----

        See module documentation at the top of this file for more
        information on how to use this module.
    """

    selected_rows = ListProperty([])
    pre_selected_rows = ListProperty([])

    def __init__(self, list_dicts=[], selectable=False, pre_selected_rows=[], *args, **kwargs):
        super(Table, self).__init__(*args, **kwargs)
        self.pre_selected_rows = pre_selected_rows
        self.cols = 2

        if list_dicts:
            self.first_col = FirstCol(list_dicts=list_dicts,
                                      selectable=selectable,
                                      pre_selected_rows=pre_selected_rows)

            self.header = TableHeader()

            # Less the first column -> [:1]
            for title in list_dicts[0].keys()[1:]:
                self.header.grid.add_widget(Cell(text=title))

            self.table_data = TableData(list_dicts=list_dicts)

            data_container = GridLayout(cols=1)
            data_container.add_widget(self.header)
            data_container.add_widget(self.table_data)

            self.add_widget(self.first_col)
            self.add_widget(data_container)

            # Bind the rows that are selected to self.selected_rows so it is an instance
            # # property accessible from the calling class.
            self.first_col.rv.bind(selected_rows=self.update_selected_rows)

            # Bind scroll behavior of header, first column and table data together.
            self.table_data.fbind('scroll_x', self.scroll_with_header)
            self.first_col.rv.fbind('scroll_y', self.scroll_with_first_col)
            self.table_data.fbind('scroll_y', self.scroll_with_data)

    def on_selected_rows(self, obj, value):
        pass

    def update_selected_rows(self, obj, value):
        self.selected_rows = value

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value

    def scroll_with_data(self, obj, value):
        self.first_col.rv.scroll_y = value

    def scroll_with_first_col(self, obj, value):
        self.table_data.scroll_y = value


if __name__ == '__main__':
    from kivy.app import App
    from random import sample
    from collections import OrderedDict

    class TableApp(App):
        def build(self):
            Window.size = (960, 640)
            data = []
            pre_selected_rows = sample(range(30), 10)

            keys = ["Title Col: {}".format(i) for i in range(15)]

            for nrow in range(30):
                row = OrderedDict.fromkeys(keys)
                for i, key in enumerate(keys):
                    row[key] = "Data col: {}, row: {}".format(i, nrow)

                    if i % 3 == 0:
                        row[key] = row[key] + ". Extra long label. " * 2
                data.append(row)

            return Table(list_dicts=data, selectable=True, pre_selected_rows=pre_selected_rows)

    TableApp().run()
