import codecs
import contextlib
import logging
import os
import shutil
import tkinter as tk
import traceback

try:  # Windows only imports
    import win32api
    import win32con
except ImportError:
    pass

import songfinder
from songfinder import __version__, commandLine
from songfinder import classSettings as settings
from songfinder import fonctions as fonc
from songfinder import messages as tkMessageBox
from songfinder.gui import guiHelper, inputFrame

logger = logging.getLogger(__name__)

COMMANDS = {
    "addAll": {"hg": ["addr"], "git": ["add", "-A"]},
    "pullUpdate": {"hg": ["pull", "-u"], "git": ["pull", "--rebase"]},
    "rebaseAbort": {"hg": ["update", "-C"], "git": ["rebase", "--abort"]},
    "resetHead": {"hg": ["update", "-C"], "git": ["reset", "--hard", "origin/master"]},
    "config_file": {"hg": ["hgrc"], "git": ["config"]},
    "insecure": {"hg": ["--insecure"], "git": []},
    "remote": {"hg": ["default"], "git": ["origin"]},
    "merge": {"hg": ["merge"], "git": ["merge"]},
}

CLEUSB = {"USBEI", "USBETIENNE"}

REMOTE_FAILURE = 2
HG_PULL_ERROR = 255
HG_PUSH_ERROR = 128


MERCURIAL_HGRC = """# example repository config (see 'hg help config' for more info)
[paths]
default = %s

# path aliases to other clones of this repo in URLs or filesystem paths
# (see 'hg help config.paths' for more info)
#
# default:pushurl = ssh://jdoe@example.net/hg/jdoes-fork
# my-fork         = ssh://jdoe@example.net/hg/jdoes-fork
# my-clone        = /home/jdoe/jdoes-clone

[auth]
sfData.prefix = %s
sfData.username = %s
sfData.password = %s

[ui]
# name and email (local to this repository, optional), e.g.
username = %s
"""

GIT_CONFIG = """[core]
    repositoryformatversion = 0
    filemode = false
    bare = false
    logallrefupdates = true
    ignorecase = true
[remote "origin"]
    url = https://%s:%s@%s
    fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
    remote = origin
    merge = refs/heads/master
[user]
    email = <>
    name = %s
"""


