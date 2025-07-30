# use following command to compil: python setup_cython.py build_ext --inplace
import contextlib
import errno
import logging
import os
import shutil
from sysconfig import get_config_var

import setuptools
from Cython.Build import cythonize

import songfinder

logger = logging.getLogger(__name__)


def prepare():
    if songfinder.__myOs__ == "windows":
        compile_args = [
            "/O2",
        ]  # Do not use /fp:fast, this will screw up with correction algorithm
    else:
        compile_args = ["-O3"]

    c_extensions = []
    cython_extensions = []
    names = []

    chemin_scr = os.path.abspath(
        os.path.join(songfinder.__chemin_root__, songfinder.__appName__),
    )
    chemin_comp = os.path.join(songfinder.__chemin_root__, "comp")
    chemin_lib = os.path.join(chemin_scr, "lib")
    lib_ext = [".so", ".dll", ".pyd"]

    logger.info(f'[cython] source dir: "{chemin_scr}"')
    logger.info(f'[cython] comp dir: "{chemin_comp}"')
    logger.info(f'[cython] lib dir: "{chemin_lib}"')

    try:
        os.makedirs(chemin_comp)
    except OSError as error:
        if error.errno == errno.EEXIST:
            pass
        else:
            raise
    try:
        os.makedirs(chemin_lib)
        with open(os.path.join(chemin_lib, "__init__.py"), "w"):
            pass
    except OSError as error:
        if error.errno == errno.EEXIST:
            pass
        else:
            raise

    file_to_compil = {"creplace"}
    file_to_cythonize = {
        "pyreplace",
        "distances",
        "fonctions",
        "data_base",
        "gestchant",
    }

    def _get_lib_name(name):
        lib_name = str(f"{songfinder.__appName__}.lib.{name}")
        if not target_info:
            lib_name = str(f"{lib_name}_{songfinder.__arch__}")
        return lib_name

    def _get_file_name(name, ext):
        if target_info:
            file_name = str(f"{name}{target_info}")
        else:
            file_name = str(f"{name}_{songfinder.__arch__}")
        return f"{file_name}{ext}"

    try:
        target_info = os.path.splitext(get_config_var("EXT_SUFFIX"))[0]
    except AttributeError:
        target_info = ""

    for _root, _dirs, files in os.walk(chemin_lib):
        for fichier in files:
            nom = os.path.splitext(os.path.split(fichier)[1])[0]
            nom = nom.replace(target_info, "")
            first_part_name = nom.split("_")[0] if target_info else nom.split(".")[0]
            set_to_test = set((nom, first_part_name))
            all_sources = file_to_cythonize | file_to_compil
            if (
                set_to_test & all_sources == set()
                and os.path.splitext(fichier)[1] in lib_ext
            ):
                with contextlib.suppress(OSError, IOError):
                    os.remove(os.path.join(chemin_lib, fichier))

    # Copy file to compile in the comp directory
    # Delete old library files
    for file_comp in file_to_cythonize:
        py_src_file = os.path.join(chemin_scr, f"{file_comp}.py")
        pyx_src_file = os.path.join(chemin_scr, f"{file_comp}.pyx")
        src_file = pyx_src_file if os.path.isfile(pyx_src_file) else py_src_file
        dst_file = os.path.join(chemin_comp, f"{file_comp}.pyx")

        if (
            not os.path.isfile(dst_file)
            or os.stat(src_file).st_mtime > os.stat(dst_file).st_mtime
        ):
            for ext in lib_ext:
                with contextlib.suppress(OSError, IOError):
                    os.remove(os.path.join(chemin_lib, _get_file_name(file_comp, ext)))
            shutil.copy(src_file, dst_file)

    # Find all module to compile with Cython
    for root, _dirs, files in os.walk(chemin_comp):
        for fichier in files:
            nom = os.path.splitext(os.path.split(fichier)[1])[0]
            full_name = os.path.join(root, fichier)
            tests = [
                os.path.isfile(tested)
                for tested in [
                    os.path.join(chemin_lib, _get_file_name(nom, ext))
                    for ext in lib_ext
                ]
            ]
            tests += [nom not in file_to_cythonize]
            if os.path.splitext(fichier)[1] == ".pyx" and not sum(tests) > 0:
                names.append(nom)
                # https://stackoverflow.com/questions/31043774/customize-location-of-so-file-generated-by-cython
                cython_extensions.append(
                    setuptools.Extension(
                        _get_lib_name(nom),
                        [str(full_name)],
                        extra_compile_args=compile_args,
                    ),
                )

    # Compiling c source files
    for root, _dirs, files in os.walk(chemin_comp):
        for fichier in files:
            nom = os.path.splitext(os.path.split(fichier)[1])[0]
            if nom in file_to_compil:
                src_file = os.path.join(root, fichier)
                max_date = os.stat(src_file).st_mtime
                for ext in lib_ext:
                    file_to_test = os.path.join(chemin_lib, _get_file_name(nom, ext))
                    if (
                        os.path.isfile(file_to_test)
                        and max_date < os.stat(file_to_test).st_mtime
                    ):
                        max_date = os.stat(file_to_test).st_mtime
                if max_date <= os.stat(src_file).st_mtime:
                    names.append(nom)
                    c_extensions.append(
                        setuptools.Extension(
                            _get_lib_name(nom),
                            [str(src_file)],
                            extra_compile_args=compile_args,
                        ),
                    )

    extensions = c_extensions + cythonize(cython_extensions)

    return names, extensions


def docompile():
    names, extensions = prepare()

    if extensions != []:
        logger.debug(f"[cython] Compiling modules: {', '.join(names)}")
        setuptools.setup(ext_modules=extensions)


if __name__ == "__main__":
    docompile()
