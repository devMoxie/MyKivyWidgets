"""
    ToolTip
    =======

    A module to provide a tooltip and hover functionality for `Label`.

    Based on https://stackoverflow.com/a/34471497/1880836

    Note
    ====

    This doesn't inherit from HoverBehavior so that collide_point isn't
    called twice.
"""

from kivy.uix.label import Label
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.bubble import Bubble
from kivy.metrics import dp
from kivy.uix.widget import Widget


class ToolTip(Bubble):
    """A bubble widget that contains a label."""
    text = StringProperty(None)
    label = ObjectProperty(None)


class ToolTipLabel(Label):
    """A `Label` based widget that adds a tooltip on haver if it's
        text is shortened

        Attributes
        ----------

        `hover` : BooleanProperty
            A property that can be used when the mouse is over a ToolTipLable instance.

        'tooltip' : None
            Initialized in init for clarity. To be reassigned if text is shortend.
    """

    hover = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        Window.fbind("mouse_pos", self.on_mouse_pos)

        super(ToolTipLabel, self).__init__(*args, **kwargs)
        self.tooltip = None
        self.trigger_tp = Clock.create_trigger(self.display_tooltip)

    def on_mouse_pos(self, window, pos):
        """A callback called when the mouse position is over the widget.

            If the mouse is within the `Cell`'s bounding box, trigger_tp
            is scheduled for the next `Clock` cycle.

            Parameters
            ----------

            `pos` : tuple of float
                Position of the mouse when the event is triggered.
        """

        if not self.get_root_window():
            return

        Window.remove_widget(self.tooltip)

        if self.collide_point(*self.to_widget(*pos)):

            self.hover = True

            if self.is_shortened:
                self.trigger_tp()

        else:
            self.hover = False

    def display_tooltip(self, *args):
        self.tooltip = ToolTip(text=self.text)
        self.tooltip.label.fbind("size", self.set_position)
        Window.add_widget(self.tooltip)

    def set_position(self, instance, size):
        """This method sets the position for a tooltip that is withhin a
            recycleview.

            Note
            ====

            This method is untested in other layouts.
        """
        pos = list(self.to_window(self.pos[0], self.pos[1], relative=False))

        self.tooltip.size = (size[0] + dp(5), size[1])

        # If tooltip fits right of self
        if pos[0] + self.width + self.tooltip.width < Window.width:
            pos[0] = pos[0] + self.width

            if self.tooltip.height > dp(30):
                self.tooltip.arrow_pos = 'left_bottom'

                # Add spacer so arrow is centered on first line of the text.
                self.tooltip._arrow_layout.add_widget(Widget(size_hint_y=None, height=dp(4)))

            else:
                self.tooltip.arrow_pos = 'left_mid'
        else:
            pos[0] = pos[0] - self.tooltip.width

            if self.tooltip.height > dp(30):
                self.tooltip.arrow_pos = 'right_bottom'
                self.tooltip._arrow_layout.add_widget(Widget(size_hint_y=None, height=dp(4)))
            else:
                self.tooltip.arrow_pos = 'right_mid'

        self.tooltip.pos = pos


if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.anchorlayout import AnchorLayout
    from kivy.graphics import Color, Rectangle

    class ToolTipApp(App):
        def build(self):

            tp_label = ToolTipLabel(text="Some really long text that doesn't fit in the label's bounding box.",
                                    size_hint=(None, None), width=300, height=60, font_size='18sp',
                                    shorten=True, shorten_from="right",
                                    color=[0, 0, 0, 1])

            tp_label.text_size = tp_label.size

            container = AnchorLayout()
            container.add_widget(tp_label)

            with container.canvas.before:
                Color(.9, .9, .9)
                Rectangle(pos=container.pos, size=Window.size)

            return container

    ToolTipApp().run()
