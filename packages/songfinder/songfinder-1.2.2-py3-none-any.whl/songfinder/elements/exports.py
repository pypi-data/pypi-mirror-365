import codecs
import os
import re

import songfinder
from songfinder import accords, classDiapo, gestchant
from songfinder import classSettings as settings
from songfinder import fonctions as fonc

MIN_WORDS_FOR_DUPLICATE_CHECK = 15
MIN_MATCH_FOR_DUPLICATE_CHECK = 14
MAX_CHARS_PER_DIAPO = 200
MAX_LINES_PER_DIAPO = 7


class ExportBase:
    def __init__(self, element, title_level, export_settings=None):
        self.element = element
        self._nbLignes = -1
        self._forcedNewLine = r"\newac"
        self._newLineSuggest = r"\newline"
        self._chordsMarker = "\t\\hspace*{\\fill}"
        self._diapos = []
        self._exportedText = ""
        self._title_level = title_level

        self._newlineMarker = "\n"
        self._supportedTypes = []
        self._specialChar = []

        if not export_settings:
            self._export_settings = settings.LATEXSETTINGS
        else:
            self._export_settings = export_settings

    @property
    def text(self):
        return self.element.text

    @property
    def transpose(self):
        return self.element.transpose

    @property
    def capo(self):
        if self._export_settings.get("Export_Parameters", "auto_capo") and self.key:
            ref_keys = set(("C", "G"))
            capo = 12
            song_key_num = accords.Chord(self.key).num + self.transpose

            for key in ref_keys:
                ref_key_num = accords.Chord(key).num
                new_capo = (song_key_num - ref_key_num) % 12
                capo = min(capo, new_capo)
        else:
            capo = self.element.capo if self.element.capo else 0
        return capo % 12

    @property
    def diapos(self):
        return self.element.diapos

    @property
    def title(self):
        return self.element.title

    @property
    def etype(self):
        return self.element.etype

    @property
    def nom(self):
        return self.element.nom

    @property
    def key(self):
        return self.element.key

    @property
    def tempo(self):
        return self.element.tempo

    @property
    def printref(self):
        return self.element.printref

    @property
    def ccli(self):
        return self.element.ccli

    @property
    def hymn_number(self):
        return self.element.hymn_number

    @property
    def custom_number(self):
        return self.element.custom_number

    @property
    def turf_number(self):
        return self.element.turf_number

    @title.setter
    def title(self, value):
        self.element.title = value

    @etype.setter
    def etype(self, value):
        self.element.etype = value

    @property
    def nb_line(self):
        if self._nbLignes == -1:
            self.export_text  # pylint: disable=pointless-statement,no-member
        return self._nbLignes

    def _process_chords(self, text):
        deb = 0
        fin = 0
        newtext = ""
        while fin != -1:
            tmp = text.find("\\ac", deb)
            if tmp == -1:
                newtext = newtext + text[deb:]
                fin = -1
            else:
                fin = text.find("\n", tmp)
                extrait = text[tmp:fin] if fin != -1 else text[tmp:]

                chords_obj = accords.Accords(
                    extrait,
                    transpose_nb=self.transpose,
                    capo=self.capo,
                    export_settings=self._export_settings,
                )
                chords = chords_obj.get_chords(key=self.key)

                add_new_line = f"{self._forcedNewLine}" if text[deb:tmp] == "" else ""
                newtext = "{}{}{}\\ac {}{}".format(
                    newtext,
                    text[deb:tmp],
                    add_new_line,
                    "~~".join(chords),
                    self._forcedNewLine,
                )
                deb = fin + 1
        return newtext

    def _process_new_line(self, text):
        if self._export_settings.get("Export_Parameters", "saut_lignes"):
            text = text.replace("\n", f" {self._newLineSuggest}")
            # Force newline if one line ends a sentence TODO to keep ?
            for ponct in [".", "!", "?"]:
                text = text.replace(f"{ponct} {self._newLineSuggest}", f"{ponct}\n")

        # Saut de ligne apres et pas avant les chaines suivantes
        for execp in ['"', ' "', " (bis)", " (ter)", " (x4)", ".", "?"]:
            text = text.replace(f"\n{execp}", f"{execp}\n")

        # Proposition de saut de ligne apres et pas avant les chaines suivantes
        for execp in [",", ";", ":"]:
            text = text.replace(f"\n{execp}", execp + self._newLineSuggest)

        # Saut de ligne apres les chaines suivantes
        for execp in ["(bis)", "(ter)", "(x4)", "(bis) ", "(ter) ", "(x4) ", "\\l "]:
            text = text.replace(execp + self._newLineSuggest, f"{execp}\n")

        text = text.replace(".\n.\n.\n", "...\n")
        text = text.replace("Oh !\n", "Oh !")
        text = text.replace("oh !\n", "oh !")
        # Avoid double newline when \l is used after chords
        text = text.replace(f"{self._forcedNewLine}\\l", self._forcedNewLine)
        text = text.replace(self._forcedNewLine, "\n")
        # Force new line after (f) if there are h/f responces)
        text = text.replace(f"(f) {self._newLineSuggest}", "(f) \n")

        supress_starts = [self._newLineSuggest, "\n"]
        supress_ends = ["(bis)", "(Bis)", "(ter)", "(x3)", "(x4)"]
        for start in supress_starts:
            for end in supress_ends:
                text = text.replace(start + end, "")
        # Must be after for the case where (bis) is just befor chords
        ac_replace = [self._newLineSuggest, "\n", "\n "]
        for start in ac_replace:
            text = text.replace(f"{start}\\ac", "\\ac")

        # Do not take away a new line if there is a bis at the end
        for multiple in ["(bis)", "(ter)", "(x4)"]:
            fin = len(text) - 1
            bis = 0
            while fin != -1 and bis != -1:
                bis = text.rfind(multiple, 0, fin)
                fin = text.rfind(self._newLineSuggest, 0, bis)
                if fin != -1 and bis != -1 and text[fin + 8 : bis].find("\n") == -1:
                    text = f"{text[:fin]}\n{text[fin + 8 :]}"
        return text

    def _match_para(self, text1, text2, ignore=()):
        text1 = f"{text1}\n"
        text2 = f"{text2}\n"
        for to_ignore in ignore:
            text1 = text1.replace(to_ignore, "")
            text2 = text2.replace(to_ignore, "")
        if text1.find("\\ac") == -1 or text2.find("\\ac") == -1:
            text1 = fonc.supress_b(text1, "\\ac", "\n")
            text2 = fonc.supress_b(text2, "\\ac", "\n")
        text1 = text1.replace("\n", "")
        text2 = text2.replace("\n", "")
        list_mot1 = text1.split(" ")
        list_mot2 = text2.split(" ")
        matches = len(set(list_mot1) & set(list_mot2))
        diff = len(set(list_mot1) ^ set(list_mot2))
        diff = diff * diff / 4
        return 10000.0 if diff == 0 else matches / diff

    def _get_diapos(self):
        if self._diapos != []:
            return self._diapos

        text = self.text
        if self._export_settings.get("Export_Parameters", "chords"):
            text = self._process_chords(text)
        else:
            text = f"{text}\n"
            text = fonc.supress_b(text, "\\ac", "\n")
            text = text.strip("\n")
        text = self._process_new_line(text)
        list_stype = []
        # La première est vide ie au dessus du premier \s
        list_text, list_stype = fonc.split_perso(
            [text],
            settings.GENSETTINGS.get("Syntax", "newslide"),
            list_stype,
            0,
        )
        del list_text[0]

        # Suprime les doublons
        new_list_text = []
        new_list_stype = []
        must_be_new_diapo = set()
        diapo_count = 0
        to_ignore = [
            self._newLineSuggest,
            settings.GENSETTINGS.get("Syntax", "newline"),
        ]
        for i, text in enumerate(list_text):
            nb_words = len(text.split(" "))
            match = 0.0
            for text_ref in new_list_text:
                match = max(self._match_para(text_ref, text, ignore=to_ignore), match)
            striped_text = text.replace(f" {self._newLineSuggest}", "")
            # This is sketchy: if number of words is small do not consider it
            # as duplicate as it would probably be merged into another diapo
            # This is valable only if the previous diapo was not removed
            if (
                (
                    (
                        nb_words < MIN_WORDS_FOR_DUPLICATE_CHECK
                        and diapo_count - 1 not in must_be_new_diapo
                    )
                    or match < MIN_MATCH_FOR_DUPLICATE_CHECK  # this is very sensible
                )
                and text.find("\\...") == -1
                and striped_text
            ):
                new_list_text.append(text)
                new_list_stype.append(list_stype[i])
                diapo_count += 1
            else:
                must_be_new_diapo.add(diapo_count - 1)
        list_text = new_list_text
        list_stype = new_list_stype

        list_stype_plus = gestchant.get_list_stype_plus(list_stype)

        # Fusion et creation des diapos
        for elem in list_stype_plus:
            text = ""
            for i, num_diapo in enumerate(elem[1]):
                text = f"{text}\n{list_text[num_diapo]}\n"
                text = self._clean(text)
                nb_lines = text.count("\n")
                try:
                    next_text = list_text[num_diapo + 1]
                    self._clean(next_text)
                    next_nb_lines = next_text.count("\n")
                except IndexError:
                    next_nb_lines = 0
                text_no_chords = fonc.supress_b(text, "\\ac", "\n")
                if (
                    num_diapo in must_be_new_diapo
                    or num_diapo == elem[1][-1]
                    or (
                        elem[0] == "\\ss"
                        and (
                            len(text_no_chords) > MAX_CHARS_PER_DIAPO
                            or nb_lines + next_nb_lines > MAX_LINES_PER_DIAPO
                            # If there is allready a new diapo that must be created dont do it with this criteria
                            or (
                                len(elem[1]) % 2 == 1
                                and set(elem[1]).intersection(must_be_new_diapo)
                                == set()
                            )
                            or i % 2 == 1
                        )
                    )
                ):
                    if elem[0] in ["\\sc", "\\spc"]:
                        max_car = 85 if text.find("\\ac") != -1 else 95
                    elif text.find("\\ac") != -1:
                        max_car = 90
                    else:
                        max_car = 100
                    diapo = classDiapo.Diapo(
                        self.element,
                        len(self._diapos) + 1,
                        elem[0],
                        max_car,
                        len(list_stype_plus),
                        text.strip("\n"),
                    )
                    self._diapos.append(diapo)
                    text = ""
        return self._diapos

    def _clean(self, text):
        for _ in range(5):
            text = text.replace("\n\n\n", "\n\n")
            text = text.replace(
                f"{self._newlineMarker}{self._newlineMarker}",
                self._newlineMarker,
            )
            text = text.replace(f"\n{self._newlineMarker}\n", "\n\n")
        text = text.strip("\n")
        return fonc.strip_perso(text, self._newlineMarker)

    def escape(self, input_data):
        """
        Adds a backslash behind latex special characters
        """
        if isinstance(input_data, str):
            output = input_data
            for char in self._specialChar:
                output = output.replace(char, f"\\{char}")
        elif isinstance(input_data, list):
            output = []
            for text_item in input_data:
                clean_text = str(text_item)
                for char in self._specialChar:
                    clean_text = clean_text.replace(char, f"\\{char}")
                output.append(clean_text)
        else:
            msg = f'Input "{input_data}"must be str or list, but is {type(input_data)}.'
            raise Exception(
                msg,
            )
        return output


