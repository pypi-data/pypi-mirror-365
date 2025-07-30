import _tkinter
import contextlib
import logging
import traceback
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox

import songfinder

logger = logging.getLogger(__name__)


def showerror(title, message, **kwargs):
    if songfinder.__unittest__ is True:
        logger.warning(message)
    else:
        logger.error(f"Error {title}: {message}")
        logger.error(f"{traceback.format_exc()}")
        with contextlib.suppress(_tkinter.TclError):
            tkMessageBox.showerror(title, message, **kwargs)


def showinfo(title, message, **kwargs):
    if songfinder.__unittest__ is True:
        logger.warning(message)
    else:
        logger.info(f"Info {title}: {message}")
        with contextlib.suppress(_tkinter.TclError):
            tkMessageBox.showinfo(title, message, **kwargs)


def askyesno(title, message):
    if songfinder.__unittest__ is True:
        logger.warning(message)
        return False
    try:
        return tkMessageBox.askyesno(title, message)
    except _tkinter.TclError:
        print(f"Askyesno {title}: {message}")  # noqa: T201
        answer = None
        while answer not in ["y", "Y", "n", "N"]:
            answer = input(f"{message} (y/n)")
            if answer in ["y", "Y"]:
                return True
            if answer in ["n", "N"]:
                return False


def askdirectory(**kwargs):
    if songfinder.__unittest__ is True:
        logger.warning("askdirectory")
        return None
    try:
        return tkFileDialog.askdirectory(**kwargs)
    except _tkinter.TclError:
        return None


def askopenfilename(**kwargs):
    if songfinder.__unittest__ is True:
        logger.warning("askopenfilename")
        return None
    try:
        return tkFileDialog.askopenfilename(**kwargs)
    except _tkinter.TclError:
        return None


def askopenfilenames(**kwargs):
    if songfinder.__unittest__ is True:
        logger.warning("askopenfilenames")
        return None
    try:
        return tkFileDialog.askopenfilenames(**kwargs)
    except _tkinter.TclError:
        return None


def asksaveasfilename(**kwargs):
    if songfinder.__unittest__ is True:
        logger.warning("asksaveasfilename")
        return None
    try:
        return tkFileDialog.asksaveasfilename(**kwargs)
    except _tkinter.TclError:
        return None
