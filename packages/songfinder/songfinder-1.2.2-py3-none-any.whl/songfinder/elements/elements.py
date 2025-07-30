import os
import re

from songfinder import classDiapo, gestchant
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder.gui import screen


class Element:
    def __init__(self, nom="", etype="empty", chemin=""):
        self.newline = settings.GENSETTINGS.get("Syntax", "newline")
        self.nom = fonc.enleve_accents(nom)
        self._title = self.nom
        self._supInfo = ""
        if nom:
            self.nom = fonc.upper_first(self.nom)

        self._diapos = []
        self._chemin = None
        self._text = None
        self._author = None
        self._copyright = None
        self._customNumber = None
        self._turfNumber = None
        self._hymnNumber = None
        self._tags = []
        self.etype = etype
        self.chemin = chemin

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.chemin}')"

    def __str__(self):
        out = f"{self.etype} -- "
        return f"{out}{self.title}"

    @property
    def text(self):
        return self._text

    @property
    def title(self):
        if self._title == "":
            self.text  # pylint: disable=pointless-statement
        return self._title

    @property
    def sup_info(self):
        return self._supInfo

    @sup_info.setter
    def sup_info(self, info_in):
        if info_in is not None:
            info_in = info_in.replace("\n", "")
            info_in = info_in.strip(" ")
            self._supInfo = info_in

    @property
    def transpose(self):
        return None

    @property
    def capo(self):
        return None

    @property
    def key(self):
        return ""

    @property
    def nums(self):
        return dict()

    @property
    def turf_number(self):
        return None

    @property
    def hymn_number(self):
        return None

    @property
    def custom_number(self):
        return None

    @property
    def author(self):
        return ""

    @property
    def copyright(self):
        return ""

    @property
    def ccli(self):
        return ""

    @property
    def tags(self):
        return ",".join(self._tags)

    @tags.setter
    def tags(self, tags):
        if isinstance(tags, list):
            self._tags = [gestchant.nettoyage(tag) for tag in tags]
        else:
            tags = (
                tags.replace(" et ", ",")
                .replace(" / ", ",")
                .replace(" - ", ",")
                .replace(";", ",")
            )

            def cleanup_tag(tag):
                tag = fonc.upper_first(gestchant.nettoyage(tag))
                return tag.replace("st-", "saint").replace("St-", "Saint")

            self._tags = [cleanup_tag(tag) for tag in tags.split(",")]
            self._tags.sort()

    @property
    def diapos(self):
        if self._diapos != []:
            return self._diapos
        # ~ self._diapos = []

        text = f"{self.text}\n"
        text = fonc.supress_b(text, "\\ac", "\n")
        text = text.strip("\n")
        ratio = screen.get_ratio(settings.GENSETTINGS.get("Parameters", "ratio"))
        max_car = int(
            settings.PRESSETTINGS.get("Presentation_Parameters", "size_line") * ratio,
        )

        list_stype = []
        # La première est vide ie au dessus du premier \s
        line_per_slide = settings.PRESSETTINGS.get(
            "Presentation_Parameters",
            "line_per_diapo",
        )
        list_text, list_stype = fonc.split_perso(
            [text],
            settings.GENSETTINGS.get("Syntax", "newslide"),
            list_stype,
            0,
        )
        del list_text[0]
        list_stype_plus = gestchant.get_list_stype_plus(list_stype)
        # Completion des diapo vide
        diapo_vide = [
            i
            for i, text in enumerate(list_text)
            if text.find("\\...") != -1 or gestchant.nettoyage(text) == ""
        ]

        plus = 0
        for index in diapo_vide:
            list_candidat = gestchant.get_indexes(list_stype[:index], list_stype[index])
            if list_candidat != []:
                # Si plus de diapos que disponibles sont demande,
                # cela veut dire qu'il faut dupliquer plusieurs fois les diapos
                if not gestchant.get_plus_num(list_stype_plus, index) > len(
                    list_candidat,
                ):
                    plus = 0
                elif plus == 0:
                    plus = gestchant.get_plus_num(list_stype_plus, index) - len(
                        list_candidat,
                    )
                to_take = -gestchant.get_plus_num(list_stype_plus, index) + plus
                index_copie = list_candidat[to_take]
                if list_text[index].find("\\...") != -1:
                    list_text[index] = list_text[index].replace(
                        "\\...",
                        list_text[index_copie],
                    )
                else:
                    list_text[index] = list_text[index_copie]

        line_per_slide = settings.PRESSETTINGS.get(
            "Presentation_Parameters",
            "line_per_diapo",
        )
        list_text, list_stype = gestchant.apply_max_number_line_per_diapo(
            list_text,
            list_stype,
            line_per_slide,
        )

        nombre = len(list_text)
        for i, text in enumerate(list_text):
            diapo = classDiapo.Diapo(self, i + 1, list_stype[i], max_car, nombre, text)
            self._diapos.append(diapo)
        return self._diapos

    @property
    def chemin(self):
        return self._chemin

    @chemin.setter
    def chemin(self, value):
        cdl_path = settings.GENSETTINGS.get("Paths", "conducteurdelouange")
        if not os.path.isfile(value) and value.find(cdl_path) == -1:
            ext = settings.GENSETTINGS.get("Extentions", self.etype)[0]
            path = fonc.get_path(value)
            name = fonc.get_file_name(value)
            name = fonc.enleve_accents(name)
            name = re.sub(r'[\/?!,;:*<>"|^\n]+', "", name)
            name = re.sub(r"[\'() ]+", "_", name)
            name = re.sub(r"_+", "_", name)
            name = name.strip("_")
            self._chemin = os.path.join(path, name) + ext
        else:
            self._chemin = value

    def reset_diapos(self):
        del self._diapos[:]

    @title.setter
    def title(self, new_title):
        if new_title:
            match = re.match(
                r"(JEM|SUP)?(\d{3,4})?([^\(\)]*)(\((.*)\))?(.*)",
                new_title,
            )
            new_title = match.group(3)
            if match.group(6):
                new_title = new_title + match.group(6)
            self.sup_info = match.group(5)
            new_title = new_title.replace("\n", "")
            new_title = new_title.strip(" ")
        else:
            new_title = ""
        self._title = new_title
        self._latexText = ""
        self._beamerText = ""
        self._markdownText = ""

    def exist(self):
        return os.path.isfile(self.chemin) and self.text

    def save(self):
        pass

    def safe_update_xml(self, xml_root, field, value):
        if isinstance(value, (int, float)):
            value = str(value).encode("utf-8").decode("utf-8")
        if value is not None:
            try:
                xml_root.find(field).text = value
            except AttributeError:
                import lxml.etree as ET_write

                ET_write.SubElement(xml_root, field)
                xml_root.find(field).text = value
