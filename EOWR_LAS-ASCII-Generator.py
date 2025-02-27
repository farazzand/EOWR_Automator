import tkinter as tk
from tkinter import filedialog, messagebox
import lasio
import numpy as np
import time
from datetime import datetime
import pandas as pd
import os
import sys
import queue
import threading

# ----------------- UI STYLING CONSTANTS ----------------- #
UI_BG = "#f7f7f7"  # Light grey background for frames
UI_FG = "#333333"  # Dark grey text color
UI_FONT = ("Arial", 10)
UI_TITLE_FONT = ("Arial", 12, "bold")
UI_BUTTON_BG = "#4CAF50"  # Green button background
UI_BUTTON_FG = "white"
UI_ENTRY_BG = "white"

# Record the start time for execution timing
START_TIME = time.time()

# Constants for clarity and maintainability
NULL_VALUE = -999.25
ASCII_SEPARATOR = "     "  # Five spaces as per Requirements
EXPECTED_NPD_COLUMNS = 2

# Utility functions for rounding numbers
def round_three_decimals(number):
    """Round a number to three decimal places."""
    return round(number, 3)

def round_two_decimals(number):
    """Round a number to two decimal places."""
    return round(number, 2)

# LAS file header template (unchanged, hardcoded here for context)
HEADER_TEMPLATE = """~VERSION INFORMATION
VERS.  2.0                                                      :CWLS LOG ASCII STANDARD - VERSION 2.0
WRAP.  NO                                                       :ONE LINE PER STEP
PROD.  Schlumberger Technology Corp.                            :LAS Producer
PROG.  GN5 Export software                                      :LAS Program name
CREA.  XX                                     :LAS Creation date  {MM/DD/YYYY}
~WELL INFORMATION BLOCK
#MNEM                   .UNIT              DATA                 DESCRIPTION OF MNEMONIC
#----                   -----              ----                 -----------------------
STRT                    .m                 XX :START DEPTH
STOP                    .m                 XX :STOP DEPTH
STEP                    .m                 XX                  :STEP VALUE
NULL                    .                  -999.25              :NULL VALUE
COMP                    .                  XX :COMPANY NAME
WELL                    .                  XX :WELL NAME
FLD                     .                  XX :FIELD NAME
RIGN                    .                  XX :RIG NAME
RIGTYP                  .                  XX :RIG TYPE
SON                     .                                       :Service Order Number
SRVC                    .                  SLB                  :SERVICE COMPANY NAME
SRVL                    .                                       :SERVICE LINE NAME
LOGC                    .                  Geoservices          :LOGGING COMPANY NAME
DEGT                    .                                       :DEGASSER TYPE NAME
DETT                    .                                       :DEECTOR TYPE NAME
APPC                    .                                       :APPLIED CORRECTIONS
DATE                    .                                       :DATE
CLAB                    .                                       :County label
SLAB                    .                                       :State/Province label
PROV                    .                                       :State or Province
CTRY                    .                  Norway               :COUNTRY
CONT_REGION             .                                       :Continent Region
SECT                    .                                       :Section
TOWN                    .                                       :Township
RANGE                   .                                       :Range
API                     .                                       :API Number
UWI                     .                                       :UNIQUE WELL IDENTIFIER
LUL                     .                                       :Logging Unit Location
LUN                     .                                       :Logging Unit Number
LOC                     .                                       :Field Location
FL1                     .                                       :Field Location line 1
FL2                     .                                       :Field Location line 2
LATI                    .deg                                    :Latitude
LONG                    .deg                                    :Local Permanent Datum
PDAT                    .                                       :Geodetic Datum
GDAT                    .                                       :Geodetic Datum
LMF                     .                                       :Logging Measured From
APD                     .m                                      :Elevation of Depth Reference (LMF) above Permanent Datum
EPD                     .m                                      :Elevation of Permanent Datum (PDAT) above Mean Sea Level
EKD                     .m                                      :Elevation of Kelly Bushing above Permanent Datum
EDF                     .m                                      :Elevation of Drill Floor above Permanent Datum
~PARAMETER INFORMATION
~CURVE INFORMATION
#MNEM                   .UNIT              API CODE             CURVE DESCRIPTION
#----                   -----              --------             -----------------
DEPT                    .m                                      :Depth from Driller
DVER                    .m                                      :TVD Depth from Driller 
BDIA                    .in                                     :Bit Size
ROPA                    .m/h                                    :Drilling Rate 
HKLA                    .t                                      :Hook Load 
HKLX                    .t                                      :Maximum Hook load
WOBA                    .t                                      :Weight on bit
TQA                     .kN.m                                   :Torque
TQX                     .kN.m                                   :Torque maximum 
RPMA                    .1/min                                  :Revs per minute
RPMB                    .1/min                                  :Revs per minute – drill bit
SPPA                    .bar                                    :Pressure – mud pump
TVA                     .m3                                     :Tank Volume
MFIA                    .L/min                                  :Mud flow – Inflow
MFOA                    .%                                      :Mud flow – Outflow
MDIA                    .g/cm3                                  :Mud density – In
MDOA                    .g/cm3                                  :Mud density – Out
MTIA                    .degC                                   :Mud temperature – In
MTOA                    .degC                                   :Mud temperature – Out
ECDT                    .g/cm3                                  :Effective Mud Circulation Density at TD
BDTI                    .h                                      :Time – on bit
BDDI                    .m                                      :Bit drilled distance 
BRVC                    .krev                                   :Revs per minute – drill bit, cumulative
TCTI                    .h                                      :Time – total circulation time
FPPG                    .g/cm3                                  :Formation Pressure – equivalent mud density 
DXC                     .unitless                               :Drilling Exponent
GASX                    .%                                      :Total Gas
HSX                    .ppm                                    :Hydrogen sulfide (H2S)
MTHA                    .ppm                                    :Gas – methane 
ETHA                    .ppm                                    :Gas – ethane
PRPA                    .ppm                                    :Gas – propane
IBTA                    .ppm                                    :Gas – iso-butane
NBTA                    .ppm                                    :Gas – Normal butane
IPNA                    .ppm                                    :Gas – iso-pentane
NPNA                    .ppm                                    :Gas – Normal pentane
C1C2                    .unitless                               :Gas ratio – methane/ethane
C1C3                    .unitless                               :Gas ratio – methane/propane
C1C4                    .unitless                               :Gas ratio – methane/butane
C1C5                    .unitless                               :Gas ratio – methane/pentane
LITH                    .unitless                               :NPD Codes
CCAL                    .%                                      :Calcite content
CDOL                    .%                                      :Dolomite content 
WLFL                    .Euc                                    :Hydrocarbon show data - direct
WLCT                    .Euc                                    :Hydrocarbon show data - cut
#
#-----------------------------------------------------------
# DEPT(m)   DVER (m)   BDIA (in)   ROPA (m/h)   HKLA (t)   HKLX (t)   WOBA (t)   TQA (kN.m)   RPMA (1/min)   RPMB (1/min)   SPPA (bar)   TVA (m3)   MFIA (L/min)   MFOA (%)   MDIA (g/cm3)   MDOA (g/cm3)   MTIA (degC)   MTOA (degC)   ECDT (g/cm3)   BDTI (h)   BDDI (m)   BRVC (krev)   TCTI (h)   FPPG (g/cm3)   DXC (unitless)   GASX (%)   HSX (ppm)   MTHA (ppm)   ETHA (ppm)   PRPA (ppm)   IBTA (ppm)   NBTA (ppm)   IPNA (ppm)   NPNA (ppm)   C1C2 (unitless)   C1C3 (unitless)   C1C4 (unitless)   C1C5 (unitless)   LITH (unitless)   CCAL (%)   CDOL (%)   WLFL (Euc)   WLCT (Euc)
#-----------------------------------------------------------
~A
"""

