from waapi import WaapiClient, WaapiRequestFailed, CannotConnectToWaapiException

from log_utils import LOGGER


class WaapiUtils(object):

    def __init__(self, client: WaapiClient):
        self.client = client

    def _inner_call(self, uri: str, args: dict, options: dict) -> dict | list | None:

        LOGGER.debug("Calling WAAPI: %s" % {"uri": uri, "args": args, "options": options})

        if self.client is None:
            LOGGER.error("WAAPI client cannot connect.")
            return None

        if not self.client.is_connected():
            LOGGER.error("WAAPI client not connected.")
            return None

        try:
            args["options"] = options
            result = self.client.call(uri, args)
        except CannotConnectToWaapiException as e:
            LOGGER.error("Failed to connect to WAAPI: %s" % e)
            return None
        except WaapiRequestFailed as e:
            LOGGER.error("Failed to call WAAPI '%s': %s" % (uri, e))
            return None

        LOGGER.debug("WAAPI result: %s" % result)

        return result

    def get_project_path(self) -> str | None:
        result = self._inner_call(
            uri="ak.wwise.core.object.get",
            args={
                "from": {"ofType": ["Project"]}
            },
            options={
                "return": ["name", "filePath"]
            }
        )
        if result is None or not isinstance(result, dict) or "return" not in result:
            return None

        result = result["return"]
        if not isinstance(result, list) or len(result) == 0:
            return None

        result = result[0]
        if not isinstance(result, dict) or "filePath" not in result or "name" not in result:
            return None

        return result["filePath"]

    def get_wwise_info(self) -> dict | None:
        result = self._inner_call(
            uri="ak.wwise.core.getInfo",
            args={},
            options={}
        )
        if result is None or not isinstance(result, dict):
            return None

        return result

    def get_event_dict(self) -> dict[str, str] | None:
        result = self._inner_call(
            uri="ak.wwise.core.object.get",
            args={
                "from": {"ofType": ["Event"]}
            },
            options={
                "return": ["name", "path"]
            }
        )
        if result is None or not isinstance(result, dict) or "return" not in result:
            return None

        result = result["return"]
        if not isinstance(result, list):
            return None

        return {event["name"]: event["path"] for event in result}

    def get_sound_bank_list(self) -> set[str] | None:
        result = self._inner_call(
            uri="ak.wwise.core.object.get",
            args={
                "from": {"ofType": ["SoundBank"]}
            },
            options={
                "return": ["name"]
            }
        )
        if result is None or not isinstance(result, dict) or "return" not in result:
            return None

        result = result["return"]
        if not isinstance(result, list):
            return None

        return {sound_bank["name"] for sound_bank in result}

    def get_sound_bank_inclusions(self, sound_bank_name: str) -> list[str] | None:
        result = self._inner_call(
            uri="ak.wwise.core.soundbank.getInclusions",
            args={
                "soundbank": "SoundBank:" + sound_bank_name
            },
            options={}
        )
        if result is None or not isinstance(result, dict) or "inclusions" not in result:
            return None

        # result format: {
        #     "inclusions": [
        #         {
        #             "object": "{GUID}",
        #             "filter": ["events","structures","media"]
        #         }
        #     ]
        # }

        return [info["object"] for info in result["inclusions"]]

    def get_include_events(self, event_or_parent_ids: list[str]) -> set[str] | None:

        include_events: set[str] = set()

        # get descendants
        result = self._inner_call(
            uri="ak.wwise.core.object.get",
            args={
                "from": {"id": event_or_parent_ids},
                "transform": [
                    {"select": ["descendants"]},
                    {"where": ["type:isIn", ["Event"]]}
                ]
            },
            options={
                "return": ["name"]
            }
        )
        if result is None or not isinstance(result, dict) or "return" not in result:
            return None

        result = result["return"]
        if not isinstance(result, list):
            return None

        include_events.update({event["name"] for event in result})

        # get self
        result = self._inner_call(
            uri="ak.wwise.core.object.get",
            args={
                "from": {"id": event_or_parent_ids},
                "transform": [
                    {"where": ["type:isIn", ["Event"]]}
                ]
            },
            options={
                "return": ["name"]
            }
        )
        if result is None or not isinstance(result, dict) or "return" not in result:
            return None

        result = result["return"]
        if not isinstance(result, list):
            return None

        include_events.update({event["name"] for event in result})

        return include_events
