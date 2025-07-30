# cython: language_level=3 # noqa: ERA001

import os

try:
    from songfinder import libLoader

    module = libLoader.load(__file__)
    globals().update(
        {n: getattr(module, n) for n in module.__all__}
        if hasattr(module, "__all__")
        else {k: v for (k, v) in module.__dict__.items() if not k.startswith("_")},
    )
except (ImportError, NameError):
    import sys

    from songfinder import classPaths, pyreplace
    from songfinder import classSettings as settings
    from songfinder import fonctions as fonc

    MIN_DIV_FOR_MULTILINE_SPLIT = 2

    def clean_line(text):
        for _ in range(5):
            text = text.replace("\n\n", "\n")
            text = text.replace("\n \n", "\n")
        newline = settings.GENSETTINGS.get("Syntax", "newline")
        return text.replace(newline, "")

    def numerote(text, numero, nombre, etype="song"):
        if (
            (nombre > 1 or settings.PRESSETTINGS.get(etype, "oneslide"))
            and settings.PRESSETTINGS.get(etype, "Numerote_diapo")
            and numero
        ):
            text = f"({numero!s}/{nombre!s}){text}"
        return text

    def print_title(text, title, numero, etype):
        if settings.PRESSETTINGS.get(etype, "Print_title") and numero == 1:
            text = f"{title.upper()}\n{text}"
        return text

    def check_bis(text, etype="song"):
        if settings.PRESSETTINGS.get(etype, "Check_bis"):
            num_dict = {"2": "bis", "3": "ter", "4": "quarter"}
            for num, litteral in num_dict.items():
                text = (
                    text.replace(f"(x{num})", f"({litteral})")
                    .replace(f"(X{num})", f"({litteral})")
                    .replace(f"({num}x)", f"({litteral})")
                    .replace(f"({num}X)", f"({litteral})")
                    .replace(f"(× {num})", f"({litteral})")  # noqa: RUF001
                    .replace(f"(* {num})", f"({litteral})")
                    .replace(f"X{num}", f"({litteral})")
                    .replace(f"x{num}", f"({litteral})")
                    .replace(f"{num}x", f"({litteral})")
                    .replace(f"{num}X", f"({litteral})")
                )
                text = text.replace(
                    f"\n ({litteral})",
                    f"\n({fonc.upper_first(litteral)})",
                )
                text = text.replace(
                    f"\n({litteral})",
                    f"\n({fonc.upper_first(litteral)})",
                )
        return text

    def clean_maj(text, etype="song"):
        # Must be before maj at starting lines
        # Must be after check of ponctuation but maybe not
        if settings.PRESSETTINGS.get(etype, "Clean_majuscule"):
            text = text + " "
            post_ponct = [",", ".", " ", "\n"]
            list_pronoms = [
                "Oint",
                "Sa",
                "Ta",
                "Il",
                "Tu",
                "Te",
                "Toi",
                "Son",
                "Ses",
                "Tes",
                "Ton",
                "Nom",
                "Lui",
                "Roi",
                "Celui",
                "Agneau",
                "Fils",
            ]
            for pronom in list_pronoms:
                for ponct in post_ponct:
                    text = text.replace(pronom + ponct, pronom.lower() + ponct)
            text = text.strip(" ")
        return text

    def majuscule(text, etype="song"):
        if settings.PRESSETTINGS.get(etype, "Majuscule"):
            lignes = text.splitlines()
            lignes = [ligne.strip(" ") for ligne in lignes if ligne.strip(" ") != ""]
            new_lignes = []
            for ligne in lignes:
                clean_ligne = fonc.upper_first(ligne)
                if (
                    clean_ligne[0] == '"'
                    or clean_ligne[0] == "'"
                    or clean_ligne[0] == "("
                ):
                    clean_ligne = clean_ligne[0] + fonc.upper_first(clean_ligne[1:])
                new_lignes.append(clean_ligne)

            text = "\n".join(new_lignes)
        return text

    def enleve_ponctuation(text):
        return (
            text.replace(".", " ")
            .replace(",", " ")
            .replace(";", " ")
            .replace(":", " ")
            .replace("!", " ")
            .replace("'", " ")
            .replace("?", " ")
            .replace("  ", " ")
            .replace("_", " ")
            .replace("-", " ")
        )

    def verifie_ponctuation(text, etype="song"):
        # verification ponctuation
        if settings.PRESSETTINGS.get(etype, "Ponctuation"):
            ponctuations0 = [":"]
            for car in ponctuations0:
                text = text.replace(car, f" {car} ").replace("  ", " ")
            ponctuations1 = [";", "!", "?"]
            for car in ponctuations1:
                text = (
                    text.replace(car, f" {car} ")
                    .replace("  ", " ")
                    .replace(f'{car} "', f'{car}"')
                )
            ponctuations2 = [".", ","]
            for car in ponctuations2:
                text = (
                    text.replace(car, f"{car} ")
                    .replace("  ", " ")
                    .replace(f'{car} "', f'{car}"')
                )
            text = text.replace(" \n", "\n")
            for _ in range(5):
                text = text.replace(". .", "..")
            for ponct in ponctuations0 + ponctuations1 + ponctuations2:
                text = text.replace(f"{ponct} )", f"{ponct})")
        return text

    def verifie_ponctuation_maj(text, etype="song"):
        # Majuscule après les points ? et !
        if settings.PRESSETTINGS.get(etype, "Ponctuation"):
            ponctuations_maj = ["!", "?", "."]
            for ponct in ponctuations_maj:
                deb = 0
                while text.find(ponct, deb) != -1:
                    index = text.find(ponct, deb)
                    if len(text) > index + 3:
                        text = (
                            text[: index + 2]
                            + text[index + 2].upper()
                            + text[index + 3 :]
                        )
                    deb = index + 1
        return text

    def new_song_title(title, max_sup):
        if not ((title[:3] == "JEM" or title[:3] == "SUP") and title[3:6].isdigit()):
            title = "SUP" + str(max_sup + 1) + " " + title

        chemin_chants = classPaths.PATHS.songs
        chemin = os.path.join(
            chemin_chants,
            fonc.enleve_accents(title)
            + settings.GENSETTINGS.get("Extentions", "song")[0],
        )
        return chemin, title

    def saut_ligne(text, max_car, etype="song", force=None):
        new_line_suggest = r"\newline"
        liste_sep = [new_line_suggest, ".", "!", "?", " et ", " Et ", ";", ","]
        liste_sep_after = [" et ", " Et ", ":"]
        do_not = ["(bis)", "(Bis)"]
        new_text = text
        if settings.PRESSETTINGS.get(etype, "Saut_ligne") or force == "force":
            for _i in range(5):
                lignes = new_text.splitlines()
                new_text = ""
                for ligne in lignes:
                    trouve = -1

                    if len(ligne) > max_car and ligne.find("\\ac") == -1:
                        ind = len(ligne) * 2 // 5
                        for sep in liste_sep:
                            trouve = ligne.find(sep, ind, -1)
                            if trouve > -1:
                                plus = 0 if sep in liste_sep_after else len(sep)
                                if (
                                    ligne[trouve + len(sep) + 1 : trouve + len(sep) + 6]
                                    not in do_not
                                ):
                                    new_text = new_text + ligne[: trouve + plus] + "\n"
                                    new_text = new_text + ligne[trouve + plus :] + "\n"
                                    break
                    if trouve == -1:
                        new_text = new_text + ligne + "\n"
            if settings.PRESSETTINGS.get(etype, "Saut_ligne_force") or force == "force":
                lignes = new_text.splitlines()
                new_text = ""
                for ligne in lignes:
                    trouve = -1
                    longueur = len(ligne)
                    if longueur > max_car:
                        div = (longueur + max_car - 1) // max_car
                        new_longueur = longueur // div
                        trouve = ligne.find(" ", new_longueur, -1)
                        new_text = new_text + " " + ligne[: trouve + 1] + "\n"
                        if div > MIN_DIV_FOR_MULTILINE_SPLIT:
                            for i in range(div - 2):
                                trouve1 = ligne.find(" ", (i + 1) * new_longueur, -1)
                                trouve = ligne.find(" ", (i + 2) * new_longueur, -1)
                                new_text = (
                                    new_text
                                    + " "
                                    + ligne[trouve1 + 1 : trouve + 1]
                                    + "\n"
                                )
                        new_text = new_text + " " + ligne[trouve + 1 :] + "\n"

                    if trouve == -1:
                        new_text = new_text + ligne + "\n"

        new_text = new_text.replace(new_line_suggest, "")

        for sep in set(liste_sep) - set(liste_sep_after):
            new_text = (
                new_text.replace(f"\n{sep}", f"{sep}\n")
                .replace(f"\n {sep}", f"{sep}\n ")
                .replace(f"{sep}\n)", f"{sep})\n")
                .replace(f'{sep}\n"', f'{sep}"\n')
                .replace(f"{sep}\n", f"{sep}\n")
            )
        for sep in [":", ": "]:
            new_text = new_text.replace(f'{sep}"\n', f'{sep}\n"').replace(
                f"{sep}\n",
                f"{sep}\n",
            )
        return new_text

    def nettoyage(text):
        newslide = settings.GENSETTINGS.get("Syntax", "newslide")
        newline = settings.GENSETTINGS.get("Syntax", "newline")

        text = (
            text.replace(". .", "..")
            .replace(". .", "..")
            .replace("\u2018", "'")
            .replace("\u2019", "'")
            .replace("\u0020", " ")
            .replace("\u00a0", " ")
        )

        text = pyreplace.cleanup_char(text.encode("utf-8"))
        text = pyreplace.cleanup_space(text).decode("utf-8")

        for _ in range(2):
            text = text.strip(" _\n")
            text = fonc.strip_perso(text, newline)
        for newslide_syntax in newslide:
            text = text.replace("\n" + newslide_syntax, "\n\n" + newslide_syntax)

        return text

    def get_list_stype_plus(list_stype):
        # Trouve les suite de type de diapo
        i = 0
        previous = ""
        list_stype_plus = []  # (type, list des numero)
        tmp = []
        for k, stype in enumerate(list_stype):
            tmp.append(k - 1)
            if stype == previous:
                i = i + 1
            else:
                list_stype_plus.append((previous, tmp))
                i = 0
                tmp = []
            previous = stype

        tmp.append(len(list_stype) - 1)
        list_stype_plus.append((previous, tmp))
        del list_stype_plus[0]
        return list_stype_plus

    # ~ def getPlusIndex(list_stype_plus, index):
    # ~ for plusIndex, (Stype, num_list) in enumerate(list_stype_plus):
    # ~ if index in num_list:
    # ~ return plusIndex

    def get_plus_num(list_stype_plus, index):
        for _, num_list in list_stype_plus:
            if index in num_list:
                return len(num_list)
        return 0

    def get_indexes(liste, elem):
        return [i for i, j in enumerate(liste) if j == elem]

    def apply_max_number_line_per_diapo(list_text, list_stype, nb_max_line):
        if nb_max_line > 0:
            index = 0
            counter = 0
            list_text_output = []
            list_stype_output = []

            newline = settings.GENSETTINGS.get("Syntax", "newline")

            for num_diapo, text in enumerate(list_text):
                lines = text.split("\n")
                # Remove line breacks if needed
                if len(lines) > nb_max_line:
                    clean_text = text.replace(f"{newline}\n", "")
                    lines = clean_text.split("\n")

                # Copie severals times a diapo if it is bis or ter
                num_iter = 1
                repet_lines = []
                if len(lines) > nb_max_line:
                    # Get all the repet syntax present in a diapo
                    for num_line, line in enumerate(lines):
                        if line.lower() == "(bis)" or line.lower() == "(x2)":
                            num_iter = 2
                            repet_lines.append(num_line)
                        elif line.lower() == "(ter)" or line.lower() == "(x3)":
                            num_iter = 3
                            repet_lines.append(num_line)

                # only take into account last repet syntax for now
                try:
                    repet_lines = [repet_lines[-1]]
                except IndexError:
                    pass
                else:
                    # Delete Lines containing bis ter etc.
                    for offset, num_line in enumerate(repet_lines):
                        del lines[num_line - offset]
                        # Update repetLine array to contains new diapo numbers correponding to repetition
                        repet_lines[offset] = num_line - offset

                nb_diapo = (len(lines) + nb_max_line - 1) // nb_max_line
                line_per_diapo = (len(lines) + nb_diapo - 1) // nb_diapo

                for iteration in range(num_iter):
                    # Stop at the repet syntax except for the last repetition
                    try:
                        if iteration == num_iter - 1:
                            raise IndexError
                        # only take into account last repet syntax for now
                        stop_line = repet_lines[-1]
                    except IndexError:
                        stop_line = sys.maxsize

                    for line_number, line in enumerate(lines):
                        # Stop at the repet syntax except for the last repetition
                        if line_number == stop_line:
                            counter = 0
                            index += 1
                        else:
                            try:
                                # Append to current diapo
                                list_text_output[index] += "\n" + line
                            except IndexError:
                                # Create new diapo
                                list_text_output.append(line)
                                list_stype_output.append(list_stype[num_diapo])
                            # New diapo if max number of line or and of diapo reached
                            if (
                                counter < line_per_diapo - 1
                                and line_number < len(lines) - 1
                            ):
                                counter += 1
                            else:
                                counter = 0
                                index += 1
        else:
            list_stype_output = list_stype
            list_text_output = list_text

        return list_text_output, list_stype_output

    def netoyage_paroles(paroles):
        newline = settings.GENSETTINGS.get("Syntax", "newline")
        newslide = settings.GENSETTINGS.get("Syntax", "newslide")

        paroles = fonc.enleve_accents_unicode(paroles)
        paroles = f"{paroles}\n"
        paroles = fonc.supress_b(paroles, "\\ac", "\n")
        paroles = paroles.strip("\n")
        for newslide_syntax in newslide:
            paroles = paroles.replace(newslide_syntax, "")

        paroles = (
            paroles.replace(newline, "")
            .replace("\u2019", " ")
            .replace("\u2018", " ")
            .replace("\u0020", " ")
            .replace("\u00a0", " ")
        )

        paroles = paroles.replace(newline, "")
        paroles = paroles.lower()

        paroles = pyreplace.simplify_char(paroles.encode("utf-8"))
        paroles = pyreplace.cleanup_space(paroles).decode("utf-8")

        return paroles.strip(" ")