# ASCII header (single line of curve names)
ASCII_HEADER = """DEPT(m)   DVER (m)   BDIA (in)   ROPA (m/h)   HKLA (t)   HKLX (t)   WOBA (t)   TQA (kN.m)   RPMA (1/min)   RPMB (1/min)   SPPA (bar)   TVA (m3)   MFIA (L/min)   MFOA (%)   MDIA (g/cm3)   MDOA (g/cm3)   MTIA (degC)   MTOA (degC)   ECDT (g/cm3)   BDTI (h)   BDDI (m)   BRVC (krev)   TCTI (h)   FPPG (g/cm3)   DXC (unitless)   GASX (%)   HSX (ppm)   MTHA (ppm)   ETHA (ppm)   PRPA (ppm)   IBTA (ppm)   NBTA (ppm)   IPNA (ppm)   NPNA (ppm)   C1C2 (unitless)   C1C3 (unitless)   C1C4 (unitless)   C1C5 (unitless)   LITH (unitless)   CCAL (%)   CDOL (%)   WLFL (Euc)   WLCT (Euc)
"""

# ----------------- THREADING IMPLEMENTATION ----------------- #
class FileGenerationThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.queue = queue.Queue()

    def run(self):
        try:
            result = self.target(*self.args, **self.kwargs, queue=self.queue)
            self.queue.put(('SUCCESS', result))
        except Exception as e:
            self.queue.put(('ERROR', str(e)))


