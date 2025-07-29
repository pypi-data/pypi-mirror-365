# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.

"""Waldiez run results module."""

from typing import TYPE_CHECKING, TypedDict, Union

if TYPE_CHECKING:
    from autogen.io.run_response import (  # type: ignore[import-untyped]
        AsyncRunResponseProtocol,
        RunResponseProtocol,
    )


class WaldiezRunResults(TypedDict):
    """Results of the Waldiez run."""

    results: Union[
        list["RunResponseProtocol"], list["AsyncRunResponseProtocol"]
    ]
    exception: Exception | None
    completed: bool
