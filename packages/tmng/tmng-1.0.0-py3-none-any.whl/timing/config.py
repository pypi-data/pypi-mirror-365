import os
import json
from pathlib import Path
import appdirs

# --- NEW: Centralized config file management ---
APP_NAME = "TimingTool"
CONFIG_DIR = Path(appdirs.user_config_dir(APP_NAME))
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_enabled_state() -> bool:
    """Reads the enabled state from the config file."""
    if not CONFIG_FILE.exists():
        return False
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("enabled", False)
    except (json.JSONDecodeError, IOError):
        return False


def set_enabled_state(is_enabled: bool):
    """Writes the enabled state to the config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"enabled": is_enabled}, f)


class TimingSettings:
    """
    A centralized class for accessing timing tool settings.
    It prioritizes environment variables over the global config file.
    """

    @property
    def IS_ENABLED(self) -> bool:
        """
        Global switch for the entire timing tool.
        1. Reads from the TIMING_TOOL_ENABLED environment variable.
        2. If not set, falls back to the global config file (~/.config/TimingTool/config.json).
        """
        enabled_str = os.getenv("TIMING_TOOL_ENABLED", "").lower()
        if enabled_str:
            return enabled_str in ("true", "1", "t", "yes")

        # Fallback to config file
        return get_enabled_state()

    @property
    def DB_PATH(self) -> Path:
        """
        The absolute path to the SQLite database file.
        Reads from the TIMING_DB_PATH environment variable.
        Defaults to 'timing_log.db' in the current working directory if not set.
        """
        default_path = Path.cwd() / "timing_log.db"
        path_str = os.getenv("TIMING_DB_PATH", str(default_path))
        return Path(path_str)


timing_settings = TimingSettings()
