import os
import json
import stat
import shutil
import argparse
import logging
from waapi import WaapiClient

from waapi_utils import WaapiUtils


EXECUTABLE_NAME = "check_event_inclusion.exe"
CMD_DEF_FILE = "check_event_inclusion.json"


LOGGER = logging.getLogger("Check event inclusion installer")


def set_logger():
    logger = LOGGER
    logger.setLevel(logging.INFO)

    # color
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def parse_args():
    parser = argparse.ArgumentParser(description='Check event packing')
    parser.add_argument('--waapi_port', type=int, default=8080, help='WAAPI port')
    parser.add_argument('--base_menu', type=str, default="CustomTools", help='Base menu')
    return parser.parse_args()


def exit_script(code: int):
    input("Press any key to exit...")
    exit(code)


if __name__ == '__main__':

    set_logger()

    cmd_args = parse_args()
    waapi_port = cmd_args.waapi_port
    base_menu = cmd_args.base_menu

    LOGGER.info(
        "Using WAAPI port: %d." % waapi_port
        + "Set custom port with --waapi_port option."
    )

    waapi_url = "ws://127.0.0.1:%d/waapi" % waapi_port

    with WaapiClient(url=waapi_url) as client:
        waapi_wrapper = WaapiUtils(client)

        # get Wwise install info
        wwise_info = waapi_wrapper.get_wwise_info()
        if wwise_info is None:
            LOGGER.error("Failed to get Wwise info from WAAPI.")
            exit_script(1)

        version_info = wwise_info["version"]["displayName"]
        LOGGER.info("Installing for Wwise: %s" % version_info)
        install_dir = wwise_info["directories"]["authoring"]
        install_dir = os.path.join(install_dir, "Data", "Add-ons", "Commands")
        install_dir = os.path.abspath(os.path.normpath(install_dir))
        LOGGER.info("Installing under: '%s'" % install_dir)

        # get project path
        waapi_proj_path = waapi_wrapper.get_project_path()
        if waapi_proj_path is None:
            LOGGER.error("Failed to get project path from WAAPI.")
            exit_script(1)
        waapi_proj_path = os.path.normpath(os.path.abspath(waapi_proj_path))
        LOGGER.info("Installing for project: %s" % waapi_proj_path)

        # log output dir
        log_out_dir = os.path.abspath(os.path.normpath("output_log"))

        if not os.path.exists(install_dir):
            os.makedirs(install_dir)

        # create command definition json
        LOGGER.info("Creating command definition... Menu base path: %s" % base_menu)
        cmd_def = {
            "commands": [
                {
                    "id": "garena.check_event_inclusion",
                    "displayName": "Check Event Inclusion",
                    "program": os.path.join(install_dir, EXECUTABLE_NAME),
                    "args": '"%s" "%s" %d' % (waapi_proj_path, log_out_dir, waapi_port),
                    "startMode": "SingleSelectionSingleProcess",
                    "mainMenu": {
                        "basePath": base_menu,
                    }
                }
            ]
        }
        cmd_def_path = os.path.join(install_dir, CMD_DEF_FILE)
        if os.path.exists(cmd_def_path):
            # set write permission
            os.chmod(cmd_def_path, stat.S_IWRITE)
        with open(cmd_def_path, "w") as f:
            json.dump(cmd_def, f, indent=4)

        # copy executable to install dir
        exe_path = os.path.join(install_dir, EXECUTABLE_NAME)
        if os.path.exists(exe_path):
            os.remove(exe_path)
        shutil.copy(EXECUTABLE_NAME, exe_path)

        LOGGER.info(
            "Install done. Restart Wwise and try %s/Check Event Inclusion in main menu." % base_menu
        )
        exit_script(0)
