import codecs
import errno
import logging
import os
import random
import shutil
import tkinter as tk
import traceback

import songfinder
from songfinder import classPaths, commandLine, exception
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder import messages as tkFileDialog
from songfinder import messages as tkMessageBox
from songfinder.elements import exports
from songfinder.gui import guiHelper

logger = logging.getLogger(__name__)

try:
    from PyPDF2 import PdfReader

    HAVEPYPDF = True
except ImportError:
    logger.warning(traceback.format_exc())
    HAVEPYPDF = False


class LatexParam(tk.Frame):
    def __init__(
        self,
        fenetre,
        chants_selection,
        papa,
        no_compile,
        screens=None,
        export_settings=None,
        **kwargs,
    ):
        tk.Frame.__init__(self, fenetre, **kwargs)
        with guiHelper.SmoothWindowCreation(fenetre, screens=screens):
            self.grid()
            self.chants_selection = chants_selection
            self.papa = papa
            self.no_compile = no_compile

            if not export_settings:
                self._export_settings = settings.LATEXSETTINGS
            else:
                self._export_settings = export_settings

            self.deps = {
                "reorder": [("list", False)],
                "alphabetic_list": [("affiche_liste", True)],
                "one_song_per_page": [("list", False)],
                "transpose": [("chords", True)],
                "capo": [("chords", True)],
                "list": [("affiche_liste", True)],
                "sol_chords": [("chords", True)],
                "num_chords": [("chords", True)],
                "two_columns": [("affiche_liste", True)],
                "simple_chords": [("chords", True)],
                "keep_first": [("chords", True), ("keep_last", False)],
                "keep_last": [("chords", True), ("keep_first", False)],
                "auto_capo": [("chords", True), ("capo", True)],
                "diapo": [
                    ("reorder", False),
                    ("alphabetic_list", False),
                    ("one_song_per_page", False),
                    ("transpose", False),
                    ("list", False),
                    ("booklet", False),
                    ("two_columns", False),
                    ("capo", False),
                    ("simple_chords", False),
                    ("keep_first", False),
                    ("keep_last", False),
                    ("sol_chords", False),
                    ("num_chords", False),
                    ("affiche_liste", False),
                    ("chords", False),
                    ("keep_first", False),
                ],
            }

            self.dictParam = {
                "Reordonner les chants pour remplir les pages.": "reorder",
                "Sommaire alphabetique.": "alphabetic_list",
                "Afficher un chant par page.": "one_song_per_page",
                "Transposer les accords.": "transpose",
                "Afficher les accords.": "chords",
                "Afficher la tonalité.": "printkey",
                "Afficher le tempo.": "printtempo",
                "Liste des chants seule.": "list",
                "Accords en français.": "sol_chords",
                "Accords en degré": "num_chords",
                "Format carnet imprimable.": "booklet",
                "Refaire les sauts de lignes.": "saut_lignes",
                "Afficher le sommaire.": "affiche_liste",
                "Afficher le sommaire sur deux collones.": "two_columns",
                "Appliquer les capo.": "capo",
                "Simplifier les accords (retire sus4, Maj6 etc.).": "simple_chords",
                "Ne garder que le premier accord (Do/Mi -> Do).": "keep_first",
                "Ne garder que le second accord (Do/Mi -> Mi).": "keep_last",
                "Utiliser le capo pour avoir les accords en Do, Mi ou Sol": "auto_capo",
                "Diaporama.": "diapo",
                "Afficher la référence.": "printref",
            }
            self.dictValeurs = dict()
            self.dictButton = dict()
            self.pressed = None
            nb_boutton = len(self.dictParam)
            column_width = 5
            nb_row = (nb_boutton + 1) // 2
            for i, (param, item) in enumerate(self.dictParam.items()):
                var = tk.IntVar()
                button = tk.Checkbutton(
                    self,
                    text=param,
                    variable=var,
                    command=lambda identifyer=item: self.save(identifyer),
                )
                self.dictValeurs[param] = var
                self.dictButton[item] = button
                column_num = i // nb_row * (column_width + 1)
                button.grid(
                    row=i % nb_row,
                    column=column_num,
                    columnspan=column_width,
                    sticky="w",
                )

            self.bouton_ok = tk.Button(self, text="OK", command=self.create_files)
            self.bouton_ok.grid(
                row=nb_row,
                column=0,
                columnspan=column_width // 2,
                sticky="w",
            )
            self.bouton_ok = tk.Button(self, text="Annuler", command=self.quit)
            self.bouton_ok.grid(
                row=nb_row,
                column=column_width // 2,
                columnspan=column_width // 2,
                sticky="w",
            )

            self.maj()

    def save(self, identifyer, _event=None):
        self.pressed = identifyer
        for param, valeur in self.dictValeurs.items():
            self._export_settings.set(
                "Export_Parameters",
                self.dictParam[param],
                bool(valeur.get()),
            )
        if self._export_settings.get("Export_Parameters", "booklet") and not HAVEPYPDF:
            self._export_settings.set("Export_Parameters", "booklet", False)
            tkMessageBox.showinfo(
                "Info",
                "pypdf2 is not installed, this fonctionality is not available. "
                'Run "pip install pypdf2" to install it.',
            )

        self.maj()

    def maj(self):
        for param in self.dictParam.values():
            if self._export_settings.get("Export_Parameters", param):
                self.dictButton[param].select()
            else:
                self.dictButton[param].deselect()

        if self.pressed:
            pressed_value = self._export_settings.get("Export_Parameters", self.pressed)
            if pressed_value and self.pressed in self.deps:
                for condition in self.deps[self.pressed]:
                    self._export_settings.set(
                        "Export_Parameters",
                        condition[0],
                        condition[1],
                    )
                    if condition[1]:
                        self.dictButton[condition[0]].select()
                    else:
                        self.dictButton[condition[0]].deselect()

            for param, conditions in self.deps.items():
                for condition in conditions:
                    if condition[0] == self.pressed and condition[1] != pressed_value:
                        self.dictButton[param].deselect()
                        self._export_settings.set("Export_Parameters", param, False)

    def create_files(self):
        self._export_settings.write()
        pdf_file = CreatePDF(
            self.chants_selection,
            export_settings=self._export_settings,
        )
        pdf_file.write_files()
        close = 0
        if self.no_compile == 0:
            try:
                close = pdf_file.compile_latex()
            except exception.CommandLineError:
                tkMessageBox.showerror("Erreur", traceback.format_exc(limit=1))
        if close == 0:
            self.quit()
        else:
            self.papa.lift_latex_window()

    def quit(self):
        self.papa.close_latex_window()


