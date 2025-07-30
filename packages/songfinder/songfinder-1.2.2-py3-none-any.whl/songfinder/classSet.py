# cython: language_level=3 # noqa: ERA001

import datetime
import errno
import logging
import os
import re
import traceback
import xml.etree.ElementTree as ET

from songfinder import classPaths, elements
from songfinder import classSettings as settings
from songfinder import fonctions as fonc

logger = logging.getLogger(__name__)


class Set:
    def __init__(self):
        self._paths = classPaths.PATHS
        self._listElem = []
        self._generate_name()
        self._changed = False

    def __hash__(self):
        return hash(tuple(self._listElem))

    def __eq__(self, other):
        return all(item == other[i] for i, item in enumerate(self._listElem))

    def __len__(self):
        return len(self._listElem)

    def __setitem__(self, key, value):
        self._listElem[key] = value
        self._changed = True

    def __getitem__(self, index):
        return self._listElem[index]

    def __delitem__(self, index):
        del self._listElem[index]
        self._changed = True

    def __contains__(self, element):
        return element in self._listElem

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._listElem}')"

    def __str__(self):
        return self._name

    def _generate_name(self):
        next_sunday = datetime.timedelta(days=6 - datetime.datetime.today().weekday())
        self._name = str(datetime.date.today() + next_sunday)
        date_length = 10  # YYYY-MM-DD format length
        while os.path.isfile(self._paths.sets + self._name):
            if len(self._name) == date_length:
                self._name = f"{self._name}_1"
            else:
                self._name = self._name[: date_length + 1] + str(
                    int(self._name[date_length + 1 :]) + 1,
                )
        self.path = (
            os.path.join(self._paths.sets, self._name)
            + settings.GENSETTINGS.get("Extentions", "liste")[0]
        )

    def _read(self, prefered_path, database):
        tmp = None
        self._listElem = []
        try:
            tree = ET.parse(self.path)
            tree.getroot().find("slide_groups")[:]  # pylint: disable=expression-not-assigned
        except (OSError, AttributeError):
            logger.warning(f'Not able to read "{self.path}"\n{traceback.format_exc()}')
            return 1, traceback.format_exc()
        xml_list = tree.getroot()

        path_to_search = [""]
        if prefered_path:
            path_to_search.append(prefered_path)
        path_to_search.append(self._paths.songs)
        self._name = xml_list.attrib["name"]

        for title in xml_list.find("slide_groups"):
            if title.attrib["type"] == "song":
                elem_path = title.attrib["path"]
                elem_name = title.attrib["name"]
                try:
                    song_ext = title.attrib["ext"]
                    elem_name = elem_name + song_ext
                except KeyError:
                    pass
                # Different ways of writting the path, test all

                for path in path_to_search:
                    tmp = elements.Chant(os.path.join(path, elem_path, elem_name))
                    if not tmp.exist():
                        tmp = elements.Chant(os.path.join(path, elem_name))
                        if not tmp.exist():
                            tmp = elements.Chant(os.path.join(path, "songs", elem_name))
                    if tmp.exist():
                        break

            elif title.attrib["type"] == "media":
                tmp = elements.Element(elem_name, title.attrib["type"], elem_path)
            elif title.attrib["type"] == "image":
                tmp = elements.ImageObj(os.path.join(elem_path, elem_name))
            elif title.attrib["type"] == "verse":
                tmp = elements.Passage(
                    title.attrib["version"],
                    int(title.attrib["livre"]),
                    int(title.attrib["chap1"]),
                    int(title.attrib["chap2"]),
                    int(title.attrib["vers1"]),
                    int(title.attrib["vers2"]),
                )
            if database:
                try:
                    tmp = database[tmp.nom]
                    tmp.reset_diapos()
                except KeyError:
                    pass
            self._listElem.append(tmp)
        self._changed = False
        # TODO Cmon remove this !
        return 0, ""

    def append(self, element):
        self._listElem.append(element)
        self._changed = True

    def insert(self, index, element):
        self._listElem.insert(index, element)
        self._changed = True

    def clear(self):
        del self._listElem[:]
        self._changed = True

    def save(self):
        new_set = ET.Element("set")
        new_set.set("name", self._name)
        slide_groups = ET.SubElement(new_set, "slide_groups")
        slide_group = []
        for i, element in enumerate(self._listElem):
            chemin = fonc.get_path(element.chemin)
            # For compatibility between linux an windows, all path are writtent with slash
            chemin = chemin.replace(os.sep, "/")
            # Write path relative to songs directory
            chemin = chemin.replace(f"{self._paths.songs.replace(os.sep, '/')}", "")

            slide_group.append(ET.SubElement(slide_groups, "slide_group"))
            slide_group[i].set("type", element.etype)
            if element.etype == "song":
                slide_group[i].set("path", chemin)
                slide_group[i].set("name", element.nom)
                slide_group[i].set("ext", element.extention)
            elif element.etype == "verse":
                slide_group[i].set("name", element.nom)
                slide_group[i].set("path", chemin)
                slide_group[i].set("version", element.version)
                slide_group[i].set("livre", str(element.livre))
                slide_group[i].set("chap1", str(element.chap1))
                slide_group[i].set("chap2", str(element.chap2))
                slide_group[i].set("vers1", str(element.vers1))
                slide_group[i].set("vers2", str(element.vers2))
            elif element.etype == "image":
                slide_group[i].set("name", element.nom)
                slide_group[i].set("path", chemin)
                slide_group[i].set("ext", element.extention)

        tree = ET.ElementTree(new_set)
        fonc.indent(new_set)
        tree.write(self.path, encoding="UTF-8", xml_declaration=True)
        self._changed = False

    def delete(self):
        try:
            os.remove(self.path)
        except OSError as error:
            if error.errno == errno.ENOENT:
                logger.warning(f'File "{self.path}" does not exist.')
            elif error.errno == errno.EACCES:
                logger.warning(f'Acces to "{self.path}" is not permited.')
            else:
                logger.exception(traceback.format_exc())
                raise
        self._changed = True

    def load(self, file_name, prefered_path=None, database=None):
        set_extention = settings.GENSETTINGS.get("Extentions", "liste")[0]
        if file_name.find("/") != -1:
            candidat = file_name
        else:
            candidat = os.path.join(self._paths.sets, file_name)
        candidat = candidat + set_extention
        candidat = candidat.replace(set_extention * 2, set_extention)
        self.path = candidat
        # For backward compatibility with old file names
        # TODO remove this
        if not os.path.isfile(self.path):
            self._fileName = candidat
        return self._read(prefered_path, database)

    @property
    def path(self):
        return self._fileName

    @path.setter
    def path(self, input_path):
        self._name = fonc.get_file_name(input_path)
        path = fonc.get_path(input_path)
        ext = fonc.get_ext(input_path)
        file_name = fonc.get_file_name(input_path)
        file_name = fonc.enleve_accents(file_name).strip(" ")
        file_name = re.sub(r'[\/?!,;:*<>"|^]+', "", file_name)
        file_name = re.sub(r"[\'() ]+", "_", file_name)
        self._fileName = os.path.join(path, file_name) + ext

    @property
    def changed(self):
        return self._changed
