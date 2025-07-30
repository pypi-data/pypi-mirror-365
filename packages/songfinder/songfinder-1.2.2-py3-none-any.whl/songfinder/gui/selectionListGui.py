import contextlib
import gc
import logging
import os
import tkinter as tk
import traceback
from tkinter import ttk

from songfinder import classPaths, classSet, classVersets, elements, exception
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder import messages as tkFileDialog  # pylint: disable=reimported
from songfinder import messages as tkMessageBox

vlc = 0

logger = logging.getLogger(__name__)

WIDTH_THRESHOLD = 2000


class SelectionListGui:
    def __init__(
        self,
        frame,
        screens=None,
        diapo_list=None,
        search_function=None,
        printer=None,
    ):
        self._verseWindow = None
        self._set = classSet.Set()
        self._searchFuntion = search_function
        self._printer = printer
        self._diapo_list = diapo_list

        self._priority_multiplicator = 1
        self._cur_selection = 0
        self._setName = ""

        lis_button_sub_panel = ttk.Frame(frame)
        list_sub_panel = ttk.Frame(frame)

        lis_button_sub_panel.pack(side=tk.TOP, fill=tk.X)
        list_sub_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self._saveButton = tk.Button(
            lis_button_sub_panel,
            text="Sauver",
            command=self._save_set,
            state=tk.DISABLED,
        )
        self._deleteSetButton = tk.Button(
            lis_button_sub_panel,
            text="Suppr",
            command=self._delete_set,
            state=tk.DISABLED,
        )

        self._upButton = tk.Button(
            lis_button_sub_panel,
            text="Monter",
            command=self._up,
            state=tk.DISABLED,
        )
        self._downButton = tk.Button(
            lis_button_sub_panel,
            text="Descendre",
            command=self._down,
            state=tk.DISABLED,
        )
        self._deleteElemButton = tk.Button(
            lis_button_sub_panel,
            text="Suppr",
            command=self._delete_elem,
            state=tk.DISABLED,
        )
        self._clearButton = tk.Button(
            lis_button_sub_panel,
            text="Initialiser",
            command=self._clear,
            state=tk.DISABLED,
        )

        name_label = tk.Label(lis_button_sub_panel, text="Liste: ")

        self._setList = []
        set_selection_var = tk.StringVar()
        self._setSelection = ttk.Combobox(
            lis_button_sub_panel,
            textvariable=set_selection_var,
            values=self._setList,
            state="readonly",
            width=20,
        )

        add_media_button = tk.Button(
            lis_button_sub_panel,
            text="Ajouter\nMedias",
            command=self._add_media,
        )
        if vlc == 0:
            add_media_button.config(state=tk.DISABLED)
        add_image_button = tk.Button(
            lis_button_sub_panel,
            text="Ajouter\nImages",
            command=self._add_image,
        )
        add_verse_button = tk.Button(
            lis_button_sub_panel,
            text="Ajouter\nVersets",
            command=self._add_vers,
        )

        width = 65 if screens and screens[0].width > WIDTH_THRESHOLD else 55

        self._listbox_elem = tk.Listbox(list_sub_panel, width=width)
        listbox_elem_scroll = tk.Scrollbar(
            list_sub_panel,
            command=self._listbox_elem.yview,
        )
        self._listbox_elem["yscrollcommand"] = listbox_elem_scroll.set

        name_label.grid(row=0, column=0, columnspan=2, rowspan=1)
        self._setSelection.grid(row=0, column=2, columnspan=6)
        self._saveButton.grid(row=0, column=8, columnspan=2)
        self._deleteSetButton.grid(row=0, column=10, columnspan=2)

        add_media_button.grid(row=1, column=6, columnspan=2, rowspan=2)
        add_image_button.grid(row=1, column=8, columnspan=2, rowspan=2)
        add_verse_button.grid(row=1, column=10, columnspan=2, rowspan=2)

        self._upButton.grid(row=1, column=0, columnspan=3)
        self._downButton.grid(row=2, column=0, columnspan=3)
        self._deleteElemButton.grid(row=1, column=3, columnspan=3)
        self._clearButton.grid(row=2, column=3, columnspan=3)

        self._listbox_elem.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        listbox_elem_scroll.pack(side=tk.LEFT, fill=tk.Y)

        self._setSelection.bind("<<ComboboxSelected>>", self._select_set)
        self._listbox_elem.bind("<ButtonRelease-1>", self._select_song)
        self._listbox_elem.bind("<KeyRelease-Up>", self._select_song)
        self._listbox_elem.bind("<KeyRelease-Down>", self._select_song)
        self._listbox_elem.bind("<u>", self._up)
        self._listbox_elem.bind("<d>", self._down)
        self._listbox_elem.bind("<Delete>", self._delete_elem)

        self.get_set_list()
        if settings.GENSETTINGS.get("Parameters", "autoload") and self._setList:
            self._setSelection.set(self._setList[0])

        self.FILETYPES = [
            ("All files", "*.*"),
        ]
        self.FILETYPES_video = [
            (ext[1:].upper(), ext)
            for ext in settings.GENSETTINGS.get("Extentions", "video")
        ] + [("All files", "*.*")]
        self.FILETYPES_audio = [
            (ext[1:].upper(), ext)
            for ext in settings.GENSETTINGS.get("Extentions", "audio")
        ] + [("All files", "*.*")]
        self.FILETYPES_image = [
            (ext[1:].upper(), ext)
            for ext in settings.GENSETTINGS.get("Extentions", "image")
        ] + [("All files", "*.*")]
        self.FILETYPES_present = [
            (ext[1:].upper(), ext)
            for ext in settings.GENSETTINGS.get("Extentions", "presentation")
        ] + [("All files", "*.*")]
        self.FILETYPES_media = [
            ("MP4", ".mp4"),
            ("All files", "*.*"),
            *self.FILETYPES_video[:-1],
            *self.FILETYPES_audio[:-1],
        ]

        self._active_save_button()
        self._select_set()

    def _select_song(self, _event=None):
        self._active_boutons()
        out_dict_elements = {}
        if self._listbox_elem.curselection() and self._set:
            self._cur_selection = int(self._listbox_elem.curselection()[0])
            to_add = self._set[self._cur_selection]
            to_add = self._check_if_element_exists(to_add)
            out_dict_elements[to_add] = 16 * self._priority_multiplicator
        if self._listbox_elem.size() > 0 and self._set:
            to_add = self._set[0]
            to_add = self._check_if_element_exists(to_add)
            out_dict_elements[to_add] = 4 * self._priority_multiplicator
        if self._printer:
            self._printer(to_print_dict=out_dict_elements)
        if self._diapo_list is not None:
            self._diapo_list.load(self.list(), wanted_diapo_number=self._cur_selection)

    def _select_set(self, _event=None):
        new_set_name = self._setSelection.get()
        if new_set_name:
            if self._saveButton["state"] != tk.DISABLED and tkMessageBox.askyesno(
                "Sauvegarde",
                "Voulez-vous sauvegarder les modifications "
                f'sur la liste "{self._setName}" ?',
            ):
                self._setSelection.set(self._setName)
                self._save_set()
            self._setName = new_set_name
            try:
                code, message = self._set.load(self._setName)
                if code:
                    tkMessageBox.showerror("Attention", message)
            except exception.DataReadError:
                tkMessageBox.showerror("Attention", traceback.format_exc(limit=1))
            self._update_list()
            self._select_song()

        self._active_save_button()
        self._active_suppr_set_button()

    def _update_list(self):
        if self._setName != "":
            self._setSelection.set(self._setName)
        self._listbox_elem.delete(0, "end")
        for i, element in enumerate(self._set):
            self._listbox_elem.insert(i, (f"{i + 1} -- {element}"))
            if not element.exist() and self._listbox_elem.itemcget(i, "fg") != "green":
                self._listbox_elem.itemconfig(i, fg="green")

        if len(self._set) != 0:
            self._listbox_elem.yview("moveto", self._cur_selection / len(self._set))
        self._listbox_elem.activate(self._cur_selection)
        self._active_save_button()
        if self._diapo_list is not None:
            self._diapo_list.load(self.list())

    def _up(self, _event=None):
        index = int(self._listbox_elem.curselection()[0])
        if index > 0:
            self._set[index - 1], self._set[index] = (
                self._set[index],
                self._set[index - 1],
            )
            self._update_list()
            self._listbox_elem.activate(index - 1)
            self._listbox_elem.selection_set(index - 1)
            self._cur_selection = index - 1

    def _down(self, _event=None):
        index = int(self._listbox_elem.curselection()[0])
        if index < len(self._set) - 1:
            self._set[index + 1], self._set[index] = (
                self._set[index],
                self._set[index + 1],
            )
            self._update_list()
            self._listbox_elem.activate(index + 1)
            self._listbox_elem.selection_set(index + 1)
            self._cur_selection = index + 1

    def _delete_elem(self, _event=None):
        select = self._listbox_elem.curselection()
        if select:
            index = int(select[0])
            del self._set[index]
            self._update_list()
            lenght = self._listbox_elem.size()
            if index < lenght:
                self._listbox_elem.activate(index)
                self._listbox_elem.selection_set(index)
            elif lenght > 0:
                self._listbox_elem.activate(lenght - 1)
                self._listbox_elem.selection_set(lenght - 1)

    def _add_media(self):
        medias = tkFileDialog.askopenfilenames(filetypes=self.FILETYPES_media)
        if medias:
            for media in medias:
                media_file = fonc.get_file_name(media)
                extention = fonc.get_ext(media)
                anwser = 1
                media_type = settings.GENSETTINGS.get(
                    "Extentions",
                    "audio",
                ) + settings.GENSETTINGS.get("Extentions", "video")
                if media and (extention not in media_type):
                    anwser = tkMessageBox.askyesno(
                        "Type de fichier",
                        f'Le fichier "{media_file}.{extention}" ne semble pas être un fichier audio ou vidéo. '
                        "Voulez-vous continuer malgré tout ?",
                    )
                if media and anwser:
                    self.add_element_to_selection(
                        elements.Element(media_file, "media", media),
                    )

    def _add_image(self):
        images = tkFileDialog.askopenfilenames(filetypes=self.FILETYPES_image)
        if images:
            for full_path in images:
                media_file = fonc.get_file_name_ext(full_path)
                extention = fonc.get_ext(full_path)
                anwser = 1
                type_image = settings.GENSETTINGS.get("Extentions", "image")
                if full_path and (extention not in type_image):
                    anwser = tkMessageBox.askyesno(
                        "Type de fichier",
                        f'Le fichier "{media_file}.{extention}" ne semble pas être un fichier image. '
                        "Voulez-vous continuer malgré tout ?",
                    )
                if full_path and anwser:
                    self.add_element_to_selection(elements.ImageObj(full_path))

    def _clear(self):
        if self._saveButton["state"] != tk.DISABLED and tkMessageBox.askyesno(
            "Sauvegarde",
            "Voulez-vous sauvegarder les modifications "
            f'sur la liste "{self._setName}" ?',
        ):
            self._setSelection.set(self._setName)
            self._save_set()
        self._cur_selection = 0
        self._setName = ""
        self._setSelection.delete(0, tk.END)
        self._set.clear()
        self._update_list()
        self._active_save_button()

    def get_set_list(self):
        # TODO print set names instead of filenames
        if classPaths.PATHS.sets:
            self._setList = []
            for _, _, files in os.walk(classPaths.PATHS.sets):
                for fichier in sorted(files, reverse=True):
                    self._setList.append(fonc.get_file_name(fichier))
            self._setSelection["values"] = self._setList

    def _delete_set(self):
        if tkMessageBox.askyesno(
            "Confirmation",
            f'Etes-vous sur de suprrimer la liste:\n"{self._set!s}" ?',
        ):
            index = self._setList.index(fonc.enleve_accents(str(self._set)))
            self._set.delete()
            self.get_set_list()
            if len(self._setList) >= index:
                self._setSelection.set(self._setList[index])
                self._select_set()
        self._active_suppr_set_button()

    def _save_set(self):
        if classPaths.PATHS.sets:
            if not self._set:
                tkMessageBox.showerror("Attention", "La liste est vide")
            else:
                extention = settings.GENSETTINGS.get("Extentions", "liste")[0]
                save_set_name = tkFileDialog.asksaveasfilename(
                    initialdir=classPaths.PATHS.sets,
                    initialfile=str(self._set),
                    defaultextension=extention,
                    filetypes=(
                        (f"{extention} file", f"*{extention}"),
                        ("All Files", "*.*"),
                    ),
                )
                self._set.path = save_set_name
                if save_set_name != "":
                    self._set.save()
                    self.get_set_list()
                    self._active_save_button()
                    self._setSelection.set(str(self._set))
                    self._select_set()

    def _active_save_button(self):
        if not classPaths.PATHS.sets or not self._set.changed:
            self._saveButton.config(state=tk.DISABLED)
        else:
            self._saveButton.config(state=tk.NORMAL)

    def _active_suppr_set_button(self):
        if classPaths.PATHS.sets and self._setSelection.get():
            self._deleteSetButton.config(state=tk.NORMAL)
        else:
            self._deleteSetButton.config(state=tk.DISABLED)

    def _add_vers(self):
        self.close_verse_window()
        self._verseWindow = tk.Toplevel()
        self._verseWindow.wm_attributes("-topmost", 1)
        self._verseInterface = classVersets.class_versets(self._verseWindow, self)
        self._verseWindow.title("Bible")
        self._verseWindow.update_idletasks()
        self._verseWindow.protocol("WM_DELETE_WINDOW", self.close_verse_window)
        self._verseWindow.resizable(False, False)
        self._verseWindow.update()

    def select_vers(self):
        try:
            passage = elements.Passage(
                self._verseInterface.version,
                self._verseInterface.livre,
                self._verseInterface.chap1,
                self._verseInterface.chap2,
                self._verseInterface.vers1,
                self._verseInterface.vers2,
            )
        except exception.DataReadError:
            tkMessageBox.showerror("Attention", traceback.format_exc(limit=1))
        else:
            self._verseInterface.select_state()
            self.add_element_to_selection(passage)
            self._select_song()

    def _active_boutons(self):
        if self._listbox_elem.curselection():  # ValueError
            self._upButton.config(state=tk.NORMAL)
            self._downButton.config(state=tk.NORMAL)
            self._deleteElemButton.config(state=tk.NORMAL)
        else:
            self._upButton.config(state=tk.DISABLED)
            self._downButton.config(state=tk.DISABLED)
            self._deleteElemButton.config(state=tk.DISABLED)

        if self._set:
            self._clearButton.config(state=tk.NORMAL)
        else:
            self._clearButton.config(state=tk.DISABLED)

    def _check_if_element_exists(self, element):
        if element and self._searchFuntion and not element.exist() and element.nom:
            clean_name = element.nom
            search_results = self._searchFuntion(clean_name)
            if search_results and search_results[0].etype == element.etype:
                tkMessageBox.showinfo(
                    "Remplacement",
                    f'L\'élément "{element.nom}" est introuvable, '
                    f'il va être échangé par "{search_results[0].nom}".',
                )
                self._set[self._cur_selection] = search_results[0]
                element = search_results[0]
            else:
                tkMessageBox.showerror(
                    "Attention",
                    f'L\'élément "{element.nom}" est introuvable, '
                    "il va être supprimé de la liste.",
                )
                self._delete_elem()
                self._cur_selection = 0
            self._update_list()
        return element

    def reset_text(self):
        for song in self._set:
            with contextlib.suppress(AttributeError):
                song.reset()

    def reset_diapos(self):
        for element in self._set:
            element.reset_diapos()

    def add_element_to_selection(self, element):
        self._cur_selection = int(self._cur_selection) + 1
        self._set.insert(self._cur_selection, element)
        self._update_list()

    def close_verse_window(self):
        if self._verseWindow:
            self._verseInterface.quit()
            self._verseInterface = None
            self._verseWindow = None
            logger.debug(f"GC collected objects : {gc.collect()}")

    def set_list(self, file_in):
        self._setSelection.set(file_in)

    def list(self):
        return [element for element in self._set if element.exist()]

    def bind_printer(self, function):
        self._printer = function

    def bind_searcher(self, function):
        self._searchFuntion = function
