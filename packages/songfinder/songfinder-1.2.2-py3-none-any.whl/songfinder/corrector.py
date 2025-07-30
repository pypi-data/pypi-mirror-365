import contextlib

from songfinder import cache, distances


class Corrector:
    CACHE_CAPACITY = 300  # Cache capacity for both cacheList and cacheWord
    DEFAULT_DIFF_SIZE = 3
    DEFAULT_TOLERANCE = 0.3

    def __init__(self, words, couples=""):
        self._words = words
        self._couples = couples
        self._sizeDict = dict()
        self._couplesDict = dict()
        self._cacheList = cache.Cache(self.CACHE_CAPACITY, self._verifie_mot_opt)
        self._cacheWord = cache.Cache(self.CACHE_CAPACITY, self._verifie_mot)
        self._diffSize = self.DEFAULT_DIFF_SIZE
        self._tolerance = self.DEFAULT_TOLERANCE

        self._counter = 0

    def _get_size_dict(self):
        self._max_length = 0
        for word in set(self._words.split(";")):
            if word:
                try:
                    self._sizeDict[len(word)].add(word)
                except KeyError:
                    self._sizeDict[len(word)] = {word}
                self._max_length = max(self._max_length, len(word))

    def _get_couples_dict(self):
        for couple in set(self._couples.split(";")):
            for word in couple.split(" "):
                if word:
                    try:
                        self._couplesDict[word].add(couple)
                    except KeyError:
                        self._couplesDict[word] = set([couple])

    MAX_PROPOSITIONS = 9  # Maximum number of propositions to return
    INITIAL_MAX_PROPOSITIONS = 1500
    SECONDARY_MAX_PROPOSITIONS = 400
    FINAL_MAX_PROPOSITIONS = 20
    INITIAL_DIST_METHOD = 0
    SECONDARY_DIST_METHOD = 3
    FINAL_DIST_METHOD = 3
    TOLERANCE_REDUCTION_STEP1 = 0.1
    TOLERANCE_REDUCTION_STEP2 = 0.25

    def _verifie_mot_opt(self, mot):
        if not self._sizeDict:
            self._get_size_dict()

        set_mots2 = set()
        taille = len(mot)
        range_low = max(1, taille - self._diffSize)
        range_high = min(self._max_length, taille + self._diffSize) + 1
        for lengths in range(range_low, range_high):
            if lengths in self._sizeDict:
                set_mots2 |= set(self._sizeDict[lengths])

        props = self._verifie_mot(
            mot,
            set_mots2,
            self._tolerance,
            self.INITIAL_MAX_PROPOSITIONS,
            self.INITIAL_DIST_METHOD,
        )
        if len(props) > self.MAX_PROPOSITIONS:
            props = self._verifie_mot(
                mot,
                props,
                self._tolerance - self.TOLERANCE_REDUCTION_STEP1,
                self.SECONDARY_MAX_PROPOSITIONS,
                self.SECONDARY_DIST_METHOD,
            )
        if len(props) > self.MAX_PROPOSITIONS:
            props = self._verifie_mot(
                mot,
                props,
                self._tolerance - self.TOLERANCE_REDUCTION_STEP2,
                self.FINAL_MAX_PROPOSITIONS,
                self.FINAL_DIST_METHOD,
            )
        return props

    SINGLE_CORRECTION_THRESHOLD = 1  # Threshold for using single correction

    def _check_couple(self):
        if not self._couplesDict:
            self._get_couples_dict()
        word1, word2 = self._checking[self._counter : self._counter + 2]
        correcs1 = self._cacheList.get(word1, args=[word1])
        correcs2 = self._cacheList.get(word2, args=[word2])
        correc_couple = set()
        for correc1 in correcs1:
            for correc2 in correcs2:
                with contextlib.suppress(KeyError):
                    correc_couple |= (
                        self._couplesDict[correc1] & self._couplesDict[correc2]
                    )
        if len(correcs1) == self.SINGLE_CORRECTION_THRESHOLD:
            word1 = next(iter(correcs1))
        if len(correcs2) == self.SINGLE_CORRECTION_THRESHOLD:
            word2 = next(iter(correcs2))
        sol = self._verifie_mot(f"{word1} {word2}", correc_couple, 0.1, 1, 3)
        word1, word2 = next(iter(sol)).split(" ")
        self._checking[self._counter : self._counter + 2] = word1, word2

    MIN_WORDS_FOR_COUPLES = 2  # Minimum words needed for couple checking

    def check(self, to_check):
        self._toCheck = to_check.split(" ")
        if len(self._toCheck) < self.MIN_WORDS_FOR_COUPLES or not self._couples:
            self._single_check()
        else:
            self._couple_check()
        return " ".join(self._checking)

    # Constants for _singleCheck method
    TOLERANCE_SINGLE = 0.05
    MAX_PROPOSITIONS_SINGLE = 1
    DIST_METHOD_SINGLE = 3

    def _single_check(self):
        self._checking = []
        for word in self._toCheck:
            args = [
                word,
                self._cacheList.get(word, args=[word]),
                self.TOLERANCE_SINGLE,
                self.MAX_PROPOSITIONS_SINGLE,
                self.DIST_METHOD_SINGLE,
            ]
            sol = self._cacheWord.get(word, args=args)
            self._checking.append(next(iter(sol)))

    def _couple_check(self):
        if self._counter > len(self._toCheck) - 2:
            self._counter = 0
        else:
            if self._counter == 0:
                self._checking = self._toCheck
            self._check_couple()
            self._counter += 1
            self.check(" ".join(self._checking))

    # Distance calculation methods
    DISTANCE_MAI = 0
    DISTANCE_JAR = 1
    DISTANCE_LEN = 2
    DISTANCE_COMBINED = 3
    MIN_SIMILARITY_THRESHOLD = 0.4

    def _verifie_mot(self, mot, set_a_tester, tolerance, max_propositions, dist):
        if not set_a_tester or not mot:
            return set([mot])
        max_ressemble = 0
        taille = len(mot)
        propositions = set()
        ressemble = 0
        if taille == 1:
            return set([mot])

        distance_functions = {
            self.DISTANCE_MAI: distances.distance_mai,
            self.DISTANCE_JAR: distances.distance_jar,
            self.DISTANCE_LEN: distances.distance_len,
        }

        corrections = dict()
        for mot_test in set_a_tester:
            if dist in distance_functions:
                ressemble = distance_functions[dist](mot, mot_test)
            elif dist == self.DISTANCE_COMBINED:
                ressemble = round(
                    (
                        distances.distance_mai(mot, mot_test)
                        + distances.distance_jar(mot, mot_test)
                        + distances.distance_len(mot, mot_test)
                    )
                    / 3.0,
                    2,
                )
            else:
                ressemble = 0

            if ressemble in corrections:
                corrections[ressemble] |= {mot_test}
            else:
                corrections[ressemble] = {mot_test}
            max_ressemble = max(ressemble, max_ressemble)
        if max_ressemble < self.MIN_SIMILARITY_THRESHOLD:
            return set([mot])
        for ressemble, mots_ressemble in corrections.items():
            if ressemble > max_ressemble - tolerance:
                propositions |= mots_ressemble
        if len(propositions) <= max_propositions:
            return propositions
        return set([mot])

    def reset_cache(self):
        self._cacheList.reset()
        self._cacheWord.reset()
