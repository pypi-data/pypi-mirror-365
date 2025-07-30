import time
import tkinter as tk

from songfinder import classSettings as settings
from songfinder.gui import screen, themes


class Preview:
    def __init__(self, frame, diapo_list, screens=None):
        self._frame = frame
        self._diapo_list = diapo_list

        self._previewSize = int(pow(screens[0].width, 1.0 / 3) * 32)

        self._previews = []

        self._frame.bind("<Button-1>", self._next_slide)
        self._frame.bind("<Button-3>", self._previous_slide)
        self._frame.bind("<Configure>", self.update_previews)
        self._delayId = None
        self._passed = 0
        self._delayAmount = 0
        self._callbackDelay = 0
        self._lastCallback = 0

        self.printer()

    def _previous_slide(self, _event):
        self._diapo_list.decremente()

    def _next_slide(self, _event):
        self._diapo_list.incremente()

    def update_previews(self, _event=None, delay=True):
        ratio = screen.get_ratio(settings.GENSETTINGS.get("Parameters", "ratio"))
        preview_count = max(
            int(self._frame.winfo_height() // (self._previewSize / ratio)),
            1,
        )
        if len(self._previews) > preview_count:
            for theme in self._previews[preview_count:]:
                theme.pack_forget()
            del self._previews[preview_count:]
        elif len(self._previews) < preview_count:
            for _ in range(preview_count - len(self._previews)):
                theme = themes.Theme(
                    self._frame,
                    width=self._previewSize,
                    height=self._previewSize / ratio,
                )
                self._previews.append(theme)
                theme.pack(side=tk.TOP)
        self.printer(delay)

    def printer(self, delay=True):
        if delay:
            self._callbackDelay = round((time.time() - self._lastCallback) * 1000)
            self._lastCallback = time.time()
            if self._delayId:
                self._frame.after_cancel(self._delayId)
            self._delayId = self._frame.after(self._delayAmount, self._printer)
        else:
            self._printer()

    def _printer(self):
        start_time = time.time()
        self._passed += 1
        ratio = screen.get_ratio(settings.GENSETTINGS.get("Parameters", "ratio"))
        for i, theme in enumerate(self._previews):
            diapo = self._diapo_list[i]
            new_theme = theme
            if theme.name != diapo.theme_name:
                theme.destroy()
                new_theme = themes.Theme(
                    self._frame,
                    width=self._previewSize,
                    height=self._previewSize / ratio,
                )
                self._previews[i] = new_theme
                new_theme.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            diapo.print_diapo(new_theme)
        self._prefetcher()

        # Compute printer delay to lower pression on slow computers
        printer_time = round((time.time() - start_time) * 1000)
        if printer_time > self._callbackDelay:
            self._delayAmount = printer_time
        else:
            self._delayAmount = 0

    def _prefetcher(self):
        self._diapo_list[-1].prefetch(self._previews)
        self._diapo_list[1].prefetch(self._previews)