class CreatePDF:
    def __init__(self, elements_selection, export_settings=None):
        if not export_settings:
            self._export_settings = settings.LATEXSETTINGS
        else:
            self._export_settings = export_settings

        if self._export_settings.get("Export_Parameters", "diapo"):
            self.__prefix = "genBeamer"
            class_type = exports.ExportBeamer
            logger.debug("Creating beamer output")
        else:
            self.__prefix = "genCarnet"
            class_type = exports.ExportLatex
            logger.debug("Creating regular latex output")

        self.__list_latex = []
        for element in elements_selection:
            newlatex = class_type(element, export_settings=self._export_settings)
            if newlatex.export_text:
                self.__list_latex.append(newlatex)

        if self._export_settings.get("Export_Parameters", "reorder"):
            self.__list_latex = reorder_latex(self.__list_latex)

        self.__pdflatex = commandLine.MyCommand("pdflatex")

        self.__chemin = os.path.join(songfinder.__settingsPath__, "latexTemplates")
        self.__songFolder = os.path.join(self.__chemin, "songs")
        self.__songList = os.path.join(self.__chemin, "listeChants.tex")
        self.__tableOfContent = os.path.join(self.__chemin, "sommaire.tex")
        self.__bookletizer = os.path.join(self.__chemin, "bookletizer.tex")
        self.__tmpName = os.path.join(self.__chemin, f"{self.__prefix}.pdf")
        logger.debug(f"Folder for latex file is '{self.__chemin}'")

        self.__check_files()

    def __get_table_of_content(self):
        text = ""
        if self._export_settings.get("Export_Parameters", "affiche_liste"):
            # Liste sommaire
            dico_titres = {
                latex_elem.title: str(self.__list_latex.index(latex_elem) + 1)
                for latex_elem in self.__list_latex
            }
            # Alphabetic
            if self._export_settings.get("Export_Parameters", "alphabetic_list"):
                list_titres = sorted(dico_titres.keys())
            else:
                list_titres = [latex_elem.title for latex_elem in self.__list_latex]

            text = "\\section*{Le Turf Auto}\n\\label{sommaire}\n"
            for title in list_titres:
                elem = self.__list_latex[int(dico_titres[title]) - 1]
                text = f"{text}\\contentsline{{section}}{{{elem.escape(title)} \\dotfill}}{{{dico_titres[title]}}}{{section.{dico_titres[title]}}}\n"

            if self._export_settings.get("Export_Parameters", "two_columns"):
                text = f"\\begin{{multicols}}{{2}}\n{text}\n\\end{{multicols}}"
        return text

    def __get_song_list(self):
        text = "\\newcommand{{\\songsPath}}{{{}}}\n".format(
            self.__songFolder.replace("\\", "/"),
        )
        if not self._export_settings.get("Export_Parameters", "list"):
            for i, latex_elem in enumerate(self.__list_latex):
                text = f'{text}\\input{{\\songsPath/"{latex_elem.nom}"}}\n'
                if (i + 1) % 99 == 0:
                    text = f"{text}\\clearpage\n"
        return text.replace("#", "\\#")

    def __get_bookletizer(self):
        # Get number of pages of original pdf file
        with open(self.__tmpName, "rb") as file_in:
            num_page = len(PdfReader(file_in).pages)
        num_page_rounded = ((num_page + 4 - 1) // 4) * 4
        logger.debug(
            f"Rounding number of PDF pages from {num_page} to {num_page_rounded}",
        )
        # Write bookletizer tex file
        return """\\documentclass[a4paper]{{article}}
\\usepackage{{pdfpages}}
\\begin{{document}}
\\includepdf[pages=-, nup=1x2, signature*={}, landscape,
angle=180, delta=0 1cm]{{{}}}
\\end{{document}}""".format(
            num_page_rounded,
            self.__tmpName.replace("\\", "/"),
        )

    def write_files(self):
        # List of song to import
        with codecs.open(self.__songList, "w", encoding="utf-8") as out:
            logger.debug(f"Writting latex song list in '{self.__songList}'")
            out.write(self.__get_song_list())
        # Songs
        if not self._export_settings.get("Export_Parameters", "list"):
            for latex_elem in self.__list_latex:
                file_name = os.path.join(self.__songFolder, f"{latex_elem.nom}.tex")
                with codecs.open(file_name, "w", encoding="utf-8") as out:
                    logger.debug(f"Writting latex song '{file_name}'")
                    out.write(latex_elem.export_text)
        # Table of content
        with codecs.open(self.__tableOfContent, "w", encoding="utf-8") as out:
            logger.debug(
                f"Writting latex table of content in '{self.__tableOfContent}'",
            )
            out.write(self.__get_table_of_content())

    def __check_files(self):
        try:
            os.makedirs(self.__chemin)
        except OSError as error:
            if error.errno == errno.EEXIST:
                pass
            else:
                raise
        try:
            logger.debug(f"Creating directory '{self.__songFolder}'")
            os.makedirs(self.__songFolder)
        except OSError as error:
            if error.errno == errno.EEXIST:
                logger.log(5, traceback.format_exc())
            else:
                raise
        source = os.path.join(songfinder.__dataPath__, "latexTemplates")
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                source_file = os.path.join(source, item)
                current_file = os.path.join(self.__chemin, item)
                if (
                    not os.path.isfile(current_file)
                    or os.stat(source_file).st_mtime > os.stat(current_file).st_mtime
                ):
                    shutil.copy(source_file, current_file)

    def __get_out_file(self):
        default_name = "turfAuto"
        default_path = classPaths.PATHS.pdf
        if not self._export_settings.get(
            "Export_Parameters",
            "reorder",
        ) and not self._export_settings.get("Export_Parameters", "alphabetic_list"):
            default_name = fonc.cree_nom_sortie()
        self.pdfName = tkFileDialog.asksaveasfilename(
            initialdir=default_path,
            initialfile=default_name,
            defaultextension=".pdf",
            filetypes=(("pdf file", "*.pdf"), ("All Files", "*.*")),
        )

    def compile_latex(self):
        self.__get_out_file()
        if not self.pdfName:
            return 1
        file_to_compile = os.path.join(self.__chemin, f"{self.__prefix}.tex")
        # Compile
        self.__pdflatex.check_command()
        os.chdir(self.__chemin)
        code, out, err = self.__pdflatex.run(
            options=["-interaction=nonstopmode", file_to_compile],
        )
        if code == 0:
            code, out, err = self.__pdflatex.run(
                options=["-interaction=nonstopmode", file_to_compile],
            )
        os.chdir(songfinder.__chemin_root__)
        if code != 0:
            tkMessageBox.showerror(
                "Attention",
                f"Error while compiling latex files.\n Error {code!s}:\n{err}",
            )
            return 1

        if not self.__is_output():
            return 1

        # Compile booklet
        if self._export_settings.get("Export_Parameters", "booklet"):
            # Write bookletizer file
            with codecs.open(self.__bookletizer, "w", encoding="utf-8") as out:
                logger.debug(f"Writting bookletizer file in '{self.__bookletizer}'")
                out.write(self.__get_bookletizer())
            os.chdir(self.__chemin)
            code, out, err = self.__pdflatex.run(
                options=["-interaction=nonstopmode", self.__bookletizer],
            )
            os.chdir(songfinder.__chemin_root__)
            if code != 0:
                tkMessageBox.showerror(
                    "Attention",
                    f"Error while compiling latex files.\n Error {code!s}:\n{err}",
                )
            else:
                self.__tmpName = os.path.join(self.__chemin, "bookletizer.pdf")

        if not self.__is_output():
            return 1

        # Move file to specified directory
        shutil.move(self.__tmpName, self.pdfName)
        logger.info("Succes creating pdf file")
        self.__clean_dir()
        self.__open_file()
        return 0

    def __is_output(self):
        if not os.path.isfile(self.__tmpName):
            tkMessageBox.showerror(
                "Attention",
                "Error while "
                f"generating latex files. Output file {self.__tmpName} does not exist",
            )
            return False
        return True

    def __open_file(self):
        if os.path.isfile(self.pdfName) and tkMessageBox.askyesno(
            "Confirmation",
            f'Le fichier "{self.pdfName}" à été créé.\nVoulez-vous l\'ouvrire ?',
        ):
            commandLine.run_file(self.pdfName)

    def __clean_dir(self):
        logger.debug(f"Cleaning latex compilation file in '{self.__chemin}'")
        list_ext = [
            ".aux",
            ".idx",
            ".ilg",
            ".ind",
            ".log",
            ".out",
            ".toc",
            ".pdf",
            ".synctex.gz",
        ]
        for root, _, files in os.walk(self.__chemin):
            for fichier in files:
                full_name = os.path.join(root, fichier)
                if fonc.get_ext(full_name) in list_ext:
                    os.remove(full_name)


def reorder_latex(list_latex):
    # Suprimme les doublons change le nombre de ligne des chant qui ont le meme
    dict_nb_ligne = dict()
    for i, elem in enumerate(list_latex):
        nb_ligne = elem.nb_line
        if nb_ligne in dict_nb_ligne:
            texte1 = elem.text
            texte2 = list_latex[dict_nb_ligne[nb_ligne]].text
            if texte1 != texte2:
                dict_nb_ligne[nb_ligne - random.randint(1, 10**7) * 10 ** (-7)] = i
        else:
            dict_nb_ligne[nb_ligne] = i
    # change les titles identiques
    titles = []
    for elem in list_latex:
        title = elem.title
        if title in titles:
            logger.warning(f'Two elements have the same title "{title}"')
            title = f"{title}~"
            elem.title = title
        titles.append(title)
    sorted_keys = sorted(dict_nb_ligne.keys(), reverse=True)
    max_line = 40
    suptitle = 4
    new_key = []
    nb = len(sorted_keys)
    in_list = []
    for i, key in enumerate(sorted_keys):
        if key > max_line:
            logger.warning(
                f'Song "{list_latex[dict_nb_ligne[key]].title}" is to big to fit one page, size: {key}, max size: {max_line}',
            )
        if i not in in_list:
            new_key.append(key)
            in_list.append(i)
            add_song(in_list, new_key, sorted_keys, max_line, suptitle, nb, key, i)

    return [list_latex[i] for i in [dict_nb_ligne[key] for key in new_key]]


def add_song(in_list, new_key, sorted_keys, max_line, suptitle, nb, nb_line, i):
    # Add song to list accrding to size of song
    previous = -1
    max_line = max_line - suptitle
    for j, key in enumerate(reversed(sorted_keys)):
        if nb_line + key > max_line or i == nb - j - 1:
            if previous != -1:
                if nb - j not in in_list:
                    new_key.append(previous)
                    in_list.append(nb - j)
                    new_nb_line = nb_line + previous
                else:
                    new_nb_line = nb_line
                    max_line = max_line + suptitle
                add_song(
                    in_list,
                    new_key,
                    sorted_keys,
                    max_line,
                    suptitle,
                    nb,
                    new_nb_line,
                    nb - j,
                )
            break
        previous = key
