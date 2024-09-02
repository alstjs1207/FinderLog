import csv
from db import localdb


def export():
    file = open("keywords.csv", mode="w")
    writer = csv.writer(file)
    writer.writerow(["timestamp", "keyword"])
    db = localdb.get('keyword')
    for data in db:
        writer.writerow([data['timestamp'], data['decoded_keyword']])