import importlib.util
import os
import pathlib
from typing import Any, Literal, TypedDict, Union, cast


class Config(TypedDict):
    display_as: Literal["widget", "html"]
    dev: bool
    defaults: dict[Any, Any]


def configure(options: dict[str, Any] = {}, **kwargs: Any) -> None:
    CONFIG.update(cast(Config, {**options, **kwargs}))


def get_config(k: str) -> Union[str, None]:
    return CONFIG.get(k)


try:
    # First try the importlib.util approach
    util_spec = importlib.util.find_spec("colight.util")
    if util_spec and util_spec.origin:
        COLIGHT_PATH = pathlib.Path(util_spec.origin).parent
    else:
        # Fallback: Get the directory of the current file
        COLIGHT_PATH = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
except Exception:
    # Another fallback approach
    COLIGHT_PATH = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


CONFIG: Config = {"display_as": "widget", "dev": False, "defaults": {}}

# CDN URLs for published assets - set during package build
VERSIONED_CDN_DIST_URL = "https://cdn.jsdelivr.net/npm/@colight/core@2025.7.7/widget.mjs"
UNVERSIONED_CDN_DIST_URL = "https://cdn.jsdelivr.net/npm/@colight/core/dist"
DIST_URL = str(VERSIONED_CDN_DIST_URL or "/dist")

# js-dist is always in the colight package directory
DIST_LOCAL_PATH = COLIGHT_PATH / "js-dist"

# Local development paths
WIDGET_PATH = DIST_LOCAL_PATH / "widget.mjs"
ANYWIDGET_PATH = str(WIDGET_PATH).replace("widget.mjs", "anywidget.mjs")
