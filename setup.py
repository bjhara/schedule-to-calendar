from cx_Freeze import setup, Executable

executables = [Executable("main.py", target_name="schedule-to-calendar")]

# packages = ["requests", "pytz", "icalendar"]
# options = {
#     'build_exe': {
#         'packages': packages,
#     },
# }

setup(
    name="schedule-to-calendar",
    # options = options,
    version="1.0.0",
    description="skol24 schedule to ical",
    executables=executables,
)
