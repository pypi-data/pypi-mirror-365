# cython: language_level=3 # noqa: ERA001

import codecs
import errno
import os
import traceback

import songfinder
from songfinder import classSettings as settings
from songfinder import exception
from songfinder import messages as tkFileDialog  # pylint: disable=reimported
from songfinder import messages as tkMessageBox
from songfinder import versionning as version


class Paths:
    def __init__(self, fenetre=None):
        self.fenetre = fenetre
        self.update(show_gui=False)
        self._root = None
        self._listPaths = None

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, path):
        if self._is_valid_dir(path):
            settings.GENSETTINGS.set("Paths", "data", path)
            self._root = path
            self.update(show_gui=False)
        else:
            self._root = None

    def _is_valid_dir(self, path):
        if not path:
            tkMessageBox.showerror(
                "Erreur",
                f'Le chemin "{path}" n\'est pas '
                "accesible valide, "
                "choisissez un autre répertoire.",
                parent=self.fenetre,
            )
            return False
        try:
            file_name = os.path.join(path, "test.test")
            with codecs.open(file_name, "w", encoding="utf-8"):
                pass
            os.remove(file_name)
        except OSError as error:
            if error.errno == errno.EACCES:
                tkMessageBox.showerror(
                    "Erreur",
                    f'Le chemin "{path}" n\'est pas '
                    "accesible en écriture, "
                    "choisissez un autre répertoire.",
                    parent=self.fenetre,
                )
                return False
        try:
            os.makedirs(path)
        except OSError as error:
            if error.errno == errno.EEXIST:
                pass
            else:
                raise
        return True

    def _ask_dir(self):
        tkMessageBox.showinfo(
            "Répertoire",
            "Aucun répertoire pour les chants et "
            "les listes n'est configuré.\n"
            "Dans le fenêtre suivante, selectionnez "
            "un répertoire existant ou créez en un nouveau. "
            'Par exemple, vous pouvez créer un répertoire "songfinderdata" '
            "parmis vos documents. "
            "Dans ce répertoire seront stocké : "
            "les chants, les listes, les bibles et les partitions pdf.",
            parent=self.fenetre,
        )
        for _ in range(5):
            if not self._root:
                path = tkFileDialog.askdirectory(
                    initialdir=os.path.expanduser("~"),
                    parent=self.fenetre,
                )
                if not path:
                    break
                self.root = path

    def update(self, show_gui=True):
        self._root = settings.GENSETTINGS.get("Paths", "data")
        if show_gui:
            if not self._root and not songfinder.__unittest__:
                self._ask_dir()
            if not self._root:
                msg = "No data directory configured, shuting down SongFinder."
                raise Exception(
                    msg,
                )

        self.songs = os.path.join(self._root, "songs")
        self.sets = os.path.join(self._root, "sets")
        self.bibles = os.path.join(self._root, "bibles")
        self.pdf = os.path.join(self._root, "pdf")
        self.preach = os.path.join(self._root, "preach")
        self._listPaths = [self.songs, self.sets, self.bibles, self.pdf, self.preach]

        self._create_sub_dirs()

    def _create_sub_dirs(self):
        if self._root:
            for path in self._listPaths:
                try:
                    os.makedirs(path)
                except OSError as error:
                    if error.errno == errno.EEXIST:
                        pass
                    else:
                        raise

    def sync(self, screens=None, update_data=None):
        scm = settings.GENSETTINGS.get("Parameters", "scm")
        if settings.GENSETTINGS.get("Parameters", "sync") and not os.path.isdir(
            os.path.join(self._root, f".{scm}"),
        ):
            if tkMessageBox.askyesno(
                "Dépot",
                "Voulez-vous définir le dépot de chants et listes ?\n"
                f'Ceci supprimera tout documents présent dans "{self._root}"',
            ):
                try:
                    version.AddRepo(self, scm, screens, update_data)
                except exception.CommandLineError:
                    tkMessageBox.showerror("Erreur", traceback.format_exc(limit=1))
            else:
                settings.GENSETTINGS.set("Parameters", "sync", False)


PATHS = Paths()
