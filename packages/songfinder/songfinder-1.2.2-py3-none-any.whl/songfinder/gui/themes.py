import math
import tkinter as tk
import tkinter.font as tkFont

from songfinder import background, cache
from songfinder import classSettings as settings


class Theme(tk.Frame):
    def __init__(self, fenetre, **kwargs):
        tk.Frame.__init__(self, fenetre, **kwargs)
        self._width = kwargs.get("width", 640)
        self._height = kwargs.get("height", 450)
        self._text = AutoSizeLabel(self, bg=self["bg"])

        self._text.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self._previousBack = None
        self._name = "theone"

    def resize_font(self):
        self._text.resize_font(self._width, self._height)

    def update_back(self, back_name, aspect_ratio="loose"):
        back = background.Background(back_name, self._width, self._height, aspect_ratio)
        if str(back) != self._previousBack:
            self._text["image"] = background.BACKGROUNDS.get(back)
            self._previousBack = str(back)

    def prefetch_back(self, back_name, aspect_ratio="loose"):
        back = background.Background(back_name, self._width, self._height, aspect_ratio)
        background.BACKGROUNDS.get(back)

    def resize(self, width, height):
        self._width = width
        self._height = height
        self._text.clean_cache()

    def update_font_color(self):
        font_color = settings.PRESSETTINGS.get("Presentation_Parameters", "FontColor")
        self._text.config(fg=font_color)

    @property
    def name(self):
        return self._name

    @property
    def text(self):
        return self._text["text"]

    @text.setter
    def text(self, value):
        self._text["text"] = value


class AutoSizeLabel(tk.Label):
    def __init__(self, frame, **kwargs):
        tk.Label.__init__(self, frame, compound=tk.CENTER, **kwargs)
        self._fontSize = settings.PRESSETTINGS.get("Presentation_Parameters", "size")
        self._font = settings.PRESSETTINGS.get("Presentation_Parameters", "font")
        self._policeCache = cache.Cache(200, self._compute_size)

    def _text_width(self, police):
        # To be more precise all lines should be measured but it is to slow
        lignes = self["text"].split("\n")
        dict_len = {len(ligne): ligne for ligne in lignes}
        ligne_max = dict_len[max(dict_len.keys())]
        return police.measure(ligne_max)

    def _text_height(self, police):
        h_line = police.metrics("linespace")
        lignes = self["text"].split("\n")
        return len(lignes) * h_line

    def _compute_size(self, width, height):
        rapport = min(width / 1920, height / 1080)
        police = tkFont.Font(
            family=self._font,
            size=math.floor(self._fontSize * rapport),
            weight="bold",
        )
        try:
            resize = min(
                width * 0.9 / self._text_width(police),
                height * 0.9 / self._text_height(police),
                1,
            )
        except ZeroDivisionError:
            resize = 1
        police["size"] = math.floor(self._fontSize * resize * rapport)
        return police

    def resize_font(self, width, height):
        self["font"] = self._policeCache.get(self["text"], [width, height])

    def clean_cache(self):
        self._policeCache.reset()
