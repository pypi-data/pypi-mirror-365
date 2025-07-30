import contextlib
import re
import warnings
from enum import Enum

from songfinder import classSettings as settings
from songfinder import corrector, dataAccords
from songfinder import fonctions as fonc

ACCORDSDATA = dataAccords.AccordsData()
CORRALL = corrector.Corrector(";".join(ACCORDSDATA.accPossible))

language = Enum("language", ["FR", "EN", "DEG"])


class Accords:
    def __init__(
        self,
        ligne_acc,
        data=ACCORDSDATA,
        transpose_nb=0,
        capo=0,
        corr_all=CORRALL,
        export_settings=settings.LATEXSETTINGS,
    ):
        self.data = data
        self._ligneAcc = ligne_acc
        self._transpose_nb = transpose_nb
        self._capo = capo
        self._accords = []

        self.corrAll = corr_all
        self.data = data
        self._export_settings = export_settings

        self._haveLeftBracket = set()
        self._haveRightBracket = set()

        self._clean()
        self._get_ligne()
        self._compact_chord()

    def get_chords(self, key=None):
        if self._export_settings.get("Export_Parameters", "transpose"):
            self._transpose(self._transpose_nb)
        if self._export_settings.get("Export_Parameters", "capo") and self._capo:
            self._transpose(-self._capo)
        if self._export_settings.get("Export_Parameters", "simple_chords"):
            self._simplify_chord()
        if self._export_settings.get("Export_Parameters", "keep_first"):
            self._keep_first()
        if self._export_settings.get("Export_Parameters", "keep_last"):
            self._keep_last()
        if self._export_settings.get("Export_Parameters", "sol_chords"):
            self._translate(language.FR)
        if (
            self._export_settings.get("Export_Parameters", "num_chords")
            and key is not None
        ):
            self._translate(language.DEG, key=key)
        self._put_brackets()
        self._no_doublon()
        return self._accords

    def _no_doublon(self):
        new_chords = []
        previous = None
        for accord in self._accords:
            if not previous or accord.replace(")", "") != previous.replace("(", ""):
                new_chords.append(accord)
            elif accord.find(")") != -1:
                new_chords[-1] = f"{new_chords[-1]})"
            previous = accord
        self._accords = new_chords

    def _clean(self):
        if not self._ligneAcc:
            warnings.warn("Empty chord", stacklevel=2)
            self._ligneAcc = ""
            return

        self._ligneAcc = self._ligneAcc.strip(" ")
        self._ligneAcc = fonc.strip_perso(self._ligneAcc, "\n")
        self._ligneAcc = fonc.strip_perso(self._ligneAcc, "\\ac")
        self._ligneAcc = self._ligneAcc.strip(" ")

        for _ in range(5):
            self._ligneAcc = self._ligneAcc.replace("  ", " ")

    def _get_ligne(self):
        self._accords = self._ligneAcc.split(" ")
        # Check if has brackets and removes them
        for i, accord in enumerate(self._accords):
            new_accord = accord
            if new_accord:
                if new_accord.startswith("("):
                    self._haveLeftBracket.add(i)
                    new_accord = new_accord[1:]
                if new_accord.endswith(")"):
                    self._haveRightBracket.add(i)
                    new_accord = new_accord[:-1]
            self._accords[i] = new_accord

        self._translate(language.EN)

        for i, accord in enumerate(self._accords):
            if not accord:  # Handle empty string after split
                continue

            if accord[:2] in self.data.execpt:
                new_accord = self.data.execpt[accord[:2]] + accord[2:]
            else:
                new_accord = accord

            if self.corrAll:
                new_accord = "/".join(
                    [self.corrAll.check(partAcc) for partAcc in new_accord.split("/")],
                )
            parts = new_accord.split("/")
            for j, part in enumerate(parts):
                with contextlib.suppress(KeyError):
                    parts[j] = self.data.execpt[part]
            self._accords[i] = "/".join(parts)

    def _put_brackets(self):
        for index in self._haveLeftBracket:
            self._accords[index] = f"({self._accords[index]}"
        for index in self._haveRightBracket:
            self._accords[index] = f"{self._accords[index]})"

    def _translate(self, lang=language.FR, key=None):
        for i, chord in enumerate(self._accords):
            parts = chord.split("/")
            for j, part in enumerate(parts):
                # Ignore multiplication in chords, that is normal
                if re.match(r"x\d{1,2}", part, flags=re.IGNORECASE):
                    break
                parts[j] = str(Chord(fonc.upper_first(part)).translate(lang, key=key))
            self._accords[i] = "/".join(parts)

    def _compact_chord(self):
        for i, chord in enumerate(self._accords):
            new_chord = chord
            for old, new in self.data.dicoCompact.items():
                new_chord = new_chord.replace(old, new)
            self._accords[i] = new_chord

    def _simplify_chord(self):
        for i, chord in enumerate(self._accords):
            parts = chord.split("/")
            for j, part in enumerate(parts):
                parts[j] = str(Chord(part).simplify)
            self._accords[i] = "/".join(parts)

    def _keep_first(self):
        for i, chord in enumerate(self._accords):
            self._accords[i] = chord.split("/")[0]

    def _keep_last(self):
        for i, chord in enumerate(self._accords):
            try:
                self._accords[i] = chord.split("/")[1]
            except IndexError:
                self._accords[i] = chord.split("/")[0]

    def _nb_alt(self, accords):
        ind = 0
        for i, diez in enumerate(self.data.ordreDiez):
            if f"{diez}#" in [accord[:2] for accord in accords]:
                ind = i + 1
        for i, bemol in enumerate(reversed(self.data.ordreDiez)):
            if f"{bemol}b" in [accord[:2] for accord in accords]:
                ind = i + 1
        return ind

    def _transpose_test(self, accords_ref, accords_non, demi_ton):
        # Transposition
        new_accords = []
        ref_alt = ""  # Initialize ref_alt to an empty string
        for chord in accords_ref:
            if len(chord) > 1:
                ref_alt = chord[-1]
                break

        for accord in self._accords:
            new_parts_list = []
            for part in accord.split("/"):
                if len(part) > 1 and part[1] in ["#", "b"] and part[1] != ref_alt:
                    new_part = accords_ref[accords_non.index(part[:2])] + part[2:]
                else:
                    new_part = part
                pre = (
                    f"{new_part[:1]} {new_part[1:]}".replace(" #", "#")
                    .replace(" b", "b")[:2]
                    .strip(" ")
                )
                for i, ref in enumerate(accords_ref):
                    if pre == ref:
                        new_part = new_part.replace(
                            ref,
                            accords_ref[(i + demi_ton) % len(accords_ref)],
                        )
                        break
                new_parts_list.append(new_part)
            new_accords.append("/".join(new_parts_list))
        return new_accords

    def _transpose(self, demi_ton):
        if demi_ton:
            accords1 = self._transpose_test(
                self.data.accordsDie,
                self.data.accordsBem,
                demi_ton,
            )
            accords2 = self._transpose_test(
                self.data.accordsBem,
                self.data.accordsDie,
                demi_ton,
            )
            if self._nb_alt(accords2) >= self._nb_alt(accords1):
                self._accords = accords1
            else:
                self._accords = accords2


