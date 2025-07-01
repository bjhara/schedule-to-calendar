from datetime import datetime
from icalendar import Calendar, Event, vText  # type: ignore

import pytz


def timetable_to_ical(timetables: list) -> Calendar:
    cal = Calendar()

    for timetable in timetables:
        time_start = pytz.utc.normalize(timetable.time_start)
        time_end = pytz.utc.normalize(timetable.time_end)

        timestamp_start = time_start.timestamp()

        event = Event()
        event.add("uid", str(int(timestamp_start)) + "-" + timetable.id + "@stc")
        event.add("summary", timetable.name)
        event.add(
            "description",
            f"Class: {timetable.group}\nTeacher: {timetable.teacher}\nRoom: {timetable.room}",
        )

        event.add("dtstart", time_start)
        event.add("dtend", time_end)
        event.add("dtstamp", datetime.today())
        event.add("location", vText(timetable.room))

        cal.add_component(event)

    return cal
