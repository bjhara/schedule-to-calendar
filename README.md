# Schedule to calendar

Get data from Skola24 and make it into a ical calendar file that can be imported into calendar software such as Outlook and Google Calendar.

## Usage

schedule-to-calendar [-h] [-u UNIT] [-o HOST]
                            [-f FILENAME] [-s START] [-e END]
                            [-y YEAR] [-t TEACHER] [-g GROUP]

```
  -h, --help                        show this help message and exit
  -u UNIT, --unit UNIT              unit name
  -o HOST, --host HOST              unit host
  -f FILENAME, --filename FILENAME  filename for calendar output
  -s START, --start START           start week number
  -e END, --end END                 end week number
  -y YEAR, --year YEAR              end week number
  -t TEACHER, --teacher TEACHER     teacher id
  -g GROUP, --group GROUP           class id
```

The unit and host will default to values for Yrgo Lärdomsgatan. The filename will default to `calendar.ics`. The date related values
will default to the current week.

You will have to supply an id for either a teacher or a class. This
is the id, and not the full name.

### Example usage

```
# generate calendar for weeks 1-23 for Nils Nilsson this year
schedule-to-calendar -s 1 -e 23 -t "Nils N"
```

```
# generate this week to java22.ics for class Java22
schedule-to-calendar -f java22.ics -g "Java22"
```