# ----------------- UI HELPER FUNCTIONS ----------------- #

def clear_workflow_area(parent):
    """Remove all widgets from the workflow area."""
    for widget in parent.winfo_children():
        widget.destroy()


def show_loading_animation(parent):
    """Display a loading animation (cycling dots) in the given parent."""
    loading_label = tk.Label(parent, text=".", font=UI_FONT, bg=UI_BG, fg=UI_FG)
    loading_label.pack(pady=10)

    def update_dots(count=1):
        dots = "." * count
        loading_label.config(text=dots)
        next_count = count + 1 if count < 3 else 1
        loading_label.after(500, update_dots, next_count)

    update_dots()
    return loading_label


# ----------------- MODIFIED UI FUNCTIONS (Using workflow area) ----------------- #

def select_las_file(parent, update_progress):
    """Prompt user to select a LAS file with requirements dialog.
    (Text remains exactly as in your original code.)"""
    clear_workflow_area(parent)
    file_path_var = tk.StringVar()
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    dialog_title = tk.Label(dialog, text="Input LAS File", font=UI_TITLE_FONT, bg=UI_BG, fg=UI_FG)
    dialog_title.pack(pady=5)
    requirements_message = (
        "*** Before proceeding with the selection of the LAS file, please ensure it meets the following requirements: ***\n\n\n"
        "- The input LAS file should be generated with a 0.5-meter step regardless of the desired outputs.\n\n"
        "- Input file includes the maximum possible depth range. For example, if drilling began at a depth that is not a whole meter (e.g., 1000.2 m), the file should start from the nearest shallower whole meter if there is data in the database(e.g., 1000 m).\n\n"
        "- Similarly, if the well’s total depth (TD) is not a whole meter (e.g., 5000.7 m), the file should extend to the nearest deeper whole meter if there is data in the database (e.g., 5001 m).\n\n"
        "- MWD memory data must be imported before generating the LAS file.\n"
    )
    tk.Label(dialog, text=requirements_message, justify=tk.LEFT, bg=UI_BG, fg=UI_FG, font=UI_FONT, wraplength=700) \
        .pack(padx=10, pady=10)

    button_frame = tk.Frame(dialog, bg=UI_BG)
    button_frame.pack(pady=5)

    def on_select():
        file_path = filedialog.askopenfilename(
            title="Select a LAS file",
            filetypes=[("LAS files", "*.las"), ("All files", "*.*")]
        )
        file_path_var.set(file_path)

    tk.Button(button_frame, text="Select LAS File", command=on_select,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised") \
        .pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=lambda: file_path_var.set(""),
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised") \
        .pack(side=tk.LEFT, padx=5)
    parent.wait_variable(file_path_var)
    file_path = file_path_var.get()
    dialog.destroy()
    if not file_path:
        update_progress("No file selected. Exiting.")
        print("No file selected. Exiting.")
    else:
        update_progress(f"Selected file: {file_path}")
        print(f"Selected file: {file_path}")
    return file_path


def collect_header_info(parent, update_progress):
    """Collect well header information through a GUI dialog """
    clear_workflow_area(parent)
    questions = [
        "Client's company name:",
        "Full well name (including country code, 'NO' f.ex.):",
        "Start depth of the well (mMD):",
        "Total depth (TD) of the well (mMD):",
        "Field Name:",
        "Rig Name:",
        "Rig Type:"
    ]
    answers = []
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    dialog_title = tk.Label(dialog, text="Header Information", font=UI_TITLE_FONT, bg=UI_BG, fg=UI_FG)
    dialog_title.pack(pady=5)
    frame = tk.Frame(dialog, bg=UI_BG)
    frame.pack(padx=10, pady=10)
    labels = []
    entries = []
    for idx, question in enumerate(questions):
        label = tk.Label(frame, text=question, font=UI_FONT, bg=UI_BG, fg=UI_FG)
        label.grid(row=idx, column=0, sticky="w", padx=(0, 10), pady=5)
        entry = tk.Entry(frame, width=50, font=UI_FONT, bg=UI_ENTRY_BG)
        entry.grid(row=idx, column=1, pady=5)
        labels.append(label)
        entries.append(entry)

    def validate_and_submit():
        nonlocal answers
        error_found = False
        temp_answers = []
        for lbl in labels:
            lbl.config(fg=UI_FG)
        for i, question in enumerate(questions):
            ans = entries[i].get().strip()
            if not ans:
                messagebox.showerror("Input Error", f"Please fill out the question:\n{question}")
                labels[i].config(fg="red")
                error_found = True
                temp_answers.append(None)
                continue
            if "depth" in question.lower():
                ans = ans.replace(',', '.')
                try:
                    float_val = float(ans)
                    if '.' not in ans:
                        ans = f"{float_val:.2f}"
                    else:
                        parts = ans.split('.')
                        if len(parts) < 2 or len(parts[1]) != 2:
                            messagebox.showerror("Input Error", "Do not use more than two decimal points for depth.\n")
                            labels[i].config(fg="red")
                            error_found = True
                            temp_answers.append(None)
                            continue
                        ans = f"{float_val:.2f}"
                except ValueError:
                    messagebox.showerror("Input Error", f"Invalid number format for:\n{question}")
                    labels[i].config(fg="red")
                    error_found = True
                    temp_answers.append(None)
                    continue
                except IndexError:
                    messagebox.showerror("Input Error", f"Error for:\n{question}")
                    labels[i].config(fg="red")
                    error_found = True
                    temp_answers.append(None)
                    continue
            temp_answers.append(ans)
        if not error_found:
            for i, ans in enumerate(temp_answers):
                entries[i].delete(0, tk.END)
                entries[i].insert(0, ans)
            answers.extend(temp_answers)
            update_progress("Header information collected.")
            dialog.destroy()

    tk.Button(dialog, text="Submit", command=validate_and_submit,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised") \
        .pack(pady=10)
    parent.wait_window(dialog)
    return answers


def select_npd_file(parent, start_depth, total_depth, update_progress):
    """Handle NPD code file selection if applicable."""
    clear_workflow_area(parent)
    npd_answer = {"value": False}
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    tk.Label(dialog, text="NPD Codes", font=UI_TITLE_FONT, bg=UI_BG, fg=UI_FG) \
        .pack(pady=5)
    tk.Label(dialog, text="Are there any NPD codes available for this well?\n", font=UI_FONT, bg=UI_BG, fg=UI_FG) \
        .pack(pady=5)
    button_frame = tk.Frame(dialog, bg=UI_BG)
    button_frame.pack(pady=5)

    def on_yes():
        npd_answer["value"] = True
        dialog.destroy()

    def on_no():
        npd_answer["value"] = False
        dialog.destroy()

    tk.Button(button_frame, text="Yes", command=on_yes,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised") \
        .pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="No", command=on_no,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised") \
        .pack(side=tk.LEFT, padx=5)
    parent.wait_window(dialog)
    has_npd = npd_answer["value"]
    npd_data = None
    if has_npd:
        clear_workflow_area(parent)
        dialog2 = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
        dialog2.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Label(dialog2, text=(
            f"Previously entered data indicates the well’s starting depth at {start_depth} mMD "
            f"and the total depth (TD) at {total_depth} mMD. \nNPD codes should ideally match the "
            "interval but can be close if exactness isn’t feasible."
        ), justify=tk.LEFT, font=UI_FONT, bg=UI_BG, fg=UI_FG, wraplength=700) \
            .pack(padx=10, pady=10)
        file_path_var = tk.StringVar()

        def on_select():
            selected_path = filedialog.askopenfilename(
                title="Select NPD Code File",
                filetypes=[("Excel Files", "*.xlsx *.xls")]
            )
            if selected_path and selected_path.lower().endswith(('.xlsx', '.xls')):
                file_path_var.set(selected_path)
                dialog2.destroy()
            elif selected_path:
                messagebox.showerror("Error", "File must be an Excel file (.xlsx or .xls)")

        def on_cancel():
            file_path_var.set('')
            dialog2.destroy()

        button_frame2 = tk.Frame(dialog2, bg=UI_BG)
        button_frame2.pack(pady=5)
        tk.Button(button_frame2, text="Select NPD Code File", command=on_select,
                  bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised") \
            .pack(side=tk.LEFT, padx=5)
        parent.wait_window(dialog2)
        file_path_npd = file_path_var.get()
        if file_path_npd:
            try:
                df = pd.read_excel(file_path_npd)
                if len(df.columns) != EXPECTED_NPD_COLUMNS:
                    messagebox.showerror("Error",
                                         "Excel file must contain exactly two columns. Please check your NPD file and try again.")
                    sys.exit(1)
                if not all(pd.api.types.is_numeric_dtype(df[col]) for col in df.columns):
                    messagebox.showerror("Error", "Both columns must contain only numbers. Please check your NPD file and try again.")
                    sys.exit(1)
                npd_data = df.values.tolist()
                update_progress("NPD file processed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read Excel file: {str(e)}")
                sys.exit(1)
    return has_npd, npd_data


def select_output_options(parent, update_progress):
    """Prompt user to select output file types and directories."""
    clear_workflow_area(parent)
    # Dialog for selecting output options.
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    tk.Label(dialog, text="Select the outputs that you want to generate:", wraplength=250,
             font=UI_FONT, bg=UI_BG, fg=UI_FG).pack(pady=10)

    selections = {}
    options = ["LAS 0.5m", "LAS 1m", "LAS 5m", "ASCII 0.5m", "ASCII 1m", "ASCII 5m"]
    checkbox_frame = tk.Frame(dialog, bg=UI_BG)
    checkbox_frame.pack(pady=10, padx=10, fill="x")

    for option in options:
        var = tk.BooleanVar()
        selections[option] = var
        cb = tk.Checkbutton(checkbox_frame, text=option, variable=var,
                            font=UI_FONT, bg=UI_BG, fg=UI_FG, anchor="w", selectcolor=UI_BG)
        if option == "LAS 1m":
            cb.config(font=UI_TITLE_FONT)
        cb.pack(anchor="w")

    selected_options = []
    las_dir, ascii_dir = None, None

    def submit_selection():
        nonlocal selected_options
        selected_options = [opt for opt, var in selections.items() if var.get()]
        dialog.destroy()

    tk.Button(dialog, text="Submit", command=submit_selection,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(pady=20)
    parent.wait_window(dialog)
    update_progress("Output selection completed.")

    # Container for directory selections and the Continue button.
    dir_container = tk.Frame(parent, bg=UI_BG)
    dir_container.pack(pady=10, padx=10, fill="x")

    # LAS directory selection frame.
    if any(opt.startswith('LAS') for opt in selected_options):
        las_frame = tk.Frame(dir_container, bg=UI_BG)
        las_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(las_frame, text="Select Directory for output LAS Files. \n Files will be named automatically.", bg=UI_BG, fg=UI_FG, font=UI_FONT).pack()
        las_label = tk.Label(las_frame, text="No directory selected", bg=UI_BG, fg=UI_FG, font=UI_FONT)
        las_label.pack()
        def browse_las():
            nonlocal las_dir
            las_dir = filedialog.askdirectory(title="Select Directory for LAS Files")
            if las_dir:
                las_label.config(text=f"LAS Directory: {las_dir}")
        tk.Button(las_frame, text="Browse", command=browse_las,
                  bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT).pack(pady=5)

    # ASCII directory selection frame.
    if any(opt.startswith('ASCII') for opt in selected_options):
        ascii_frame = tk.Frame(dir_container, bg=UI_BG)
        ascii_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(ascii_frame, text="Select Directory for output ASCII Files. \n Files will be named automatically.", bg=UI_BG, fg=UI_FG, font=UI_FONT).pack()
        ascii_label = tk.Label(ascii_frame, text="No directory selected", bg=UI_BG, fg=UI_FG, font=UI_FONT)
        ascii_label.pack()
        def browse_ascii():
            nonlocal ascii_dir
            ascii_dir = filedialog.askdirectory(title="Select Directory for ASCII Files")
            if ascii_dir:
                ascii_label.config(text=f"ASCII Directory: {ascii_dir}")
        tk.Button(ascii_frame, text="Browse", command=browse_ascii,
                  bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT).pack(pady=5)

    # Handler for the Continue button.
    def on_continue():
        if any(opt.startswith('LAS') for opt in selected_options) and not las_dir:
            messagebox.showerror("Error", "Please select a directory for LAS Files.")
            return
        if any(opt.startswith('ASCII') for opt in selected_options) and not ascii_dir:
            messagebox.showerror("Error", "Please select a directory for ASCII Files.")
            return
        # If both required paths are selected, proceed.
        dir_container.destroy()

    # Continue button placed below the directory selections.
    tk.Button(dir_container, text="Continue", command=on_continue,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(pady=20)

    parent.wait_window(dir_container)
    return selected_options, las_dir, ascii_dir


# ----------------- THE REST OF THE CODE (DATA PROCESSING, FORMATTING, FILE GENERATION) REMAINS UNCHANGED -----------------#

def process_data_buffer(data_buffer, curve_index_map, update_progress):
    """Process the data buffer with vectorized operations for curves."""
    intended_curve_names = [
        "BRVC", "GASX", "MTHA", "ETHA", "PRPA",
        "NBTA", "NPNA", "C1C2", "C1C3", "C1C4", "C1C5", "LITH"
    ]
    intended_parameters = {name: curve_index_map[name.upper()] for name in intended_curve_names if
                           name.upper() in curve_index_map}

    # Apply NPD codes if provided (LITH curve at index 39)
    if "LITH" in intended_parameters and "npd_data" in globals():
        for depth_val, npd_code in globals()["npd_data"]:
            mask = (data_buffer[:, 0] == float(depth_val))
            data_buffer[mask, 39] = float(npd_code)  # 39 is LITH curve index

    # Process specific curves
    if "BRVC" in curve_index_map:
        data_buffer[:, curve_index_map["BRVC"]] /= 1000  # Convert to krev
        update_progress("Revs per minute, converted to Krev ( /1000).")
    if "GASX" in curve_index_map:
        data_buffer[:, curve_index_map["GASX"]] = np.round(data_buffer[:, curve_index_map["GASX"]], 3)
        update_progress("Total gas values set to 3 decimal points")

    def process_ratio(target_mnemonic, numerator_key, denominator_key):
        """Calculate ratio between two curves, handling invalid cases."""
        if target_mnemonic in curve_index_map and numerator_key in intended_parameters and denominator_key in intended_parameters:
            idx = curve_index_map[target_mnemonic]
            num = data_buffer[:, intended_parameters[numerator_key]]
            denom = data_buffer[:, intended_parameters[denominator_key]]
            mask_invalid = (num == 0) | (denom == 0) | (num == NULL_VALUE) | (denom == NULL_VALUE)
            data_buffer[:, idx] = np.where(mask_invalid, NULL_VALUE, np.round(num / denom, 2))

    process_ratio("C1C2", "MTHA", "ETHA")
    update_progress("C1/C2 ratio processed and format set to 2 decimal points.")
    process_ratio("C1C3", "MTHA", "PRPA")
    update_progress("C1/C3 ratio processed and format set to 2 decimal points.")
    process_ratio("C1C4", "MTHA", "NBTA")
    update_progress("C1/C4 ratio processed and format set to 2 decimal points.")
    process_ratio("C1C5", "MTHA", "NPNA")
    update_progress("C1/C5 ratio processed and format set to 2 decimal points.")

    # Subsample data for different step sizes
    mask_whole = (data_buffer[:, 0] % 1 == 0)
    data_one_meter = data_buffer[mask_whole]
    indices_whole = np.where(mask_whole)[0]
    first_whole_row = indices_whole[0] if indices_whole.size > 0 else 0
    data_five_meter = data_buffer[first_whole_row::10]
    update_progress("0.5m, 1m, and 5m data filtering completed.")

    return data_buffer, data_one_meter, data_five_meter


def format_data(data_subset, las):
    """Format data rows according to curve mnemonics."""
    formatted_lines = []
    for row in data_subset:
        formatted_row = []
        for j, value in enumerate(row):
            mnemonic = las.curves[j].mnemonic.upper()
            if np.isnan(value):
                formatted_value = str(NULL_VALUE)
            else:
                if mnemonic == "DXC":
                    formatted_value = f"{value:.5f}"
                elif mnemonic in ["GASX", "MDIA", "MDOA", "ECDT", "BDTI", "BDDI", "BRVC", "LITH"]:
                    formatted_value = f"{value:.3f}"
                elif mnemonic in ["C1C2", "C1C3", "C1C4", "C1C5", "Depth", "DVER", "ROPA", "TQA", "TQX", "TVA", "MFIA",
                                  "TCTI"]:
                    formatted_value = f"{value:.2f}"
                elif mnemonic in ["BDIA", "HKLA", "HKLX", "WOBA", "SPPA", "MTIA", "MTOA"]:
                    formatted_value = f"{value:.1f}"
                elif mnemonic in ["RPMA", "RPMB", "HSX", "MTHA", "ETHA", "PRPA", "IBTA", "NBTA", "IPNA", "NPNA"]:
                    formatted_value = f"{value:.0f}"
                else:
                    formatted_value = f"{value:.2f}"
            formatted_row.append(formatted_value)
        formatted_lines.append(ASCII_SEPARATOR.join(formatted_row) + "\n")
    return formatted_lines


def update_step_header(header_lines, step_value):
    """Update the STEP value in the LAS header."""
    return [line.replace("XX", f"{step_value:.1f}", 1) if line.strip().startswith("STEP") else line for line in
            header_lines]


def generate_output_files(selected_options, las_dir, ascii_dir, data_buffer, data_one_meter, data_five_meter, las,
                          modified_header_lines, update_progress):
    """Generate selected LAS and ASCII output files."""

    update_progress("Output files are being processed and saved...")
    for option in selected_options:
        if option.startswith("LAS") and las_dir:
            if "0.5m" in option:
                step, step_name, data_subset = 0.5, 0.5, data_buffer
                update_progress("LAS 0.5m components prepared. \n Please wait...")
            elif "1m" in option:
                step, step_name, data_subset = 1.0, 1, data_one_meter
                update_progress("LAS 1m components prepared. \n Please wait...")
            elif "5m" in option:
                step, step_name, data_subset = 5.0, 5, data_five_meter
                update_progress("LAS 5m components prepared. \n Please wait...")
            else:
                continue
            las_header = update_step_header(modified_header_lines.copy(), step)
            formatted_data = format_data(data_subset, las)
            content = las_header + formatted_data
            filename = f"MUD_LOG_{step_name}m.las"
            save_path = os.path.join(las_dir, filename)
            try:
                with open(save_path, 'w', encoding="utf-8") as f:
                    f.writelines(content)
                update_progress(f"{filename} generated and saved successfully.")
                print(f"{filename}  generated and saved successfully.")
            except Exception as e:
                update_progress(f"Error saving {filename}: {e}")
                print(f"Error saving {filename}: {e}")

        elif option.startswith("ASCII") and ascii_dir:
            if "0.5m" in option:
                data_subset = data_buffer
                step_name = "0.5m"
                update_progress("ASCII 0.5 components prepared. \n Please wait...")
            elif "1m" in option:
                data_subset = data_one_meter
                step_name = "1m"
                update_progress("ASCII 1m components prepared. \n Please wait...")
            elif "5m" in option:
                data_subset = data_five_meter
                step_name = "5m"
                update_progress("ASCII 5m components prepared.\n Please wait...")
            else:
                continue
            ascii_header = [ASCII_HEADER]
            formatted_data = format_data(data_subset, las)
            content = ascii_header + formatted_data
            filename = f"MUD_LOG_{step_name}.asc"
            save_path = os.path.join(ascii_dir, filename)
            try:
                with open(save_path, 'w') as f:
                    f.writelines(content)
                update_progress(f"{filename}  generated and saved successfully.")
                print(f"{filename} generated and saved successfully.")
            except Exception as e:
                update_progress(f"Error saving {filename}: {e}")
                print(f"Error saving {filename}: {e}")


# ----------------- MODIFIED MAIN FUNCTION ----------------- #
def main():
    root = tk.Tk()
    root.title("EOWR LAS/ASCII Generator")
    root.configure(bg=UI_BG)

    def on_closing():
        root.destroy()  # Closes the window properly
        os._exit(0)  # Ensures the script terminates completely

    root.protocol("WM_DELETE_WINDOW", on_closing)  # Handle window close button

    # Set a custom window size
    WINDOW_WIDTH = 800  # Change this to your desired width
    WINDOW_HEIGHT = 600  # Change this to your desired height
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Create a vertical paned window: top for workflow, bottom for progress reporting.
    paned = tk.PanedWindow(root, orient=tk.VERTICAL, bg=UI_BG)
    paned.pack(fill=tk.BOTH, expand=True)

    workflow_frame = tk.Frame(paned, bg=UI_BG)
    paned.add(workflow_frame, stretch="always")

    progress_frame = tk.Frame(paned, height=150, bg=UI_BG)
    paned.add(progress_frame)

    # Progress text widget
    progress_text = tk.Text(progress_frame, height=8, font=UI_FONT, bg="white", fg=UI_FG)
    progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Watermark label at the bottom (only in progress area)
    watermark_label = tk.Label(progress_frame, text="Developed by Faraz Zand", font=("Arial", 8), fg="grey", bg=UI_BG)
    watermark_label.pack(side=tk.BOTTOM, anchor="e", padx=5, pady=2)

    def update_progress(message):
        progress_text.insert(tk.END, message + "\n")
        progress_text.see(tk.END)
        root.update_idletasks()

    update_progress("Application started.")

    # Step 1: Select LAS file (with full original text)
    las_file_path = select_las_file(workflow_frame, update_progress)
    if not las_file_path:
        return

    # Step 2: Read LAS file (show loading animation during processing)
    clear_workflow_area(workflow_frame)
    loading = show_loading_animation(workflow_frame)
    try:
        las = lasio.read(las_file_path)
        update_progress("LAS input file imported and read successfully.")
    except Exception as e:
        update_progress(f"Error reading LAS file: {e}")
        messagebox.showerror("Error", f"Failed to read LAS file. Make sure right format is selected\n Error: {str(e)}")
        print("Error reading LAS file:", e)
        loading.destroy()
        sys.exit(1)

    loading.destroy()

    # Step 3: Prepare data buffer and curve index map (show loading animation)
    clear_workflow_area(workflow_frame)
    loading = show_loading_animation(workflow_frame)
    try:
        data_buffer = np.array(las.data.copy())
    except AttributeError:
        data_buffer = np.array([row[:] for row in las.data])
    update_progress("Data buffer created.")
    curve_index_map = {curve.mnemonic.upper(): idx for idx, curve in enumerate(las.curves)}
    update_progress("Curve index map created.")
    loading.destroy()

    # Step 4: Collect header information (text unchanged)
    header_answers = collect_header_info(workflow_frame, update_progress)
    if not header_answers:
        sys.exit(0)

    # Step 5: Handle NPD codes
    has_npd, npd_data = select_npd_file(workflow_frame, header_answers[2], header_answers[3], update_progress)
    if has_npd and npd_data:
        globals()["npd_data"] = npd_data  # Store for use in process_data_buffer

    # Step 6: Process data (show loading animation)
    clear_workflow_area(workflow_frame)
    loading = show_loading_animation(workflow_frame)
    data_half_meter, data_one_meter, data_five_meter = process_data_buffer(data_buffer, curve_index_map,
                                                                           update_progress)
    if data_one_meter.shape[0] > 0 and data_one_meter[-1, 0] > float(header_answers[3]):
        update_progress("Depth associated with the last row > actual TD")
        data_one_meter[-1, 3:] = NULL_VALUE
        update_progress("First three columns of the last row kept unchanged. Rest set to -999.25")
    loading.destroy()

    # Step 7: Update header with user inputs
    clear_workflow_area(workflow_frame)
    loading = show_loading_animation(workflow_frame)
    today = datetime.now()
    date_string = today.strftime("%m/%d/%Y")
    field_mapping = {
        "COMP": header_answers[0], "WELL": header_answers[1], "STRT": header_answers[2],
        "STOP": header_answers[3], "FLD": header_answers[4], "RIGN": header_answers[5],
        "RIGTYP": header_answers[6], "CREA.": date_string
    }
    header_lines = HEADER_TEMPLATE.splitlines(keepends=True)
    modified_header_lines = header_lines.copy()
    for field, new_value in field_mapping.items():
        for i, line in enumerate(modified_header_lines):
            if field in line.split():
                try:
                    xx_index = line.index("XX")
                    input_length = len(new_value)
                    padded_value = new_value + " " * (20 - input_length) if input_length < 21 else new_value + " "
                    modified_header_lines[i] = line.replace("XX", padded_value, 1)
                    break
                except ValueError:
                    continue
    update_progress("Header updated with provided inputs by user.")
    loading.destroy()

    # Step 8: Select output options and directories
    selected_options, las_dir, ascii_dir = select_output_options(workflow_frame, update_progress)
    if not las_dir and not ascii_dir:
        update_progress("No directories selected. Exiting.")
        print("No directories selected. Exiting.")
        return

    # Step 9: Generate output files using a background thread
    clear_workflow_area(workflow_frame)
    loading = show_loading_animation(workflow_frame)

    def handle_generation_completion():
        loading.destroy()
        clear_workflow_area(workflow_frame)
        tk.Button(workflow_frame, text="Close", command=lambda: (root.destroy(), sys.exit(0)),
                  bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised") \
            .pack(pady=10)
        update_progress("LAS/ASCII Processing completed. Please find the output file(s) in the selected path(s). \n Click 'Close' to exit.")

    def check_generation_queue():
        while True:
            try:
                msg_type, content = generation_thread.queue.get_nowait()
                if msg_type == 'PROGRESS':
                    update_progress(content)
                elif msg_type == 'SUCCESS':
                    handle_generation_completion()
                    return
                elif msg_type == 'ERROR':
                    messagebox.showerror("Generation Error", content)
                    sys.exit(1)
            except queue.Empty:
                break
        root.after(100, check_generation_queue)

    # Modified generate_output_files to use queue
    def threaded_generate_output_files(*args, queue=None, **kwargs):
        def queue_update(message):
            queue.put(('PROGRESS', message))

        generate_output_files(*args,
                              update_progress=queue_update,
                              **kwargs)
        queue.put(('SUCCESS', None))

    # Start the generation in a background thread
    generation_thread = FileGenerationThread(
        target=threaded_generate_output_files,
        args=(selected_options, las_dir, ascii_dir, data_half_meter,
              data_one_meter, data_five_meter, las, modified_header_lines)
    )
    generation_thread.start()

    # Start checking the queue
    check_generation_queue()



    root.mainloop()
    # Finalize execution timing
    end_time = time.time()
    execution_time = end_time - START_TIME
    update_progress(f"Execution completed in {execution_time:.6f} seconds")


if __name__ == "__main__":
    main()
