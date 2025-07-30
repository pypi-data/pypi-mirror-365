import logging
import os
import shutil
import subprocess
import sys
import threading
import traceback

import songfinder
from songfinder import exception

logger = logging.getLogger(__name__)

try:
    __MAX_TIMEOUT__ = threading.TIMEOUT_MAX
except AttributeError:
    __MAX_TIMEOUT__ = float("inf")


class MyCommand:
    def __init__(self, command):
        self._command = command
        self._locaPaths = os.path.join(
            songfinder.__chemin_root__,
            songfinder.__dependances__,
            "",
        )
        self._myOs = songfinder.__myOs__

    def check_command(self):
        if (
            self._command != ""
            and self._check_in_path()
            and self._check_auto()
            and self._check_local()
        ):
            logger.error(f'Command "{self._command}" not found')
            raise exception.CommandLineError(self._command)
        logger.debug(f'Command "{self._command}" found')
        return 0

    def _check_in_path(self):
        # try to find command in path
        if self._myOs in ["ubuntu", "linux", "darwin"]:
            code, _, _ = self.run(before=["bash", "type", "-a"])
        elif self._myOs == "windows":
            code, _, _ = self.run(before=["where"])
        else:
            code = 1
        return code

    def _check_auto(self):
        command = shutil.which(self._command)
        if not command:
            return 1
        self._command = command
        return 0

    def _check_local(self):
        # Look for portable instalaltion packaged with the software
        for root, _, files in os.walk(self._locaPaths):
            for fichier in files:
                if fichier in [self._command, f"{self._command}.exe"]:
                    self._command = os.path.join(root, fichier)
                    return 0
        return 1

    def run(self, options=(), time_out=__MAX_TIMEOUT__, **kwargs):
        before = kwargs.get("before")
        win_options = kwargs.get("win_options")
        linux_options = kwargs.get("linux_options")
        darwin_options = kwargs.get("darwin_options")

        command_list = []
        if before:
            command_list = before
        command_list.append(self._command)

        if self._myOs in ["ubuntu", "linux"] and linux_options:
            command_list += linux_options
        elif self._myOs == "windows" and win_options:
            command_list += win_options
        elif self._myOs == "darwin" and darwin_options:
            command_list += darwin_options

        command_list += list(options)
        if "|" in command_list:
            # do import latter to enable deletion of fonction compiled librarie when needed
            from songfinder import fonctions as fonc

            command_lists = fonc.split_list(command_list, "|")
            proc = subprocess.Popen(
                command_lists[0],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for command_list in command_lists[1:]:
                proc = subprocess.Popen(
                    command_list,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=proc.stdout,
                )
        else:
            proc = subprocess.Popen(
                command_list,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        timer = threading.Timer(time_out, proc.kill)
        try:
            timer.start()
            stdout, stderr = proc.communicate()
            try:
                stdout = stdout.decode(sys.getfilesystemencoding())
                stderr = stderr.decode(sys.getfilesystemencoding())
            except UnicodeDecodeError:
                logger.debug(traceback.format_exc())
                try:
                    stdout = stdout.decode("latin-1")
                    stderr = stderr.decode("latin-1")
                except (UnicodeDecodeError, AttributeError):
                    logger.debug(traceback.format_exc())
        finally:
            timer.cancel()
            returncode = proc.returncode
        if not stdout:
            stdout = ""
        if not stderr:
            stderr = ""
        stderr = f"{' '.join(command_list)}\n{stderr!s}"
        if returncode:
            logger.error(f'FAILED run "{" ".join(command_list)}"')
        else:
            logger.debug(f'Succesfully run "{" ".join(command_list)}"')
        return returncode, stdout, stderr


class Ping(MyCommand):
    def __init__(self, host):
        self._host = host
        MyCommand.__init__(self, "ping")
        self._timeout = 10  # in seconds
        self._retry = 2

    def run(self):
        code, _, _ = super().run(
            linux_options=["-c", f"{self._retry}", "-w", f"{self._timeout}"],
            darwin_options=["-c", f"{self._retry}", "-t", f"{self._timeout}"],
            win_options=["-n", f"{self._retry}", "-w", f"{self._timeout * 1000}"],
            options=[self._host],
            timeout=self._timeout,
        )
        return code


def run_file(path):
    # Pas de EAFP cette fois puisqu'on est dans un process externe,
    # on ne peut pas gérer l'exception aussi facilement, donc on fait
    # des checks essentiels avant.

    # Vérifier que le fichier existe
    if not os.path.exists(path):
        msg = f"No such file: {path}"
        raise OSError(msg)

    # On a accès en lecture ?
    if hasattr(os, "access") and not os.access(path, os.R_OK):
        msg = f"Cannot access file: {path}"
        raise OSError(msg)

    # Lancer le bon programme pour le bon OS:

    if hasattr(os, "startfile"):  # Windows
        # Startfile est très limité sous Windows, on ne pourra pas savoir
        # si il y a eu une erreu
        proc = os.startfile(path)  # pylint: disable=no-member

    elif sys.platform.startswith("linux"):  # Linux:
        proc = subprocess.Popen(
            ["xdg-open", path],
            # on capture stdin et out pour rendre le
            # tout non bloquant
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    elif sys.platform == "darwin":  # Mac:
        proc = subprocess.Popen(
            ["open", "--", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    else:
        msg = f"Your `{sys.platform}` isn't a supported operatin system`."
        raise NotImplementedError(
            msg,
        )

    # Proc sera toujours None sous Windows. Sous les autres OS, il permet de
    # récupérer le status code du programme, and lire / ecrire sur stdin et out
    return proc
