import importlib
import logging
import os
from sysconfig import get_config_var

from songfinder import __appName__, __arch__

logger = logging.getLogger(__name__)


def load(full_file_name, py2c=False):
    file_name_in = os.path.splitext(os.path.split(full_file_name)[1])[0]
    file_names = [file_name_in]
    if py2c:
        file_names.insert(0, f"c{file_name_in[2:]}")
    try:
        target_info = os.path.splitext(get_config_var("EXT_SUFFIX"))[0]
    except AttributeError:
        target_info = None

    imported = False
    for file_name in file_names:
        lib_name = str(f"{__appName__}.lib.{file_name}")
        if not target_info:
            lib_name = str(f"{lib_name}_{__arch__}")
        try:
            module = importlib.import_module(lib_name)
        except (ImportError, NameError):
            pass
        else:
            imported = True
            logger.debug(f"Using compiled version {file_name} module")
            return module

    if not imported:
        raise ImportError

    return None
