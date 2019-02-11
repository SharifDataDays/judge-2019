import sys
import csv


def extract_category():
    read_file = open(sys.argv[1])
    csv_read = csv.reader(read_file)

    write_path=sys.argv[2]
    write_file = open(write_path, mode='w')
    write_csv = csv.writer(write_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    next(csv_read)

    # written by mrtaalebi in most newbie style :)
    for row in csv_read:
        cats = row[3:6]
        new_cats = []
        for cat in cats:
            if cat == "":
                new_cats.append("NONE")
            else:
                new_cats.append(cat)
        write_csv.writerow(new_cats)
    

if __name__ == "__main__":
    extract_category()
