import tkinter as tk
from tkinter import filedialog
import csv

# Function to convert CSV to GLIM
def csv_to_glim(csv_file, glim_file):
    with open(csv_file, mode='r') as infile, open(glim_file, mode='w') as outfile:
        reader = csv.reader(infile)
        for row in reader:
            # Example conversion logic; replace it with your specific logic
            formatted_row = ' '.join(row) + '\n'
            outfile.write(formatted_row)

# Function to convert GLIM to CSV
def glim_to_csv(glim_file, csv_file):
    with open(glim_file, mode='r') as infile, open(csv_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        for line in infile:
            # Example conversion logic; adjust as necessary
            row = line.strip().split(' ')
            writer.writerow(row)

# Function to open file dialog and select CSV file
def select_csv_file():
    csv_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    return csv_file

# Function to open file dialog and select GLIM file
def select_glim_file():
    glim_file = filedialog.askopenfilename(filetypes=[("GLIM files", "*.glim")])
    return glim_file

# Function for saving a CSV file
def save_csv_file():
    csv_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    return csv_file

# Function for saving a GLIM file
def save_glim_file():
    glim_file = filedialog.asksaveasfilename(defaultextension=".glim", filetypes=[("GLIM files", "*.glim")])
    return glim_file

# Main function to run the program
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask user to select conversion type
    conversion_type = input("Choose conversion type: (1) CSV to GLIM (2) GLIM to CSV: ")

    if conversion_type == "1":
        # CSV to GLIM conversion
        csv_file = select_csv_file()
        glim_file = save_glim_file()
        csv_to_glim(csv_file, glim_file)
        print(f"Converted {csv_file} to {glim_file}")
    elif conversion_type == "2":
        # GLIM to CSV conversion
        glim_file = select_glim_file()
        csv_file = save_csv_file()
        glim_to_csv(glim_file, csv_file)
        print(f"Converted {glim_file} to {csv_file}")
    else:
        print("Invalid choice. Exiting...")

if __name__ == "__main__":
    main()
