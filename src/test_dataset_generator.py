import csv
import random
import sys
import os
import string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def remove_brand(arr):
    return arr[:2] + arr[3:], arr[2]

'''
    @param Amount of data in the sample
    @param how many of these mini test sets do we want?
    @param do the test sets need to be distinct?
'''
def small_test_generation(size_of_test_samples=1000, number_of_samples=1000, distinct=True):
    test_data_file_name = sys.argv[1]
    read_file = open(test_data_file_name)
    csv_read = csv.reader(read_file)
    row_count = sum(1 for row in csv_read)
    # if distinct and size_of_test_samples * number_of_samples > row_count:
    # 	print("Too little data for non intersecting samples")
    # 	return None

    rands = [[0] for _ in range(number_of_samples)]

    for i in range(number_of_samples):
        for _ in range(size_of_test_samples):
            while True:
                r = random.randint(0, row_count-1)
                if r not in rands[i]:
                    break
            rands[i].append(r)

    # read_file.seek(0)
    # for i, row in enumerate(csv_read):
    # 	print(row)

    for i in range(number_of_samples):
        name = id_generator(20) + ".csv"
        write_file = open(os.path.join(sys.argv[2], name), mode='w')
        write_csv = employee_writer = csv.writer(write_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        read_file.seek(0)
        randomly_selected_rows = [row for idx, row in enumerate(csv_read) if idx in rands[i]]
        answers = []
        for row in randomly_selected_rows:
            q, ans = remove_brand(row)
            write_csv.writerow(q)
            answers += [ans]
        with open(os.path.join(sys.argv[3], name + '_answer'), mode='w') as file:
            file.write("\n".join(answers[1:]))
        write_file.close()

if __name__ == '__main__':
    small_test_generation()