class AddRepo:  # TODO integrate to repo class
    def __init__(self, paths, exe, screens=None, update_data=None):
        fenetre = tk.Toplevel()
        with guiHelper.SmoothWindowCreation(fenetre, screens=screens):
            fenetre.title("Clonage d'un dépôt")
            self._update_data = update_data
            self.paths = paths
            self.fenetre = fenetre
            self.__exe = exe
            self.__ping = commandLine.Ping("google.fr")
            self.__scm = commandLine.MyCommand(self.__exe)
            self.__scm.check_command()

            self.prog = tk.Label(fenetre, text="", justify="left")
            self.ok_button = tk.Button(fenetre, text="Cloner", command=self._clone_repo)
            self.cancel_button = tk.Button(
                fenetre,
                text="Annuler",
                command=self._close_add_repo,
            )

            self._pathEntryFrame = inputFrame.entryField(
                fenetre,
                packing=tk.LEFT,
                text="Chemin",
                width=60,
            )
            self._userEntryFrame = inputFrame.entryField(
                fenetre,
                packing=tk.LEFT,
                text="Utilisateur",
                width=30,
            )
            self._passwordEntryFrame = inputFrame.entryField(
                fenetre,
                packing=tk.LEFT,
                text="Mot de passe",
                width=30,
            )

            self._pathEntryFrame.pack(side=tk.TOP, fill=tk.BOTH)
            self._userEntryFrame.pack(side=tk.TOP, fill=tk.BOTH)
            self._passwordEntryFrame.pack(side=tk.TOP, fill=tk.BOTH)

            self.ok_button.pack(side=tk.TOP)
            self.cancel_button.pack(side=tk.TOP)

            fenetre.bind_all("<KeyRelease-Return>", self._clone_repo)

    def _close_add_repo(self):
        if self.fenetre:
            self.fenetre.destroy()
            self.fenetre = None

    def _clone_repo(self, _event=None):
        self.update_fen("Récupération des informations ...")
        repo = self._pathEntryFrame.get()  # pylint: disable=no-member
        name = self._userEntryFrame.get()  # pylint: disable=no-member
        mdp = self._passwordEntryFrame.get()  # pylint: disable=no-member
        if not (repo and name and mdp):
            self.update_fen("    échec\n")
            tkMessageBox.showerror(
                "Erreur",
                "Erreur: les informations sont incomplètes",
            )
        else:
            self.prog.pack(side=tk.TOP, fill=tk.BOTH)
            self.update_fen("    ok\nVerification de la connexion ...")
            if self.__ping.run() == 0:
                self.update_fen("    ok\n")
            else:
                self.update_fen("    échec\n")
                # https://epef@bitbucket.org/epef/data

            return_code = -1
            err = "Invalid information"

            prefix = ""
            user = ""
            if repo:
                self.update_fen(
                    "Clonage du dépôt (ceci peut prendre quelques minutes) ...",
                )
                shutil.rmtree(self.paths.root)
                os.makedirs(self.paths.root)
                os.chdir(self.paths.root)
                arrobase = repo.find("@")
                user = repo[repo.find("://") + 3 : arrobase]
                prefix = repo[arrobase + 1 :]
                fullrepo = repo[:arrobase] + ":" + mdp + repo[arrobase:]
                return_code, _, err = self.__scm.run(
                    options=["clone"]
                    + COMMANDS["insecure"][self.__exe]
                    + [fullrepo, "."],
                )
                try:
                    self._make_hidden(os.path.join(self.paths.root, ".hg"))
                    self._make_hidden(os.path.join(self.paths.root, ".hgignore"))
                    self._make_hidden(
                        os.path.join(self.paths.root, "bitbucket-pipelines.yml"),
                    )
                except Exception:  # pylint: disable=broad-except
                    logger.warning(
                        f"Failed to make file hidden\n:{traceback.format_exc()}",
                    )
            if return_code != 0:
                self.update_fen("    échec\n")
                tkMessageBox.showerror(
                    "Erreur",
                    f"Erreur: le clonage du dépôt à échoué\nErreur {return_code}:\n{err}",
                )
                logger.error(
                    f'Clone of repository "{repo}" for user "{name}" in directory "{self.paths.root}" FAILED',
                )
                self._close_add_repo()
                settings.GENSETTINGS.set("Parameters", "sync", False)
            else:
                if self.__exe == "hg":
                    config_content = MERCURIAL_HGRC % (repo, prefix, user, mdp, name)
                elif self.__exe == "git":
                    config_content = GIT_CONFIG % (user, mdp, prefix, name)
                else:
                    config_content = ""
                config_file_path = os.path.join(
                    f".{self.__exe}",
                    COMMANDS["config_file"][self.__exe][0],
                )
                with codecs.open(
                    config_file_path,
                    "w",
                    encoding="utf-8",
                ) as config_file:
                    config_file.write(config_content)
                self.update_fen("    ok\n")
                tkMessageBox.showinfo("Confirmation", "Le dépôt à été cloné.")
                logger.info(
                    f'Repository "{repo}" as been cloned for user "{name}" in directory "{self.paths.root}"',
                )
                if self._update_data:
                    self._update_data()
                self._close_add_repo()
            os.chdir(songfinder.__chemin_root__)

    def update_fen(self, message):
        self.prog["text"] = self.prog["text"].replace("...", "") + message
        self.fenetre.update()
        self.fenetre.geometry(
            f"{self.fenetre.winfo_reqwidth()}x{self.fenetre.winfo_reqheight()}",
        )

    def _make_hidden(self, path):
        with contextlib.suppress(NameError):  # For Ubuntu
            win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_HIDDEN)


