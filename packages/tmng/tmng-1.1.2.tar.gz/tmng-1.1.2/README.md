# Performance Timing Module (`tmng`)

<img
  src="https://raw.githubusercontent.com/lguibr/timing/main/logo.png"
  alt="screenshot"
  width="400"
/>

A framework-agnostic, process-safe, local performance timer for Python applications, designed for easy development and debugging. It logs timing data to a local SQLite file, avoiding external dependencies and network latency.

This module is built for reliability, using **Pydantic** for rigorous data validation and serialization, ensuring that every timing event recorded is structured and correct.

## Key Features

- **Simple CLI:** Manage the tool with intuitive commands like `timing enable`, `timing report`.
- **Framework-Agnostic:** Works with Django, Flask, FastAPI, or any Python script.
- **Pydantic-Powered Validation:** All timing events are validated against a strict schema.
- **Process-Safe:** Works flawlessly across multiple processes.
- **Globally Switchable:** Enable or disable via the CLI or an environment variable.
- **Rich, Validated Context:** Attach metadata (e.g., `user_id`, `task_id`) to your timing events.

---

## Quickstart

1.  **Install the Package from PyPI:**
    ```bash
    pip install tmng
    ```

2.  **Enable the Timer:**
    This only needs to be done once. It creates a config file in your user directory.
    ```bash
    timing enable
    ```

3.  **Initialize the Database:**
    Run this once in your project's root directory to create the `timing_log.db` file.
    ```bash
    timing init
    ```

4.  **Add Timing to Your Code:**
    Use the decorators or context managers as needed.
    ```python
    from timing import time_block, time_function

    # Best for specific blocks
    with time_block("api_call", service="xero"):
        # ... timed code ...

    # Best for entire functions
    @time_function
    def send_weekly_emails(user_id):
        # ... timed function ...
    ```

5.  **Generate a Report:**
    After your code has run, generate an interactive HTML dashboard.
    ```bash
    timing report
    ```
    This will generate `timing_dashboard.html` and open it in your browser.

---

## CLI Usage

The `timing` command is your main entry point for managing the tool.

| Command                                        | Description                                                |
| :--------------------------------------------- | :--------------------------------------------------------- |
| `timing status`                                | Check if the tool is enabled and see the event count.      |
| `timing enable`                                | Globally enables the timing tool for your user.            |
| `timing disable`                               | Globally disables the timing tool.                         |
| `timing init`                                  | Creates the SQLite database file in the current directory. |
| `timing report`                                | Generates the interactive HTML report.                     |
| `timing report --output "perf.html" --no-open` | Customize report generation.                               |

---

## Environment Variables

For servers or CI/CD, you can override the global config with environment variables:

-   `TIMING_TOOL_ENABLED`: Set to `true` to enable the timer. This takes precedence over the CLI setting.
-   `TIMING_DB_PATH`: Set the full path to your database file (e.g., `/var/data/my_app_timing.db`).

---

## Viewing the Data

You can still use any SQLite client to view the `timing_log.db` file or use the built-in report generator:
```bash
timing report
```