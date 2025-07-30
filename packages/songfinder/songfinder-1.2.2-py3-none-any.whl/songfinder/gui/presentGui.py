import contextlib
import tkinter as tk
from tkinter import ttk

from songfinder import background
from songfinder import classSettings as settings
from songfinder import messages as tkMessageBox
from songfinder.gui import fullScreenPresent, screen


class PresentGui:
    def __init__(
        self,
        frame,
        diapo_list,
        screens=None,
        element_to_present=None,
        list_to_present=None,
        callback=None,
    ):
        self._frame = frame
        self._element_to_present = element_to_present
        self._list_to_present = list_to_present
        self._callback = callback
        self._screens = screens
        self._diapo_list = diapo_list
        self._force_list_update = False
        self._activate_button = None
        self._update_list_button = None
        self._ratio_label = None
        self._ratio_select = None
        self._presentation = fullScreenPresent.Presentation(
            self._frame,
            self._diapo_list,
            screens=self._screens,
        )
        self._presentation.bind_close_callback(self._update_buttons)
        self._pack_widgets()
        frame.bind_all("<F5>", self._activate_present)

        self._diapo_list.bind_gui_update(self._presentation.printer)

    def _pack_widgets(self):
        for widget in [
            self._activate_button,
            self._update_list_button,
            self._ratio_label,
            self._ratio_select,
        ]:
            with contextlib.suppress(AttributeError):
                widget.pack_forget()
        self._activate_button = tk.Button(self._frame, command=self._activate_present)
        self._update_list_button = tk.Button(
            self._frame,
            text="Mettre à jour la liste",
            command=self._update_list,
        )
        self._activate_button.pack(side=tk.TOP, fill=tk.X)
        if len(self._screens) > 1:
            self._update_list_button.pack(side=tk.TOP, fill=tk.X)

        self._ratio_label = tk.Label(self._frame, text="Format de l'écran :")
        ratio_list = settings.GENSETTINGS.get("Parameters", "ratio_avail")
        self._ratio_select = ttk.Combobox(
            self._frame,
            values=ratio_list,
            state="readonly",
            width=20,
        )
        self._ratio_select.bind("<<ComboboxSelected>>", self._set_ratio)
        self._ratio_select.set(settings.GENSETTINGS.get("Parameters", "ratio"))
        self._ratio_label.pack(side=tk.TOP)
        self._ratio_select.pack(side=tk.TOP)
        self._update_buttons()

    def _set_ratio(self, _event=None):
        ratio = self._ratio_select.get()
        settings.GENSETTINGS.set("Parameters", "ratio", ratio)
        self._ratio = screen.get_ratio(ratio)
        if self._callback:
            self._callback()

    def _update_list(self):
        if self._presentation.is_hided():
            self._activate_present()
        elif self._list_to_present:
            self._force_list_update = True
            self._diapo_list.load(self._list_to_present())
            self._force_list_update = False
            self._presentation.printer()

    def _activate_present(self, _event=None):
        if self._presentation.is_hided():
            missing_backs = background.check_backgrounds()
            if missing_backs != []:
                tkMessageBox.showerror(
                    "Attention",
                    'Les fonds d\'écran pour les types "{}" sont introuvable.'.format(
                        ", ".join(missing_backs),
                    ),
                )
            settings.PRESSETTINGS.write()
            self._screens.update(reference_widget=self._frame)
            self._presentation.show()
            self._pack_widgets()
        else:
            self._presentation.hide()

    def _update_buttons(self):
        if self._activate_button:
            if len(self._screens) > 1:
                if self._presentation.is_hided():
                    self._activate_button["text"] = "Activer la présentation"
                else:
                    self._activate_button["text"] = "Désactiver la présentation"
            else:
                self._activate_button["text"] = "Présentation de la liste"
        if self._presentation.is_hided():
            self._update_list_button.config(state=tk.DISABLED)
        else:
            self._update_list_button.config(state=tk.NORMAL)

    def present_is_off(self):
        return self._presentation.is_hided() or self._force_list_update

    def bind_list_to_present(self, function):
        self._list_to_present = function

    def bind_element_to_present(self, function):
        self._element_to_present = function

    def bind_ratio_callback(self, function):
        self._callback = function