class ExportLatex(ExportBase):
    def __init__(self, element, title_level=1, export_settings=None):
        ExportBase.__init__(self, element, title_level, export_settings=export_settings)
        self._newlineMarker = r"\\"
        self._supportedTypes = ["latex", "verse"]
        self._specialChar = ["#", "_"]

    @property
    def export_text(self):
        if self.etype == "song":
            self.etype = "latex"
        if self.etype not in self._supportedTypes:
            self.etype = "song"
            return ""
        # ~ if self._exportedText != '':
        # ~ self.etype = 'song'
        # ~ return self._exportedText
        self._get_diapos()
        text = "\n\n".join([diapo.latex for diapo in self._diapos])
        text = self.escape(text)
        text = text.replace(r"\ac", self._chordsMarker)
        text = text.replace("\n", f"{self._newlineMarker}\n")
        text = text.replace(f"\n{self._newlineMarker}", "\n")
        text = text.replace(f"\n\\tab {self._newlineMarker}", "\n")

        # Move chords to left side when there is no lyrics
        # Add a new line after each intro chord line
        regex_chord_pattern = r"(\\tab )?\t\\hspace\*\{\\fill\}"
        text = re.sub(
            f"^({regex_chord_pattern} .*$)",
            r"\1\n",
            text,
            flags=re.MULTILINE,
        )
        # Remove new line bewteen intro chords
        text = re.sub(
            f"^\n({regex_chord_pattern} .*$)",
            r"\1",
            text,
            flags=re.MULTILINE,
        )
        # Remove tabs, spaces and alignment
        text = re.sub(f"^{regex_chord_pattern} ", r"\1", text, flags=re.MULTILINE)

        text = self._clean(text)
        self._nbLignes = len(text.splitlines())

        # Capo
        if self._export_settings.get("Export_Parameters", "capo") and self.capo:
            text = f"\\emph{{Capo {self.capo!s}}}{self._newlineMarker}\n{text}"

        # Title
        text = f"\\begin{{figure}}\n\\section{{{self.escape(self.title)}}}\n{text}\n\\end{{figure}}\n"

        # Song per page
        if self._export_settings.get("Export_Parameters", "one_song_per_page"):
            text = f"{text}\n\\clearpage"

        self._exportedText = text
        self.etype = "song"
        return text

    @property
    def title(self):
        # Title key
        if self._export_settings.get("Export_Parameters", "printkey"):
            chord = accords.Accords(
                self.key,
                transpose_nb=self.transpose,
                capo=self.capo,
                export_settings=self._export_settings,
            )
            key = chord.get_chords()[0]
            if key != "":
                key = f"~--~\\emph{{{key}}}"
        else:
            key = ""
        if self.tempo and self._export_settings.get("Export_Parameters", "printtempo"):
            tempo = f"~--~\\emph{{{self.tempo}}}bpm"
        else:
            tempo = ""

        # Reference in title
        if self._export_settings.get("Export_Parameters", "printref") and self.ccli:
            ref_id = f" ({self.ccli})"
        else:
            ref_id = ""

        # Title
        return f"{self.element.title}{ref_id}{key}{tempo}"


