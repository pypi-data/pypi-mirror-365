import functools
import logging
import time

from songfinder import corrector, gestchant

logger = logging.getLogger(__name__)

MIN_FOUND_FOR_RETRY = 5
MIN_WORDS_FOR_RETRY = 2


class SearcherBase:
    def search(self, to_search):
        raise NotImplementedError


class SearcherNum(SearcherBase):
    def __init__(self, num_dict):
        self._num_dict = num_dict

    def search(self, num_to_search):
        if not isinstance(num_to_search, int):
            msg = "Search input should be integer type"
            raise TypeError(msg)

        try:
            return list(self._num_dict[num_to_search])
        except KeyError:
            logger.warning(
                f"{num_to_search} does not correspond to any number song number",
            )
            return []


class SearcherString(SearcherBase):
    def __init__(self, song_dict):
        self._song_dict = song_dict

    def search(self, to_search):
        if not isinstance(to_search, str):
            msg = "Search input should be string type"
            raise TypeError(msg)

        self._found = list(self._song_dict.keys())
        self._retry_threshold = min(len(self._found), 10)
        self._search_core(to_search)
        return self._found

    def _search_core(self, to_search):
        to_search_list = to_search.split(" ")

        for _ in range(2):
            nb_found = len(self._found)
            if nb_found != 1 and nb_found >= self._retry_threshold:
                self._key_word_search(1, to_search_list)
                if len(to_search_list) > 1 and len(self._found) > MIN_FOUND_FOR_RETRY:
                    self._key_word_search(2, to_search_list)
                if (
                    len(to_search_list) > MIN_WORDS_FOR_RETRY
                    and len(self._found) > MIN_FOUND_FOR_RETRY
                ):
                    self._key_word_search(3, to_search_list)
                if len(to_search_list) > 1 and len(self._found) > MIN_FOUND_FOR_RETRY:
                    self._key_word_search(2, to_search_list, tolerance=0.2)
                if len(to_search_list) > 1 and len(self._found) > MIN_FOUND_FOR_RETRY:
                    self._key_word_search(2, to_search_list, tolerance=0.1)
                if (
                    len(to_search_list) > MIN_WORDS_FOR_RETRY
                    and len(self._found) > MIN_FOUND_FOR_RETRY
                ):
                    self._key_word_search(3, to_search_list)

    def _key_word_search(self, nb_words, to_search_list, tolerance=0.3):
        dico_taux = dict()
        to_search_set = set()
        plusieurs_mots = []
        for i, mot in enumerate(to_search_list):
            plusieurs_mots.append(mot)
            if i > nb_words - 2:
                to_search_set.add(" ".join(plusieurs_mots))
                plusieurs_mots = plusieurs_mots[1:]
        taux_max = 0
        for song in self._found:
            ref_words = self._song_dict[song][nb_words - 1]
            ref_set = set(ref_words.split(";"))
            taux = len(to_search_set & ref_set) / len(to_search_set)

            try:
                dico_taux[taux].append(song)
            except KeyError:
                dico_taux[taux] = [song]

            taux_max = max(taux_max, taux)

        self._found = []
        taux_ordered = sorted(dico_taux.keys(), reverse=True)
        for taux in taux_ordered:
            if taux > taux_max - tolerance - nb_words / 10:
                self._found += sorted(dico_taux[taux])


class SearcherWrapper(SearcherBase):
    def __init__(self, database):
        self._database = database
        self._searchers = dict()
        for mode in self._database.available_modes:
            # TODO Accessing private member here
            # Remove this when refactoring if finished
            self._searchers[mode] = SearcherString(self._database._dicts[mode])  # noqa: SLF001
        self._searchers["num"] = SearcherNum(self._database.dict_nums)

        self._debugPrintMod = 10
        self._searchCounter = 0
        self._searchTimeCumul = 0
        self._correctTimeCumul = 0

        self._get_corrector()

    def _get_corrector(self):
        singles = ";".join(sets[0] for sets in self._database.values())
        couples = ""
        if self._database.mode != "tags":
            couples = ";".join(sets[1] for sets in self._database.values())
        self._corrector = corrector.Corrector(singles, couples)

    @property
    def mode(self):
        return self._database.mode

    @mode.setter
    def mode(self, in_mode):
        self._database.mode = in_mode
        self._get_corrector()
        self._cached_search.cache_clear()

    def search(self, string_to_search):
        if not string_to_search.isdigit():
            string_to_search = gestchant.netoyage_paroles(string_to_search)
            start = time.time()
            string_to_search = self._corrector.check(string_to_search)
            self._correctTimeCumul += time.time() - start
        if self._searchCounter % self._debugPrintMod == 0:
            try:
                correct_time_mean = self._correctTimeCumul / self._searchCounter
                search_time_mean = self._searchTimeCumul / self._searchCounter
            except ZeroDivisionError:
                correct_time_mean = 0
                search_time_mean = 0

            # pylint: disable=no-value-for-parameter,no-member
            hits = self._cached_search.cache_info().hits
            misses = self._cached_search.cache_info().misses
            try:
                ratio = hits / (hits + misses)
            except ZeroDivisionError:
                ratio = float("inf")
            logger.debug(
                f'Searcher "{type(self).__name__}": {self._searchCounter} searches,\n'
                f"\tCorrect time (mean): {correct_time_mean:.3f}s, "
                f"Search time (mean): {search_time_mean:.3f}s,\n"
                f"\tCache hit/miss ratio: {ratio:.2f}, "
                f'Searching "{string_to_search}"',
            )
        self._searchCounter += 1
        return self._cached_search(string_to_search)

    @functools.lru_cache(maxsize=100)  # noqa: B019
    def _cached_search(self, string_to_search):  # Use of caching
        start = time.time()
        try:
            num_to_search = int(string_to_search)
        except ValueError:
            found = self._searchers[self._database.mode].search(string_to_search)
        else:
            found = self._searchers["num"].search(num_to_search)
        self._searchTimeCumul += time.time() - start
        return found

    def reset_cache(self):
        # pylint: disable=no-member
        self._cached_search.cache_clear()
        self._corrector.reset_cache()
