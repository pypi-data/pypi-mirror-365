import contextlib
import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CDLParser:
    def __init__(self, input_url_or_html):
        self._reset()
        try:
            html_page = requests.get(input_url_or_html)
        except requests.exceptions.InvalidSchema:
            if bool(BeautifulSoup(input_url_or_html, "html.parser").find()):
                # The input is actualy html content not an URL
                self._url = ""
                logger.debug("parsing html content")
                self._parsedPage = BeautifulSoup(input_url_or_html, "html.parser")
            else:
                raise
        else:
            self._url = input_url_or_html
            logger.debug(f"parsing {self._url}")
            self._parsedPage = BeautifulSoup(html_page.content, "html.parser")
            # Make sure link is valid
            self._is_valid_link()

    def _reset(self):
        self._tags = []
        self._authors = ""
        self._sources = ""
        self._copyright = ""
        self._key = ""
        self._text = ""
        self._title = ""
        self._song_book = ""
        self._hymnNumber = None
        self._invalidLink = False

    def _get_section(self, section_name):
        if not self._invalidLink:
            section = self._parsedPage.find_all("section", section_name)
            if len(section) != 1:
                logger.info(
                    f'Parsed section is not of size 1 for "{self.title}": "{section!s}"',
                )
                return self._parsedPage
        return section[0]

    @property
    def hymn_number(self):
        if not self._invalidLink and not self._hymnNumber:
            sources = self.sources
            start = sources.find("#")
            if start != -1:
                hymn_number = sources[start + 1 :]
                self._hymnNumber = int(hymn_number.strip(" "))
        return self._hymnNumber

    @property
    def song_book(self):
        if not self._invalidLink and not self._song_book:
            rep_dict = {
                "J'aime l'Éternel": "JEM",
                "EXO": "EXO",
                "ailes de la foi": "AF",
                "Hillsong": "H",
                "Dan Luiten": "DL",
                "Reckless love": "RL",
                "Jesus Culture": "JC",
            }
            sources = self.sources
            for key, value in rep_dict.items():
                if sources.lower().find(key.lower()) != -1:
                    self._song_book = f"{value}"
                    break
        return self._song_book

    @property
    def tags(self):
        if not self._invalidLink and not self._tags:
            categories = self._get_section("categories")
            labels = categories.find_all("span", "label label-primary")
            for label in labels:
                self._tags.append(label.text.replace("\n", ""))
        return self._tags

    @property
    def authors(self):
        if not self._invalidLink and not self._authors:
            song_gredits = self._get_section("credits")
            song_authors = song_gredits.find_all("span", "author")
            authors_list = [author.text.replace("\n", "") for author in song_authors]
            self._authors = " - ".join(authors_list)
        return self._authors

    @property
    def sources(self):
        if not self._invalidLink and not self._sources:
            song_gredits = self._get_section("credits")
            song_sources = song_gredits.find_all("span", "source")
            sources_list = [source.text.replace("\n", "") for source in song_sources]
            if len(sources_list) > 1:
                logger.debug(
                    'Number of sources is greater than 1 for "{}", taking only the first one: "{}"'.format(
                        self.title,
                        ", ".join(sources_list),
                    ),
                )
            with contextlib.suppress(IndexError):
                self._sources = sources_list[0]
        return self._sources

    @property
    def copyright(self):
        if not self._invalidLink and not self._copyright:
            song_copyright = self._get_section("copyright")
            self._copyright = song_copyright.text.replace("\n", "")
        return self._copyright

    @property
    def key(self):
        if not self._invalidLink and not self._key:
            body = self._get_section("body")
            keys = body.find_all("div", "chordpro-key")
            # ~ if len(keys) != 1:
            # ~ raise Exception('Parsed keys is not of size 1 %s'%str(keys))
            self._key = keys[0].text.replace("\n", "")
        return self._key

    @property
    def text(self):
        if not self._invalidLink and not self._text:
            body = self._get_section("body")
            text = ""
            for elem in body:
                try:
                    name = elem["class"][0]
                except (TypeError, KeyError):
                    pass
                else:
                    if name == "chordpro-start_of_verse":
                        text = f"{text}\n\\ss"
                    elif name == "chordpro-chorus":
                        text = f"{text}\n\\sc"
                        for sub_elem in elem:
                            text = f"{text}\n{sub_elem.text}"
                    elif name == "chordpro-verse":
                        text = f"{text}\n{elem.text}"
            self._text = text.strip("\n")
        return self._text

    @property
    def title(self):
        if not self._invalidLink and not self._title:
            title = self._parsedPage.find_all("h2")
            if len(title) != 1:
                msg = f'Parsed title is not of size 1: "{title!s}"'
                raise Exception(msg)
            self._title = title[0].text.strip("\n ")
        return self._title

    def _is_valid_link(self):
        if self.title == "Une erreur 404 est survenue":
            logger.error(f'404 ERROR While parsing link "{self._url}"')
            self._invalidLink = True

    def __str__(self):
        name = f"{self.song_book}{self.hymn_number} {self.title}"
        return name.strip(" \n")