class ExportMarkdown(ExportBase):
    def __init__(self, element, title_level=1, export_settings=None):
        ExportBase.__init__(self, element, title_level, export_settings=export_settings)
        self._newlineMarker = "  "
        self._supportedTypes = ["markdown"]
        self._specialChar = ["*", "_"]

    @property
    def export_text(self):
        if self.etype == "song":
            self.etype = "markdown"
        if self.etype not in self._supportedTypes:
            self.etype = "song"
            return ""
        # ~ if self._exportedText != '':
        # ~ self.etype = 'song'
        # ~ return self._exportedText
        self._get_diapos()
        text = "\n\n".join([diapo.markdown for diapo in self._diapos])
        text = f"{text}\n"
        deb = 0
        fin = 0
        to_find_start = "\\ac"
        to_find_end = "\n"
        while deb != -1:
            deb = text.find(to_find_start, fin)
            fin = text.find(to_find_end, deb)
            if deb == -1 or fin == -1:
                break
            text = "{}`{}`\n{}".format(
                text[:deb],
                text[deb + len(to_find_start) : fin].strip(" "),
                text[fin + len(to_find_end) :],
            )
            fin -= len(to_find_start) + 2

        text = text.replace("\n", f"{self._newlineMarker}\n")
        text = text.replace("~~", "  ")
        text = self._clean(text)
        text = f"{text}\n"
        self._nbLignes = len(text.splitlines())

        # Capo
        if self._export_settings.get("Export_Parameters", "capo") and self.capo:
            text = f"*Capo {self.capo!s}*  \n{text}"

        # Title key
        if self.key and self._export_settings.get("Export_Parameters", "printkey"):
            chord = accords.Accords(
                self.key,
                transpose_nb=self.transpose,
                capo=self.capo,
                export_settings=self._export_settings,
            )
            key = chord.get_chords()[0]
            if key != "":
                key = f" -- *{key}*"
        else:
            key = ""

        tempo = ""
        if self.tempo and self._export_settings.get("Export_Parameters", "printtempo"):
            tempo = f" -- *{self.tempo}bpm*"
        else:
            tempo = ""

        # Title
        title = f"{'#' * self._title_level} {self.title}{key}{tempo}\n"

        if not self._export_settings.get("Export_Parameters", "list"):
            text = f"{title}{text}"
        else:
            text = f"{title}"

        self._exportedText = text
        self.etype = "song"
        return text


