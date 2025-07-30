# cython: language_level=3 # noqa: ERA001

import contextlib
import logging
import os
import traceback

logger = logging.getLogger(__name__)

try:
    from songfinder import libLoader

    module = libLoader.load(__file__)
    globals().update(
        {n: getattr(module, n) for n in module.__all__}
        if hasattr(module, "__all__")
        else {k: v for (k, v) in module.__dict__.items() if not k.startswith("_")},
    )
except (ImportError, NameError):
    import datetime
    import errno
    import unicodedata

    with contextlib.suppress(ImportError):
        import cython

    def enleve_accents(text):
        """
        Strip accents from input String.

        :param text: The input string.
        :type text: String.

        :returns: The processed String.
        :rtype: String.
        """
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore")
        text = text.decode("utf-8")
        return str(text)

    def enleve_accents_unicode(text):
        """
        Strip accents from input String.

        :param text: The input string.
        :type text: String.

        :returns: The processed String.
        :rtype: String.
        """
        text = unicodedata.normalize("NFD", text)
        text = text.encode("ascii", "ignore")
        text = text.decode("utf-8")
        return str(text)

    def get_file_name(full_path):
        return os.path.splitext(os.path.split(full_path)[1])[0]

    def get_file_name_ext(full_path):
        return os.path.split(full_path)[1]

    def get_path(full_path):
        if os.path.isdir(full_path):
            return full_path
        return os.path.split(full_path)[0]

    def get_ext(full_path):
        return os.path.splitext(full_path)[1]

    def get_file_path(full_path):
        return os.path.splitext(full_path)[0]

    def upper_first(mot):
        return mot[0].upper() + mot[1:] if len(mot) > 1 else mot.upper()

    def cree_nom_sortie():
        proch_dimanche = datetime.timedelta(
            days=6 - datetime.datetime.today().weekday(),
        )
        nom_sortie = str(datetime.date.today() + proch_dimanche)
        return no_overrite(nom_sortie)

    def no_overrite(in_name):
        while os.path.isfile(in_name):
            ext = get_ext(in_name)
            name = get_file_name(in_name)
            under_score = name.rfind("_")
            if under_score != -1 and name[under_score + 1 :].isdigit():
                num = int(name[under_score + 1 :])
                in_name = in_name.replace(f"_{num}{ext}", f"_{num + 1}{ext}")
            else:
                in_name = in_name.replace(f"{ext}", f"_1{ext}")
        return in_name

    def strip_perso(text, car):
        while text[-len(car) :] == car:
            text = text[: -len(car)]
        while text[: len(car)] == car:
            text = text[len(car) :]
        return text

    def split_perso(list_text, list_sep, list_stype, index):
        try:
            index_i = cython.declare(cython.int)  # pylint: disable=no-member
            index_j = cython.declare(cython.int)  # pylint: disable=no-member
        except NameError:
            pass
        tmp = []
        index_i = 0
        for text in list_text:
            new_list_text = text.split(list_sep[index])
            for index_j, elem in enumerate(new_list_text):
                tmp.append(strip_perso(elem, "\n"))
                if index_j > 0:
                    list_stype.insert(index_i - 1, list_sep[index])
                index_i = index_i + 1
        if index + 1 < len(list_sep):
            tmp, list_stype = split_perso(tmp, list_sep, list_stype, index + 1)
        return tmp, list_stype

    def supress_b(text, deb, fin):
        sub_list = [
            sub.split(fin, 1)[1] if i > 0 and len(sub.split(fin, 1)) > 1 else sub
            for (i, sub) in enumerate(text.split(deb))
        ]
        return "".join(sub_list)

    def get_b(text, deb, fin):
        return [
            sub.split(fin, 1)[0] for (i, sub) in enumerate(text.split(deb)) if i > 0
        ]

    def take_one(stype_process, list_in):
        # Take the first slide of selected type
        ok = True
        new_list = []
        for elem in list_in:
            if elem[0] == stype_process:
                if ok:
                    ok = False
                    new_list.append(elem)
            else:
                new_list.append(elem)

        return new_list

    def clean_file(file_rm):
        try:
            os.remove(file_rm)
        except OSError as error:
            if error.errno == errno.ENOENT:
                logger.debug(traceback.format_exc())
            else:
                raise

    def indent(elem, level=0):
        i = f"\n{level * '  '}"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = f"{i}  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for sub_elem in elem:
                indent(sub_elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        elif level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    def no_new_line(text, command, newline):
        try:
            deb = cython.declare(cython.int)  # pylint: disable=no-member
            fin = cython.declare(cython.int)  # pylint: disable=no-member
        except NameError:
            pass
        deb = 0
        fin = 0
        end = "}"
        for _ in range(10000):
            deb = text.find(command, fin) + len(command)
            fin = text.find(end, deb) + len(end)
            if deb == -1 or fin == -1:
                break
            if text[fin : fin + len(newline)] == newline:
                text = text[:fin] + text[fin + len(newline) :]
        return text

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def split_list(test_list, delimiter):
        """
        Split a list in chunks by delimiter
        The delimiter is not included in any list
        Returns a list of lists
        """
        size = len(test_list)
        idx_list = [idx + 1 for idx, val in enumerate(test_list) if val == delimiter]
        return [
            test_list[i : j - 1]
            for i, j in zip(
                [0, *idx_list],
                idx_list + ([size + 1] if idx_list[-1] != size else []),
            )
            if test_list[i : j - 1]
        ]
