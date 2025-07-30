import logging
import time

from songfinder import classDiapo, elements, exception
from songfinder import classSettings as settings

logger = logging.getLogger(__name__)


class DiapoList:
    def __init__(
        self,
        element_list=(),
        gui_update=(),
        load_callbacks=(),
        is_load_allowed=lambda: True,
    ):
        self._elementList = element_list
        self._emptyDiapo = classDiapo.Diapo(
            elements.Element(),
            0,
            settings.GENSETTINGS.get("Syntax", "newslide")[0],
            90,
        )
        self._diapos = []
        self._element2diapo = []
        self._diapo2element = []
        self._diapoNum = 0
        self._upToDate = False

        self._guiUpdate = list(gui_update)
        self._loadCallbacks = list(load_callbacks)
        self._isLoadAlowed = is_load_allowed

    @property
    def list(self):
        self._construct_lists()
        return self._diapos

    def _construct_lists(self):
        if not self._upToDate and self._elementList:
            del self._diapos[:]
            del self._element2diapo[:]
            del self._diapo2element[:]
            self._element2diapo.append(0)
            previous = "empty"
            for i, element in enumerate(self._elementList):
                if element.etype != "image" or previous != "image":
                    self._diapos += [self._emptyDiapo]
                    self._diapo2element += [i]
                self._diapos += element.diapos
                self._element2diapo.append(len(self._diapos))
                self._diapo2element += [i] * len(element.diapos)
                previous = element.etype
            self._diapo2element.append(len(self._elementList) - 1)
            self._diapos += [self._emptyDiapo]
        self._upToDate = True

    def __len__(self):
        return len(self.list)

    def prefetch(self, themes, callback=None, args=()):
        tmp = time.time()
        self._construct_lists()
        self._construct_lists()
        self._construct_lists()
        for diapo in reversed(self._diapos):
            diapo.prefetch(themes, text=False)
            if callback:
                callback(*args)
        logger.debug(f"Image prefetching time: {time.time() - tmp:f}")

    def incremente(self, focus=False, _event=None):
        self._diapoNum = min(self._diapoNum + 1, len(self) - 1)
        if self._guiUpdate:
            for gui_update in self._guiUpdate:
                try:
                    gui_update(focus=focus)
                except TypeError:
                    gui_update()

    def decremente(self, focus=False, _event=None):
        self._diapoNum = max(self._diapoNum - 1, 0)
        if self._guiUpdate:
            for gui_update in self._guiUpdate:
                try:
                    gui_update(focus=focus)
                except TypeError:
                    gui_update()

    @property
    def diapo_number(self):
        return self._diapoNum

    @diapo_number.setter
    def diapo_number(self, num):
        if num >= len(self) or num < 0:
            raise exception.DiapoError(num)
        self._diapoNum = num
        if self._guiUpdate:
            for gui_update in self._guiUpdate:
                gui_update()

    @property
    def element_number(self):
        self._construct_lists()
        if self._diapo2element:
            return self._diapo2element[self._diapoNum]
        return 0

    @element_number.setter
    def element_number(self, value):
        self._construct_lists()
        if self._element2diapo:
            self.diapo_number = self._element2diapo[value]
        else:
            self.diapo_number = 0

    def bind_gui_update(self, function):
        self._guiUpdate.append(function)

    def bind_load_callback(self, function):
        self._loadCallbacks.append(function)

    def bind_is_load_allowed(self, function):
        self._isLoadAlowed = function

    def load(self, element_list, wanted_diapo_number=0, wanted_element_number=None):
        if self._isLoadAlowed():
            new_element_list = [element for element in element_list if element]
            old_names = {element.nom for element in self._elementList}
            new_names = {element.nom for element in new_element_list}
            num_commun = len(old_names & new_names)
            num_total = len(old_names | new_names)
            similarity_threshold = 0.5
            if num_total and num_commun / num_total > similarity_threshold:
                current_elem = self.element_number
                current_elem_diapo = (
                    self.diapo_number - self._element2diapo[current_elem]
                )
                current_elem_name = self._elementList[current_elem].nom
                self._elementList = new_element_list
                self._upToDate = False
                self._construct_lists()
                for i, element in enumerate(self._elementList):
                    if (
                        element.nom == current_elem_name
                        and self._element2diapo[i + 1] - self._element2diapo[i]
                        > current_elem_diapo
                    ):
                        self.diapo_number = self._element2diapo[i] + current_elem_diapo
                        break
                if wanted_element_number is not None:
                    self.element_number = wanted_element_number
            else:
                self._elementList = new_element_list
                self._upToDate = False
                if wanted_element_number is not None:
                    self.element_number = wanted_element_number
                else:
                    self.diapo_number = wanted_diapo_number
            for callback in self._loadCallbacks:
                callback()

    def reset_text(self):
        for element in self._elementList:
            element.reset()
        self._upToDate = False

    def __getitem__(self, key):
        self._construct_lists()
        num = self._diapoNum + key
        return self._diapos[num] if num < len(self) and num >= 0 else self._emptyDiapo

    def bind_frame_event(self, frame):
        global_bindings = {"<Prior>": self.decremente, "<Next>": self.incremente}
        for key, value in global_bindings.items():
            frame.bind_all(key, value)
