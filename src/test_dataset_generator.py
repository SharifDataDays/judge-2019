import csv
import random

'''
	@param Amount of data in the sample
	@param how many of these mini test sets do we want?
	@param do the test sets need to be distinct?
'''
def small_test_generation(size_of_test_samples=10, number_of_samples=10, distinct=True):
	test_data_file_name = '../../final_dataset.csv'
	read_file = open(test_data_file_name)
	csv_read = csv.reader(read_file)
	row_count = sum(1 for row in csv_read)
	# if distinct and size_of_test_samples * number_of_samples > row_count:
	# 	print("Too little data for non intersecting samples")
	# 	return None
	
	rands = [[] for _ in range(number_of_samples)]
	
	for i in range(number_of_samples):
		for _ in range(size_of_test_samples):
			r = random.randint(0, row_count-1)
			if r not in rands[i]:
				rands[i].append(r)

	# read_file.seek(0)
	# for i, row in enumerate(csv_read):
	# 	print(row)

	for i in range(number_of_samples):
		write_file = open('result/test' + str(i) + ".csv", mode='w')
		write_csv = employee_writer = csv.writer(write_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		read_file.seek(0)
		randomly_selected_rows = [row for idx, row in enumerate(csv_read) if idx in rands[i]]
		for row in randomly_selected_rows:
			# print(row)
			write_csv.writerow(row)
		



if __name__ == '__main__':
	small_test_generation()