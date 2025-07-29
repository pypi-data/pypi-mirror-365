# Question Timer Application

A simple command-line application that helps you track the time spent on each question, with audible time announcements and logging.

## Features

- Starts and stops the timer using the spacebar key.
- Announces elapsed time using text-to-speech.
- Automatically logs the elapsed time to a CSV file (`Question-Log.csv`).
- Allows you to mark each question as correct, incorrect, or not applicable (yes/no/n/a).

## Prerequisites

- Python 3.10, 3.11, or 3.12 (Python 3.13 is **not supported** due to dependencies).
- macOS, Linux, or Windows.

## Installation

You can install the package via [PyPI](https://pypi.org/):

```bash
pip install stress-timer
```

Or, if installing from source:

```bash
git clone https://github.com/yourusername/stress-timer-oce4nm4n.git
cd stress-timer-oce4nm4n
pip install .
```

If you use Poetry:

```bash
poetry install
```

## Running the Application

To start the timer application, run:

```bash
stress-timer
```

Or, if running from source:

```bash
python -m stress_timer_oce4nm4n.main
```

## Controls

- **Spacebar**: Start or stop the timer. Press again when you finish a question.
- **q**: Quit the application.

## Logging

The elapsed time for each question is automatically logged to `Question-Log.csv` in the same directory as the script. You can open this file in any CSV editor or spreadsheet software.

### Example Log File Format

| Question | Time (seconds) | Correct |
|----------|----------------|---------|
| 1        | 30             | yes     |
| 2        | 45             | no      |

## Troubleshooting

- **Python version errors:**
  If you encounter errors about missing or incompatible dependencies, ensure you are using Python 3.10, 3.11, or 3.12.
- **Audio issues:**
  Make sure your system audio is working and you have the necessary permissions.

## License

MIT License

