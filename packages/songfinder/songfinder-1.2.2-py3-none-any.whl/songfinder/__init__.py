import codecs
import datetime
import errno
import logging
import os
import platform
import sys

from songfinder import logger_formatter

logger = logging.getLogger(__name__)

__version__ = "1.2.2"
__author__ = "danbei"
__appName__ = "songfinder"

# Define root diretcory
__chemin_root__ = os.getcwd()

# Define data directory
__dataPath__ = os.path.join(os.path.split(__file__)[0], "data")


def _is_portable():
    # Check if installation is portable
    is_portable = os.path.isfile(os.path.join(__chemin_root__, "PORTABLE"))
    try:
        with codecs.open(
            os.path.join(__chemin_root__, "test.test"),
            "w",
            encoding="utf-8",
        ):
            pass
        os.remove(os.path.join(__chemin_root__, "test.test"))
    except OSError as error:
        if error.errno == errno.EACCES:
            is_portable = False
        else:
            raise
    return is_portable


__portable__ = _is_portable()

# Define Settings directory
if __portable__:
    __settingsPath__ = os.path.join(__chemin_root__, f".{__appName__}", "")
else:
    __settingsPath__ = os.path.join(os.path.expanduser("~"), f".{__appName__}", "")


def _logger_configuration():
    # Set logger configuration
    log_formatter = logger_formatter.MyFormatter()
    console_handler = logging.StreamHandler(sys.stdout)
    log_directory = os.path.join(__settingsPath__, "logs")
    log_file = os.path.join(
        log_directory,
        f"{datetime.datetime.now().strftime('%Y-%m-%d-%Hh%Mm%Ss')}.log",
    )
    try:
        os.makedirs(log_directory)
    except OSError as error:
        if error.errno == errno.EEXIST:
            pass
        else:
            raise
    file_handler = logging.FileHandler(log_file)
    console_handler.setFormatter(log_formatter)
    file_handler.setFormatter(log_formatter)
    logging.root.addHandler(console_handler)
    logging.root.addHandler(file_handler)

    logging.root.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    return console_handler


__consoleHandler__ = _logger_configuration()


def _get_os():
    system = platform.system()
    if system == "Linux":
        platform_info = platform.platform().split("-")
        out_os = "ubuntu" if platform_info[0] == "Ubuntu" else "linux"
    elif system == "Windows":
        out_os = "windows"
    elif system == "Darwin":
        out_os = "darwin"
    else:
        out_os = "notSupported"
        logger.info(f"Your `{system}` isn't a supported operatin system`.")
    return out_os


__myOs__ = _get_os()

# Define constant for 64-bit architecture check
MAX_SIZE_64BIT = 9223372036854775807

__arch__ = "x64" if sys.maxsize == MAX_SIZE_64BIT else "x86"
__dependances__ = f"deps-{__arch__}"
__unittest__ = False


