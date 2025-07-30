import tkinter as tk


class DiapoListGui:
    def __init__(self, frame, diapo_list, callbacks=None):
        self._diapo_list = diapo_list
        if not callbacks:
            self._callbacks = dict()
        self._listBox = tk.Listbox(frame, selectmode=tk.BROWSE, width=40)
        self._scrollBar = tk.Scrollbar(frame, command=self._listBox.yview)
        self._listBox["yscrollcommand"] = self._scrollBar.set

        self._listBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self._scrollBar.pack(side=tk.LEFT, fill=tk.Y)

        self._listBox.bind("<KeyRelease-Up>", self._get_select)
        self._listBox.bind("<KeyRelease-Down>", self._get_select)
        self._listBox.bind("<ButtonRelease-1>", self._get_select)

    def _get_select(self, _event=None):
        if self._listBox.curselection():
            self._diapo_list.diapo_number = int(self._listBox.curselection()[0])
        for callback in self._callbacks.values():
            callback()

    def update_selected(self, focus=False):
        if focus:
            self._listBox.select_clear(0, tk.END)
            self._listBox.select_set(self._diapo_list.diapo_number)
        else:
            self._listBox.activate(self._diapo_list.diapo_number)
            self._listBox.see(self._diapo_list.diapo_number)

    def write(self):
        self._listBox.delete(0, "end")
        for i, diapo in enumerate(self._diapo_list.list):
            self._listBox.insert(i, diapo.title)
            if diapo.etype == "empty":
                self._listBox.itemconfig(i, bg="green")
            elif diapo.etype == "image":
                self._listBox.itemconfig(i, bg="blue")

    def width(self):
        return self._listBox.winfo_reqwidth() + self._scrollBar.winfo_reqwidth()

    def bind_diapo_list(self, diapo_list):
        self._diapo_list = diapo_list
        self.write()

    def bind_callback(self, callback, class_id):
        self._callbacks[class_id] = callback
