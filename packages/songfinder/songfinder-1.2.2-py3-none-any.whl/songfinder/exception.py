class CommandLineError(NotImplementedError):
    def __init__(self, command):
        self._command = command
        self._packetDict = {
            "sox": "sox libsox-fmt-mp3",
            "flac": "flac",
            "opusenc": "opus-tools",
            "oggenc": "vorbis-tools",
            "lame": "ubuntu-restricted-extras lame",
            "hg": "mercurial",
        }

    def __str__(self):
        apt_command = self._packetDict.get(self._command, None)
        if apt_command:
            ubuntu_info = f" On Ubuntu try 'sudo apt install {apt_command}'."
        else:
            ubuntu_info = ""
        out = f"{self._command} is not a valid command. Please install it to use this feature.{ubuntu_info}"
        return repr(out)


class DataReadError(IOError):
    def __init__(self, the_file):
        self._theFile = the_file

    def __str__(self):
        out = f'Impossible de lire le fichier "{self._theFile}"'
        return repr(out)


class DiapoError(Exception):
    def __init__(self, number):
        self._number = number

    def __str__(self):
        out = f'Le numero de diapo "{self._number}" n\'est pas valide'
        return repr(out)


class ConversionError(Exception):
    def __init__(self, the_type):
        self._theType = the_type
        self._types = ["html", "markdown"]

    def __str__(self):
        out = 'Invalid type conversion "{}". The available types are {}.'.format(
            self._theType,
            ", ".join(self._types),
        )
        return repr(out)
