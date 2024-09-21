import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox

def clac_group_measures():
    try:
        # Define the correct directory path to save the file in the current directory
        directory = os.getcwd()  # Get the current working directory
        output_file = os.path.join(directory, 'Group_Measures.xlsx')
        
        # Print the absolute file path for debugging
        print(f"Attempting to save the file to: {output_file}")
        
        # Create a new Excel writer object to write the results
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        workbook = writer.book
        worksheet = workbook.add_worksheet('Group Measures')  # Initialize the worksheet
        writer.sheets['Group Measures'] = worksheet
        print(f"Created Excel writer for file: {output_file}")
        
       
        columns = ['Patient', 'Average Degree (Global)', 'Global Efficiency', 'Average Shortest Path Length', 'Clustering Coefficient', 'Modularity']
        
        # Function to write data for a group (ADHD or NonADHD)
        def write_group_data(title, folder_name, patient_range, start_row):
            data = []
            for i in patient_range:
                file_name = f'patient {i}_analysis.csv'  # Updated file naming convention
                file_path = os.path.join(directory, folder_name, file_name)  # Corrected path
                
                # Print the file path for debugging
                print(f"Looking for file: {file_path}")
                
                # Check if the file exists
                if os.path.exists(file_path):
                    # Read the CSV file
                    df = pd.read_csv(file_path)
                    
                    # Get the last line of the relevant columns
                    last_line = df.iloc[-1, -5:].values.tolist()
                    
                    # Append the results to the list
                    data.append([f'patient{i}'] + last_line)
                    print(f"Processed {title} patient {i}")
                else:
                    print(f"File {file_path} does not exist!")
            
            # Write the title and headers
            worksheet.write(start_row, 0, title)
            start_row += 1
            for col_num, header in enumerate(columns):
                worksheet.write(start_row, col_num, header)
            
            # Adjust the width of each column to fit the header
            for col_num, header in enumerate(columns):
                worksheet.set_column(col_num, col_num, len(header) + 2)
            
            # Write the patient data
            for row_num, row_data in enumerate(data, start=start_row + 1):
                for col_num, value in enumerate(row_data):
                    worksheet.write(row_num, col_num, value)
            
            # Return the next row to start writing data
            return row_num + 2
        
        # Start writing ADHD data at row 0
        next_row = write_group_data('ADHD', 'ADHDexcel', range(1, 62), 0)
        
        # Start writing NonADHD data after a blank row
        write_group_data('NonADHD', 'NonADHDexcel', range(1, 61), next_row)
        
        # Save the Excel file by closing the writer
        writer.close()

        # Check if the file was created successfully
        if os.path.exists(output_file):
            print(f"File created successfully: {output_file}")
        else:
            print(f"File was not created: {output_file}")
        
        # Display a pop-up to confirm that the file was saved
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showinfo("Process Complete", "Data has been successfully saved!")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror("Error", f"An error occurred: {e}")

