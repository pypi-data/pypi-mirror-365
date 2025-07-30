import contextlib
import errno
import tkinter as tk
from tkinter import ttk

from songfinder import classSettings as settings
from songfinder import elements, gestchant
from songfinder import fonctions as fonc
from songfinder import messages as tkMessageBox
from songfinder.gui import guiHelper, inputFrame

WIDTH_THRESHOLD = 2000


class EditGui:
    def __init__(
        self,
        frame,
        database=None,
        screens=None,
        printer_callback=None,
        save_callback=None,
        new_callback=None,
        diapo_list=None,
    ):
        self._database = database
        self._screens = screens
        self._printerCallback = printer_callback
        self._saveCallback = save_callback
        self._setSong = new_callback
        self._diapo_list = diapo_list

        button_sub_panel = ttk.Frame(frame)
        title_sub_panel = ttk.Frame(frame)
        chords_sub_panel = ttk.Frame(frame)
        supinfo_sub_panel = ttk.Frame(frame)
        tags_sub_panel = ttk.Frame(frame)
        text_sub_panel = ttk.Frame(frame)

        button_sub_panel.pack(side=tk.TOP)
        title_sub_panel.pack(side=tk.TOP, fill=tk.X)
        chords_sub_panel.pack(side=tk.TOP, fill=tk.X)
        supinfo_sub_panel.pack(side=tk.TOP, fill=tk.X)
        tags_sub_panel.pack(side=tk.TOP, fill=tk.X)
        text_sub_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self._newSongWindow = None
        self._printedElement = None

        self._inputTitle = inputFrame.TextField(
            title_sub_panel,
            width=20,
            text="Titre :",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputAuthor = inputFrame.TextField(
            title_sub_panel,
            width=10,
            text="Auteur :",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputKey = inputFrame.TextField(
            chords_sub_panel,
            width=3,
            text="Tonalité: ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputTranspose = inputFrame.TextField(
            chords_sub_panel,
            width=3,
            text="Transposition: ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputCapo = inputFrame.TextField(
            chords_sub_panel,
            width=3,
            text="Capo: ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputTempo = inputFrame.TextField(
            chords_sub_panel,
            width=3,
            text="Tempo: ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._input_song_book = inputFrame.TextField(
            supinfo_sub_panel,
            width=3,
            text="Receuil: ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputNumCCLI = inputFrame.TextField(
            supinfo_sub_panel,
            width=3,
            text="Num (CCLI): ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputNumTurf = inputFrame.TextField(
            supinfo_sub_panel,
            width=3,
            text="Num (Turf): ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputNumCustom = inputFrame.TextField(
            supinfo_sub_panel,
            width=3,
            text="Num (Custom): ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )
        self._inputTags = inputFrame.TextField(
            tags_sub_panel,
            width=30,
            text="Tags: ",
            packing=tk.LEFT,
            state=tk.DISABLED,
        )

        self._buttonSaveSong = tk.Button(
            button_sub_panel,
            text="Sauver",
            command=self._save_song,
            state=tk.DISABLED,
        )
        button_create_song = tk.Button(
            button_sub_panel,
            text="Créer un nouveau chant",
            command=self._create_new_song_window,
        )
        self._buttonCreateNewVersion = tk.Button(
            button_sub_panel,
            text="Créer une autre version du chant",
            command=lambda: self._create_new_song_window(self._printedElement),
        )

        width = 56 if screens and screens[0].width > WIDTH_THRESHOLD else 48
        height = 46 if screens and screens[0].height > WIDTH_THRESHOLD else 32

        self._songTextField = tk.Text(
            text_sub_panel,
            width=width,
            height=height,
            undo=True,
            state=tk.DISABLED,
        )
        self._songTextFieldScroller = tk.Scrollbar(
            text_sub_panel,
            command=self._songTextField.yview,
        )
        self._songTextField["yscrollcommand"] = self._songTextFieldScroller.set

        self._inputTitle.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputAuthor.pack(side=tk.LEFT, fill=tk.X, expand=1)

        self._inputKey.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputTranspose.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputCapo.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputTempo.pack(side=tk.LEFT, fill=tk.X, expand=1)

        self._input_song_book.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputNumCCLI.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputNumTurf.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputNumCustom.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self._inputTags.pack(side=tk.LEFT, fill=tk.X, expand=1)

        self._buttonSaveSong.pack(side=tk.LEFT)
        button_create_song.pack(side=tk.LEFT)
        self._buttonCreateNewVersion.pack(side=tk.LEFT)

        self._songTextField.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self._songTextFieldScroller.pack(side=tk.LEFT, fill=tk.Y)

        self._inputFieldsList = [
            self._inputTitle,
            self._inputAuthor,
            self._inputTranspose,
            self._inputCapo,
            self._inputKey,
            self._inputTempo,
            self._input_song_book,
            self._inputNumCCLI,
            self._inputNumTurf,
            self._inputNumCustom,
            self._inputTags,
        ]

        for field in self._inputFieldsList:
            field.bind("<KeyRelease>", self._change_song_state)
        # Edition de la liste de selection
        frame.bind_all("<Control-s>", self._save_song)
        self._songTextField.bind("<KeyRelease>", self._change_song_state)
        frame.bind_class("Text", "<Control-a>", self._select_all_text)

    def _printer_off(self):
        guiHelper.change_text(self._songTextField, "")
        self._songTextField["state"] = tk.DISABLED
        for field in self._inputFieldsList:
            guiHelper.change_text(field, "")
            field.state = tk.DISABLED

    def _print_on(self):
        self._songTextField["state"] = tk.NORMAL
        for field in self._inputFieldsList:
            field.state = tk.NORMAL

    def _update_content(self, element=None):
        if not element:
            element = self._printedElement
        guiHelper.change_text(self._songTextField, element.text or "")
        guiHelper.change_text(self._inputTitle, element.title or "")
        guiHelper.change_text(self._inputAuthor, element.author or "")
        guiHelper.change_text(self._inputTranspose, element.transpose or "")
        guiHelper.change_text(self._inputCapo, element.capo or "")
        guiHelper.change_text(self._inputKey, element.key or "")
        guiHelper.change_text(self._inputTempo, element.tempo or "")
        guiHelper.change_text(self._input_song_book, element.song_book or "")
        guiHelper.change_text(self._inputNumCCLI, element.nums.get("hymn") or "")
        guiHelper.change_text(self._inputNumTurf, element.nums.get("turf") or "")
        guiHelper.change_text(self._inputNumCustom, element.nums.get("custom") or "")
        guiHelper.change_text(self._inputTags, element.tags or "")

    def _save_song(self, _event=None):
        if self._database and self._printedElement.etype == "song":
            cursor_position = self._songTextField.index("insert")
            scroll_position = self._songTextFieldScroller.get()[0]

            # TODO a retirer
            title = self._printedElement.title
            if title[:3] in ["JEM", "SUP"] and title[3:6].isdigit():
                self._printedElement.title = title[7:]
            # pylint: disable=no-member
            self._printedElement.transpose = self._inputTranspose.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.capo = self._inputCapo.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.key = self._inputKey.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.tempo = self._inputTempo.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.turf_number = self._inputNumTurf.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.song_book = self._input_song_book.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.hymn_number = self._inputNumCCLI.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.text = self._songTextField.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.title = self._inputTitle.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.author = self._inputAuthor.get(1.0, tk.END)
            # pylint: disable=no-member
            self._printedElement.tags = self._inputTags.get(1.0, tk.END)
            try:
                self._database.save(songs=[self._printedElement])
            except OSError as error:
                if error.errno == errno.ENOENT:
                    try:
                        tkMessageBox.showerror(
                            "Erreur",
                            f'Le chemin du chant "{self._printedElement.chemin}" n\'est pas valide. ',
                        )
                    except UnicodeEncodeError:
                        tkMessageBox.showerror(
                            "Erreur",
                            f'Le chemin du chant "{self._printedElement.chemin!r}" n\'est pas valide. ',
                        )
                    return 1
                raise

            self._update_content()
            self._syntax_highlighting()

            self._songTextField.mark_set("insert", cursor_position)
            self._songTextField.yview("moveto", scroll_position)
            self._songTextField.edit_modified(False)

            for field in self._inputFieldsList:
                field.edit_modified(False)  # pylint: disable=no-member

            self._buttonSaveSong.config(state=tk.DISABLED)
            if self._saveCallback:
                self._saveCallback()
            return 0
        return 1

    def _change_song_state(self, _event=None):
        not_modified = all(
            # pylint: disable=no-member
            [not field.edit_modified() for field in self._inputFieldsList],
        )

        if (
            (self._songTextField.edit_modified() or not not_modified)
            and self._printedElement
            and self._printedElement.etype == "song"
        ):
            self._buttonSaveSong.config(state=tk.NORMAL)
            self._syntax_highlighting()

    def _select_all_text(self, event):
        event.widget.tag_add("sel", "1.0", "end")

    def _syntax_highlighting(self):
        guiHelper.coloration(self._songTextField, "black")
        guiHelper.coloration(
            self._songTextField,
            "blue",
            settings.GENSETTINGS.get("Syntax", "newline"),
        )
        guiHelper.coloration(self._songTextField, "red", "\\ac")
        guiHelper.coloration(self._songTextField, "red", "[", "]")
        guiHelper.coloration(self._songTextField, "red", "\\...")
        guiHelper.coloration(self._songTextField, "red", "(bis)")
        guiHelper.coloration(self._songTextField, "red", "(ter)")
        for newslide_syntax in settings.GENSETTINGS.get("Syntax", "newslide"):
            guiHelper.coloration(
                self._songTextField,
                "blue",
                newslide_syntax,
            )  # TclError None

    def _create_new_song_window(self, copied_song=""):
        if self._newSongWindow:
            self._newSongWindow.destroy()
        self._newSongWindow = tk.Toplevel()
        with guiHelper.SmoothWindowCreation(self._newSongWindow, screens=self._screens):
            self._newSongWindow.title("Nouveau chant")
            self.newTitle = inputFrame.TextField(
                self._newSongWindow,
                width=40,
                text="Titre du nouveau chant: ",
                packing=tk.TOP,
            )
            if copied_song:
                self.newTitle.insert(1.0, copied_song.nom)  # pylint: disable=no-member
            bouton = tk.Button(
                self._newSongWindow,
                text="Créer",
                command=lambda chant=copied_song: self._create_new_song(chant),
            )

            self.newTitle.pack(side=tk.TOP, fill=tk.X, expand=1)
            bouton.pack(side=tk.TOP)
            self.newTitle.focus_set()

    def _create_new_song(self, copied_song=""):
        if self._database:
            tmp = self.newTitle.get(1.0, tk.END)  # pylint: disable=no-member
            tmp = fonc.upper_first(tmp)
            tmp, title = gestchant.new_song_title(tmp, self._database.max_custom_number)
            new_song = elements.Chant(tmp, title)
            new_song.text = f"{settings.GENSETTINGS.get('Syntax', 'newslide')[0]}"

            if new_song not in self._database or (
                new_song in self._database
                and tkMessageBox.askyesno(
                    "Création",
                    f'Le chant "{new_song.nom}" existe déjà, voulez-vous l\'écraser ?',
                )
            ):
                self._newSongWindow.destroy()
                self._newSongWindow = None
                self._printedElement = new_song
                self._songTextField.focus_set()
                if not copied_song:
                    self._printer_off()
                    self._print_on()
                    guiHelper.change_text(
                        self._songTextField,
                        f"{settings.GENSETTINGS.get('Syntax', 'newslide')[0]}\n",
                    )
                    guiHelper.change_text(self._inputTitle, self._printedElement.title)
                if not self._save_song():
                    self._database.add(new_song)

                    if self._saveCallback:
                        self._saveCallback()
                    if self._setSong:
                        self._setSong(new_song)
                    self.printer(to_print_dict={new_song: 100})

                    tkMessageBox.showinfo(
                        "Confirmation",
                        f'Le chant "{new_song.nom}" a été créé.',
                    )

            if self._newSongWindow is not None:
                self._newSongWindow.focus_set()
                self.newTitle.insert(1.0, "")  # pylint: disable=no-member
            self._active_buttons()

    def _active_buttons(self):
        if self._printedElement:
            self._buttonCreateNewVersion.config(state=tk.NORMAL)
        else:
            self._buttonCreateNewVersion.config(state=tk.DISABLED)

    def printer(
        self,
        to_print_dict=None,
        load_diapo=False,
    ):
        if not to_print_dict:
            to_print_dict = dict()
        max_priority = 0
        to_print = None
        for element, priority in to_print_dict.items():
            if element and priority > max_priority:
                to_print = element
                max_priority = priority

        if to_print:
            self._print_on()
            not_modified = all(
                # pylint: disable=no-member
                [not field.edit_modified() for field in self._inputFieldsList],
            )
            if (
                (self._songTextField.edit_modified() or not not_modified)
                and to_print.title
                and tkMessageBox.askyesno(
                    "Sauvegarde",
                    "Voulez-vous sauvegarder les modifications "
                    f'sur le chant:\n"{self._printedElement.title}" ?',
                )
            ):
                self._save_song()
            self._printedElement = to_print
            self._update_content(element=to_print)
            self._syntax_highlighting()
            if load_diapo and hasattr(self._diapo_list, "load"):
                self._diapo_list.load([to_print], wanted_diapo_number=1)
        else:
            self._printer_off()

        self._songTextField.edit_modified(False)
        for field in self._inputFieldsList:
            field.edit_modified(False)  # pylint: disable=no-member
        self._buttonSaveSong.config(state=tk.DISABLED)
        self._songTextField.edit_reset()
        self._active_buttons()
        if self._printerCallback:
            self._printerCallback()

    def reset_text(self):
        with contextlib.suppress(AttributeError):
            self._printedElement.reset_text()

    def printed_element(self):
        return self._printedElement

    def bind_printer_callback(self, function):
        self._printerCallback = function

    def bind_save_callback(self, function):
        self._saveCallback = function

    def bind_set_song(self, function):
        self._setSong = function

    def use_data_base(self, database):
        self._database = database
