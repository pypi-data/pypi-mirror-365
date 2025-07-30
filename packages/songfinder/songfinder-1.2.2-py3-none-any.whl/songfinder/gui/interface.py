import logging
import os
import sys
import tkinter as tk
import tkinter.font as tkFont
import traceback
from tkinter import ttk

import songfinder
from songfinder import (
    __version__,
    background,
    classPaths,
    commandLine,
    dataBase,
    diapoList,
    diapoPreview,
    elements,
    exception,
    latex,
)
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder import messages as tkMessageBox
from songfinder import versionning as version
from songfinder.gui import (
    diapoListGui,
    editGui,
    guiHelper,
    presentGui,
    searchGui,
    selectionListGui,
    simpleProgress,
)
from songfinder.gui import preferences as pref

logger = logging.getLogger(__name__)

WIDTH_THRESHOLD_LOW = 1000
WIDTH_THRESHOLD_HIGH = 2000


class Interface(tk.Frame):
    def __init__(self, window, screens=None, file_in=None, **kwargs):
        tk.Frame.__init__(self, window, **kwargs)

        self._screens = screens
        self._window = window

        if screens[0].width < WIDTH_THRESHOLD_LOW:
            font_size = 8
        elif screens[0].width < WIDTH_THRESHOLD_HIGH:
            font_size = 9
        else:
            font_size = 10

        logger.debug(f"FontSize {font_size}")

        for font in ["TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont"]:
            tkFont.nametofont(font).configure(size=font_size)

        mainmenu = tk.Menu(window)  ## Barre de menu
        menu_fichier = tk.Menu(mainmenu)  ## tk.Menu fils menuExample
        menu_fichier.add_command(
            label="Mettre à jour la base de données",
            command=self.update_data,
        )
        menu_fichier.add_command(
            label="Utiliser les bases de données additionelles",
            command=self._add_remove_data_bases,
        )
        menu_fichier.add_command(
            label="Mettre à jour SongFinder",
            command=self._update_song_finder,
        )
        menu_fichier.add_command(label="Quitter", command=self.quit)
        mainmenu.add_cascade(label="Fichier", menu=menu_fichier)

        menu_editer = tk.Menu(mainmenu)
        menu_editer.add_command(label="Paramètres généraux", command=self._param_gen)
        menu_editer.add_command(
            label="Paramètres de présentation",
            command=self._param_pres,
        )
        mainmenu.add_cascade(label="Paramètres", menu=menu_editer)

        menu_sync = tk.Menu(mainmenu)
        menu_sync.add_command(label="Envoyer les chants", command=self._send_songs)
        menu_sync.add_command(label="Recevoir les chants", command=self._receive_songs)
        mainmenu.add_cascade(label="Réception/Envoi", menu=menu_sync)

        menu_latex = tk.Menu(mainmenu)
        menu_latex.add_command(label="Générer un fichier PDF", command=self._quick_pdf)
        menu_latex.add_command(
            label="Générer les fichiers Latex",
            command=lambda no_compile=1: self._write_latex(no_compile),
        )
        menu_latex.add_command(
            label="Compiler les fichiers Latex",
            command=self._compile_latex,
        )
        mainmenu.add_cascade(label="PDF", menu=menu_latex)

        menu_help = tk.Menu(mainmenu)
        menu_help.add_command(label="Version", command=self._show_version)
        menu_help.add_command(label="README", command=self._show_readme)
        menu_help.add_command(label="Documentation", command=self._show_doc)
        mainmenu.add_cascade(label="Aide", menu=menu_help)

        window.config(menu=mainmenu)

        self._generalParamWindow = None
        self._presentationParamWindow = None
        self._latexWindow = None
        self._scrollWidget = None

        self._databaseAreMerged = False

        left_panel = ttk.Frame(window)
        search_panel = ttk.Frame(left_panel)
        list_panel = ttk.Frame(left_panel)
        edit_panel = ttk.Frame(window)
        right_panel = ttk.Frame(window)
        expand_panel = ttk.Frame(window)
        present_panel = ttk.Frame(left_panel)
        presented_list_panel = ttk.Frame(window)
        preview_panel = ttk.Frame(presented_list_panel)
        list_gui_panel = ttk.Frame(presented_list_panel)

        search_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        list_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        left_panel.pack(side=tk.LEFT, fill=tk.BOTH)
        edit_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        right_panel.pack(side=tk.LEFT, fill=tk.X)
        expand_panel.pack(side=tk.LEFT, fill=tk.X)
        present_panel.pack(side=tk.TOP, fill=tk.X)
        preview_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        list_gui_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        #######

        ####### Path definition
        classPaths.PATHS.update()
        try:
            scm = settings.GENSETTINGS.get("Parameters", "scm")
            self._repo = version.Repo(classPaths.PATHS.root, scm, self, screens=screens)
        except exception.CommandLineError:
            logger.exception(traceback.format_exc())
            tkMessageBox.showerror("Erreur", traceback.format_exc(limit=1))
        self._database = dataBase.DataBase()

        self._diapo_list = diapoList.DiapoList()

        # Modular panels
        self._editGui = editGui.EditGui(
            edit_panel,
            database=self._database,
            screens=screens,
            diapo_list=self._diapo_list,
        )
        self._selectionListGui = selectionListGui.SelectionListGui(
            list_panel,
            diapo_list=self._diapo_list,
        )
        self._searchGui = searchGui.SearchGui(
            search_panel,
            self._database,
            screens=screens,
            diapo_list=self._diapo_list,
        )
        self._presentGui = presentGui.PresentGui(
            present_panel,
            self._diapo_list,
            screens=screens,
        )
        self._diapo_listGui = diapoListGui.DiapoListGui(
            list_gui_panel,
            self._diapo_list,
        )
        self._previews = diapoPreview.Preview(
            preview_panel,
            self._diapo_list,
            screens=screens,
        )
        #######

        # Modular panels bindings
        self._editGui.bind_save_callback(self._reset_text_and_cache)
        self._editGui.bind_set_song(self._searchGui.set_song)
        self._selectionListGui.bind_printer(self._editGui.printer)
        self._selectionListGui.bind_searcher(self._searchGui.searcher.search)
        self._searchGui.bind_printer(self._editGui.printer)
        self._searchGui.bind_add_element_to_selection(
            self._selectionListGui.add_element_to_selection,
        )
        self._presentGui.bind_element_to_present(self._editGui.printed_element)
        self._presentGui.bind_list_to_present(self._selectionListGui.list)
        self._presentGui.bind_ratio_callback(self._previews.update_previews)

        self._diapo_listGui.bind_callback(self._previews.printer, "self._previews")
        self._diapo_list.bind_load_callback(self._diapo_listGui.write)
        self._diapo_list.bind_load_callback(self._previews.printer)
        self._diapo_list.bind_is_load_allowed(self._presentGui.present_is_off)
        self._diapo_list.bind_frame_event(window)
        self._diapo_list.bind_gui_update(self._previews.printer)
        self._diapo_list.bind_gui_update(self._diapo_listGui.update_selected)
        #######

        # List present panel
        #######
        self._expandInLook = "<\n" * 15
        self._expandOutLook = ">\n" * 15
        preview_expanded = False
        edit_expanded = False
        expand_gui_button = tk.Button(
            expand_panel,
            text=self._expandOutLook,
            command=lambda name="preview": self._expand_gui(name),
        )
        expand_edit_button = tk.Button(
            expand_panel,
            text=self._expandOutLook,
            command=lambda name="edit": self._expand_gui(name),
        )

        expand_gui_button.pack(side=tk.TOP, fill=tk.X)

        self._expandables = {
            "preview": {
                "isExpanded": preview_expanded,
                "panel": presented_list_panel,
                "button": expand_gui_button,
            },
            "edit": {
                "isExpanded": edit_expanded,
                "panel": edit_panel,
                "button": expand_edit_button,
            },
        }

        self.bind_all("<Enter>", self._bound_to_mousewheel)
        self.bind_all("<Leave>", self._unbound_to_mousewheel)

        # Open file in argument
        if file_in:
            file_in = os.path.abspath(file_in)
            ext = fonc.get_ext(file_in)
            if ext in settings.GENSETTINGS.get("Extentions", "song"):
                element = elements.Chant(file_in)
                if element.exist():
                    self._searchGui.set_song(element)
                    self._editGui.printer(to_print_dict={element: 100})
            elif ext in settings.GENSETTINGS.get("Extentions", "liste"):
                self._selectionListGui.set_list(file_in)

        if settings.GENSETTINGS.get("Parameters", "autoexpand"):
            self._expand_gui("preview", resize=False)
            self._diapo_listGui.write()

        if settings.GENSETTINGS.get("Parameters", "autoreceive"):
            self._receive_songs(show_gui=False)

    def _add_remove_data_bases(self):
        if self._databaseAreMerged:
            self._database.remove_extra_databases()
            self._databaseAreMerged = False
            self.update_data()
        else:
            jemaf_path = settings.GENSETTINGS.get("Paths", "jemaf")
            shir_path = settings.GENSETTINGS.get("Paths", "shir")
            top_chretiens_path = settings.GENSETTINGS.get("Paths", "topchretiens")
            logger.info(f'Adding "{jemaf_path}" to database.')
            logger.info(f'Adding "{shir_path}" to database.')
            logger.info(f'Adding "{top_chretiens_path}" to database.')
            jemaf_data_base = dataBase.DataBase(jemaf_path)
            shir_data_base = dataBase.DataBase(shir_path)
            top_chretiens_data_base = dataBase.DataBase(top_chretiens_path)
            self._database.merge(
                [jemaf_data_base, shir_data_base, top_chretiens_data_base],
            )
            self._databaseAreMerged = True

    def __sync_path__(self):
        # Workaround should reorganize path class
        classPaths.PATHS.sync(self._screens, self.update_data)

    def _expand_gui(self, name, resize=True):
        if self._expandables[name]["isExpanded"]:
            self._expandables[name]["panel"].pack_forget()
            self._expandables[name]["button"]["text"] = self._expandOutLook
            self._expandables[name]["isExpanded"] = False
        else:
            self._expandables[name]["panel"].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
            self._expandables[name]["button"]["text"] = self._expandInLook
            self._expandables[name]["isExpanded"] = True
            self._previews.update_previews(delay=False)
        if resize:
            self._resize_main_window()

    def _resize_main_window(self):
        self._window.update()
        width = max(self._window.winfo_width(), self._window.winfo_reqwidth())
        height = max(self._window.winfo_height(), self._window.winfo_reqheight())
        self._screens.resize_frame(self._window, width, height)

    def close_latex_window(self):
        if self._latexWindow:
            self._latexWindow.destroy()
            self._latexWindow = None

    def lift_latex_window(self):
        guiHelper.up_front(self._latexWindow)

    def _reset_text_and_cache(self):
        if self._searchGui:
            self._searchGui.reset_cache()
            self._searchGui.reset_text()
        if self._selectionListGui:
            self._selectionListGui.reset_text()
        if self._diapo_list is not None:
            self._diapo_list.reset_text()
        self._diapo_listGui.write()
        self._previews.printer()

    def _bound_to_mousewheel(self, event):
        self._scrollWidget = event.widget
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, _event):
        self._scrollWidget = None
        self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        try:
            self._scrollWidget.focus_set()
            self._scrollWidget.yview_scroll(-1 * (event.delta // 8), "units")
        except AttributeError:
            pass

    def update_data(self, show_gui=True):
        if show_gui:
            progress_bar = simpleProgress.SimpleProgress(
                "Mise à jour de la base de données",
                screens=self._screens,
            )
            total = len(self._database) if self._database else 1000
            progress_bar.start(total=total)
            self._database.update(callback=progress_bar.update)
        else:
            self._database.update()
        self._selectionListGui.get_set_list()
        self._searchGui.reset_text()
        self._selectionListGui.reset_text()
        self._searchGui.reset_cache()
        self._editGui.reset_text()
        self._editGui.printer()
        if show_gui:
            progress_bar.stop()
            tkMessageBox.showinfo(
                "Confirmation",
                f"La base de donnée a été mise à jour: {len(self._database)} chants.",
            )

    def quit(self):
        try:
            settings.GENSETTINGS.write()
            settings.PRESSETTINGS.write()
            settings.LATEXSETTINGS.write()
        except Exception:  # pylint: disable=broad-except
            logger.exception(traceback.format_exc())
            tkMessageBox.showerror(
                "Attention",
                f"Error while writting settings:\n{traceback.format_exc(limit=1)}",
            )
        try:
            background.clean_disk_cache_image()
        except Exception:  # pylint: disable=broad-except
            logger.exception(traceback.format_exc())
            tkMessageBox.showerror(
                "Attention",
                f"Error in clean cache:\n{traceback.format_exc(limit=1)}",
            )
        self.destroy()
        sys.exit()

    def _param_gen(self):
        if self._generalParamWindow:
            self._generalParamWindow.close()
            self._generalParamWindow = None
        self._generalParamWindow = pref.ParamGen(self, screens=self._screens)

    def _param_pres(self):
        if self._presentationParamWindow:
            self._presentationParamWindow.close()
            self._presentationParamWindow = None
        self._presentationParamWindow = pref.ParamPres(self, screens=self._screens)
        self._searchGui.reset_diapos()
        self._selectionListGui.reset_diapos()

    def _write_latex(self, no_compile=0):
        chants_selection = self._selectionListGui.list()
        if chants_selection == []:
            tkMessageBox.showerror("Erreur", "Il n'y a aucun chants dans la liste.")
        elif len(set(chants_selection)) != len(chants_selection):
            tkMessageBox.showerror(
                "Erreur",
                "Certains chants apparaissent plusieurs fois dans la liste. Ceci est proscrit",
            )
        else:
            if self._latexWindow:
                self._latexWindow.destroy()
                self._latexWindow = None
            self._latexWindow = tk.Toplevel()
            self._latexWindow.title("Paramètres Export PDF")
            self.latex_param = latex.LatexParam(
                self._latexWindow,
                chants_selection,
                self,
                no_compile,
                screens=self._screens,
            )

    def _compile_latex(self):
        latex_compiler = latex.CreatePDF([])
        latex_compiler.compile_latex()

    def _quick_pdf(self):
        self._write_latex()

    def _show_doc(self):
        doc_path = os.path.join(songfinder.__dataPath__, "documentation")
        doc_file = os.path.join(doc_path, f"{songfinder.__appName__}.pdf")
        if not os.path.isfile(doc_file):
            file_to_compile = os.path.join(doc_path, f"{songfinder.__appName__}.tex")
            if os.path.isfile(file_to_compile):
                os.chdir(doc_path)
                pdflatex = commandLine.MyCommand("pdflatex")
                pdflatex.check_command()
                code, _, err = pdflatex.run(
                    options=[fonc.get_file_name_ext(file_to_compile)],
                    timeOut=10,
                )
                if code == 0:
                    code, _, err = pdflatex.run(
                        options=[fonc.get_file_name_ext(file_to_compile)],
                        timeOut=10,
                    )
                os.chdir(songfinder.__chemin_root__)
                if code != 0:
                    tkMessageBox.showerror(
                        "Attention",
                        f"Error while compiling latex files. Error {code!s}:\n{err}",
                    )
        if os.path.isfile(doc_file):
            commandLine.run_file(doc_file)
        else:
            tkMessageBox.showerror(
                "Attention",
                "Impossible d'ouvrire "
                f'la documentation, le fichier "{doc_file}" n\'existe pas.',
            )

    def _show_readme(self):
        file_name = "README.md"
        paths_readme = [
            os.path.join(songfinder.__dataPath__, "documentation", file_name),
            os.path.join(file_name),
        ]
        found = False
        for readme_file in paths_readme:
            if os.path.isfile(readme_file):
                commandLine.run_file(readme_file)
                found = True
                break
        if not found:
            tkMessageBox.showerror(
                "Attention",
                "Impossible d'ouvrire "
                'le fichier README, le fichier "{}" n\'existe pas.'.format(
                    ", ".join(paths_readme),
                ),
            )

    def _show_version(self):
        tkMessageBox.showinfo(
            f"Songfinder Version {__version__}",
            f"Songfinder Version {__version__}.",
        )

    def _send_songs(self, show_gui=True):
        if self._repo.send(show_gui=show_gui) == 0:
            self.update_data(show_gui=show_gui)

    def _receive_songs(self, show_gui=True):
        if self._repo.receive(show_gui=show_gui) == 0:
            self.update_data(show_gui=show_gui)

    def _update_song_finder(self):
        pip = commandLine.MyCommand(sys.executable)
        try:
            pip.check_command()
        except exception.CommandLineError:
            logger.exception(traceback.format_exc())
            tkMessageBox.showerror("Erreur", traceback.format_exc(limit=1))
        else:
            job = simpleProgress.UpdateJob(
                pip.run,  # Pass function positionally
                kwargs={  # Pass pip.run arguments via kwargs
                    "options": [
                        "-m",
                        "pip",
                        "install",
                        f"{songfinder.__appName__}[gui]",
                        "--upgrade",
                    ],
                    "timeOut": 120,
                },
            )
            progress_bar = simpleProgress.Progress(
                "Mise à jour de SongFinder",
                job,
                screens=self._screens,
            )
            progress_bar.start()
