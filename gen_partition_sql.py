year_month = True
year = 2023
month = 5

if not year_month:
    pi = 0
    print("PARTITION BY RANGE(partition_year) (")
    for i in range(10):
        print(f"PARTITION p{pi} VALUES LESS THAN ({year+i}),")
        pi += 1
    print(f"    PARTITION p{pi} VALUES LESS THAN MAXVALUE\n);")

if year_month:
    pi = 0
    print("PARTITION BY RANGE(partition_year_month) (")
    for i in range(4):
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