class Chord:
    def __init__(self, chord_str):
        self._str = chord_str
        self._str = self._str.replace("Re", "Ré")

        self._check()

    def __str__(self):
        return self._str

    def __hash__(self):
        return hash(self.translate(language.EN)._str)  # noqa: SLF001

    def __eq__(self, other):
        return self.translate(language.EN)._str == other.translate(language.EN)._str

    def _check(self):
        work_chord = self.translate(language.EN)
        if not str(work_chord) or str(work_chord)[0] not in ACCORDSDATA.accordsTonang:
            warnings.warn(f"Unknown chord '{work_chord}'", stacklevel=2)

    @property
    def _is_major(self):
        return not re.match(r".+m", self._str)

    @property
    def _relative_major(self):
        if self._is_major:
            return self.translate(language.EN).sharp
        work_chord = self.translate(language.EN).sharp
        stripped_chord = re.sub(r"(.+)m", r"\1", str(work_chord))
        index = ACCORDSDATA.accordsDie.index(stripped_chord)
        relative_str = ACCORDSDATA.accordsDie[(index + 3) % 12]
        return Chord(relative_str)

    @property
    def _relative_minor(self):
        if self._is_major:
            work_chord = self.translate(language.EN).sharp
            index = ACCORDSDATA.accordsDie.index(str(work_chord))
            relative_str = ACCORDSDATA.accordsDie[(index - 3) % 12]
            return Chord(f"{relative_str}m")
        return self.translate(language.EN).sharp

    @property
    def sharp(self):
        if not re.search(r"b", self._str):
            return self.translate(language.EN)
        eng_chord = self.translate(language.EN)
        striped_chord = re.sub(r"([A-Z]b).*", r"\1", str(eng_chord))
        index = ACCORDSDATA.accordsBem.index(striped_chord)
        return Chord(ACCORDSDATA.accordsDie[index])

    @property
    def flat(self):
        if not re.search(r"#", self._str):
            return self.translate(language.EN)
        eng_chord = self.translate(language.EN)
        striped_chord = re.sub(r"([A-Z]#).*", r"\1", str(eng_chord))
        index = ACCORDSDATA.accordsDie.index(striped_chord)
        return Chord(ACCORDSDATA.accordsBem[index])

    @property
    def num(self):
        try:
            return ACCORDSDATA.accordsDie.index(str(self._relative_major))
        except ValueError:
            return ACCORDSDATA.accordsBem.index(str(self._relative_major))

    @property
    def simplify(self):
        simp_chord = str(self)
        for spe in ACCORDSDATA.modulation:
            simp_chord = simp_chord.replace(spe, "")
        return Chord(simp_chord)

    def _get_relative_notation(self, key):
        """Returns the chord numerotation notation relative to the given key.

        Args:
            key (str): The key to get the relative notation from (e.g. 'C', 'Am')

        Returns:
            str: Roman numeral notation of the chord relative to the key
        """
        if key is None:
            msg = "Reference key is None"
            raise ValueError(msg)

        # Convert key to Chord object for easier manipulation
        key_chord = Chord(key)

        # Get the major chord (if chord is minor, get its relative major)
        if key_chord._is_major:
            chord_major = self.simplify
        else:
            chord_major = self._relative_major.simplify

        # Get the major key reference (if key is minor, get its relative major)
        if key_chord._is_major:
            key_chord_major = key_chord
        else:
            key_chord_major = key_chord._relative_major

        # Calculate the interval between the chord and the key
        key_pos = key_chord_major.num
        chord_pos = chord_major.num
        interval = (chord_pos - key_pos) % 12

        # Define the roman numerals for major and minor
        major_numerals = ["I", "II", "III", "IV", "V", "VI", "VII"]
        minor_numerals = ["i", "ii", "iii", "iv", "v", "vi", "vii"]

        # Map intervals to scale degrees (0=I, 2=II, 4=III, 5=IV, 7=V, 9=VI, 11=VII)
        interval_to_degree = {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}

        # Get the scale degree
        if interval not in interval_to_degree:
            return "?"  # Return ? for chords not in the diatonic scale

        degree = interval_to_degree[interval]

        # Choose numerals based on chord quality
        numerals = minor_numerals if not self._is_major else major_numerals

        # If chord is minor key, shift the numerals
        if not self._is_major:
            degree = (degree - 2) % 7

        # If key is minor, shift the numerals
        if not key_chord._is_major:
            degree = (degree + 2) % 7

        return re.sub(
            pattern=rf"{self.simplify}(.*)",
            repl=rf"{numerals[degree]}\1",
            string=str(self),
        )

    def translate(self, lang, key=None):
        assert lang in language

        if lang == language.DEG:
            return self._get_relative_notation(key)

        from_chords, to_chords = [], []
        from_m7, to_m7 = "", ""
        if lang == language.FR:
            from_chords, to_chords = ACCORDSDATA.accordsTonang, ACCORDSDATA.accordsTon
            from_m7, to_m7 = "M7", "7M"
        elif lang == language.EN:
            from_chords, to_chords = ACCORDSDATA.accordsTon, ACCORDSDATA.accordsTonang
            from_m7, to_m7 = "7M", "M7"

        for i, chord in enumerate(from_chords):
            base_translation = to_chords[i]
            translation = re.sub(
                pattern=rf"{chord}(.*)",
                repl=rf"{base_translation}\1",
                string=str(self),
            )
            if translation != self._str and translation not in ["Faa", "Réo"]:
                return Chord(translation.replace(from_m7, to_m7))
        return self
