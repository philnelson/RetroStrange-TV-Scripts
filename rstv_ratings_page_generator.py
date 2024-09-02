import json
import csv
import os
import rstv_config

def json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as f:
        print(f)
        data = json.load(f)

    with open(csv_file, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(data[0].keys())
        for item in data:
            csv_writer.writerow(item.values())

def merge_csvs(input_folder, output_file):
    csv_files = [file for file in os.listdir(input_folder) if file.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the input folder.")
        return

    with open(output_file, 'w', newline='') as f_out:
        csv_writer = csv.writer(f_out)
        first_file = True
        for csv_file in csv_files:
            with open(os.path.join(input_folder, csv_file), 'r') as f_in:
                csv_reader = csv.reader(f_in)
                if first_file:
                    for row in csv_reader:
                        csv_writer.writerow(row)
                    first_file = False
                else:
                    next(csv_reader)  # Skip the header row in subsequent files
                    for row in csv_reader:
                        csv_writer.writerow(row)

if __name__ == "__main__":
    input_folder = rstv_config.ratings_path
    output_file = "ratings_merged.csv"
    print(input_folder)

    # Convert JSON files to CSVs
    for file in os.listdir(input_folder):
        if file.endswith('.txt'):
            json_file_path = os.path.join(input_folder, file)
            csv_file_path = os.path.splitext(json_file_path)[0] + '.csv'
            json_to_csv(json_file_path, csv_file_path)

    # Merge the CSV files
    merge_csvs(input_folder, output_file)

    print("JSON to CSV conversion and merging completed.")