class ExportBeamer(ExportBase):
    def __init__(self, element, title_level=1, export_settings=None):
        ExportBase.__init__(self, element, title_level, export_settings=export_settings)
        self._newlineMarker = "\\\\"
        self._supportedTypes = ["beamer", "image", "verse"]
        self._specialChar = ["#", "_"]

    @property
    def export_text(self):
        if self.etype == "song":
            self.etype = "beamer"
        if self.etype not in self._supportedTypes:
            self.etype = "song"
            return ""
        # ~ if self._exportedText != '':
        # ~ self.etype = 'song'
        # ~ return self._exportedText
        self._diapos = []
        text = ""
        for diapo in self.diapos:
            to_add = self.escape(diapo.beamer)
            to_add = to_add.replace("\n", f"{self._newlineMarker}\n")
            to_add = to_add.replace(f"\n{self._newlineMarker}", "\n")
            back_str = diapo.background_name.replace("\\", "/")
            back_str = f'"{fonc.get_path(back_str)}/{fonc.get_file_name(back_str)}"{fonc.get_ext(back_str)}'
            text += f"\\newframe{{{back_str}}}\n{to_add}\n\\end{{frame}}\n\n"
        text = self._clean(text)
        self._nbLignes = len(text.splitlines())
        text = fonc.no_new_line(text, "\\newframe", self._newlineMarker)
        text = fonc.no_new_line(text, "\\vspace", self._newlineMarker)
        text = f"{text}\n"
        self._exportedText = text
        self.etype = "song"
        return text


