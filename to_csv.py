from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import csv
import icalendar
import pytz
import re
import sys


@dataclass(order=True, frozen=True)
class TimetableEvent:
    course: str
    group: str
    teacher: str
    room: str
    time_start: datetime
    time_end: datetime


def convert_event(event: icalendar.cal.Component) -> TimetableEvent:
    summary = event.get("SUMMARY")
    dtstart = event.get("DTSTART")
    dtend = event.get("DTEND")
    description = event.get("DESCRIPTION")
    location = event.get("LOCATION")

    assert isinstance(summary, str)
    assert isinstance(description, str)
    assert isinstance(dtstart, icalendar.prop.vDDDTypes)
    assert isinstance(dtend, icalendar.prop.vDDDTypes)
    assert isinstance(location, icalendar.prop.vText)

    [group, course] = summary.split(sep="-", maxsplit=1)

    teacher_pattern = r"Teacher:\s*(.*)\s*Room"
    teacher_match = re.search(teacher_pattern, description, flags=re.MULTILINE)

    teacher_name = ""
    if teacher_match:
        teacher_name = teacher_match.group(1)

    time_start = dtstart.dt.astimezone(pytz.timezone("Europe/Berlin"))
    time_end = dtend.dt.astimezone(pytz.timezone("Europe/Berlin"))

    return TimetableEvent(
        course, group, teacher_name, str(location), time_start, time_end
    )


def read_ical(filename: Path) -> list:
    with filename.open(encoding="UTF-8") as file:
        cal = icalendar.Calendar.from_ical(file.read())
        return [convert_event(event) for event in cal.walk("VEVENT")]


def write_to_csv(filename: Path, events: list):
    with filename.open(mode="w", newline="", encoding="UTF-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        for event in events:
            writer.writerow(
                [
                    event.course,
                    event.group,
                    event.teacher,
                    event.room,
                    event.time_start,
                    event.time_end,
                ]
            )


def main():
    events = set()
    for file in sys.argv[1:]:
        for event in read_ical(Path(file)):
            events.add(event)

    event_list = list(events)
    event_list.sort()
    write_to_csv(Path("output.csv"), event_list)


if __name__ == "__main__":
    main()
