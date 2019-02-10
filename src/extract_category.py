import sys
import csv


def extract_category():
    read_file = open(sys.argv[1])
    csv_read = csv.reader(read_file)

    write_path=sys.argv[2]
    write_file = open(write_path, mode='w')
    write_csv = csv.writer(write_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    next(csv_read)

    for row in csv_read:
        write_csv.writerow(row[3:6])
    

if __name__ == "__main__":
    extract_category()