class ExportHtml(ExportBase):
    def __init__(
        self,
        element,
        title_level=1,
        markdowner=None,
        html_style=None,
        html_style_path=None,
        export_settings=None,
    ):
        ExportBase.__init__(self, element, title_level, export_settings=export_settings)
        self._element = element
        self._supportedTypes = ["markdown"]
        if markdowner:
            self._markdowner = markdowner
        else:
            import markdown  # Consumes lots of memory

            self._markdowner = markdown.Markdown()
        self._htmlStyle = html_style

        if not html_style_path:
            html_style_path = os.path.join(
                songfinder.__dataPath__,
                "htmlTemplates",
                "defaultStyle.html",
            )
        if not html_style and os.path.isfile(html_style_path):
            with codecs.open(html_style_path, "r", encoding="utf-8") as style_file:
                self._htmlStyle = style_file.read()

    def _add_title(self, text):
        if self.title:
            text = f"<title>{self.title}</title>\n{text}"
        return text

    @property
    def export_text(self):
        if self.etype == "song":
            self.etype = "markdown"
        if self.etype not in self._supportedTypes:
            self.etype = "song"
            return ""
        markdown_text = ExportMarkdown(
            self._element,
            title_level=self._title_level,
            export_settings=self._export_settings,
        ).export_text

        text = self._markdowner.convert(markdown_text)
        if self._title_level == 1:
            text = self._add_title(text)
        if self._htmlStyle:
            text = self._htmlStyle.replace("@@body@@", text)
        self._markdowner.reset()
        self._exportedText = text
        self.etype = "song"
        return text
