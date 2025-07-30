import codecs
import contextlib
import logging
import os
import re
import string
import traceback
import xml.etree.ElementTree as ET

from songfinder import classPaths, gestchant, pyreplace
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder import messages as tkMessageBox
from songfinder.elements import Element, cdlparser

logger = logging.getLogger(__name__)

RECEUILS = [
    "JEM",
    "ASA",
    "WOC",
    "HER",
    "HEG",
    "FAP",
    "MAR",
    "CCO",
    "PBL",
    "LDM",
    "JFS",
    "THB",
    "EHO",
    "ALG",
    "BLF",
    "ALR",
    "HLS",
    "IMP",
    "PNK",
    "DNL",
    "ROG",
    "WOC",
    "SOL",
    "FRU",
    "OST",
    "ENC",
    "DIV",
]


class Chant(Element):
    def __init__(self, chant, nom=""):
        self.etype = "song"
        self.extention = fonc.get_ext(chant)
        if self.extention == "" and chant.find("http") == -1:
            self.extention = settings.GENSETTINGS.get("Extentions", "song")[0]
            chant = chant + self.extention
        self.chemin = chant

        Element.__init__(self, chant, self.etype, self.chemin)
        self.nom = fonc.get_file_name(self.chemin)

        self._title = nom
        self._song_book = ""
        self.reset()

    def _get_cdl(self):
        parsed_song = cdlparser.CDLParser(self.chemin)
        # Text should be the first to be get because other depends on it
        # Infinite loop is possible if text is not first
        self.text = parsed_song.text
        self.key = parsed_song.key
        self.hymn_number = parsed_song.hymn_number
        self.song_book = parsed_song.song_book
        self.title = parsed_song.title
        self.copyright = parsed_song.copyright
        self.tags = parsed_song.tags
        self.author = parsed_song.authors
        file_name = str(parsed_song) + settings.GENSETTINGS.get("Extentions", "song")[0]
        root_path = classPaths.PATHS.songs
        self.chemin = os.path.join(root_path, file_name)

    def reset(self):
        self._reset_text()
        self._transpose = None
        self._capo = None
        self._key = None
        self._turfNumber = None
        self._hymnNumber = None
        self._tempo = None

    def _reset_text(self):
        self._text = None
        self._words = ""
        self._textHash = None
        self.reset_diapos()

    def __save__(self):
        # This function is keept for hidden functionality
        # This is probably not the function you actualy want to edit
        # Look at database save method

        # We use a different xml lib here because it does not add carriage return on Windows for writes
        # There might be a way to use xml.etree.cElementTree that don't but have not figured out
        # xml.etree.cElementTree is faster at parsing so keep it for song parsing
        import lxml.etree as ET_write

        ext = settings.GENSETTINGS.get("Extentions", "song")[0]
        if fonc.get_ext(self.chemin) != ext:
            self.chemin = f"{self.song_book}{self.hymn_number}_{self.title}"
        try:
            tree = ET_write.parse(self.chemin)
            chant_xml = tree.getroot()
        except OSError:
            chant_xml = ET_write.Element(self.etype)
        self.safe_update_xml(chant_xml, "lyrics", self.text)
        self.safe_update_xml(chant_xml, "title", self.title)
        self.safe_update_xml(chant_xml, "sup_info", self.sup_info)
        self.safe_update_xml(chant_xml, "transpose", self.transpose)
        self.safe_update_xml(chant_xml, "capo", self.capo)
        self.safe_update_xml(chant_xml, "key", self.key)
        self.safe_update_xml(chant_xml, "tempo", self.tempo)
        self.safe_update_xml(chant_xml, "turf_number", self.turf_number)
        self.safe_update_xml(chant_xml, "hymn_number", self.hymn_number)
        self.safe_update_xml(chant_xml, "author", self.author)
        self.safe_update_xml(chant_xml, "copyright", self.copyright)
        self.safe_update_xml(chant_xml, "ccli", self.ccli)
        self.safe_update_xml(chant_xml, "tags", self.tags)
        fonc.indent(chant_xml)

        tree = ET_write.ElementTree(chant_xml)
        tree.write(self.chemin, encoding="UTF-8", xml_declaration=True)
        self.reset_diapos()

    def _replace_in_text(self, to_replace, replace_by):
        self.text = self.text.replace(to_replace, replace_by)
        self.__save__()

    @property
    def nums(self):
        return {
            "custom": self.custom_number,
            "turf": self.turf_number,
            "hymn": self.hymn_number,
        }

    @property
    def turf_number(self):
        self.text  # pylint: disable=pointless-statement
        return self._turfNumber

    @property
    def hymn_number(self):
        self.text  # pylint: disable=pointless-statement
        return self._hymnNumber

    @property
    def custom_number(self):
        match = re.match("([A-Z]{3})(\\d{3,4})", self.nom)
        if match:
            self._customNumber = int(match.group(2))
            return self._customNumber
        return None

    @property
    def transpose(self):
        self.text  # pylint: disable=pointless-statement
        return self._transpose

    @property
    def capo(self):
        self.text  # pylint: disable=pointless-statement
        return self._capo

    @property
    def key(self):
        self.text  # pylint: disable=pointless-statement
        return self._key

    @property
    def tempo(self):
        self.text  # pylint: disable=pointless-statement
        return self._tempo

    @property
    def author(self):
        self.text  # pylint: disable=pointless-statement
        return self._author

    @property
    def copyright(self):
        self.text  # pylint: disable=pointless-statement
        return self._copyright

    @property
    def ccli(self):
        if self.song_book and self.hymn_number:
            return f"{self.song_book}{self.hymn_number:>04}"
        return None

    @property
    def text(self):
        if self._text is None:
            cdl_path = settings.GENSETTINGS.get("Paths", "conducteurdelouange")
            if fonc.get_ext(self.chemin) in settings.GENSETTINGS.get(
                "Extentions",
                "chordpro",
            ):
                self._get_chord_pro()
            elif fonc.get_ext(self.chemin) in settings.GENSETTINGS.get(
                "Extentions",
                "song",
            ):
                self._get_xml()
            elif self.chemin.find(cdl_path) != -1:
                self._get_cdl()
            else:
                logger.warning(f'Unknown file format for "{self.chemin}".')
        return self._text

    def _get_xml(self):
        self.reset()
        try:
            tree = ET.parse(self.chemin)
            chant_xml = tree.getroot()
        except OSError:
            logger.warning(
                f'Not able to read "{self.chemin}"\n{traceback.format_exc()}',
            )
            self.title = self.nom
            chant_xml = ET.Element(self.etype)
        except ET.ParseError:
            logger.info(f"Error on {self.chemin}:\n{traceback.format_exc()}")
            tkMessageBox.showerror(
                "Erreur",
                f'Le fichier "{self.chemin}" est illisible.',
            )
            return

        self._parse_xml_attributes(chant_xml)
        self._parse_xml_numeric_attributes(chant_xml)
        self._parse_xml_text_attributes(chant_xml)

    @transpose.setter
    def transpose(self, value):
        with contextlib.suppress(AttributeError):
            value = value.strip("\n")
        try:
            self._transpose = int(value)
        except (ValueError, TypeError):
            if not value:
                self._transpose = 0
            else:
                self._transpose = None

    @capo.setter
    def capo(self, value):
        with contextlib.suppress(AttributeError):
            value = value.strip("\n")
        try:
            self._capo = int(value)
        except (ValueError, TypeError):
            if not value:
                self._capo = 0
            else:
                self._capo = None

    @tempo.setter
    def tempo(self, value):
        with contextlib.suppress(AttributeError):
            value = value.strip("\n")
        try:
            self._tempo = int(value)
        except (ValueError, TypeError):
            if not value:
                self._tempo = 0
            else:
                self._tempo = None

    @turf_number.setter
    def turf_number(self, value):
        with contextlib.suppress(AttributeError):
            value = value.strip("\n")
        try:
            self._turfNumber = int(value)
        except (ValueError, TypeError):
            if not value:
                self._turfNumber = 0
            else:
                self._turfNumber = None

    @hymn_number.setter
    def hymn_number(self, value):
        with contextlib.suppress(AttributeError):
            value = value.strip("\n")
        try:
            self._hymnNumber = int(value)
        except (ValueError, TypeError):
            if not value:
                self._hymnNumber = 0
            else:
                self._hymnNumber = None

    @key.setter
    def key(self, value):
        self._key = value.strip(" \n")

    @text.setter
    def text(self, value):
        self._reset_text()
        value = fonc.supress_b(value, "[", "]")  ######
        value = gestchant.nettoyage(value)
        value = f"{value}\n"
        self._text = value

    @author.setter
    def author(self, value):
        self._author = value.replace("\n", " ").replace("  ", " ").strip(" ")

    @copyright.setter
    def copyright(self, value):
        self._copyright = value.strip(" \n")

    @property
    def words(self):
        if not self._words:
            text = gestchant.netoyage_paroles(self.text)
            self._words = text.split()
            nb_words = 3
            add_list = [
                " ".join(self._words[i : i + nb_words])
                for i in range(max(len(self._words) - nb_words + 1, 0))
            ]
            self._words += add_list
        return self._words

    @property
    def song_book(self):
        if not self._song_book:
            match = re.match("([A-Z]{3})\\d{3,4}", self.nom)
            if match:
                self._song_book = match.group(1)
        return self._song_book

    SONG_BOOK_LENGTH = 3

    @song_book.setter
    def song_book(self, in_song_book):
        in_str = str(in_song_book).strip(" \n")
        if in_str == "":
            in_str = "SUP"
        if len(in_str) != self.SONG_BOOK_LENGTH:
            msg = f"Song book must be {self.SONG_BOOK_LENGTH} characters long but got: '{in_str}'"
            raise ValueError(
                msg,
            )
        self._song_book = in_str.upper()

    def _get_chord_pro(self):
        try:
            with codecs.open(self.chemin, encoding="utf-8") as f:
                brut = f.read()
                if not brut:
                    logger.warning(
                        f'File "{self.chemin}" is empty\n{traceback.format_exc()}',
                    )
                    return ""
        except OSError:
            logger.warning(
                f'Not able to read "{self.chemin}"\n{traceback.format_exc()}',
            )
            return ""

        def get_cp(char):
            return re.search(f"{{{char}:(.*)}}", brut).group(1)

        self.title = get_cp("t")
        self.author = get_cp("st")
        self.copyright = get_cp("c")
        self.key = get_cp("key")
        ccli_brut = re.search("{c: *(jemaf.fr|shir.fr).*([A-Z]{3})(\\d{3,4})}", brut)
        self.song_book = ccli_brut.group(2)
        self.hymn_number = ccli_brut.group(3)

        brut = pyreplace.cleanup_char(brut.encode("utf-8"))
        brut = pyreplace.cleanup_space(brut).decode("utf-8")

        # Interprete chorpro syntax
        if re.search("{c: *shir.fr.*}", brut):
            brut = " \\ss\n" + brut
            brut = re.sub("\n\n", "\\n\\n\\\\ss\\n", brut)
            brut = re.sub("{(eoc|start_of_verse|sov)}", "\\n\\n\\\\ss\\n", brut)
            brut = re.sub("{(start_of_chorus|soc)}", "\\n\\n\\\\sc\\n", brut)
        else:
            brut = re.sub("\\W\\d\\.\\W", "", brut)
            brut = re.sub("{c: ?Strophe(.*?)}", "\\n\\n\\\\ss\\n", brut)
            brut = re.sub("{c: ?Refrain(.*?)}", "\\n\\n\\\\sc\\n", brut)
        brut = re.sub("{c: ?Pont(.*?)}", "\\n\\n\\\\sb\\n", brut)

        brut = re.sub("{.*?}", "", brut)

        brut = gestchant.nettoyage(brut)
        brut = gestchant.nettoyage(brut)
        brut = brut.replace("\\ss\n\n\\sc", "\\sc")
        brut = brut.replace("\\ss\n\n\\sb", "\\sb")

        # Put double back slash at the last chord of each line
        brut = brut + "\n"
        fin = len(brut)
        got_to_the_limit = True
        for _ in range(1000):
            if fin == -1:
                got_to_the_limit = False
                break
            line = brut.rfind("\n", 0, fin)
            fin = brut.rfind("]", 0, line)
            if line == fin + 1:
                precedant = fin
                while brut[precedant] == "]":
                    precedant = brut.rfind("[", 0, precedant) - 1
                brut = (
                    brut[: precedant + 2]
                    + ""
                    + brut[precedant + 2 : fin]
                    + "\\"
                    + brut[fin:]
                )
            else:
                brut = brut[:fin] + "\\" + brut[fin:]
        if got_to_the_limit:
            logger.error(
                f"Could not properly handle chords for '{self.chemin}', stoping now",
            )
        brut = fonc.strip_perso(brut, "\\\n")

        # Remove space after chord
        for letter in string.ascii_uppercase[:7]:
            brut = brut.replace(f"\n[{letter}] ", f"\n[{letter}]")
        brut = self._convert_chords_format(brut)
        self.text = brut
        return brut

    def _convert_chords_format(self, text):
        if text != "":
            text = text + "\n"
            list_chords = fonc.get_b(text, "[", "]")
            where = 0
            last = 0
            for i, chord in enumerate(list_chords):
                # Add parenthesis for chord at end of lines
                if chord.find("\\") != -1:
                    to_add = (
                        "\\ac "
                        + " ".join(list_chords[last : i + 1]).replace("\\", "")
                        + "\n"
                    )
                    where = text.find(chord, where)
                    where = text.find("\n", where) + 1
                    text = text[:where] + to_add + text[where:]
                    last = i + 1
            text = fonc.strip_perso(text, "\n")

            text = fonc.supress_b(text, "[", "]")

            for newslide in settings.GENSETTINGS.get("Syntax", "newslide")[0]:
                text = text.replace(f"{newslide}\n\n\\ac", f"{newslide}\n\\ac")
            return text
        return ""

    def __ne__(self, other):
        return not self == other

    SIMILARITY_THRESHOLD = 0.93

    def __eq__(self, other):
        if not isinstance(other, Chant):
            msg = f"Expected instance of '{self.__class__.__name__}', but got instance of '{type(other)}'"
            raise TypeError(
                msg,
            )
        if not self.words and not other.words:
            return bool(self.title == other.title and self.sup_info == other.sup_info)
        my_words = set(self.words)
        other_words = set(other.words)
        commun = len(my_words & other_words)
        ratio = 2 * commun / (len(my_words) + len(other_words))
        return ratio > self.SIMILARITY_THRESHOLD

    def __hash__(self):
        return hash(repr(self))

    def __gt__(self, other):
        return self.title > other.title

    def __ge__(self, other):
        return self.title >= other.title

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.chemin}')"

    def _parse_xml_attributes(self, chant_xml):
        try:
            self.sup_info = chant_xml.find("sup_info").text
        except (AttributeError, KeyError):
            self.sup_info = ""

    def _parse_xml_numeric_attributes(self, chant_xml):
        self._transpose = self._get_xml_int(chant_xml, "transpose")
        self._capo = self._get_xml_int(chant_xml, "capo")
        self._tempo = self._get_xml_int(chant_xml, "tempo")
        self._hymnNumber = self._get_xml_int(chant_xml, "hymn_number")
        self._turfNumber = self._get_xml_int(chant_xml, "turf_number")

    def _parse_xml_text_attributes(self, chant_xml):
        self.title = self._get_xml_text(chant_xml, "title")
        self.text = self._get_xml_text(chant_xml, "lyrics")
        self._key = self._get_xml_text(chant_xml, "key").replace("\n", "")
        self._author = self._get_xml_text(chant_xml, "author")
        self._copyright = self._get_xml_text(chant_xml, "copyright")
        self._parse_song_book(chant_xml)
        self.tags = self._get_xml_text(chant_xml, "tags")

    def _get_xml_int(self, chant_xml, tag):
        try:
            return int(chant_xml.find(tag).text)
        except (AttributeError, KeyError, ValueError, TypeError):
            return None

    def _get_xml_text(self, chant_xml, tag):
        try:
            return chant_xml.find(tag).text or ""
        except (AttributeError, KeyError):
            return ""

    def _parse_song_book(self, chant_xml):
        try:
            ccli = chant_xml.find("ccli").text.replace(" ", "")
            match = re.match("([A-Z]{3})\\d{3,4}", ccli)
            if match:
                self._song_book = match.group(1)
        except (AttributeError, KeyError):
            self._song_book = ""

    def __str__(self):
        out = f"{self.etype} -- "
        num = self._hymnNumber or self._turfNumber or self._customNumber
        if self.song_book and num:
            out = f"{out}{self.song_book}{num:04d} "
        out = f"{out}{self.title}"
        if self.sup_info:
            out = f"{out} ({self.sup_info})"
        return out