def _gui(fenetre, file_in=None):
    # Creat main window and splash icon
    import traceback

    from songfinder.gui import guiHelper, screen, splash

    screens = screen.Screens()
    with guiHelper.SmoothWindowCreation(fenetre, screens):
        screens.update(reference_widget=fenetre)

        with splash.Splash(fenetre, os.path.join(__dataPath__, "icon.png"), screens):
            # Compile cython file and cmodules
            if not __portable__:
                try:
                    import subprocess

                    python = sys.executable
                    if python:
                        command = [
                            python,
                            os.path.join(os.path.split(__file__)[0], "setup_cython.py"),
                            "build_ext",
                            "--inplace",
                        ]
                        proc = subprocess.Popen(
                            command,
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        out, err = proc.communicate()
                        try:
                            logger.debug(out.decode())
                            logger.debug(err.decode())
                        except UnicodeDecodeError:
                            logger.debug(out)
                            logger.debug(err)
                except Exception:  # pylint: disable=broad-except
                    logger.warning(traceback.format_exc())

            from songfinder.gui import interface

            # Set bar icon
            try:
                from PIL import ImageTk

                if os.name == "posix":
                    img = ImageTk.PhotoImage(
                        file=os.path.join(__dataPath__, "icon.png"),
                    )
                    fenetre.tk.call("wm", "iconphoto", fenetre._w, img)  # pylint: disable=protected-access # noqa: SLF001
                else:
                    fenetre.iconbitmap(os.path.join(__dataPath__, "icon.ico"))
            except Exception:  # pylint: disable=broad-except
                logger.warning(traceback.format_exc())
            if file_in:
                file_in = file_in[0]
            song_finder = interface.Interface(fenetre, screens=screens, file_in=file_in)
            fenetre.title("SongFinder")
            fenetre.protocol("WM_DELETE_WINDOW", song_finder.quit)

    song_finder.__sync_path__()  # TODO This is a hack
    fenetre.mainloop()


def _song2markdown(file_in, file_out):
    from songfinder import fileConverter

    converter = fileConverter.Converter()
    converter.make_sub_dir_on()
    converter.markdown(file_in, file_out)


def _song2latex(file_in, file_out):
    from songfinder import fileConverter

    converter = fileConverter.Converter()
    converter.make_sub_dir_on()
    converter.latex(file_in, file_out)


def _song2html(file_in, file_out):
    from songfinder import fileConverter

    converter = fileConverter.Converter()
    converter.make_sub_dir_off()
    converter.html(file_in, file_out)


def _add_info_from(database_names):
    from songfinder import dataBase

    local_data = dataBase.DataBase()
    local_data.add_info_from(database_names)


def _parse_args():
    import argparse

    arg_parser = argparse.ArgumentParser()
    arg_parser = argparse.ArgumentParser(
        description=f"{__appName__} v{__version__}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "-f",
        "--file",
        nargs=1,
        metavar=("inputFile",),
        help="Song file or set file to open",
    )

    arg_parser.add_argument(
        "-m",
        "--songtomarkdown",
        nargs=2,
        metavar=("song[File/Dir]", "markdown[File/Dir]"),
        help="Convert song file (xml or chordpro) files to markdown file",
    )

    arg_parser.add_argument(
        "-L",
        "--songtolatex",
        nargs=2,
        metavar=("song[File/Dir]", "latex[File/Dir]"),
        help="Convert song file (xml or chordpro) files to latex file",
    )

    arg_parser.add_argument(
        "-t",
        "--songtohtml",
        nargs=2,
        metavar=("song[File/Dir]", "html[File/Dir]"),
        help="Convert song file (xml or chordpro) files to html file",
    )

    arg_parser.add_argument(
        "-a",
        "--addinfo",
        nargs=1,
        metavar=("database_names"),
        help="Scan database for songs additional songs infos",
    )

    arg_parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="Print songfinder version",
    )

    level_choices = [
        logging.getLevelName(x)
        for x in range(1, 101)
        if not logging.getLevelName(x).startswith("Level")
    ]

    arg_parser.add_argument(
        "-l",
        "--loglevel",
        choices=level_choices,
        default="INFO",
        help="Increase output verbosity",
    )

    return arg_parser.parse_args()


def song_finder_main():
    args = _parse_args()
    numeric_level = logging.getLevelName(args.loglevel)
    __consoleHandler__.setLevel(numeric_level)

    logger.info(f"{__appName__} v{__version__}")
    platform_infos = [
        platform.node(),
        platform.python_implementation(),
        platform.python_version(),
        platform.python_compiler(),
        platform.platform(),
        platform.processor(),
    ]
    logger.info(", ".join(platform_infos))

    logger.info(f'Settings are in "{__settingsPath__}"')
    logger.info(f'Datas are in "{__dataPath__}"')
    logger.info(f'Root dir is "{__chemin_root__}"')

    if __portable__:
        logger.info("Portable version")
    else:
        logger.info("Installed version")
    if args.songtomarkdown:
        _song2markdown(*args.songtomarkdown)
    elif args.songtolatex:
        _song2latex(*args.songtolatex)
    elif args.songtohtml:
        _song2html(*args.songtohtml)
    elif args.addinfo:
        _add_info_from(args.addinfo)
    elif args.version:
        print(f"{__appName__} v.{__version__} by {__author__}")  # noqa: T201
    else:
        import tkinter as tk
        import traceback

        from songfinder import messages as tkMessageBox

        fenetre = tk.Tk()
        dpi_value = fenetre.winfo_fpixels("1i")
        logger.info(f"Screen DPI: {dpi_value}")
        fenetre.tk.call("tk", "scaling", "-displayof", ".", dpi_value / 72.0)

        # Override tkinter methode to raise exception occuring in tkinter callbacks
        def report_callback_exception():
            tkMessageBox.showerror("Erreur", traceback.format_exc(limit=1))

        tk.Tk.report_callback_exception = report_callback_exception

        try:
            _gui(fenetre, file_in=args.file)
        except SystemExit:
            raise
        except:
            if not getattr(sys, "frozen", False):
                tkMessageBox.showerror("Erreur", traceback.format_exc(limit=1))
            logger.critical(traceback.format_exc())
            raise


if __name__ == "__main__":
    song_finder_main()
