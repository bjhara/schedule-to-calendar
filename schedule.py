from dataclasses import dataclass
from datetime import datetime, time
from time import sleep
from typing import Callable

import json
import pytz
import requests


@dataclass
class TimetableEvent:
    id: str
    name: str
    group: str
    teacher: str
    room: str
    time_start: datetime
    time_end: datetime


@dataclass
class SchoolYear:
    guid: str
    time_start: datetime
    time_end: datetime


def get_timetable_for_teacher(
    unit_name: str,
    unit_host: str,
    teacher_id: str,
    year: int,
    start_week: int,
    end_week: int,
) -> list:
    return _get_timetable_for(
        _get_teacher_by_id,
        _get_timetable_for_teacher,
        _convert_to_event_for_teacher,
        unit_name,
        unit_host,
        teacher_id,
        year,
        start_week,
        end_week,
    )


def get_timetable_for_group(
    unit_name: str,
    unit_host: str,
    group_id: str,
    year: int,
    start_week: int,
    end_week: int,
) -> list:
    return _get_timetable_for(
        _get_class_by_id,
        _get_timetable_for_class,
        _convert_to_event_for_class,
        unit_name,
        unit_host,
        group_id,
        year,
        start_week,
        end_week,
    )


def _get_timetable_for(
    get_guid: Callable[[requests.Session, dict, str], dict],
    get_timetable: Callable[
        [requests.Session, dict, dict, str, list[SchoolYear], int, int], list
    ],
    convert_timetable: Callable[[list, str, int, int], list],
    unit_name: str,
    unit_host: str,
    id: str,
    year: int,
    start_week: int,
    end_week: int,
) -> list:
    session = requests.Session()
    session.headers.update(
        {
            "X-Scope": "8a22163c-8662-4535-9050-bc5e1923df48",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
        }
    )

    school_years = _get_school_years(session, unit_host)
    unit = _get_unit_by_name(session, unit_name, unit_host)
    guid = get_guid(session, unit, id)

    all_weeks = []
    for week in range(start_week, end_week + 1):
        # don't blast the server with requests
        sleep(0.5)

        # the web interface seems to get a new render key every time
        render_key = _get_render_key(session)

        timetable = get_timetable(
            session, unit, guid, render_key, school_years, year, week
        )
        if timetable != None:
            all_weeks.extend(convert_timetable(timetable, id, year, week))

    return all_weeks


def _get_school_years(session: requests.Session, host: str) -> list[SchoolYear]:
    school_year_request_data = json.dumps(
        {"hostName": host, "checkSchoolYearsFeatures": False}
    )

    resp = session.post(
        "https://web.skola24.se/api/get/active/school/years",
        data=school_year_request_data,
    )

    if resp.status_code != 200:
        raise RuntimeError("could not get school year data")

    school_year_response = resp.json()
    active_school_years: list = school_year_response["data"]["activeSchoolYears"]
    return [
        SchoolYear(
            year["guid"], _str_to_datetime(year["from"]), _str_to_datetime(year["to"])
        )
        for year in active_school_years
    ]


def _get_unit_by_name(session: requests.Session, name: str, host: str) -> dict:
    units_request_data = json.dumps(
        {"getTimetableViewerUnitsRequest": {"hostName": host}}
    )

    resp = session.post(
        "https://web.skola24.se/api/services/skola24/get/timetable/viewer/units",
        data=units_request_data,
    )

    if resp.status_code != 200:
        raise RuntimeError("could not get data")

    units_response_data = resp.json()
    data = units_response_data["data"]
    time_table_viewer_units_response = data["getTimetableViewerUnitsResponse"]
    host_name = time_table_viewer_units_response["hostName"]
    units = time_table_viewer_units_response["units"]

    for unit in units:
        if "unitId" in unit and unit["unitId"] == name:
            unit["hostName"] = host_name
            return unit

    raise RuntimeError("could not find unit by name")


def _get_teacher_by_id(session: requests.Session, unit: dict, id: str) -> dict:
    selection_request_data = {
        "hostName": unit["hostName"],
        "unitGuid": unit["unitGuid"],
        "filters": {
            "class": False,
            "course": False,
            "group": False,
            "period": False,
            "room": False,
            "student": False,
            "subject": False,
            "teacher": True,
        },
    }

    resp = session.post(
        "https://web.skola24.se/api/get/timetable/selection",
        data=json.dumps(selection_request_data),
    )

    if resp.status_code != 200:
        raise RuntimeError("could not get data")

    selection_response_data = resp.json()
    data = selection_response_data["data"]
    teachers = data["teachers"]

    for teacher in teachers:
        if "id" in teacher and teacher["id"] == id:
            return teacher

    raise RuntimeError("could not find teacher by id")


