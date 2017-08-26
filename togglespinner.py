from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.togglebutton import ToggleButton
from icons.iconfonts import icon

"""
    ToggleSpinner
    =============

    The :class:`ToggleSpinner` is a custom Kivy spinner widget that uses
    togglebuttons in a group.

    Features
    --------

        * Unlike the default `Spinner` class, the text of the spinner button
          is not bound to the selected value.

        * Adds a reset property to trigger a rebuild of the spinner.
"""


class ToggleSpinner(Spinner):
    """A spinner/dropdown widget that utilizes togglebuttons.

        Attributes
        ----------
        val : str
            The value to store the text in the selected togglebutton.

        cur_button : ObjectProperty
            Stores most recently selected togglebutton in the dropdown. This is utilized
            in self._on_dropdown_select inorder to select/deselect a button and correctly
            set or clear `val`.

        reset : bool
            When `True` this resets the `state` of the buttons and moves the scrollview
            to the top.

        options_cls : str
            The class to use for the buttons in the dropdown.

        open_text, close_text : str
            The title of the spinner button to trigger the dropdown. Changes on `is_open`.
    """

    val = StringProperty(None, allownone=True)

    cur_button = ObjectProperty(None)

    reset = BooleanProperty(False)

    def __init__(self, *args, **kwargs):

        ico_down = u"{}".format(icon('fa-toggle-down', '16sp', "20c100"))
        ico_up = u"{}".format(icon('fa-toggle-up', '16sp', "4d8cf5"))
        self.open_text = ico_down + "  Choose From List."
        self.close_text = ico_up + "  Close."

        super(ToggleSpinner, self).__init__(*args, **kwargs)
        self.option_cls = "SpinnerBtns"

        spinner_scroll = self.dropdown_cls
        spinner_scroll.bar_width = 10
        spinner_scroll.scroll_type = ['bars', 'content']
        spinner_scroll.bar_color = [0.2, 0.7, 0.9, 1]
        spinner_scroll.bar_inactive_color = [0.2, 0.7, 0.9, .5]

    def _on_dropdown_select(self, dropdown_obj, data, *largs):
        """A callback to correctly handle toggle buttons within a spinner dropdown.

            Note
            ----

            This method overrides the inherited method from kivy.uix.spinner

            If a toggle button in the dropdown is selected, this method will deselect
            the button and clear the value of the instance attribute `val`.

            Otherwise, the `val` attribute is set to `data`.


            Parameters
            ----------
            dropdown_obj : kivy.uix.dropdown.DropDown
                dropdown_obj is self._dropdown.
                The list of toggle buttons are found in dropdown_obj.children[0].children

            data : str
                The text value of the togglebutton.
        """

        self.cur_button = [btn for btn in dropdown_obj.children[0].children if btn.text == data][0]
        self.is_open = False

        if self.val == data:
            self.val = ""
        else:
            self.val = data

    def on_reset(self, instance, value):
        """A callback when `self.reset` changes value.

            Resets the state of the class.

            Parameters
            ----------
            instance : self

            value : bool
                The value of self.reset
        """

        if self.cur_button and self.reset is True:
            self.cur_button.state = 'normal'
            self._dropdown.scroll_y = 1
            self.val = None

        self.reset = False


class SpinnerBtns(SpinnerOption, ToggleButton):
    """Overrides ToggleSpinner's default options class.

        This class provides the toggle buttons to be used within the dropdown ToggleSpinner.
    """
    pass


if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.lang import Builder
    from icons.iconfonts import register

    Builder.load_file("togglespinner.kv")

    register('default_font', 'icons/fontawesome-webfont.ttf', 'icons/font-awesome.fontd')

    class Example(BoxLayout):

        def __init__(self, *args, **kwargs):
            super(Example, self).__init__(*args, **kwargs)

            spinner = ToggleSpinner(pos_hint={'top': .9, 'center_x': .5})
            spinner.values = ["Button {}".format(i) for i in range(10)]
            self.add_widget(spinner)

            self.lbl = Label(text="No value selected, yet.",
                             size_hint=(None, None),
                             width=350,
                             height=80,
                             font_size='16sp',
                             pos_hint={'top': .9})

            self.add_widget(self.lbl)

            spinner.bind(val=self.on_selection)

        def on_selection(self, instance, value):
            self.lbl.text = value

    class TestApp(App):

        def build(self):
            return Example()

    TestApp().run()
