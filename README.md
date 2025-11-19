EOWR LAS/ASCII Generator

A Python application for processing and generating well log files in LAS (Log ASCII Standard) and ASCII formats. Designed for drilling and mud logging workflows, it supports multi-step depth processing, metadata handling, validation, and flexible export options.

Features

Cross-platform GUI built with tkinter.

Output generation for LAS and ASCII at 0.5 m, 1 m, and 5 m step sizes.

Header and metadata dialogs for company, well, field, rig, and related info.

Depth-range validation with user-defined start and total depth (TD).

Optional integration of NPD (Lithology) codes from Excel files (.xlsx/.xls).

Multiple-file export with overwrite warnings.

Threaded processing to maintain UI responsiveness.

LAS input validation for step size and depth consistency.

Rounding and formatting utilities for drilling parameters and gas ratios.

Progress and error reporting panel within the UI.

Requirements

Python 3.x

tkinter (bundled with most Python installations)

lasio

numpy

pandas

Install dependencies:

pip install lasio numpy pandas

Usage

Start the application
Run the script to open the main GUI.

Select output types
Choose LAS and/or ASCII formats and the step sizes (0.5 m, 1 m, 5 m).

Provide LAS input files
Select the corresponding LAS files for each chosen step size. The application validates depth intervals.

Enter well metadata
Complete the dialog fields for company, well info, field, rig, and type.

Specify depth (if generating 1 m files)
Provide the actual start depth and total depth.

Optional: Load NPD codes
Select an Excel file with two numeric columns, or choose “No NPD”.

Choose output directories
Set the destinations for LAS and/or ASCII files.

Process and export
The program applies rounding, depth logic, and optional NPD codes, then generates the selected outputs with correct headers.

Completion
Files such as MUDLOG1m.las or MUDLOG0.5m.asc are saved in the selected folders.

Supported File Types

Input:

LAS v2.0

Excel (.xlsx, .xls) for NPD/Lithology codes

Output:

LAS

ASCII

Notes

Input LAS files must match the selected step size.

MWD memory data must be imported before generating the LAS file.

NPD Excel files must contain exactly two numeric columns.

Existing files in output directories may be overwritten.

All dialogs include validation and error handling.

Credits

Developed by Faraz Zand
For the SLB WCM, Geoservices team
