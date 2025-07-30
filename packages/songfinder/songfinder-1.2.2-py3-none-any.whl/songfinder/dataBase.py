# cython: language_level=3 # noqa: ERA001
import contextlib

try:
    from songfinder import libLoader

    module = libLoader.load(__file__)
    globals().update(
        {n: getattr(module, n) for n in module.__all__}
        if hasattr(module, "__all__")
        else {k: v for (k, v) in module.__dict__.items() if not k.startswith("_")},
    )
except (ImportError, NameError):
    import logging
    import os
    import time
    import traceback

    logger = logging.getLogger(__name__)

    try:
        import cython
    except ImportError:
        logger.debug(traceback.format_exc())

    from songfinder import classPaths, elements, gestchant
    from songfinder import classSettings as settings
    from songfinder import fonctions as fonc

    class DataBase:
        def __init__(self, song_path=None):
            self._sizeMax = 3
            if song_path:
                self._songPath = song_path
                self._genPath = False
            else:
                self._songPath = classPaths.PATHS.songs
                self._genPath = True
            self._mergedDataBases = []
            self._maxCustomNumber = 0
            self._tagList = []

            self._available_modes = ("lyrics", "titles", "tags", "num")
            self._default_mode = "lyrics"
            self._mode = self._default_mode

            self.update()

        def __contains__(self, key):
            return key in self._dicts[self._default_mode]

        def __getitem__(self, key):
            return self._dicts[self._mode][key]

        def keys(self):
            return self._dicts[self._default_mode].keys()

        def values(self):
            return self._dicts[self._mode].values()

        def __iter__(self):
            return iter(self._dicts[self._mode])

        def __len__(self):
            return len(self._dicts[self._mode])

        @property
        def default_mode(self):
            return self._default_mode

        @property
        def available_modes(self):
            return self._available_modes

        @property
        def mode(self):
            return self._mode

        @mode.setter
        def mode(self, in_mode):
            if in_mode in self.available_modes:
                self._mode = in_mode
            else:
                available_mode_str = " ".join(self.available_modes)
                msg = f'Database mode "{in_mode}" is not allowed.\nOnly "{available_mode_str}" are allowed'
                raise KeyError(
                    msg,
                )

        @property
        def tags(self):
            if not self._tagList:
                tags = set()
                for song in self.keys():
                    tags = tags | set(song.tags.split(","))
                self._tagList = list(tags)
                self._tagList.sort()
            return self._tagList

        @property
        def dict_nums(self):
            return self._dict_nums

        def remove(self, song):
            for mode in self.available_modes:
                if mode != "num":
                    del self._dicts[mode][song]
            for num in song.nums.values():
                # Num can be None or 0 both are invalid
                if num:
                    # Song can have several time the same number (for custom and CCLI number)
                    # The try/except is to avoid trying to remove the same song several times
                    with contextlib.suppress(KeyError):
                        self._dict_nums[num].remove(song)
                    if self._dict_nums[num] == set():
                        del self._dict_nums[num]

        def add(self, song):
            self._dicts["lyrics"][song] = self._get_strings(f"{song.title} {song.text}")
            self._dicts["titles"][song] = self._get_strings(song.title)
            self._dicts["tags"][song] = self._get_strings(song.tags)
            self.add_dict_nums(song)
            if (
                song.song_book == "SUP"
                and song.custom_number is not None
                and song.custom_number > self._maxCustomNumber
            ):
                self._maxCustomNumber = song.custom_number

        def add_dict_nums(self, song):
            for num in [num for num in song.nums.values() if num]:
                try:
                    self._dict_nums[num].add(song)
                except KeyError:
                    self._dict_nums[num] = set([song])

        def update(self, callback=None, args=()):
            tmps_ref = time.time()
            logger.debug("Updating database ...")
            if self._genPath:
                self._songPath = classPaths.PATHS.songs

            self._dict_nums = dict()
            self._dicts = dict()
            for mode in self.available_modes:
                self._dicts[mode] = dict()

            self._find_songs(callback, args)
            logger.info(
                f"Updated data_base in {time.time() - tmps_ref:f}s, {len(self)} songs",
            )
            self._merge(update=True)
            self._tagList = []
            self.sanity_check()

        def sanity_check(self):
            for song in self.keys():
                if song is None:
                    logger.exception(f'"{song}" is not itself')

        def _find_songs(self, callback, args):
            cdl_path = settings.GENSETTINGS.get("Paths", "conducteurdelouange")
            logger.debug(f"Looking for songs in '{self._songPath}'")
            if self._songPath.find(cdl_path) != -1:
                self._find_songs_cdl(callback, args)
            else:
                self._find_songs_local(callback, args)

        def _find_songs_local(self, callback, args):
            ext_chant = settings.GENSETTINGS.get(
                "Extentions",
                "song",
            ) + settings.GENSETTINGS.get("Extentions", "chordpro")
            exclude = [
                "LSG",
                "DAR",
                "SEM",
                "KJV",
            ]
            counter = 0
            if self._songPath:
                for root, _, files in os.walk(self._songPath):
                    for fichier in files:
                        path = os.path.join(root, fichier)
                        if (
                            (path).find(f"{os.sep}.") == -1
                            and fonc.get_ext(fichier) in ext_chant
                            and fichier not in exclude
                        ):
                            new_chant = elements.Chant(
                                os.path.join(root, fichier),
                            )  # About 2/3 of the time
                            # ~ new_chant._replace_in_text('raDieux', 'radieux') # noqa: ERA001
                            if new_chant.exist():  # About 1/3 of the time
                                self.add(new_chant)
                                self.add_dict_nums(new_chant)
                            if callback:
                                callback(*args)
                            counter += 1

        def _find_songs_cdl(self, callback, args):
            counter = 0
            if self._songPath:
                for number in range(1, 3000):
                    url = f"{self._songPath}/{number}"
                    new_chant = elements.Chant(url)
                    self.add(new_chant)
                    self.add_dict_nums(new_chant)
                    if callback:
                        callback(*args)
                    counter += 1

        def _get_strings(self, paroles):
            try:
                size = cython.declare(cython.int)  # pylint: disable=no-member
                nb_mots = cython.declare(cython.int)  # pylint: disable=no-member
            except NameError:
                pass

            paroles = gestchant.netoyage_paroles(paroles)  # Half the time

            list_mots = paroles.split()
            nb_mots = len(list_mots) - 1

            out_put = [
                paroles.replace(" ", ";"),
            ]  # First word list can be done faster with replace
            for size in range(1, self._sizeMax):  # Half the time
                add_list = [
                    " ".join(list_mots[i : i + size + 1])
                    for i in range(max(nb_mots - size, 0))
                ]
                add_list.append(" ".join(list_mots[-size - 1 :]))
                out_put.append(";".join(add_list))
            return out_put

        @property
        def max_custom_number(self):
            return self._maxCustomNumber

        def merge(self, others, receuil_to_save=()):
            self._mergedDataBases += others
            self._merge(receuil_to_save=receuil_to_save)

        def _merge(self, update=False, receuil_to_save=()):
            if self._mergedDataBases:
                tmps_ref = time.time()
                for data_base in self._mergedDataBases:
                    if update:
                        data_base.update()
                    tmp = list(self.keys())
                    for song in data_base:
                        if song not in tmp:
                            self.add(song)
                            if song.song_book in receuil_to_save:
                                self.save((song,))
                        else:
                            tmp.remove(song)
                logger.info(
                    f"Merged {len(self._mergedDataBases) + 1} data_base in {time.time() - tmps_ref}s, {len(self)} songs",
                )

        def remove_extra_databases(self, update=False):
            del self._mergedDataBases[:]
            if update:
                self.update()

        def save(self, songs=()):
            # We use a different xml lib here because it does not add carriage return on Windows for writes
            # There might be a way to use xml.etree.cElementTree that don't but have not figured out
            # xml.etree.cElementTree is faster at parsing so keep it for song parsing
            import lxml.etree as ET_write

            if not songs:
                songs = self.keys()
            for song in songs:
                ext = settings.GENSETTINGS.get("Extentions", "song")[0]
                if fonc.get_ext(song.chemin) != ext:
                    song.chemin = os.path.join(
                        f"{self._songPath}",
                        f"{song.song_book}{song.hymn_number}_{song.title}",
                    )
                try:
                    tree = ET_write.parse(song.chemin)
                    chant_xml = tree.getroot()
                except OSError:
                    logger.debug(traceback.format_exc())
                    chant_xml = ET_write.Element(song.etype)
                song.safe_update_xml(chant_xml, "lyrics", song.text)
                song.safe_update_xml(chant_xml, "title", song.title)
                song.safe_update_xml(chant_xml, "sup_info", song.sup_info)
                song.safe_update_xml(chant_xml, "transpose", song.transpose)
                song.safe_update_xml(chant_xml, "capo", song.capo)
                song.safe_update_xml(chant_xml, "key", song.key)
                song.safe_update_xml(chant_xml, "tempo", song.tempo)
                song.safe_update_xml(chant_xml, "turf_number", song.turf_number)
                song.safe_update_xml(chant_xml, "hymn_number", song.hymn_number)
                song.safe_update_xml(chant_xml, "author", song.author)
                song.safe_update_xml(chant_xml, "copyright", song.copyright)
                song.safe_update_xml(chant_xml, "ccli", song.ccli)
                song.safe_update_xml(chant_xml, "tags", song.tags)
                fonc.indent(chant_xml)

                tree = ET_write.ElementTree(chant_xml)
                tree.write(song.chemin, encoding="UTF-8", xml_declaration=True)
                song.reset_diapos()

                try:
                    logger.info(f'Saved "{song.chemin}"')
                except UnicodeEncodeError:
                    logger.info(f'Saved "{song.chemin!r}"')
                self.add(song)

        def add_info_from(self, database_names):
            for name in database_names:
                base_path = settings.GENSETTINGS.get("Paths", name)
                add_data = DataBase(base_path)
                for song in self:
                    for add_song in add_data:
                        if song == add_song:
                            if not song.author:
                                song.author = add_song.author
                            if not song.tags:
                                song.tags = add_song.tags
                            if not song.copyright:
                                song.copyright = add_song.copyright
                            if add_song.hymn_number:
                                song.hymn_number = add_song.hymnNumber
                            if add_song.song_book:
                                song.song_book = add_song.song_book
            self.save()
