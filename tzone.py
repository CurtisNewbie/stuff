import pytz
import datetime
import sys

D_FORMAT = "%Y-%m-%d"
T_FORMAT = "%Y-%m-%d %H:%M:%S"
UTC = "UTC"
timezones = [UTC, 'Asia/Shanghai', 'Europe/London', 'Asia/Singapore']


def printnow():
    utct = datetime.datetime.utcnow()

    for tz in timezones:
        print(f"{tz:<15} {utct.astimezone(pytz.timezone(tz))}")


def printspecified(s: str):
    scn = s.count(":")
    while scn < 2:
        s += ":00"
        scn = scn + 1

    print()
    _printtz(s, UTC)
    print()


def _printtz(s: str, tz: str):
    fmt = datetime.datetime.now().strftime(D_FORMAT) + " " + s
    t = pytz.timezone(tz).localize(datetime.datetime.strptime(fmt, T_FORMAT))
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
