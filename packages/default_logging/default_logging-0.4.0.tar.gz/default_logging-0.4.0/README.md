# default_logging

A Python package for standardized logging configuration with millisecond-precision timestamps, timezone-aware formatting, and seamless OpenTelemetry trace context integration.

## Features

- **Millisecond-precision timestamps** in log output.
- **Timezone-aware formatting** (local or UTC with 'Z' suffix).
- **YAML-based logging configuration** for easy customization.
- **Rotating file handler** and console logging out-of-the-box.
- **OpenTelemetry trace context** support in log messages.
- **Automatic log directory creation** for file handlers.

## Usage

1. **Import and set up logging:**

```python
from default_logging import setup_logging

setup_logging()
```

2. **(Optional) Use your own config:**

```python
setup_logging(config_path="path/to/your_logging_config.yaml")
```

## Example

```python
from default_logging import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)
logger.info("Hello, world!")
```

## Logging Configuration

The default configuration is defined in [`default_logging/logging_config.yaml`](https://github.com/kquiet/python_default_logging/blob/main/default_logging/logging_config.yaml):

- **Formatters:**  
  - `simple`: UTC timestamps, millisecond precision.
  - `simple_with_trace_context`: Adds OpenTelemetry trace info to each log line.
- **Handlers:**  
  - `console_stdout`: Logs to stdout.
  - `rotating_file_handler`: Logs to `logs/app.log` with rotation.
- **Root logger:**  
  - Level: `DEBUG`
  - Handlers: both console and file.

You can customize the YAML config or provide your own.

## MillisecondFormatter

Custom formatters in [`default_logging/millisecond_formatter.py`](https://github.com/kquiet/python_default_logging/blob/main/default_logging/millisecond_formatter.py) provide:

- `%f` for milliseconds
- `%z` for timezone offset (`+HH:MM`, `-HH:MM`, or `Z` for UTC)

## OpenTelemetry Integration

The package is compatible with OpenTelemetry. Check example usage [here](https://github.com/kquiet/python_default_logging/blob/main/app.py), and then execute `opentelemetry-instrument python app.py` to see logs that contain trace and span IDs.


## License

[MIT License](https://github.com/kquiet/python_default_logging/blob/main/LICENSE)