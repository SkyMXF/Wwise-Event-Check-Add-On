import os
import datetime
import argparse
import subprocess

from waapi import WaapiClient

from log_utils import LOGGER, set_logging_config
from waapi_utils import WaapiUtils


def parse_args():
    parser = argparse.ArgumentParser(description='Check event packing')
    parser.add_argument('project_path', type=str, help='Project path')
    parser.add_argument('output_path', type=str, help='Output path')
    parser.add_argument('waapi_port', type=int, help='WAAPI port')
    return parser.parse_args()


def exit_script(code: int):
    input("Press any key to exit...")
    exit(code)


if __name__ == '__main__':

    cmd_args = parse_args()
    proj_path = cmd_args.project_path
    output_path = cmd_args.output_path
    waapi_port = cmd_args.waapi_port

    set_logging_config()

    waapi_url = "ws://127.0.0.1:%s/waapi" % waapi_port

    with WaapiClient(url=waapi_url) as client:
        waapi_wrapper = WaapiUtils(client)

        # check project path
        waapi_proj_path = waapi_wrapper.get_project_path()
        if waapi_proj_path is None:
            LOGGER.error("Failed to get project path from WAAPI.")
            exit_script(1)
        waapi_proj_path = os.path.normpath(os.path.abspath(waapi_proj_path))
        proj_path = os.path.normpath(os.path.abspath(proj_path))
        if waapi_proj_path is None or waapi_proj_path != proj_path:
            LOGGER.error(
                "Failed to match project path from WAAPI. waapi: %s, expect: %s" % (
                    waapi_proj_path, proj_path
                )
            )
            exit_script(1)

        # get all events
        event_dict = waapi_wrapper.get_event_dict()
        if event_dict is None:
            LOGGER.error("Failed to get event info from WAAPI.")
            exit_script(1)

        # get included events
        sound_bank_list = waapi_wrapper.get_sound_bank_list()
        inclusion_objects: list[str] = []
        for sound_bank_name in sound_bank_list:
            inclusion_objects.extend(waapi_wrapper.get_sound_bank_inclusions(sound_bank_name))
        include_events = waapi_wrapper.get_include_events(inclusion_objects)

    # remove included events from dict
    for event_name in include_events:
        event_dict.pop(event_name, None)

    # print not included events
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    print_file = os.path.join(
        output_path, datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    )
    with open(print_file, "w", encoding="utf-8", errors="ignore") as f:
        print("EventName,Path", file=f)
        LOGGER.info("Not included events:")
        for event_name, event_path in event_dict.items():
            print("%s,%s" % (event_name, event_path), file=f)
            print(event_name)

    # open output dir in explorer
    subprocess.Popen('explorer /select,"%s"' % print_file)

    LOGGER.info("Check event inclusion done. Output: %s" % print_file)
    exit_script(0)
