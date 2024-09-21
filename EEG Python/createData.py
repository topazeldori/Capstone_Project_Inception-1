import pandas as pd
import os


def calculate_and_save_connectivity_matrix(eeg_segment, segment_file_path):
    correlation_matrix = eeg_segment.corr()
    output_matrix_path = segment_file_path.replace('.csv', '_connectivity.csv')
    correlation_matrix.to_csv(output_matrix_path, index=False)

def segment_eeg_to_8_seconds(csv_file_path, output_folder, sampling_rate=128):
    eeg_data = pd.read_csv(csv_file_path)
    num_points = 8 * sampling_rate
    total_segments = len(eeg_data) // num_points

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for segment in range(total_segments):
        start_index = segment * num_points
        end_index = start_index + num_points
        eeg_segment = eeg_data.iloc[start_index:end_index]
        segment_file_path = os.path.join(output_folder, f'segment_{segment+1}_{os.path.basename(csv_file_path)}')
        eeg_segment.to_csv(segment_file_path, index=False)
        calculate_and_save_connectivity_matrix(eeg_segment, segment_file_path)

def find_patient_file(input_directory, patient_prefix):
    # Search for the first file that starts with the specified patient prefix
    for filename in os.listdir(input_directory):
        if filename.startswith(patient_prefix) and filename.endswith('.csv'):
            return filename
    return None  # Return None if no file is found

def process_patient_files(input_directory, patient_csv_filename, output_directory, selected_analysis_type):
    csv_file_path = os.path.join(input_directory, patient_csv_filename)
    if os.path.isfile(csv_file_path):
        if selected_analysis_type == 'ADHD':
            patient_output_folder = os.path.join(output_directory, f'ADHD_{patient_csv_filename[:-4]}')
        elif selected_analysis_type == 'NonADHD':
            patient_output_folder = os.path.join(output_directory, f'NonADHD_{patient_csv_filename[:-4]}')
        else:
            print(f"Error: Unexpected analysis type '{selected_analysis_type}'.")
            return

        if os.path.exists(patient_output_folder):
            print(f"Folder already exists for {patient_csv_filename[:-4]}. Skipping creation.")
        else:
            segment_eeg_to_8_seconds(csv_file_path, patient_output_folder)
    else:
        print("CSV file not found:", csv_file_path)

def main(selected_analysis_type, selected_patient):
    base_input_directory = r'C:\EEG Python'
    base_output_directory = r'C:\EEG Python\creatdata'
    
    input_directory = base_input_directory 
    if selected_analysis_type == 'ADHD':
        input_directory = os.path.join(base_input_directory, 'preproccesADHD')
    elif selected_analysis_type == 'NonADHD':
        input_directory = os.path.join(base_input_directory, 'preproccesNonADHD')
    else:
        print(f"Error: Unexpected analysis type '{selected_analysis_type}'. Defaulting to base input directory.")

    patient_prefix = f'{selected_patient}'  # patient names start with "Patient "
    patient_csv_filename = find_patient_file(input_directory, patient_prefix)
    if patient_csv_filename:
        print(f"Processing: {patient_csv_filename} in {input_directory}")  
        process_patient_files(input_directory, patient_csv_filename, base_output_directory, selected_analysis_type)
    else:
        print(f"No file found starting with {patient_prefix} in {input_directory}")

if __name__ == "__main__":
    # Example call for testing:
    # main('ADHD', 'Patient 1')
    main()