def _get_class_by_id(session: requests.Session, unit: dict, id: str) -> dict:
    selection_request_data = {
        "hostName": unit["hostName"],
        "unitGuid": unit["unitGuid"],
        "filters": {
            "class": True,
            "course": False,
            "group": False,
            "period": False,
            "room": False,
            "student": False,
            "subject": False,
            "teacher": False,
        },
    }

    resp = session.post(
        "https://web.skola24.se/api/get/timetable/selection",
        data=json.dumps(selection_request_data),
    )

    if resp.status_code != 200:
        raise RuntimeError("could not get data")

    selection_response_data = resp.json()
    data = selection_response_data["data"]
    groups = data["classes"]

    for group in groups:
        if "groupName" in group and group["groupName"] == id:
            return group

    raise RuntimeError("could not find group by id")


def _get_render_key(session: requests.Session) -> str:
    resp = session.post(
        "https://web.skola24.se/api/get/timetable/render/key", data="null"
    )

    if resp.status_code != 200:
        raise RuntimeError("could not get data")

    render_key_data = resp.json()
    data = render_key_data["data"]

    return data["key"]


def _get_timetable_for_teacher(
    session: requests.Session,
    unit: dict,
    teacher: dict,
    render_key: str,
    school_years: list[SchoolYear],
    year: int,
    week: int,
) -> list:
    return _get_timetable(
        session, unit, teacher["personGuid"], 7, render_key, school_years, year, week
    )


def _get_timetable_for_class(
    session: requests.Session,
    unit: dict,
    klass: dict,
    render_key: str,
    school_years: list[SchoolYear],
    year: int,
    week: int,
) -> list:
    return _get_timetable(
        session, unit, klass["groupGuid"], 0, render_key, school_years, year, week
    )


def _get_timetable(
    session: requests.Session,
    unit: dict,
    guid: str,
    selectionType: int,
    render_key: str,
    school_years: list[SchoolYear],
    year: int,
    week: int,
) -> list:
    school_year = _get_school_year_guid(school_years, year, week)

    timetable_request_data = {
        "renderKey": render_key,
        "host": unit["hostName"],
        "unitGuid": unit["unitGuid"],
        "width": 1050,  # not relevant, set to typical size
        "height": 1223,  # not relevant, set to typical size
        "selectionType": selectionType,
        "selection": guid,
        "scheduleDay": 0,
        "week": week,
        "year": year,
        "schoolYear": school_year,
    }

    # print(timetable_request_data)

    resp = session.post(
        "https://web.skola24.se/api/render/timetable",
        data=json.dumps(timetable_request_data),
    )

    if resp.status_code != 200:
        raise RuntimeError("could not get data")

    timetable_response_data = resp.json()

    # print(timetable_response_data)

    data = timetable_response_data["data"]

    # print(data)

    return data["lessonInfo"]


def _convert_to_event_for_class(
    timetable: list, class_name: str, year: int, week: int
) -> list:
    classes = []
    for klass in timetable:
        texts = klass["texts"]
        (name, teacher, room) = _get_texts(texts)

        id = klass["guidId"]

        day = int(klass["dayOfWeekNumber"])

        time_start = _to_datetime(year, week, day, klass["timeStart"])
        time_end = _to_datetime(year, week, day, klass["timeEnd"])

        classes.append(
            TimetableEvent(id, name, class_name, teacher, room, time_start, time_end)
        )

    return classes


def _convert_to_event_for_teacher(
    timetable: list, teacher: str, year: int, week: int
) -> list:
    classes = []
    for klass in timetable:
        texts = klass["texts"]
        (name, group, room) = _get_texts(texts)

        id = klass["guidId"]

        day = int(klass["dayOfWeekNumber"])

        time_start = _to_datetime(year, week, day, klass["timeStart"])
        time_end = _to_datetime(year, week, day, klass["timeEnd"])

        classes.append(
            TimetableEvent(id, name, group, teacher, room, time_start, time_end)
        )

    return classes


def _to_datetime(year: int, week: int, day: int, time_of_day: str) -> datetime:
    class_date = datetime.fromisocalendar(year, week, day)
    time_notz = time.fromisoformat(time_of_day)
    class_time = time(time_notz.hour, time_notz.minute, time_notz.second)
    dt = datetime.combine(class_date, class_time)
    tz = pytz.timezone("Europe/Stockholm")
    return tz.localize(dt)


def _str_to_datetime(date_string: str) -> datetime:
    date_format = "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(date_string, date_format)


def _get_school_year_guid(school_years: list[SchoolYear], year: int, week: int) -> str:
    date_string = f"{year}-{week}-1"
    dt = datetime.strptime(date_string, "%Y-%W-%w")
    return next(
        sy.guid for sy in school_years if sy.time_start <= dt and sy.time_end >= dt
    )


def _get_texts(texts):
    if texts == None:
        return ("", "", "")

    count = len(texts)
    if count == 0:
        return ("", "", "")
    elif count == 1:
        return (texts[0], "", "")
    elif count == 2:
        return (texts[0], texts[1], "")
    else:
        return (texts[0], texts[1], texts[2])
