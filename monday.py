from datetime import *

if __name__ == '__main__':
    today: date = date.today()
    dt: datetime = datetime(today.year, today.month, today.day)
    fmon = dt + timedelta(-dt.weekday())
    print(fmon.strftime('%Y%m%d'))
