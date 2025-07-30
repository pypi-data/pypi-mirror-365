import math
import time
import tkinter as tk

from songfinder import classSettings as settings
from songfinder.gui import screen, simpleProgress, themes


class Presentation:
    def __init__(self, frame, diapo_list, screens=None, close_callback=None):
        self._closeCallback = close_callback
        self._frame = frame
        self._diapo_list = diapo_list
        self._themePres = None

        if not screens:
            self._screens = screen.Screens()
        else:
            self._screens = screens

        # Fenetre de presentation
        self._presentationWindow = tk.Toplevel(frame)
        self.hide()
        self._presentationWindow.title("Presentation")
        self._presentationWindow.protocol("WM_DELETE_WINDOW", self.hide)

        frame.bind_all("<Escape>", self.hide)
        self._presentationWindow.bind("<Button-1>", self._next_slide)
        self._presentationWindow.bind("<Button-3>", self._previous_slide)
        self._presentationWindow.bind("<KeyRelease-Right>", self._next_slide)
        self._presentationWindow.bind("<KeyRelease-Left>", self._previous_slide)
        self._presentationWindow.bind("<KeyRelease-Down>", self._next_slide)
        self._presentationWindow.bind("<KeyRelease-Up>", self._previous_slide)

        self._delayId = None
        self._passed = 0
        self._total = 0
        self._delayAmount = 0
        self._callbackDelay = 0
        self._lastCallback = 0

        self._linePerDiapo = 0

    def is_hided(self):
        return self._isHided

    def hide(self, _event=None):
        self._presentationWindow.withdraw()
        self._isHided = True
        if self._closeCallback:
            self._closeCallback()

    def show(self):
        input_ratio = screen.get_ratio(
            settings.GENSETTINGS.get("Parameters", "ratio"),
            self._screens[-1].ratio,
        )
        self._screens.full_screen(self._presentationWindow)
        if input_ratio != 0:
            self._width = math.floor(
                min(input_ratio * self._screens[-1].height, self._screens[-1].width),
            )
            self._height = math.floor(
                min(self._screens[-1].width // input_ratio, self._screens[-1].height),
            )
        else:
            self._width = self._screens[-1].width
            self._height = self._screens[-1].height
        self._create_theme()
        self._prefetch()
        self.printer()
        self._presentationWindow.focus_set()
        self._presentationWindow.deiconify()
        self._isHided = False

    def _prefetch(self):
        progress_bar = simpleProgress.SimpleProgress(
            "Création du cache des images",
            screens=self._screens,
        )
        progress_bar.start(len(self._diapo_list))
        self._diapo_list.prefetch([self._themePres], progress_bar.update)
        progress_bar.stop()

    def _previous_slide(self, _event=None):
        self._diapo_list.decremente(focus=True)

    def _next_slide(self, _event=None):
        self._diapo_list.incremente(focus=True)

    def _create_theme(self):
        if self._themePres:
            self._themePres.destroy()
        self._themePres = themes.Theme(
            self._presentationWindow,
            width=self._width,
            height=self._height,
            bg="black",
        )
        self._themePres.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def _prefetcher(self):
        if self._diapo_list is not None:
            self._diapo_list[-1].prefetch([self._themePres])
            for i in reversed(range(2)):
                self._diapo_list[i + 1].prefetch([self._themePres])

    def printer(self):
        self._parameter_update()
        self._total += 1
        self._callbackDelay = round((time.time() - self._lastCallback) * 1000)
        self._lastCallback = time.time()
        if self._delayId:
            self._frame.after_cancel(self._delayId)
        self._delayId = self._frame.after(self._delayAmount, self._printer)

    def _parameter_update(self):
        new_line_per_diapo = settings.PRESSETTINGS.get(
            "Presentation_Parameters",
            "line_per_diapo",
        )
        if new_line_per_diapo != self._linePerDiapo:
            self._diapo_list.reset_text()

    def _printer(self):
        start_time = time.time()
        self._passed += 1
        if self._themePres:
            diapo = self._diapo_list[0]
            if self._themePres.name != diapo.theme_name:
                self._create_theme()
            diapo.print_diapo(self._themePres)
            self._prefetcher()

        # Compute printer delay to lower pression on slow computers
        printer_time = round((time.time() - start_time) * 1000)
        if printer_time > self._callbackDelay:
            self._delayAmount = printer_time
        else:
            self._delayAmount = 0

    def bind_close_callback(self, function):
        self._closeCallback = function
