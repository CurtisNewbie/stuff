import pytz
import datetime
import sys

dformat = "%Y-%m-%d"
tformat = "%Y-%m-%d %H:%M:%S"
utc = "UTC"
timezones = ['Asia/Shanghai', utc, 'Europe/London', 'Asia/Singapore']


def printnow():
    t = datetime.datetime.now(pytz.timezone(utc))
    t = t.replace(tzinfo=pytz.utc)

    for tz in timezones:
        localDatetime = t.astimezone(pytz.timezone(tz))
        print(f"{tz:<15} {localDatetime.strftime(tformat)}")


def printspecified(s: str):
    scn = s.count(":")
    while scn < 2:
        s += ":00"
        scn = scn + 1

    print()
    _printtz(s, utc)
    print()


def _printtz(s: str, tz: str):
    fmt = datetime.datetime.now().strftime(dformat) + " " + s
    t = pytz.timezone(tz).localize(datetime.datetime.strptime(fmt, tformat))
    print(f'From {tz:<15} {t}\n')
    for tzz in timezones:
        if tzz == tz:
            continue

        print(
            f" ->  {tzz:<15} {t.astimezone(pytz.timezone(tzz))}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        printspecified(sys.argv[1])
    else:
        printnow()
