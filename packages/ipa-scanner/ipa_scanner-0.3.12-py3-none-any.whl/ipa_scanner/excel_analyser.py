import os
import csv
import pandas as pd

# Path to the Downloads folder
# downloads_folder = os.path.expanduser("/Users/I527370/Library/CloudStorage/OneDrive-SAPSE/Desktop/codes/PP/ui5upgrade/procplan-projects/IPA/ipa-scanner/downloads")
# csv_file_path = os.path.join(downloads_folder, "download.csv")  # Replace 'your_file_name.csv' with the actual file name
# log_file_path = os.path.join(downloads_folder, "spike_log.txt")
def is_spike(prev, curr):
    if pd.isna(prev) or pd.isna(curr) or prev == 0:
        return False

    ratio = curr / prev
    diff = abs(curr - prev)

    # Ultra-small values (under 1): very sensitive to small changes
    if prev <= 1:
        return diff >= 0.2 or ratio >= 2

    # Small values (1–5): treat 1+ unit change as a spike
    elif prev <= 5:
        return diff >= 1 or ratio >= 1.5

    # Medium values (5–20): more relaxed
    elif prev <= 20:
        return diff >= 3 or ratio >= 1.4

    # Large values (20–100): need noticeable jump
    elif prev <= 100:
        return diff >= 10 or ratio >= 1.3

    # Very large (100–1000): even larger jump needed
    elif prev <= 1000:
        return diff >= 100 or ratio >= 1.25

    # Extremely large (>1000): only react to very big jumps
    else:
        return diff >= 500 or ratio >= 1.2

def analyze_csv(download_dir):
    downloads_folder = download_dir
    csv_file_path = downloads_folder+'/download.csv' 
    log_file_path = downloads_folder + '/spike_log.txt'
     # Replace 'your_file_name.csv' with the actual file name
    # Open and read the CSV file
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            # for row in csv_reader:
            #     print(row)
    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

        # Create a dictionary to group rows by the 'Scenario' column
    grouped_data = {}

    files_list = []

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Read the header row
            scenario_index = header.index("Scenario")  # Find the index of the 'Scenario' column
            print(scenario_index)

            for row in csv_reader:
                scenario = row[scenario_index]
                if scenario not in grouped_data:
                    grouped_data[scenario] = []
                grouped_data[scenario].append(row)

        # Create separate CSV files for each group
        for scenario, rows in grouped_data.items():
            scenario_file_path = os.path.join(downloads_folder, f"{scenario}.csv")
            with open(scenario_file_path, mode='w', encoding='utf-8', newline='') as scenario_file:
                csv_writer = csv.writer(scenario_file)
                csv_writer.writerow(header)  # Write the header row
                csv_writer.writerows(rows)  # Write the grouped rows
                files_list.append(scenario)

            print(f"File created: {scenario_file_path}")

    except FileNotFoundError:
        print(f"File not found: {csv_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


        # Analyze spikes in the 'Step' column
    import pandas as pd
    if os.path.exists(log_file_path):
            os.remove(log_file_path)
    for scenario in files_list:
        
        try:
            # Load the CSV file into a DataFrame
            print("ffffile", downloads_folder +scenario+ '+.csv')
            df = pd.read_csv(downloads_folder+'/' +scenario+ '.csv')

            # Ensure the 'Date' column is in datetime format
            df['Date'] = pd.to_datetime(df['Date'])

            last_four_dates = sorted(df['Date'].dt.normalize().dropna().unique())[-2:]
            df = df[df['Date'].dt.normalize().isin(last_four_dates)]


            # Convert all columns (except 'Step' and 'Date') to numeric (coerce errors to NaN)
            for col in df.columns:
                if col not in ['Step', 'Date']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Sort the DataFrame by 'Step' and 'Date'
            df.sort_values(by=['Step', 'Date'], inplace=True)
            count_row = 0
            # Iterate through each unique 'Step'
            for step in df['Step'].unique():
                step_data = df[df['Step'] == step]
                count_col = 0


                # Iterate through each column (excluding 'Step' and 'Date') to check for spikes
                for column in df.columns:
                    count_col += 1
                    if column not in ['Step', 'Date', 'ID', 'Scenario','HANA HANA Par Mem [MB]', 'HANA HANA CPU Time [s]','Dynatrace APM DB Child Calls [total]','Dynatrace APM CPU Time [s]','Client CPU Time [s]','Dynatrace APM Non DB Child Calls [total]','Total Http Messages Size [KB]']:
                        previous_value = None
                        for index, row in step_data.iterrows():
                            # print(column, row['Date'], row[column])
                            count_row+=1
                            
                            current_value = row[column]
                            if pd.notna(current_value) and pd.notna(previous_value):
                                if is_spike(previous_value, current_value):  # 50% increase
                                    log_message = f"Scenario Name: '{scenario}', Spike detected in Step '{step}', Column '{column}' on Date {row['Date'].date()}: {current_value} (previous: {previous_value})"
                                    print(log_message)
                                    
                                    # Write the log message to a text file
                                    
                                    with open(log_file_path, mode='a', encoding='utf-8') as log_file:
                                        log_file.write(log_message + '\n')
                                    
                            previous_value = current_value
            print(f"Total columns checked: {count_col}, Total rows checked: {count_row}")
        except FileNotFoundError:
            print(f"File not found: {downloads_folder}/Manage Procurement Projects.csv")
        except Exception as e:
            print(f"An error occurred: {e}")
