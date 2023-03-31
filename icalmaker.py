from datetime import datetime
from icalendar import Calendar, Event, vText  # type: ignore


def timetable_to_ical(timetables: list) -> Calendar:
    cal = Calendar()

    for timetable in timetables:
        event = Event()
        event.add("uid", timetable.id + "@scheduletocalendar")
        event.add("summary", timetable.name)
        event.add(
            "description",
            f"Class: {timetable.group}\nTeacher: {timetable.teacher}\nRoom: {timetable.room}",
        )
        event.add("dtstart", timetable.time_start)
        event.add("dtend", timetable.time_end)
        event.add("dtstamp", datetime.today())
        event.add("location", vText(timetable.room))

        cal.add_component(event)

    return cal
