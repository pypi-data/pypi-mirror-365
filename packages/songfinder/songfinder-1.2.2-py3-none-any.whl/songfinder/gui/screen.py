import contextlib
import logging
import sys
import tkinter as tk
import traceback

with contextlib.suppress(ImportError):
    import screeninfo

import songfinder
from songfinder import commandLine, exception

logger = logging.getLogger(__name__)

EXPECTED_SIZE_LIST_LEN = 2
EXPECTED_POSITION_LIST_LEN = 3


class Screen:
    def __init__(
        self,
        width=720,
        height=480,
        xposition=0,
        yposition=0,
        string_screen=None,
    ):
        if not string_screen:
            try:
                self._width = int(width)
                self._height = int(height)
                self._xposition = int(xposition)
                self._yposition = int(yposition)
                self._isOK = True
            except ValueError:
                logger.warning(
                    "Erreur de lecture des donnees de l'ecran :\n{}".format(
                        "\n".join(
                            [
                                repr(data)
                                for data in [width, height, xposition, yposition]
                            ],
                        ),
                    ),
                )
                self._isOK = False
        else:
            self._set_screen(string_screen)
        self._areUsableSet = False

    def _set_screen(self, string_screen):
        size_list = string_screen.split("x")
        if len(size_list) != EXPECTED_SIZE_LIST_LEN:
            logger.warning(
                "Erreur de lecture de la resolution de l"
                "ecran, "
                "le format des donnees n"
                f'est pas valide : "{string_screen}". '
                'Le format valide est : "wxh+pw+ph',
            )
            self._isOK = False
        else:
            position_list = size_list[1].split("+")
            if len(position_list) != EXPECTED_POSITION_LIST_LEN:
                logger.warning(
                    "Erreur de lecture de la position de l"
                    "ecran, "
                    "le format des donnees n"
                    f'est pas valide : "{string_screen}". '
                    'Le format valide est : "wxh+pw+ph',
                )
                self._isOK = False
            else:
                try:
                    self._width = int(float(size_list[0]))
                    self._height = int(float(position_list[0]))
                    self._xposition = int(float(position_list[1]))
                    self._yposition = int(float(position_list[2]))
                    self._isOK = True
                except ValueError:
                    logger.warning(
                        "Erreur de lecture des donnees de l'ecran :\n{}".format(
                            "\n".join(
                                [
                                    repr(data)
                                    for data in [
                                        size_list[0],
                                        position_list[0],
                                        position_list[1],
                                        position_list[2],
                                    ]
                                ],
                            ),
                        ),
                    )
                    self._isOK = False

    def __bool__(self):
        return self._isOK

    def __nonzero__(self):
        return self.__bool__()

    @property
    def xposition(self):
        return self._xposition

    @property
    def yposition(self):
        return self._yposition

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def usable_xposition(self):
        self._get_usable_screen()
        return self._usableXposition

    @property
    def usable_yposition(self):
        self._get_usable_screen()
        return self._usableYposition

    @property
    def usable_width(self):
        self._get_usable_screen()
        return self._usableWidth

    @property
    def usable_height(self):
        self._get_usable_screen()
        return self._usableHeight

    @property
    def ratio(self):
        return self._width / self._height if self._height != 0 else 1

    def _get_usable_screen(self):
        if not self._areUsableSet:
            try:
                frame = tk.Toplevel()
                frame.wm_attributes("-alpha", 0)
                frame.withdraw()
                frame.geometry(f"+{self.xposition}+{self.yposition}")
                frame.update()
                frame.state("zoomed")
                frame.withdraw()
            except tk.TclError:
                logger.debug(traceback.format_exc())
                self._usableWidth = int(self.width * 0.9)
                self._usableHeight = int(self.height * 0.9)
                self._usableXposition = int(self.xposition * 0.9)
                self._usableYposition = int(self.yposition * 0.9)
            else:
                frame.update()
                self._usableWidth = frame.winfo_width()
                self._usableHeight = frame.winfo_height()
                self._usableXposition = frame.winfo_rootx()
                self._usableYposition = frame.winfo_rooty()
                frame.destroy()
            self._areUsableSet = True

    def __str__(self):
        return "".join(
            [
                str(self._width),
                "x",
                str(self._height),
                "+",
                str(self._xposition),
                "+",
                str(self._yposition),
            ],
        )

    @property
    def usable(self):
        self._get_usable_screen()
        return "".join(
            [
                str(self._usableWidth),
                "x",
                str(self._usableHeight),
                "+",
                str(self._usableXposition),
                "+",
                str(self._usableYposition),
            ],
        )

    def is_widget_screen_size_mine(self, widget):
        widget.update()
        return (
            widget.winfo_width() == self.width and widget.winfo_height() == self.height
        )

    def is_widget_in_screen(self, widget):
        widget.update()
        xposition = widget.winfo_rootx() - self.xposition
        yposition = widget.winfo_rooty() - self.yposition
        logger.debug(
            f"Widget position is: {widget.winfo_rootx()}+{widget.winfo_rooty()}, Screen is: {self}",
        )
        return (
            not self.is_widget_screen_size_mine(widget)
            and xposition >= 0
            and xposition < self.width
            and yposition >= 0
            and yposition < self.height
        )

    def center_frame(self, frame):
        newx = (self.usable_width - frame.winfo_reqwidth()) // 2 + self.usable_xposition
        newy = (
            self.usable_height - frame.winfo_reqheight()
        ) // 2 + self.usable_yposition
        frame.geometry(f"+{newx}+{newy}")

    def resize_frame(self, frame, width, height):
        new_width = min(self.usable_width, width)
        new_height = min(self.usable_height, height)
        clipx = self.usable_width - new_width + self.usable_xposition - 1
        clipy = self.usable_height - new_height + self.usable_yposition - 1
        newx = max(min(frame.winfo_x(), clipx), self.usable_xposition)
        newy = max(min(frame.winfo_y(), clipy), self.usable_yposition)
        # TODO this is a hack
        # On Ubuntu the frame.winfo_y() is not correct
        if newx == frame.winfo_x() and newy == frame.winfo_y():
            frame.geometry(f"{new_width}x{new_height}")
        else:
            frame.geometry(f"{new_width}x{new_height}+{newx}+{newy}")

    def choose_orientation(self, ratio, decal_w, decal_h):
        use_w = self.usable_width - decal_w
        use_h = self.usable_height - decal_h
        use_ratio = use_w / use_h
        if use_ratio < ratio:
            return tk.TOP
        return tk.LEFT

    def full_screen(self, frame):
        frame.geometry(str(self))
        if songfinder.__myOs__ == "ubuntu":
            frame.attributes("-fullscreen", True)
        if songfinder.__myOs__ == "darwin":
            frame.tk.call(
                "::tk::unsupported::MacWindowStyle",
                "style",
                frame.winfo_id(),
                "plain",
                "none",
            )
            frame.update_idletasks()
            frame.wm_attributes("-fullscreen", True)
        else:
            frame.overrideredirect(1)
        logger.info(f"Fullscreen on: {self!s}")

    def __repr__(self):
        return repr(str(self))


