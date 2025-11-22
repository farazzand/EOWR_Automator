# EOWR LAS/ASCII Generator  
#### Description:

EOWR LAS/ASCII Generator is a Python application for processing and generating well log files in LAS (Log ASCII Standard) and ASCII formats. Designed for drilling and mud logging workflows, it supports multi-step depth processing, metadata handling, validation, and flexible export options.

---

## Features

- **Cross-Platform Graphical Interface**  
  GUI built with tkinter, providing an intuitive workflow for file selection, configuration, and export.

- **Multi-Step Output Generation**  
  Supports LAS and ASCII output at 0.5 m, 1 m, and 5 m step sizes.

- **Metadata Handling**  
  Dedicated dialogs for entering company, well, field, rig, and related header information.

- **Depth Validation**  
  User-defined start depth and total depth (TD) with validation to ensure consistency.

- **NPD Integration (Optional)**  
  Ability to import NPD (Lithology) codes from Excel files (.xlsx / .xls).

- **File Management & Safety**  
  Multiple-file export with overwrite warnings and directory selection.

- **Performance & Stability**  
  Threaded processing to keep the UI responsive during operations.

- **Data Integrity Checks**  
  Validation of LAS input for correct step size and depth consistency.

- **Formatting & Calculations**  
  Rounding and formatting utilities for drilling parameters and gas ratios.

- **User Feedback System**  
  Built-in progress and error reporting panel within the interface.

---

## Requirements

- Python 3.x  
- tkinter (bundled with most Python installations)  
- lasio  
- numpy  
- pandas  

Install dependencies:

pip install lasio numpy pandas

---

## Usage

1. **Start the Application**  
   Run the script to open the main GUI.

2. **Select Output Types**  
   Choose LAS and/or ASCII formats and the step sizes (0.5 m, 1 m, 5 m).

3. **Provide LAS Input Files**  
   Select the corresponding LAS files for each chosen step size. The application validates depth intervals.

4. **Enter Well Metadata**  
   Fill in company details, well information, field, rig, and type.

5. **Specify Depth (if generating 1 m files)**  
   Provide the actual start depth and total depth.

6. **Optional: Load NPD Codes**  
   Select an Excel file with two numeric columns, or choose “No NPD”.

7. **Choose Output Directories**  
   Define destination folders for LAS and/or ASCII files.

8. **Process and Export**  
   The program applies rounding logic, validates data, integrates NPD (if applicable), and generates outputs with correct headers.

9. **Completion**  
   Files such as MUDLOG1m.las or MUDLOG0.5m.asc are saved in the selected directories.

---

## Supported File Types

### Input:
- LAS v2.0  
- Excel (.xlsx, .xls) for NPD / Lithology codes  

### Output:
- LAS  
- ASCII  

---

## Notes and Constraints

- Input LAS files must match the selected step size.  
- MWD memory data must be imported before generating the LAS file.  
- NPD Excel files must contain exactly two numeric columns.  
- Existing files in output directories may be overwritten.  
- All dialogs include built-in validation and error handling.

---

## Credits

Developed by Faraz Zand  
For the SLB WCM, Geoservices team
