from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.core.text import LabelBase
from icons.iconfonts import register

from extend_button_behavior import ExtendedButtonBehavior

"""
    Typography
    ==========

    A module for designing `html` inspired text widgets.

    Font files are required. Or, roll your own.
"""

FONTS = [
    {
        "name": "Roboto",
        "fn_regular": 'fonts/Roboto-Regular.ttf',
        "fn_bold": 'fonts/Roboto-Medium.ttf',
        "fn_italic": 'fonts/Roboto-Italic.ttf',
        "fn_bolditalic": 'fonts/Roboto-MediumItalic.ttf'
    },
    {
        "name": "RobotoLight",
        "fn_regular": 'fonts/Roboto-Thin.ttf',
        "fn_bold": 'fonts/Roboto-Light.ttf',
        "fn_italic": 'fonts/Roboto-ThinItalic.ttf',
        "fn_bolditalic": 'fonts/Roboto-LightItalic.ttf'
    },
]

register('default_font', 'icons/fontawesome-webfont.ttf', 'icons/font-awesome.fontd')

for font in FONTS:
    LabelBase.register(**font)


class Heading(Label):
    pass


class H1(Heading):
    pass


class H2(Heading):
    pass


class H3(Heading):
    pass


class H4(Heading):
    pass


class H5(Heading):
    pass


class H6(Heading):
    pass


class P(Label):
    pass


class Lead(Label):
    pass


class Li(BoxLayout):
    """List item widget.

        Attributes
        ----------

        text : str

        ico : str
            Name of the icon to be used as the bullet.

        icon_color : str
            Hex code.

        icon_size : str
    """

    text = StringProperty(None)
    ico = StringProperty(None)
    icon_color = StringProperty(None)
    icon_size = StringProperty(None)

    def __init__(self, *args, **kwargs):
        super(Li, self).__init__(*args, **kwargs)


class Link(ExtendedButtonBehavior, P):
    """Provides link behavior to text.

        This widget has a link hover behavior and opens up attr `url`
        in the system's browser. the module `webbrowser` is imported in
        `typography.kv`.

        Attributes
        ----------

        url : str
            The url string. "http://" is required a required prefix.
    """

    url = StringProperty(None)


if __name__ == '__main__':
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.scrollview import ScrollView
    from kivy.properties import ObjectProperty
    Builder.load_file("typography.kv")

    class Example(ScrollView):

        grid = ObjectProperty(None)

        def __init__(self, *args, **kwargs):
            super(Example, self).__init__(*args, **kwargs)

            t1 = "This also leads to some other annoying behaviour - as well as the text not wrapping, you might have observed that the halign and valign properties seem to do nothing by default."
            t2 = "A shorter li"

            self.grid.add_widget(H1(text='Heading 1'))
            self.grid.add_widget(H2(text='Heading 2'))
            self.grid.add_widget(H3(text='Heading 3'))
            self.grid.add_widget(H4(text='Heading 4'))
            self.grid.add_widget(H5(text='Heading 5'))
            self.grid.add_widget(H6(text='Heading 6'))
            self.grid.add_widget(P(text=t1))
            self.grid.add_widget(Link(text="Stack Overflow", url="https://stackoverflow.com"))
            self.grid.add_widget(Lead(text="Lead text. " * 10))
            self.grid.add_widget(Li(text=t1, icon_color="4d8cf5"))
            self.grid.add_widget(Li(text=t2,
                                    ico="fa-arrow-circle-o-right",
                                    icon_size="18sp"))

    class TestApp(App):

        def build(self):
            return Example()

    TestApp().run()