class Repo:
    def __init__(self, path, exe, papa=None, screens=None):
        self.__papa = papa
        self.__path = path
        self.__screens = screens

        self.__exe = exe
        self.__scm = commandLine.MyCommand(self.__exe)
        self.__ping = commandLine.Ping("google.fr")
        self.__scm.check_command()
        self.__commitName = f"Song Finder v{__version__}"
        self.__fen_recv = None

        self.__remotes = []
        self.__usbFound = []

        self.__show_gui = False

    def __gui(self):
        if self.__fen_recv:
            # This is the case where the windows as not been clsed properly
            # Ex the user closed the window
            try:
                self.__fen_recv.prog["text"]
            except tk.TclError:
                self.__close_send_recv_progress()
        if self.__show_gui and not self.__fen_recv:
            self.__fen_recv = tk.Toplevel(self.__papa)
            with guiHelper.SmoothWindowCreation(
                self.__fen_recv,
                screens=self.__screens,
            ):
                self.__fen_recv.title("Reception/Envoi")
                self.__fen_recv.prog = tk.Label(
                    self.__fen_recv,
                    text="",
                    justify="left",
                )
                self.__fen_recv.prog.grid(sticky="w")

    def __close_send_recv_progress(self):
        if self.__show_gui and self.__fen_recv:
            self.__fen_recv.destroy()
            self.__fen_recv = None

    def __update_fen(self, message):
        if self.__show_gui and self.__fen_recv:
            new_text = self.__fen_recv.prog["text"].replace("...", "")
            exce_list = set(self.__usbFound) | {"ok", "échec", "aucune"}
            if not set(message.split(" ")) & exce_list:
                new_text += "\n"
            new_text += message
            new_text = fonc.strip_perso(new_text.replace("\n\n", "\n"), "\n")
            self.__fen_recv.prog["text"] = new_text
            self.__fen_recv.update()
            self.__fen_recv.geometry(
                f"{self.__fen_recv.winfo_reqwidth()}x{self.__fen_recv.winfo_reqheight()}",
            )
            self.__fen_recv.update()

    def __show_error(self, message):
        self.__update_fen("    échec")
        tkMessageBox.showerror("Erreur", message)
        self.__close_add_repo()
        return 2

    def __show_info(self, message):
        self.__update_fen("    ok")
        if self.__show_gui and self.__fen_recv:
            tkMessageBox.showinfo("Confirmation", message)
        self.__close_add_repo()
        return 0

    def __close_add_repo(self):
        os.chdir(songfinder.__chemin_root__)
        self.__close_send_recv_progress()

    def __check_connection(self):
        self.__update_fen("Vérification de la connexion ...")
        if self.__ping.run() == 0:
            self.__update_fen("    ok")
            self.__remotes.append(COMMANDS["remote"][self.__exe][0])
        else:
            self.__update_fen("    échec\n")

    def __get_remotes(self):
        if not self.__remotes:
            self.__check_connection()
            if not self.__remotes:
                return self.__show_error(
                    "La connection a échoué. Verifiez votre connexion à internet.",
                )
        return 0

    def receive(self, send=False, show_gui=True):
        self.__show_gui = show_gui
        self.__gui()
        if self.__get_remotes() == REMOTE_FAILURE:
            return REMOTE_FAILURE
        os.chdir(self.__path)
        self.__update_fen("Réception des modifications ...")
        code, out, err = self.__scm.run(
            options=COMMANDS["pullUpdate"][self.__exe] + [self.__remotes[0]],
        )

        outerr = out + err

        if (
            outerr.find("no changes found") != -1
            or outerr.find("aucun changement trouv") != -1
            or outerr.find("Already up to date") != -1
            or outerr.find("Déjà à jour") != -1
        ):
            if send:
                self.__update_fen("    ok")
            else:
                self.__show_info("Rien a recevoir")
            return 1
        if outerr.find("You have unstaged changes") != -1:
            self.__show_info(
                "Des modifications sont en cours. Essayez d'envoyer vos modifications directement. Pour éviter cette erreur, réceptionnez d'abord les modifications des autres utilisateurs avant d'appliquer les vôtres.",
            )
            return 1
        if self.__exe == "hg" and code == HG_PULL_ERROR:
            return self.__show_error(
                f"Erreur: Impossible de recupérer les modifications.\nErreur {code}:\n{out}\n{err}",
            )
        if self.__exe == "hg" and code == HG_PUSH_ERROR:
            self.__close_add_repo()
            return 0
        if (
            outerr.find("other heads") != -1
            or outerr.find(" autre instantan") != -1
            or outerr.find("CONFLICT") != -1
        ):
            logger.info(f"git conflict impossible to rebase:\n{out}\n{err}")
            ask_message = (
                f"Erreur: Impossible de recupérer les modifications.\n"
                f"Erreur {code}:\n{out}\n{err}\n"
                "Ceci peut être du au fait que vos modifications sont incompatibles "
                "avec les modifications faites par un autre utilisateur."
                "Pour résoudre ce conflit vous devez annuler vos modifications "
                "et receptionner les modifications faites par l"
                "autre utilisateurs."
                "Voulez vous annuler vos modifications (ceci effacera tout vos changements.) ?"
            )
            if tkMessageBox.askyesno("Erreur", ask_message):
                if self.__exe == "hg":
                    code, out, err = self.__scm.run(
                        options=COMMANDS["merge"][self.__exe],
                    )
                    code, out, err = self.__scm.run(
                        options=["resolve", "-t", "internal:other", "--all"],
                    )
                    code, out, err = self.__scm.run(
                        options=["commit", "-m", f'"{self.__commitName} merge"'],
                    )
                elif self.__exe == "git":
                    code, out, err = self.__scm.run(
                        options=COMMANDS["rebaseAbort"][self.__exe],
                    )
                    code, out, err = self.__scm.run(
                        options=COMMANDS["resetHead"][self.__exe],
                    )
                if code != 0:
                    return self.__show_error(
                        f"Erreur: la reception forcé à échoué\nErreur {code}:\n{out}\n{err}",
                    )
        if code == 0:
            if send:
                self.__update_fen("    ok")
                return 0
            self.__close_send_recv_progress()
            return self.__show_info("Les modifications ont bien été recus.")
        return 0

    def send(self, what="all", show_gui=True):
        self.__show_gui = show_gui
        self.__gui()
        if self.__get_remotes() == REMOTE_FAILURE:
            return REMOTE_FAILURE
        os.chdir(self.__path)
        returns = []
        errs = []
        self.__update_fen("Validation des modifications ...")
        code = 0
        out = ""
        err = ""
        if what == "all":
            code, out, err = self.__scm.run(options=COMMANDS["addAll"][self.__exe])
            if not code:
                code, out, err = self.__scm.run(
                    options=["commit", "-m", f'"{self.__commitName}"'],
                )
        elif what:
            if self.__exe == "hg":
                code, out, err = self.__scm.run(
                    options=["commit", "-I", what, "-m", f'"{self.__commitName}"'],
                )
            elif self.__exe == "git":
                code, out, err = self.__scm.run(options=["add", what])
                if not code:
                    code, out, err = self.__scm.run(
                        options=["commit", "-m", f'"{self.__commitName}"'],
                    )

        outerr = out + err
        if (
            outerr.find("nothing changed") != -1
            or outerr.find("aucun changement") != -1
            or outerr.find("nothing to commit") != -1
            or outerr.find("rien à valider") != -1
        ):
            self.__show_info("Rien à envoyer")
            return 1
        if code != 0:
            self.__update_fen("    échec\n")
            return self.__show_error(
                f"Erreur: la validation a échoué.\nErreur {code}:\n{out}\n{err}",
            )
        self.__update_fen("Envoi des modifications ...")
        receive_return = self.receive(send=True, show_gui=show_gui)
        if receive_return == REMOTE_FAILURE:
            return REMOTE_FAILURE
        for remote in self.__remotes:
            code, out, err = self.__scm.run(options=["push", remote])
            errs.append(err)
            returns.append(str(code))
        if returns == ["0"] * len(self.__remotes):
            self.__close_send_recv_progress()
            return (
                self.__show_info(
                    f"Les modifications ont été envoyées sur : {', '.join(self.__remotes)}",
                )
                or receive_return
            )
        return self.__show_error(f"Erreur {' '.join(returns)}:\n{''.join(errs)}")
