field = 'partition_year'
typ = 'year_month_int'

# starting from 2023, May
year = 2023
month = 5
total_years = 4  # four years of partition in total

if typ == 'year':
    pi = 0
    print(f"PARTITION BY RANGE({field}) (")
    for i in range(10):
        print(f"PARTITION p{pi} VALUES LESS THAN ({year+i}),")
        pi += 1
    print(f"    PARTITION p{pi} VALUES LESS THAN MAXVALUE\n);")

if typ == 'year_month_int':
    pi = 0
    print(f"PARTITION BY RANGE({field}) (")
    for i in range(total_years):
        while True:
            jstr = "0" + str(month+1) if month < 9 else str(month+1)
            score = int(f"{year+i}{jstr}")
            print(f"    PARTITION p{pi} VALUES LESS THAN ({score}),")
            pi += 1
            month += 1
            if month > 11:
                month = 0
                break
    print(f"    PARTITION p{pi} VALUES LESS THAN MAXVALUE\n);")

if typ == 'year_month_timestamp':
    pi = 0
    print(f"PARTITION BY RANGE(UNIX_TIMESTAMP({field})) (")
    for i in range(total_years):
        while True:
            jstr = "0" + str(month+1) if month < 9 else str(month+1)
            score = int(f"{year+i}{jstr}")
            print(
                f"    PARTITION p{pi} VALUES LESS THAN (unix_timestamp('{year+i}-{jstr}-01 00:00:00')),")
            pi += 1
            month += 1
            if month > 11:
                month = 0
                break
    print(f"    PARTITION p{pi} VALUES LESS THAN MAXVALUE\n);")
