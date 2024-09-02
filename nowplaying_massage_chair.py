import json
import rstv_config

def text_to_json(input_file, output_file):
    # Read the lines from the text file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Ensure there are exactly two lines in the file
    if len(lines) != 2:
        raise ValueError("Input file must contain exactly two lines.")

    # Split the second line on the '/' character
    time_parts = lines[1].strip().split('/')
    if len(time_parts) != 2:
        raise ValueError("The second line must contain exactly one '/' character separating 'remaining' and 'duration'.")

    # Create a dictionary with the desired keys and values
    data = {
        'nowplaying': lines[0].strip(),
        'remaining': time_parts[0].strip(),
        'duration': time_parts[1].strip()
    }

    # Write the dictionary to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Get the input and output file paths from the configuration
input_file = '{}rstv1-nowplaying.txt'.format(rstv_config.nowplaying_status_path)
output_file = '{}rstv1-nowplaying.json'.format(rstv_config.nowplaying_status_path)

# Convert the text file to a JSON file
text_to_json(input_file, output_file)
