import codecs
import errno
import logging
import os
import re
import time

import songfinder
from songfinder import classSet, elements
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder.elements import exports

logger = logging.getLogger(__name__)


class Converter:
    def __init__(self, html_style_path=None, export_settings=None, do_decline=False):
        import markdown  # Consumes lots of memory

        self._markdowner = markdown.Markdown()
        self._songExtentions = settings.GENSETTINGS.get(
            "Extentions",
            "chordpro",
        ) + settings.GENSETTINGS.get("Extentions", "song")
        self._listeExtentions = settings.GENSETTINGS.get("Extentions", "liste")
        self._set = classSet.Set()

        self._dateList = dict()
        self._doDecline = do_decline
        self._toDecline = set()
        self._decliningPass = False
        self._counter = 0
        self._makeSubDir = False
        self._elementDict = dict()

        if not export_settings:
            self._export_settings = settings.LATEXSETTINGS
        else:
            self._export_settings = export_settings
        self._export_settingsOrig = self._export_settings

        self._declineFunctionsSetter = (
            self._set_list_options,
            self._set_bass_options,
            self._set_guitare_options,
        )

        if not html_style_path:
            html_style_path = os.path.join(
                songfinder.__dataPath__,
                "htmlTemplates",
                "defaultStyle.html",
            )
        if os.path.isfile(html_style_path):
            with codecs.open(html_style_path, "r", encoding="utf-8") as style_file:
                self._htmlStyle = style_file.read()
        else:
            self._htmlStyle = ""

    def _set_default_options(self):
        self._export_settings = self._export_settingsOrig
        self._export_settings.set("Export_Parameters", "sol_chords", True)
        self._suffix = ""

    def _set_list_options(self):
        self._set_default_options()
        self._export_settings.set("Export_Parameters", "list", True)
        self._suffix = "_list"

    def _set_bass_options(self):
        self._set_default_options()
        self._export_settings.set("Export_Parameters", "keep_last", True)
        self._export_settings.set("Export_Parameters", "simple_chords", True)
        self._suffix = "_bass"

    def _set_guitare_options(self):
        self._set_default_options()
        self._export_settings.set("Export_Parameters", "keep_first", True)
        self._export_settings.set("Export_Parameters", "capo", True)
        self._export_settings.set("Export_Parameters", "simple_chords", True)
        self._suffix = "_guitar"

    def markdown(self, input_files, output_files, verbose=True):
        self._exportClass = exports.ExportMarkdown
        self._optionSongs = {"export_settings": self._export_settings}
        self._optionSets = {"export_settings": self._export_settings, "title_level": 2}
        self._ext = ".md"
        self._titleMark = "# @@title@@\n"
        self._bodyMark = ""
        if verbose:
            logger.info(f'Converting files in "{input_files}" to markdown.')
        self._convert(input_files, output_files, verbose)

    def latex(self, input_files, output_files, verbose=True):
        self._exportClass = exports.ExportLatex
        self._optionSongs = {"export_settings": self._export_settings}
        self._optionSets = {"export_settings": self._export_settings}
        self._ext = ".tex"
        self._titleMark = "@@title@@\n"
        self._bodyMark = ""
        if verbose:
            logger.info(f'Converting files in "{input_files}" to markdown.')
        self._convert(input_files, output_files, verbose)

    def html(self, input_files, output_files, verbose=True):
        self._exportClass = exports.ExportHtml
        self._optionSongs = {
            "export_settings": self._export_settings,
            "markdowner": self._markdowner,
        }
        self._optionSets = {
            "export_settings": self._export_settings,
            "markdowner": self._markdowner,
            "html_style": "@@body@@",
            "title_level": 2,
        }
        self._ext = ".html"
        self._titleMark = "<title>@@title@@</title>\n<h1>@@title@@</h1>\n"
        self._bodyMark = self._htmlStyle
        if verbose:
            logger.info(f'Converting files in "{input_files}" to html.')
        self._convert(input_files, output_files, verbose)

    def _force_ccli_ref(self, input_file, output_file):
        elem = elements.Chant(input_file)
        filename = fonc.get_file_name(input_file)
        if elem.ccli:
            filename = re.sub(r"SUP\d{3,4}", elem.ccli, filename)
        return os.path.join(fonc.get_path(output_file), filename + self._ext)

    def _is_not_songfinder_file(self, file_name):
        return (
            fonc.get_ext(file_name) not in self._songExtentions + self._listeExtentions
        )

    def _convert(self, input_files, output_files, verbose=True):
        ref_time = time.time()
        self._set_default_options()
        if os.path.isfile(input_files):
            input_file = input_files
            if self._is_not_songfinder_file(input_file):
                return
            output_file = self._force_ccli_ref(input_file, output_files)
            self._convert_one_file(input_file, output_file, prefered_path=input_files)
        elif os.path.isdir(input_files):
            if output_files[-1] != os.sep:
                output_files = output_files + os.sep
            for root, _, files in os.walk(input_files):
                for file_name in files:
                    if self._is_not_songfinder_file(file_name):
                        continue

                    input_file = os.path.join(root, file_name)
                    output_file = input_file.replace(input_files, output_files)
                    output_file = self._force_ccli_ref(input_file, output_file)
                    self._convert_one_file(
                        input_file,
                        output_file,
                        prefered_path=input_files,
                    )

        if self._doDecline:
            # Declining file to guitar/bass/list version
            self._decliningPass = True
            if self._dateList:
                last_key = sorted(self._dateList.keys())[-1]
                to_add = (last_key, self._dateList[last_key])
                self._toDecline.add(to_add)
            if self._toDecline:
                for decline_parameter_set in self._declineFunctionsSetter:
                    decline_parameter_set()
                    for input_file, _ in self._toDecline:
                        if self._is_not_songfinder_file(input_file):
                            continue
                        output_file = input_file.replace(input_files, output_files)
                        output_file = (
                            fonc.get_file_path(output_file) + self._suffix + self._ext
                        )
                        self._convert_one_file(
                            input_file,
                            output_file,
                            prefered_path=input_files,
                        )
            self._set_default_options()
            self._dateList = dict()
            self._toDecline = set()
            self._decliningPass = False

        if verbose:
            logger.info(
                f"Converted {self._counter} files. Convertion took {time.time() - ref_time}s.",
            )
        self._counter = 0

    def _convert_one_file(self, input_file, output_file, prefered_path=None):
        output_file = _sanitize_output_filename(output_file)
        output_file = self._make_dirs(output_file)
        logger.info(f'Converting "{input_file}" to "{output_file}"')
        if fonc.get_ext(input_file) in self._songExtentions:
            my_elem = elements.Chant(input_file)
            try:
                my_elem = self._elementDict[my_elem.nom]
                my_elem.reset_diapos()
            except KeyError:
                self._elementDict[my_elem.nom] = my_elem
            my_export = self._exportClass(my_elem, **self._optionSongs)
            with codecs.open(output_file, "w", encoding="utf-8") as out:
                out.write(my_export.export_text)
            self._counter += 1

        elif fonc.get_ext(input_file) in self._listeExtentions:
            self._set.load(
                input_file,
                prefered_path=prefered_path,
                database=self._elementDict,
            )
            text = ""
            for my_elem in self._set:
                logger.debug(f'Converting "{my_elem.chemin}"')
                my_export = self._exportClass(my_elem, **self._optionSets)
                text += f"{my_export.export_text}\n"
            title = self._fill_mark("title", self._titleMark, str(self._set))
            text = f"{title}{text}"
            text = self._fill_mark("body", self._bodyMark, text)
            with codecs.open(output_file, "w", encoding="utf-8") as out:
                out.write(text)

            # Filling set to decline in guitar/bass/list versions
            if not self._decliningPass:
                if self._is_date(input_file):
                    self._dateList[input_file] = output_file
                else:
                    self._toDecline.add((input_file, output_file))
            self._counter += 1

    def _fill_mark(self, mark, styled_text, content):
        return styled_text.replace(f"@@{mark}@@", content) if styled_text else content

    def _make_dirs(self, output_file):
        if self._makeSubDir:
            output_file = self._make_sub_directory(output_file)
        try:
            os.makedirs(fonc.get_path(output_file))
        except OSError as error:
            if error.errno == errno.EEXIST:
                pass
            else:
                raise
        return output_file

    def _make_sub_directory(self, full_path):
        file_path = fonc.get_path(full_path)
        file_name = fonc.get_file_name_ext(full_path)
        sub_directory = ""
        # Match songs
        match = re.match(r"([A-Z]{3})\d{3,4}", file_name)
        # Match sets
        if not match:
            match = re.match(r"(\d{4})-\d{2}-\d{2}", file_name)
        # Match special sets
        if not match:
            match = re.match(r"(\d{2})", file_name)
        if match:
            sub_directory = match.group(1)

        file_path = os.path.join(file_path, sub_directory)
        try:
            os.makedirs(file_path)
        except OSError as error:
            if error.errno == errno.EEXIST:
                pass
            else:
                raise
        return os.path.join(file_path, file_name)

    def _is_date(self, path):
        file_name = fonc.get_file_name(path)
        list_elem = [
            subsubsubElem
            for elem in file_name.split("-")
            for sub_elem in elem.split("_")
            for subsubElem in sub_elem.split(".")
            for subsubsubElem in subsubElem.split(" ")
        ]
        return bool(all([elem.isdigit() for elem in list_elem]))

    def make_sub_dir_on(self):
        self._makeSubDir = True

    def make_sub_dir_off(self):
        self._makeSubDir = False


def _sanitize_output_filename(output_file):
    """Replaces underscores with spaces in the filename part of the path."""
    path = fonc.get_path(output_file)
    filename_ext = fonc.get_file_name_ext(output_file)
    sanitized_filename = filename_ext.replace("_", " ")
    return os.path.join(path, sanitized_filename)