class Screens:
    def __init__(self):
        self._screens = []
        self._maxScreens = sys.maxsize

    def center_frame(self, frame):
        if hasattr(frame, "master") and frame.master:
            for screen in self._screens:
                if screen.is_widget_in_screen(frame.master):
                    screen.center_frame(frame)
                    break
        else:
            self._screens[0].center_frame(frame)

    def resize_frame(self, frame, width, height):
        for screen in self._screens:
            if screen.is_widget_in_screen(frame):
                screen.resize_frame(frame, width, height)
                break

    def full_screen(self, frame):
        self[-1].full_screen(frame)

    def __getitem__(self, index):
        if index > len(self):
            raise IndexError
        return self._screens[(index % len(self)) % self._maxScreens]

    def __len__(self):
        if not self._screens:
            self.update()
        return len(self._screens)

    @property
    def max_screens(self):
        return self._maxScreens

    @max_screens.setter
    def max_screens(self, value):
        self._maxScreens = int(value)

    def update(self, reference_widget=None, verbose=True):
        del self._screens[:]
        try:
            monitors = screeninfo.get_monitors()
        except Exception:  # pylint: disable=broad-except
            logger.debug(traceback.format_exc())
            monitors = []
        if monitors:
            for monitor in monitors:
                self._screens.append(
                    Screen(monitor.width, monitor.height, monitor.x, monitor.y),
                )
        else:
            logger.warning("Screeninfo did not output any screen infos")
            if songfinder.__myOs__ == "windows":
                self._get_windows_screens()
            elif songfinder.__myOs__ == "ubuntu":
                self._get_linux_screens()
            elif songfinder.__myOs__ == "darwin":
                self._get_mac_os_screens()
            else:
                logger.warning("No screen found, OS is not supported.")
                self._get_linux_screens()

        if reference_widget:
            self._reorder(reference_widget)
        if verbose:
            logger.info(f"Using {len(self._screens)} screens: ")
            for screen in self._screens:
                logger.info(f"Fullscreen: {screen!s}, Usable: {screen.usable}")

    def _reorder(self, reference_widget):
        for i, screen in enumerate(self._screens):
            if screen.is_widget_in_screen(reference_widget):
                self._screens[0], self._screens[i] = self._screens[i], self._screens[0]
                logger.debug(
                    "Reordering screens: {}".format(
                        ", ".join([str(screen) for screen in self._screens]),
                    ),
                )
                return
        screens_str = "\n\t\t".join([str(screen) for screen in self._screens])
        logger.warning(
            f"Main widget did not appear to be in any screen!\n"
            f"\tWidget info:\n"
            f"\t\tgeometry: {reference_widget.winfo_geometry()}\n"
            f"\t\trootx: {reference_widget.winfo_rootx()}\n"
            f"\t\trooty: {reference_widget.winfo_rooty()}\n"
            f"\tScreens:\n\t\t{screens_str}",
        )
        # Try again with a less reliable method (comparing only screen size)
        # Will not work if several screen have the same sizes
        for i, screen in enumerate(self._screens):
            if screen.is_widget_screen_size_mine(reference_widget):
                self._screens[0], self._screens[i] = self._screens[i], self._screens[0]
                logger.debug(
                    "Reordering screens: {}".format(
                        ", ".join([str(screen) for screen in self._screens]),
                    ),
                )
                return

    def _get_linux_screens(self):
        if not self._get_xrandr_screen():
            logger.warning("Could not get screen infos with xrand method")
            if not self._get_by_top_level_screens():
                logger.warning("Could not get screen infos with TopLevel method")
                self._get_default_screen()

    def _get_windows_screens(self):
        if not self._get_windows_top_level_screens():
            logger.warning("Could not get screen infos with Windows TopLevel method")
            self._get_default_screen()

    def _get_mac_os_screens(self):
        if not self._get_xrandr_screen():
            logger.warning("Could not get screen infos with xrand method")
            if not self._get_window_server_screens():
                logger.warning("Could not get screen infos with WindowServer method")
                if not self._get_system_profiler_screens():
                    logger.warning("Could not get screen infos with Profiler method")
                    if not self._get_by_top_level_screens():
                        logger.warning(
                            "Could not get screen infos with TopLevel method",
                        )
                        self._get_default_screen()

    def _get_default_screen(self):
        self._screens.append(Screen())

    def _get_xrandr_screen(self):
        xrandr = commandLine.MyCommand("xrandr")
        try:
            xrandr.check_command()
        except exception.CommandLineError:
            return False
        else:
            code, out, err = xrandr.run(["|", "grep", "\\*", "|", "cut", "-d ", "-f4"])
            if code != 0:
                logger.warning(f"Erreur de detection des ecrans\nError {code!s}\n{err}")
                return False
            liste_res = out.strip("\n").splitlines()
            if "" in liste_res:
                liste_res.remove("")
            if not liste_res:
                liste_res = []
                code, out, err = xrandr.run(["|", "grep", "connected"])
                if code != 0:
                    logger.warning(
                        f"Erreur de detection des ecrans\nError {code!s}\n{err}",
                    )
                    return False
                line_res = out.replace("\n", "")
                deb = line_res.find("connected")
                fin = line_res.find("+", deb + 1)
                deb = line_res.rfind(" ", 0, fin)
                liste_res.append(line_res[deb + 1 : fin])

            code, out, err = xrandr.run()
            if code != 0:
                logger.warning(f"Erreur de detection des ecrans: Error {code!s}\n{err}")
                return False
            deb = 0
            for res in liste_res:
                deb = out.find(res + "+", deb)
                fin = out.find(" ", deb)
                add_screen = Screen(string_screen=out[deb:fin])
                if add_screen:
                    self._screens.append(add_screen)
                else:
                    return False
                deb = fin + 1
        return True

    def _get_windows_top_level_screens(self):
        try:
            test = tk.Toplevel()
        except tk.TclError:
            return False
        else:
            test.wm_attributes("-alpha", 0)
            test.withdraw()
            test.update_idletasks()
            test.overrideredirect(1)
            test.state("zoomed")
            test.withdraw()
            w1 = test.winfo_width()
            h1 = test.winfo_height()
            posw1 = test.winfo_x()
            posh1 = test.winfo_y()
            test.state("normal")
            test.withdraw()
            add_screen = Screen(w1, h1, posw1, posh1)
            if add_screen:
                self._screens.append(add_screen)
            else:
                return False
            # Scan for second screen
            test.overrideredirect(1)
            for decal in [
                [w, h] for w in [w1, w1 // 2, -w1 // 8] for h in [h1 // 2, h1, -h1 // 8]
            ]:
                test.geometry(f"{w1 // 8}x{h1 // 8}+{decal[0]}+{decal[1]}")
                test.update_idletasks()
                test.state("zoomed")
                test.withdraw()
                if test.winfo_x() != posw1 or test.winfo_y() != posh1:
                    new_w = test.winfo_width()
                    new_h = test.winfo_height()
                    new_pos_w = test.winfo_x()
                    new_pos_h = test.winfo_y()
                    add_screen = Screen(
                        width=new_w,
                        height=new_h,
                        xposition=new_pos_w,
                        yposition=new_pos_h,
                    )
                    if add_screen:
                        self._screens.append(add_screen)
                    else:
                        return False
                test.state("normal")
                test.withdraw()
            test.destroy()
            return True

    def _get_window_server_screens(self):
        read = commandLine.MyCommand("defaults read")
        try:
            read.check_command()
        except exception.CommandLineError:
            return False
        code, _, err = read.run(["/Library/Preferences/com.apple.windowserver.plist"])
        if code != 0:
            logger.warning(f"Erreur de detection des ecrans\nError {code!s}\n{err}")
            return False
        return False

    def _get_system_profiler_screens(self):
        system_profiler = commandLine.MyCommand("system_profiler")
        try:
            system_profiler.check_command()
        except exception.CommandLineError:
            return False
        key_word = "Resolution:"
        code, out, err = system_profiler.run(
            ["SPDisplaysDataType", "|", "grep", key_word],
        )
        if code != 0:
            logger.warning(f"Erreur de detection des ecrans\nError {code!s}\n{err}")
            return False
        width_offset = 0
        height_offset = 0
        for line in [line for line in out.split("\n") if line]:
            deb = line.find(key_word) + len(key_word)
            end = line.find("x", deb)
            width = line[deb:end].strip(" ")
            height = line[end + 1 : line.find(" ", end + 2)].strip(" ")
            add_screen = Screen(
                width=width,
                height=height,
                xposition=width_offset,
                yposition=height_offset,
            )
            if add_screen:
                self._screens.append(add_screen)
            else:
                return False
            width_offset = width
        return True

    def _get_by_top_level_screens(self):
        try:
            test = tk.Toplevel()
        except tk.TclError:
            return False
        else:
            test.wm_attributes("-alpha", 0)
            test.withdraw()
            test.update_idletasks()
            scr_w = test.winfo_screenwidth()
            scr_h = test.winfo_screenheight()
            test.destroy()
            if scr_w > 31 * scr_h // 9:
                scr_w = scr_w // 2
            elif scr_w < 5 * scr_h // 4:
                scr_h = scr_h // 2
            add_screen = Screen(width=scr_w, height=scr_h)
            if add_screen:
                self._screens.append(add_screen)
            else:
                return False
            return True


def get_ratio(ratio, default=None):
    try:
        a, b = ratio.split("/")
        value = round(int(a) / int(b), 3)
    except (ValueError, AttributeError):
        logger.log(0, traceback.format_exc())
        value = default or 16 / 9
    return value
