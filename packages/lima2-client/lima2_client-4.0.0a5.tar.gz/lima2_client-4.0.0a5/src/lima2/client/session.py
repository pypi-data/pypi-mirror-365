# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client session."""


from typing import Any

import requests

from lima2.client.exceptions import (
    ConductorClientError,
    ConductorConnectionError,
    ConductorServerError,
    ConductorUnhandledError,
    MalformedConductorResponse,
)


def decode_error(response: requests.Response) -> tuple[dict[str, Any], str]:
    """Decode an error contained in the conductor's HTTP response.

    If the response is unexpectedly formed (invalid JSON, 'error' key missing),
    raises a ConductorMalformedResponseError with an appropriate message.

    Returns the tuple (payload, error).

    Raises:
      ConductorMalformedResponseError: The response contains an invalid JSON
        payload, or the 'error' key is missing.
    """

    try:
        payload = response.json()
    except requests.JSONDecodeError as e:
        raise MalformedConductorResponse(
            f"Conductor returned a {response.status_code} "
            f"error, but the payload isn't valid json.\nContent: {repr(response.content)}\n"
            f"See decoding error above.",
        ) from e

    try:
        error = payload["error"]
    except KeyError:
        raise MalformedConductorResponse(
            f"Conductor returned a {response.status_code} "
            f"error with a valid json payload, but the 'error' key is missing.\n"
            f"Payload: {repr(payload)}",
        )

    return payload, error


class ConductorSession:
    def __init__(self, hostname: str, port: int) -> None:
        self.hostname = hostname
        self.port = port
        self.session = requests.Session()

    @property
    def base_url(self) -> str:
        return f"http://{self.hostname}:{self.port}"

    def get(self, endpoint: str, *args, **kwargs) -> requests.Response:
        """Make a GET request at /{endpoint}.

        Raises:
          ConductorConnectionError: The conductor fails to respond.
          ConductorClientError: The status code is in [400, 499].
          ConductorUnhandledError: The status code is 500.
          ConductorServerError: The status code is in [501, 599].
          ConductorMalformedResponseError: The status code is 4xx
            or 5xx, but the contained payload cannot be interpreted.
        """
        try:
            res = self.session.get(f"{self.base_url}{endpoint}", *args, **kwargs)
        except requests.ConnectionError as e:
            raise ConductorConnectionError(
                f"Conductor server at {self.base_url} is unreachable"
            ) from e

        if 400 <= res.status_code < 500:
            _, error = decode_error(response=res)
            raise ConductorClientError(reason=res.reason, error=error)
        elif 501 <= res.status_code < 600:
            _, error = decode_error(response=res)
            raise ConductorServerError(reason=res.reason, error=error)
        elif res.status_code == 500:
            payload, error = decode_error(response=res)
            raise ConductorUnhandledError(
                method=res.request.method or "?",
                url=res.request.url or "?",
                error=error,
                trace=payload["trace"],
            )
        else:
            return res

    def post(self, endpoint: str, *args, **kwargs) -> requests.Response:
        """Make a POST request at /{endpoint}.

        Raises:
          ConductorConnectionError: The conductor fails to respond.
          ConductorClientError: The status code is in [400, 499].
          ConductorUnhandledError: The status code is 500.
          ConductorServerError: The status code is in [501, 599].
          ConductorMalformedResponseError: The status code is 4xx
            or 5xx, but the contained payload cannot be interpreted.
        """
        try:
            res = self.session.post(f"{self.base_url}{endpoint}", *args, **kwargs)
        except requests.ConnectionError as e:
            raise ConductorConnectionError(
                f"Conductor server at {self.base_url} is unreachable"
            ) from e

        if 400 <= res.status_code < 500:
            _, error = decode_error(response=res)
            raise ConductorClientError(reason=res.reason, error=error)
        elif 501 <= res.status_code < 600:
            _, error = decode_error(response=res)
            raise ConductorServerError(reason=res.reason, error=error)
        elif res.status_code == 500:
            payload, error = decode_error(response=res)
            raise ConductorUnhandledError(
                method=res.request.method or "?",
                url=res.request.url or "?",
                error=error,
                trace=payload["trace"],
            )
        else:
            return res
