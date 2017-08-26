from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder

from icons.iconfonts import register

from typography import Li
from extend_button_behavior import ExtendedButtonBehavior

"""
    modals
    ======

    This module contains classes for 3 different types of modal widgets.

    Required Modules
    ----------------

        * `typography`

        * `extend_button_behavior`

        * `icons`
"""

Builder.load_file('modals.kv')
Builder.load_file('typography.kv')
register('default_font', 'icons/fontawesome-webfont.ttf', 'icons/font-awesome.fontd')


class CloseButton(ExtendedButtonBehavior, Label):
    """This widget uses an icon and to display a button with a hover effect."""
    pass


class Dialog(Popup):
    """Defines a modal based on `kivy.uix.popup`.

        Features
        --------
            * A title bar with markup enabled.

            * A content container container a variable length of Li widgets.

        Attributes
        ----------

        grid : ObjectProperty
            This property is defined in `<Dialog>` in `modals.kv`.

        title : str
            Inherited from `Popup`. Text for the title bar.

        Parameters
        ----------

        title : str
            Required.

        messages : list of str
            For each string in `messages` an Li widget is added to `grid`.
            Required.

        ico : str
            Icon name. Optional. Defaults to "fa-circle".

        icon_color : str
            Optional. Defaults to "20c100".

        icon_size : str
            Optional. Defaults to "12sp".
    """

    def __init__(self,
                 messages,
                 title,
                 ico="fa-circle",
                 icon_color="20c100",
                 icon_size="12sp",
                 *args, **kwargs):

        super(Dialog, self).__init__(*args, **kwargs)
        self.title = title
        self.title_align = 'center'
        self.title_size = '18sp'

        # Hack: Enable markup on the the title Label.
        self.children[0].children[2].markup = True

        for msg in messages:
            self.grid.add_widget(Li(text=msg,
                                    ico=ico,
                                    icon_color=icon_color,
                                    icon_size=icon_size))


class LoadingModal(ModalView):
    """A modal that displays "loading".

        This modal does not have a close button and needs to be closed
        programmatically using `kivy.clock.Clock`.

        The layout is defing in `modals.kv`.
    """
    pass


class ModalBtnClose(ModalView):
    """A modal widget with more custom styles and a close button.

        This modal is designed for a single string with an icon.

        Attributes
        ----------

        msg : StringProperty
            Text to display. Required.

        ico : StringProperty
            The icon to display. The default icon is 'fa-circle'.
            Optional.

        icon_color : StringProperty
            The color of the icon. The default icon_color is '20c100'.
            Optional.
    """
    # msg = StringProperty(None)
    # ico = StringProperty(None)
    # icon_color = StringProperty(None)

    def __init__(self, msg, ico="fa-circle", icon_color="20c100", *args, **kwargs):
        self.msg = msg
        self.ico = ico
        self.icon_color = icon_color
        super(ModalBtnClose, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    from kivy.app import App
    from kivy.uix.anchorlayout import AnchorLayout
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.clock import Clock
    from icons.iconfonts import icon

    class RootWidget(AnchorLayout):

        def __init__(self, *args, **kwargs):
            super(RootWidget, self).__init__(*args, **kwargs)

            cont = BoxLayout(orientation='horizontal', size_hint=(None, None), width=1020, height=120)

            btn1 = Button(text="Open Dialog", size_hint=(None, None), size=(340, 120))
            btn1.bind(on_release=self.open_dialog)

            btn2 = Button(text="Open LoadingModal", size_hint=(None, None), size=(340, 120))
            btn2.bind(on_release=self.open_loading_modal)

            btn3 = Button(text="Open ModalBtnClose", size_hint=(None, None), size=(340, 120))
            btn3.bind(on_release=self.open_modal_btn_close)

            for b in [btn1, btn2, btn3]:
                cont.add_widget(b)

            self.add_widget(cont)

        def open_dialog(self, *args):
            title = u"{}  [b]Dialog Title[/b]".format(icon("fa-th-list", "18sp", "4d8cf5"))
            msgs = ["This is message {}.".format(i) for i in range(10)]
            d = Dialog(title=title,
                       messages=msgs,
                       ico="fa-angle-right",
                       icon_size="16sp")
            d.open()

        def open_loading_modal(self, *args):
            mod = LoadingModal()
            mod.open()
            Clock.schedule_once(lambda dt: mod.dismiss(), 2)

        def open_modal_btn_close(self, *args):
            mod = ModalBtnClose(msg="Are you sure you made the right move?",
                                ico="fa-warning",
                                icon_color="ff2222")
            mod.open()

    class TestApp(App):
        def build(self):

            return RootWidget()

    TestApp().run()
