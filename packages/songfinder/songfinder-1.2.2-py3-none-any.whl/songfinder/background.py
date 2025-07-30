import errno
import logging
import os
import shutil
import traceback

from PIL import Image, ImageTk

import songfinder
from songfinder import cache
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder.gui import screen

logger = logging.getLogger(__name__)


try:
    import psutil
except ImportError:
    logger.warning("psutil is not available.")


class Background:
    def __init__(self, path, width, height, keep_ratio):
        self.width = width
        self.height = height
        self._path = path
        self._keep_ratio = keep_ratio

    @property
    def keep_ratio(self):
        return self._keep_ratio

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = int(value)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = int(value)

    @property
    def path(self):
        return self._path

    def __str__(self):
        file_name = fonc.get_file_name(self._path)
        return f"{file_name}_{self.width}_{self.height}"

    def __repr__(self):
        return repr(str(self))


class Backgrounds:
    def __init__(self):
        self._imageFile = None
        self._cachePath = os.path.join(songfinder.__settingsPath__, "cache")
        try:
            os.makedirs(self._cachePath)
        except OSError as error:
            if error.errno == errno.EEXIST:
                pass
            else:
                raise
        self._cache = cache.Cache(0, self._get_image_file)
        self._screens = screen.Screens()
        if settings.GENSETTINGS.get("Parameters", "highmemusage"):
            self.resize_cache("high")
        else:
            self.resize_cache("low")

    def _get_image_file(self, back: Background):
        try:
            path = os.path.join(self._cachePath, f"{back!s}.png")
            self._imageFile = Image.open(path)
        except OSError:
            try:
                self._imageFile = Image.open(back.path)
            except OSError:
                logger.debug(traceback.format_exc())
                return None
            self._resize(back)
            self._imageFile.save(path)
        return ImageTk.PhotoImage(self._imageFile)

    def _resize(self, back: Background):
        if back.keep_ratio == "keep":
            im_w, im_h = self._imageFile.size
            aspect_ratio = im_w / im_h
            back.width = min(back.width, int(back.height * aspect_ratio))
            back.height = int(back.width / aspect_ratio)
        self._imageFile = self._imageFile.resize(
            (back.width, back.height),
            Image.Resampling.LANCZOS,
        )

    def get(self, back: Background):
        return self._cache.get(str(back), [back])

    def resize_cache(self, mode="low"):
        self._screens.update(verbose=False)
        max_widths = max([_screen.width for _screen in self._screens])
        max_height = max([_screen.height for _screen in self._screens])
        size_ratio = max_widths * max_height / (1920 * 1080)
        try:
            if mode == "high":
                cache_slots = 20 + int(psutil.virtual_memory()[1] * 6e-8 / size_ratio)
            elif mode == "low":
                cache_slots = 10 + int(psutil.virtual_memory()[1] * 2e-8 / size_ratio)
            else:
                cache_slots = self._cache.max_size
                logger.warning(
                    f'Cache size mode "{mode}" for backgrounds not recognize',
                )
        except NameError:
            logger.debug(traceback.format_exc())
            cache_slots = 40
        logger.info(f"Using {cache_slots} cache slots for backgrounds")
        self._cache.max_size = cache_slots


def clean_disk_cache_image():
    path = os.path.join(songfinder.__settingsPath__, "cache")
    if os.path.isdir(path):
        size = directory_size(path)
        if size > 10**8:
            logger.info(f"Cleaning image cache: {pretty_size(size)}")
            shutil.rmtree(path, ignore_errors=True, onerror=None)


def directory_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += directory_size(itempath)
    return total_size


def pretty_size(size):
    base = 1024
    echelles = [" o", " Ko", " Mo", " Go", " To", "Po"]
    str_size = str(0)
    for i, echelle in enumerate(echelles):
        if size >= base ** (i):
            str_size = str(round(size / base ** (i), 2)) + echelle
    return str_size


def check_backgrounds():
    etypes = settings.GENSETTINGS.get("Syntax", "element_type")
    not_ok = []
    for etype in etypes:
        file_to_check = settings.PRESSETTINGS.get(etype, "Background")
        if not os.path.isfile(file_to_check):
            not_ok.append(etype)
    return not_ok


BACKGROUNDS = Backgrounds()
