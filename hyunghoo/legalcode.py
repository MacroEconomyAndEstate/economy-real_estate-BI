import csv


input_file_path = '법정동코드_전체자료.txt'


output_csv_path = '법정동코드.csv'


extracted_data = set()
with open(input_file_path, 'r', encoding='cp949') as file:
    next(file) 
    for line in file:
        code, name, status = line.strip().split('\t')
        if status == '존재':
            short_code = code[:5]
            words = name.split()
            short_name = ' '.join(words[:2]) if len(words) >= 2 else name
            extracted_data.add((short_code, short_name))


sorted_data = sorted(extracted_data)


with open(output_csv_path, 'w', newline='', encoding='cp949') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['법정동코드', '지역구'])
    for code, name in sorted_data:
        csvwriter.writerow([code, name])
