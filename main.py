from datetime import datetime

import argparse
import icalmaker
import schedule


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
                    prog='scheduletocalendar',
                    description='Make a schedule from Skola24 into a ical file')

    (year, week, _) = datetime.today().isocalendar()

    parser.add_argument('-u', '--unit', default="Yrgo Lärdomsgatan", help="unit name")
    # want to call it -h but that is a problem...
    parser.add_argument('-o', '--host', default="studiumyrgo.skola24.se", help="unit host")
    parser.add_argument('-f', '--filename', default="calendar.ics", help="filename for calendar output")
    parser.add_argument('-s', '--start', default=week, type=int, help="start week number") 
    parser.add_argument('-e', '--end', default=week, type=int, help="end week number") 
    parser.add_argument('-y', '--year', default=year, type=int, help="end week number")
    parser.add_argument('-t', '--teacher', help="teacher id")
    # want to call it class but that is a problem...
    parser.add_argument('-g', '--group', help="class id")

    return parser

def valid_arguments(args: argparse.Namespace) -> bool:
    if args.start < 1 or args.start > 53:
        return False
    
    if args.end < 1 or args.end > 53 or args.end < args.start:
        return False
    
    (year, _, _) = datetime.today().isocalendar()
    if args.year < year or args.year > year + 1:
        return False
    
    return True

def main():
    arg_parser = create_argument_parser()
    args = arg_parser.parse_args()

    if args.group == None and args.teacher == None:
        print("error: You must supply either a teacher id or a class id.\n")
        arg_parser.print_usage()
        exit(-1)

    if args.group != None and args.teacher != None:
        print("error: You can't supply both a teacher id and a class id.\n")
        arg_parser.print_usage()
        exit(-1)

    if not valid_arguments(args):
        print("error: Invalid arguments.\n")
        arg_parser.print_usage()
        exit(-1)

    if args.group != None:
        timetable = schedule.get_timetable_for_group(args.unit, args.host, args.group, args.year, args.start, args.end)

        with open(args.filename, "wb") as file:
            file.write(icalmaker.timetable_to_ical(timetable).to_ical())
    
    elif args.teacher != None:
        timetable = schedule.get_timetable_for_teacher(args.unit, args.host, args.teacher, args.year, args.start, args.end)

        with open(args.filename, "wb") as file:
            file.write(icalmaker.timetable_to_ical(timetable).to_ical())

if __name__ == "__main__":
    main()
