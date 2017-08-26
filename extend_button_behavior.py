from kivy.uix.behaviors.button import ButtonBehavior
from kivy.properties import BooleanProperty
from kivy.core.window import Window


class ExtendedButtonBehavior(ButtonBehavior):
    """Extends the class `ButtonBehavior`.

        Attributes
        ----------

        hover : BooleanProperty
            When the mouse hovers over the widget that inherits from this class,
            hover is set to `True`.

            The calling class can bind to this Kivy property to create, for example,
            a background change on hover.
    """

    hover = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(ExtendedButtonBehavior, self).__init__(*args, **kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return

        pos = args[1]

        if self.collide_point(*self.to_widget(*pos)):
            self.hover = True
        else:
            self.hover = False
