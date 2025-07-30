import logging
import os
import time
import tkinter as tk
from tkinter import ttk

import songfinder
from songfinder import messages as tkMessageBox
from songfinder import search
from songfinder.gui import inputFrame

logger = logging.getLogger(__name__)

WIDTH_THRESHOLD = 2000


class SearchGui:
    def __init__(
        self,
        frame,
        database=None,
        screens=None,
        add_element_to_selection=None,
        printer=None,
        diapo_list=None,
    ):
        # TODO remove _database reference if possible

        self._frame = frame
        self._printer = printer
        self._song_found = []

        self.use_data_base(database)

        self._diapo_list = diapo_list

        self._add_element_to_selection = add_element_to_selection

        self._priority_multiplicator = 1

        width = 65 if screens and screens[0].width > WIDTH_THRESHOLD else 55

        self._input_search = inputFrame.entryField(
            frame,
            width=width,
            text="Recherche: ",
        )

        type_search_sub_panel = ttk.Frame(frame)
        search_result_panel = ttk.Frame(frame)

        self._varSearcher = tk.IntVar()
        lyrics_searcher_button = tk.Radiobutton(
            type_search_sub_panel,
            text="Paroles",
            variable=self._varSearcher,
            value=0,
            command=lambda str_id="lyrics": self._change_searcher(str_id),
        )
        title_searcher_button = tk.Radiobutton(
            type_search_sub_panel,
            text="Titres",
            variable=self._varSearcher,
            value=1,
            command=lambda str_id="titles": self._change_searcher(str_id),
        )
        tags_searcher_button = tk.Radiobutton(
            type_search_sub_panel,
            text="Tags",
            variable=self._varSearcher,
            value=2,
            command=lambda str_id="tags": self._change_searcher(str_id),
        )

        self._allSearcher_buttons = [
            lyrics_searcher_button,
            title_searcher_button,
            tags_searcher_button,
        ]

        tag_label = tk.Label(type_search_sub_panel, text="Tags :")
        tag_selection_var = tk.StringVar()
        # TODO update tag list when database is updated
        self._tagSelection = ttk.Combobox(
            type_search_sub_panel,
            textvariable=tag_selection_var,
            values=self._database.tags,
            state="readonly",
            width=30,
        )

        explain_label = tk.Label(
            frame,
            text="Chants trouvés: \n"
            "Utilisez leur numéro dans la liste pour les selectionner",
        )
        self._search_results = tk.Listbox(search_result_panel, width=width, height=9)
        search_results_scroll = tk.Scrollbar(
            search_result_panel,
            command=self._search_results.yview,
        )
        self._search_results["yscrollcommand"] = search_results_scroll.set

        self._upButton = tk.Button(
            frame,
            text="Ajouter chant",
            command=lambda event=None, mouse_click=1: self._select(event, mouse_click),
        )

        self._input_search.pack(side=tk.TOP, fill=tk.X)
        type_search_sub_panel.pack(side=tk.TOP, fill=tk.X)
        for searcher_buttons in self._allSearcher_buttons:
            searcher_buttons.pack(side=tk.LEFT, fill=tk.X)
        self._tagSelection.pack(side=tk.RIGHT, fill=tk.X)
        tag_label.pack(side=tk.RIGHT, fill=tk.X)

        explain_label.pack(side=tk.TOP, fill=tk.X)

        search_result_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self._search_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        search_results_scroll.pack(side=tk.LEFT, fill=tk.Y)

        self._upButton.pack(side=tk.TOP, fill=tk.X)
        self._search_results.bind("<ButtonRelease-1>", self._printer_wrapper)
        self._search_results.bind(
            "<Double-Button-1>",
            lambda event, mouse_click=1: self._select(event, mouse_click),
        )

        self._search_results.bind("<KeyRelease-Up>", self._printer_wrapper)
        self._search_results.bind("<KeyRelease-Down>", self._printer_wrapper)
        self._search_results.bind("<Delete>", self._delete_song)

        self._input_search.bind("<Key>", self._search)
        self._input_search.bind("<KeyRelease-BackSpace>", self._nothing)
        self._input_search.bind("<KeyRelease-Left>", self._nothing)
        self._input_search.bind("<KeyRelease-Right>", self._nothing)
        self._input_search.bind("<KeyRelease-Up>", self._nothing)
        self._input_search.bind("<KeyRelease-Down>", self._nothing)

        self._tagSelection.bind("<<ComboboxSelected>>", self._select_tag)
        self._tagSelection.bind("<FocusIn>", self._update_tags)

        self._input_search.focus_set()

        self._delayId = None
        self._passed = 0
        self._total = 0
        self._delay_amount = 0
        self._callback_delay = 0
        self._last_callback = 0

        self._search()

        self._printMod = 10
        self._print_counter = 0

    def _select_tag(self, _event):
        self._change_searcher("tags")
        self._varSearcher.set(2)
        tag = self._tagSelection.get()
        self._input_search.delete(0, tk.END)  # pylint: disable=no-member
        self._input_search.insert(0, tag)  # pylint: disable=no-member
        self._search()

    def _update_tags(self, _event=None):
        self._tagSelection["values"] = self._database.tags

    @property
    def searcher(self):
        return self._searcher

    def _change_searcher(self, new_mode):
        if new_mode != self._searcher.mode:
            logger.info(
                f'Changing searcher from "{self._searcher.mode}" to "{new_mode}"',
            )
            self._searcher.mode = new_mode
            self._search()

    def _printer_wrapper(self, _event=None):
        out_dict_elements = {}
        if self._search_results.curselection() and self._song_found:
            select = self._search_results.curselection()[0]
            to_add = self._song_found[select]
            out_dict_elements[to_add] = 18 * self._priority_multiplicator
        if self._search_results.size() > 0 and self._song_found:  # ValueError None
            to_add = self._song_found[0]
            out_dict_elements[to_add] = 6 * self._priority_multiplicator

        if self._printer:
            time.sleep(
                0.1,
            )  # TTODO, this is a hack for linux/mac, it enable double clic binding
            self._printer(to_print_dict=out_dict_elements, load_diapo=True)
        elif self._diapo_list is not None and hasattr(self._diapo_list, "load"):
            self._diapo_list.load([to_add], wantedDiapoNumber=1)

    def _search(self, event=None):
        current_time = time.time()
        self._callback_delay = round((current_time - self._last_callback) * 1000)
        self._last_callback = current_time
        self._priority_multiplicator = 10
        self._total += 1
        if self._delayId:
            self._frame.after_cancel(self._delayId)
        self._delayId = self._frame.after(self._delay_amount, self._search_core, event)
        self._priority_multiplicator = 1

    def _search_core(self, event):
        start_time = time.time()
        self._passed += 1
        if self._searcher:
            if self._input_search.get():  # pylint: disable=no-member
                search_input = self._input_search.get()  # pylint: disable=no-member
                self._song_found = self._searcher.search(search_input)
            else:
                self._song_found = list(self._database.keys())
            self._show_results()
            self._select(event)
            self._printer_wrapper(event)
        else:
            logger.warning("No searcher have been defined for searchGui")

        # Compute printer delay to lower pression on slow computers
        printer_time = round((time.time() - start_time) * 1000)
        if printer_time > self._callback_delay:
            self._delay_amount = min(printer_time, 2)
        else:
            self._delay_amount = 0

    def _show_results(self):
        self._search_results.delete(0, "end")
        for i, song in enumerate(self._song_found):
            self._search_results.insert(i, (f"{i + 1} -- {song}"))
        if self._print_counter % self._printMod == 0:
            logger.debug(f"Printing {len(self._song_found)} search results")
        self._print_counter += 1

    def _select(self, event, mouse_click=0):
        if self._add_element_to_selection:
            keyboard_input = ""
            if event:
                # For ubuntu num lock wierd behaviour
                touche_num_pad = event.keycode
                if songfinder.__myOs__ in ["ubuntu", "darwin"]:
                    list_num_pad = [87, 88, 89, 83, 84, 85, 79, 80, 81]
                else:
                    list_num_pad = []
                if not self._input_search.get().isdigit():  # pylint: disable=no-member
                    if touche_num_pad in list_num_pad:
                        keyboard_input = str(list_num_pad.index(touche_num_pad) + 1)
                    else:
                        keyboard_input = event.keysym
            if mouse_click == 1:
                if self._search_results.curselection():
                    keyboard_input = str(
                        int(self._search_results.curselection()[0]) + 1,
                    )
                    if int(keyboard_input) >= self._search_results.size() + 1:
                        logger.warning(
                            f'The input element number "{keyboard_input}" is invalid, '
                            "can not figure out what element to add."
                            f'Maximum entry is "{self._search_results.size() + 1}"',
                        )
                else:
                    logger.warning(
                        "The result list was not selected, "
                        "can not figure out what element to add.",
                    )

            if keyboard_input.isdigit():
                if int(keyboard_input) < self._search_results.size() + 1:
                    element = self._song_found[int(keyboard_input) - 1]
                    self._add_element_to_selection(element)
                    self._input_search.delete(0, tk.END)  # pylint: disable=no-member
                    self._input_search.focus_set()
                else:
                    logger.warning(
                        f'Got an invalid number from event "{keyboard_input}", '
                        "can not figure out what element to add.",
                    )

    def _delete_song(self, _event):
        if self._database and self._search_results.curselection():
            select = self._search_results.curselection()[0]
            to_delete = self._song_found[select]
            if tkMessageBox.askyesno(
                "Confirmation",
                f'Etes-vous sur de supprimer le chant:\n"{to_delete.nom}" ?',
            ):
                path = to_delete.chemin
                if os.path.isfile(path):
                    os.remove(path)
                self._database.remove(to_delete)
                self.reset_cache()
                if to_delete in self._song_found:
                    self._song_found.remove(to_delete)
                try:
                    logger.info(f'Deleted "{to_delete.chemin}"')
                except UnicodeEncodeError:
                    logger.info(f'Deleted "{to_delete.chemin!r}"')
                self._show_results()
                self._printer_wrapper()

    def _nothing(self, event=0):
        pass

    def set_song(self, song):
        self._song_found = [song]
        self._show_results()

    def reset_cache(self):
        self._searcher.reset_cache()

    def reset_text(self):
        for song in self._song_found:
            song.reset()

    def reset_diapos(self):
        for element in self._song_found:
            element.reset_diapos()

    def bind_add_element_to_selection(self, function):
        self._add_element_to_selection = function

    def bind_printer(self, function):
        self._printer = function

    def use_data_base(self, database):
        self._database = database
        self._searcher = search.SearcherWrapper(self._database)
