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
from decimal import Decimal, ROUND_HALF_UP


# ----------------- UI STYLING CONSTANTS ----------------- #
UI_BG = "#f7f7f7"         # Light grey background for frames
UI_FG = "#333333"         # Dark grey text color
UI_FONT = ("Arial", 10)
UI_TITLE_FONT = ("Arial", 12, "bold")
UI_BUTTON_BG = "#555555"  # Green button background
UI_BUTTON_FG = "white"
UI_ENTRY_BG = "white"

# Record the start time for execution timing
START_TIME = time.time()

# Constants for clarity and maintainability
NULL_VALUE = -999.25
ASCII_SEPARATOR = "     "  # Five spaces – only applied to LAS 1m
EXPECTED_NPD_COLUMNS = 2

# Utility functions for rounding numbers
def round_three_decimals(number):
    """Round a number to three decimal places. If ending in 5, round up."""
    return float(Decimal(str(number)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))

def round_two_decimals(number):
    """Round a number to two decimal places. If ending in 5, round up."""
    try:
        if np.isnan(number) or np.isinf(number):
            return number
        return float(Decimal(str(number)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except (ValueError, Exception):
        return number

# LAS file header template (unchanged)
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
SRVL                    .                  WCM Geoservices      :SERVICE LINE NAME
LOGC                    .                  Geoservices          :LOGGING COMPANY NAME
DEGT                    .                                       :DEGASSER TYPE NAME
DETT                    .                                       :DEECTOR TYPE NAME
APPC                    .                                       :APPLIED CORRECTIONS
DATE                    .                                       :DATE
CLAB                    .                                       :County label
SLAB                    .                                       :State/Province label
PROV                    .                                       :State or Province
CTRY                    .                  NORWAY               :COUNTRY
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
HSX                     .ppm                                    :Hydrogen sulfide (H2S)
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
# DEPT(m)   DVER (m)   BDIA (in) ROPA (m/h)   HKLA (t)   HKLX (t)   WOBA (t) TQA (kN.m) TQX (kN.m) RPMA (1/min) RPMB (1/min) SPPA (bar)   TVA (m3) MFIA (L/min)   MFOA (%) MDIA (g/cm3) MDOA (g/cm3) MTIA (degC) MTOA (degC) ECDT (g/cm3)   BDTI (h)   BDDI (m) BRVC (krev)   TCTI (h) FPPG (g/cm3) DXC (unitless)   GASX (%)  HSX (ppm) MTHA (ppm) ETHA (ppm) PRPA (ppm) IBTA (ppm) NBTA (ppm) IPNA (ppm) NPNA (ppm) C1C2 (unitless) C1C3 (unitless) C1C4 (unitless) C1C5 (unitless) LITH (unitless)   CCAL (%)   CDOL (%) WLFL (Euc) WLCT (Euc)
#-----------------------------------------------------------
~A
"""

# ASCII header (extra newline removed)
ASCII_HEADER = """Depth (m)\t  DVER (m)\t  BDIA (in)\tROPA (m/h)\t  HKLA (t)\t  HKLX (t)\t  WOBA (t)\tTQA (kN.m)\tTQX (kN.m)\tRPMA (1/min)\tRPMB (1/min)\tSPPA (bar)\t  TVA (m3)\tMFIA (L/min)\t  MFOA (%)\tMDIA (g/cm3)\tMDOA (g/cm3)\tMTIA (degC)\tMTOA (degC)\tECDT (g/cm3)\t  BDTI (h)\t  BDDI (m)\tBRVC (krev)\t  TCTI (h)\tFPPG (g/cm3)\tDXC (unitless)\t  GASX (%)\t HSX (ppm)\tMTHA (ppm)\tETHA (ppm)\tPRPA (ppm)\tIBTA (ppm)\tNBTA (ppm)\tIPNA (ppm)\tNPNA (ppm)\tC1C2 (unitless)\tC1C3 (unitless)\tC1C4 (unitless)\tC1C5 (unitless)\tLITH (unitless)\t  CCAL (%)\t  CDOL (%)\tWLFL (Euc)\tWLCT (Euc)	
\n\n"""

# ----------------- THREADING IMPLEMENTATION ----------------- #
"""Handle the generation of files in a separate thread, allowing the main application to remain responsive during the file generation process."""
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

# ----------------- DIALOG FUNCTIONS WITH BACK BUTTON SUPPORT ----------------- #
# Each interactive dialog returns "BACK" when the Back button is pressed.
def select_output_options(parent, update_progress):
    """Step 1: Prompt user to select output file types."""
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    title = tk.Label(dialog, text="Output Files Selection", font=UI_TITLE_FONT, bg=UI_BG, fg=UI_FG)
    title.pack(pady=5)
    tk.Label(dialog, text="Select the outputs that you want to generate:", wraplength=280,
             font=UI_FONT, bg=UI_BG, fg=UI_FG).pack(pady=10)
    selections = {}
    options = ["LAS 0.5m", "LAS 1m", "LAS 5m", "ASCII 0.5m", "ASCII 1m", "ASCII 5m"]
    checkbox_frame = tk.Frame(dialog, bg=UI_BG)
    checkbox_frame.pack(pady=10, padx=10, fill="x")
    checkbox_vars = {}
    for option in options:
        var = tk.BooleanVar()
        checkbox_vars[option] = var
        cb = tk.Checkbutton(checkbox_frame, text=option, variable=var,
                            font=UI_FONT, bg=UI_BG, fg=UI_FG, anchor="w", selectcolor=UI_BG)
        if option == "LAS 1m":
            cb.config(font=UI_TITLE_FONT)
        cb.pack(anchor="w")
    def submit_selection():
        for opt, var in checkbox_vars.items():
            if var.get():
                selections[opt] = True
        if not selections:
            messagebox.showwarning("Warning", "At least one option should be selected.")
            return
        dialog.destroy()
    tk.Button(dialog, text="Submit", command=submit_selection,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(pady=20)
    parent.wait_window(dialog)
    update_progress("Desired outputs collected from user. \nOutput selection completed.")
    return selections

def select_las_file(parent, update_progress, selected_outputs):
    """Step 2: Prompt user to select required LAS file(s) for chosen step sizes."""
    required_steps = set()
    for opt in selected_outputs:
        if "0.5m" in opt:
            required_steps.add(0.5)
        elif "1m" in opt:
            required_steps.add(1.0)
        elif "5m" in opt:
            required_steps.add(5.0)
    required_steps = sorted(required_steps)
    selected_files = {step: None for step in required_steps}
    back_pressed = False
    messagebox.showwarning(
        "Input File Requirements",
        "Please make sure your input files meet the following requirements: \n\n\n"
        "- Choose LAS 2 file option upon generating the input file.\n\n"
        "- Input file includes the maximum possible depth range. For example, if drilling began at a depth that is not a whole meter (e.g., 1000.2 m), the file should start from the nearest shallower whole meter if there is data in the database(e.g., 1000 m).\n\n"
        "- Similarly, if the well’s total depth (TD) is not a whole meter (e.g., 5000.7 m), the file should extend to the nearest deeper whole meter if there is data in the database (e.g., 5001 m).\n\n"
        "- MWD memory data must be imported before generating the LAS file.\n"
    )
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    title = tk.Label(dialog, text="Select Required Input LAS Files", font=UI_TITLE_FONT, bg=UI_BG, fg=UI_FG)
    title.pack(pady=5)
    instructions = ("For each required step size, please select a LAS file that has the corresponding depth step size. "
                    "You cannot continue until all required files are selected.")
    tk.Label(dialog, text=instructions, justify=tk.LEFT, bg=UI_BG, fg=UI_FG, font=UI_FONT, wraplength=700).pack(padx=10, pady=10)
    row_widgets = {}
    def select_file_for_step(step):
        file_path = filedialog.askopenfilename(
            title=f"Select an input LAS file for {step} m step size",
            filetypes=[("LAS files", "*.las"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            las = lasio.read(file_path)
            depths = las.index
            if len(depths) < 2:
                raise ValueError("LAS file does not contain enough depth values for validation.")
            step_size = depths[1] - depths[0]
            if step_size != step:
                messagebox.showerror("Invalid Step Size",
                                     f"Error: The depth step size is {step_size} m instead of {step} m.\n"
                                     f"Please select a file with a {step} m step size.")
                return
            selected_files[step] = file_path
            row_widgets[step]["file_label"].config(text=file_path)
            update_progress(f"Selected valid file for {step} m step: {file_path}")
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading LAS file: {e}\nPlease select a valid file.")
    for step in required_steps:
        row = tk.Frame(dialog, bg=UI_BG)
        row.pack(fill="x", padx=10, pady=5)
        step_label = tk.Label(row, text=f"Input LAS File for {step} m:", font=UI_FONT, bg=UI_BG, fg=UI_FG)
        step_label.pack(side=tk.LEFT)
        file_label = tk.Label(row, text="No file selected", font=UI_FONT, bg=UI_BG, fg=UI_FG, wraplength=400)
        file_label.pack(side=tk.LEFT, padx=10)
        select_button = tk.Button(row, text="Select File", font=UI_FONT, bg=UI_BUTTON_BG, fg=UI_BUTTON_FG,
                                  relief="raised", command=lambda s=step: select_file_for_step(s))
        select_button.pack(side=tk.LEFT, padx=5)
        row_widgets[step] = {"frame": row, "file_label": file_label}
    def submit_selection():
        if any(selected_files[step] is None for step in required_steps):
            messagebox.showerror("Incomplete Selection", "Please select a file for every required step size before submitting.")
        else:
            dialog.destroy()
    def back():
        nonlocal back_pressed
        back_pressed = True
        dialog.destroy()
    button_frame = tk.Frame(dialog, bg=UI_BG)
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Back", command=back,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Submit", font=UI_FONT, bg=UI_BUTTON_BG, fg=UI_BUTTON_FG,
              relief="raised", command=submit_selection).pack(side=tk.LEFT, padx=5)
    parent.wait_window(dialog)
    if back_pressed:
        return "BACK"
    return selected_files

def collect_header_info(parent, update_progress):
    """Step 3: Collect well header information."""
    back_pressed = False
    questions = [
        "Client's company name:",
        "Full well name (including country code, 'NO' f.ex.):",
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
            if question in ["Field Name:", "Rig Name:", "Rig Type:"]:
                ans = ans.upper()
            temp_answers.append(ans)
        if not error_found:
            for i, ans in enumerate(temp_answers):
                entries[i].delete(0, tk.END)
                entries[i].insert(0, ans)
            answers.extend(temp_answers)
            update_progress("Header information collected.")
            dialog.destroy()
    def back():
        nonlocal back_pressed
        back_pressed = True
        dialog.destroy()
    button_frame = tk.Frame(dialog, bg=UI_BG)
    button_frame.pack(pady=5)
    tk.Button(button_frame, text="Back", command=back,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Submit", command=validate_and_submit,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    parent.wait_window(dialog)
    if back_pressed:
        return "BACK"
    return answers

def collect_depth_info(parent, update_progress):
    """Step 4: Collect depth information from user."""
    back_pressed = False
    depth_answers = []
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    dialog_title = tk.Label(dialog, text="Depth Information", font=UI_TITLE_FONT, bg=UI_BG, fg=UI_FG)
    dialog_title.pack(pady=5)
    sample_text_label = tk.Label(dialog, text="This is to identify how to handle the first and last row of the output LAS 1m file. \nIf the actual start depth and TD is different from what is the input file generated from/to, \nthen the first 3 columns of the 1st/last row will remain unchanged, and the rest will be set to -999.25", font=UI_FONT, bg=UI_BG, fg=UI_FG)
    sample_text_label.pack(pady=5)
    frame = tk.Frame(dialog, bg=UI_BG)
    frame.pack(padx=10, pady=10)
    questions = [
        "Actual start depth of the well:",
        "Actual TD of the well:"
    ]
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
        nonlocal depth_answers
        error_found = False
        temp_depth_answers = []
        for lbl in labels:
            lbl.config(fg=UI_FG)
        for idx, question in enumerate(questions):
            raw_input = entries[idx].get().strip()
            processed_input = raw_input.replace(",", ".")
            try:
                value = float(processed_input)
                temp_depth_answers.append(value)
            except ValueError:
                messagebox.showerror("Input Error", f"Please enter a valid number for:\n{question}")
                labels[idx].config(fg="red")
                error_found = True
        if not error_found:
            for idx, value in enumerate(temp_depth_answers):
                entries[idx].delete(0, tk.END)
                entries[idx].insert(0, str(value))
            depth_answers.extend(temp_depth_answers)
            update_progress("Depth information collected.")
            dialog.destroy()
    def back():
        nonlocal back_pressed
        back_pressed = True
        dialog.destroy()
    button_frame = tk.Frame(dialog, bg=UI_BG)
    button_frame.pack(pady=5)
    tk.Button(button_frame, text="Back", command=back,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Submit", command=validate_and_submit,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    parent.wait_window(dialog)
    if back_pressed:
        return "BACK"
    return depth_answers

def select_npd_file(parent, update_progress):
    """Step 5: Handle NPD code file selection. If 'No NPD' is chosen, returns (False, None)."""
    back_pressed = False
    npd_result = None
    dialog = tk.Frame(parent, borderwidth=2, relief="groove", bg=UI_BG)
    dialog.pack(padx=10, pady=10, fill="both", expand=True)
    tk.Label(dialog, text="NPD Codes", font=UI_TITLE_FONT, bg=UI_BG, fg=UI_FG).pack(pady=5)
    tk.Label(dialog, text="If there are NPD codes available for this well, please select the file.\nIf no NPD available, please select 'No NPD'.", font=UI_FONT, bg=UI_BG, fg=UI_FG).pack(pady=5)
    button_frame = tk.Frame(dialog, bg=UI_BG)
    button_frame.pack(pady=5)
    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select NPD Code File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        if file_path:
            if file_path.lower().endswith(('.xlsx', '.xls')):
                try:
                    df = pd.read_excel(file_path)
                    if len(df.columns) != EXPECTED_NPD_COLUMNS:
                        messagebox.showerror("Error", "Excel file must contain exactly two columns. Please check your NPD file and try again.")
                        sys.exit(1)
                    if not all(pd.api.types.is_numeric_dtype(df[col]) for col in df.columns):
                        messagebox.showerror("Error", "Both columns must contain only numbers. Please check your NPD file and try again.")
                        sys.exit(1)
                    npd_data = df.values.tolist()
                    update_progress("NPD file processed successfully.")
                    nonlocal npd_result
                    npd_result = (True, npd_data)
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read Excel file: {str(e)}")
                    sys.exit(1)
            else:
                messagebox.showerror("Error", "File must be an Excel file (.xlsx or .xls)")
    def no_npd():
        nonlocal npd_result
        npd_result = (False, None)
        dialog.destroy()
    def back():
        nonlocal back_pressed
        back_pressed = True
        dialog.destroy()
    tk.Button(button_frame, text="Back", command=back,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Select NPD File", command=select_file,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="No NPD", command=no_npd,
              bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side=tk.LEFT, padx=5)
    parent.wait_window(dialog)
    if back_pressed:
        return "BACK"
    return npd_result if npd_result is not None else (False, None)

def select_output_directories(parent, selected_options):
    """Step 8: Prompt user to select directories for output files."""
    back_pressed = False
    dir_container = tk.Frame(parent, bg=UI_BG)
    dir_container.pack(pady=10, padx=10, fill="x")
    las_dir, ascii_dir = None, None
    if any(opt.startswith('LAS') for opt in selected_options):
        las_frame = tk.Frame(dir_container, bg=UI_BG)
        las_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(las_frame, text="Select Directory for output LAS Files. \nFiles will be named automatically.", bg=UI_BG, fg=UI_FG, font=UI_FONT).pack()
        las_label = tk.Label(las_frame, text="No directory selected", bg=UI_BG, fg=UI_FG, font=UI_FONT)
        las_label.pack()
        def browse_las():
            nonlocal las_dir
            las_dir = filedialog.askdirectory(title="Select Directory for LAS Files")
            if las_dir:
                las_label.config(text=f"LAS Directory: {las_dir}")
                if os.listdir(las_dir):
                    messagebox.showwarning("Warning", "The selected folder contains files. Existing files with the same name may be deleted and replaced.")
        tk.Button(las_frame, text="Browse", command=browse_las, bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT).pack(pady=5)
    if any(opt.startswith('ASCII') for opt in selected_options):
        ascii_frame = tk.Frame(dir_container, bg=UI_BG)
        ascii_frame.pack(pady=10, padx=10, fill="x")
        tk.Label(ascii_frame, text="Select Directory for output ASCII Files. \nFiles will be named automatically.", bg=UI_BG, fg=UI_FG, font=UI_FONT).pack()
        ascii_label = tk.Label(ascii_frame, text="No directory selected", bg=UI_BG, fg=UI_FG, font=UI_FONT)
        ascii_label.pack()
        def browse_ascii():
            nonlocal ascii_dir
            ascii_dir = filedialog.askdirectory(title="Select Directory for ASCII Files")
            if ascii_dir:
                ascii_label.config(text=f"ASCII Directory: {ascii_dir}")
                if os.listdir(ascii_dir):
                    messagebox.showwarning("Warning", "The selected folder contains files. Existing files with the same name may be deleted and replaced.")
        tk.Button(ascii_frame, text="Browse", command=browse_ascii, bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT).pack(pady=5)
    def on_continue():
        if any(opt.startswith('LAS') for opt in selected_options) and not las_dir:
            messagebox.showerror("Error", "Please select a directory for LAS Files.")
            return
        if any(opt.startswith('ASCII') for opt in selected_options) and not ascii_dir:
            messagebox.showerror("Error", "Please select a directory for ASCII Files.")
            return
        dir_container.destroy()
    def on_back():
        nonlocal back_pressed
        back_pressed = True
        dir_container.destroy()
    button_frame = tk.Frame(dir_container, bg=UI_BG)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Back", command=on_back, bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side="left", padx=10)
    tk.Button(button_frame, text="Continue", command=on_continue, bg=UI_BUTTON_BG, fg=UI_BUTTON_FG, font=UI_FONT, relief="raised").pack(side="left", padx=10)
    parent.wait_window(dir_container)
    if back_pressed:
        return "BACK"
    return (las_dir, ascii_dir)

# ----------------- DATA PROCESSING & FILE GENERATION -----------------#
def process_data_buffer(data_buffer0_5, data_buffer1, data_buffer5,
                        curve_index_map, npd_result, update_progress, selected_options):
    """Process the data buffers for 0.5m, 1m, and 5m data."""
    intended_curve_names = [
        "BRVC", "GASX", "MTHA", "ETHA", "PRPA",
        "NBTA", "NPNA", "C1C2", "C1C3", "C1C4", "C1C5", "LITH"
    ]
    def process_single_buffer(data_buffer, curve_index_map, apply_npd=False):
        if data_buffer.size == 0 or data_buffer.shape[1] == 0:
            update_progress("Data buffer is empty; skipping processing for this buffer.")
            return data_buffer
        intended_parameters = {name: curve_index_map[name.upper()]
                               for name in intended_curve_names if name.upper() in curve_index_map}
        if apply_npd and "LITH" in intended_parameters and npd_result is not None:
            has_npd, npd_data = npd_result
            if has_npd and npd_data is not None:
                for depth_val, npd_code in npd_data:
                    mask = (data_buffer[:, 0] == float(depth_val))
                    data_buffer[mask, 39] = float(npd_code)
                update_progress("NPD codes applied to 1m data.")
        if "BRVC" in curve_index_map:
            data_buffer[:, curve_index_map["BRVC"]] /= 1000
            update_progress("Revs per minute – drill bit, cumulative, converted to Krev ( /1000).")
        if "GASX" in curve_index_map:
            data_buffer[:, curve_index_map["GASX"]] = np.vectorize(round_three_decimals)(data_buffer[:, curve_index_map["GASX"]])
            update_progress("Total gas (GASX) values rounded and set to 3 decimal points.")
        def process_ratio(target_mnemonic, numerator_key, denominator_key):
            if (target_mnemonic in curve_index_map and
                    numerator_key in intended_parameters and denominator_key in intended_parameters):
                idx = curve_index_map[target_mnemonic]
                num = data_buffer[:, intended_parameters[numerator_key]]
                denom = data_buffer[:, intended_parameters[denominator_key]]
                mask_invalid = (num == 0) | (denom == 0) | (num == NULL_VALUE) | (denom == NULL_VALUE) | np.isnan(num) | np.isnan(denom)
                ratio = num / denom
                rounded_ratio = np.vectorize(round_two_decimals)(ratio)
                data_buffer[:, idx] = np.where(mask_invalid, NULL_VALUE, rounded_ratio)
        process_ratio("C1C2", "MTHA", "ETHA")
        update_progress("Methane/Ethane (C1/C2) ratio is being processed...\n  Gas ratio format set to 2 decimal points.")
        process_ratio("C1C3", "MTHA", "PRPA")
        update_progress("Methane/Propane (C1/C3) ratio is being processed...\n  Gas ratio format set to 2 decimal points.")
        process_ratio("C1C4", "MTHA", "NBTA")
        update_progress("Methane/Normal Butane (C1/C4) ratio is being processed...\n  Gas ratio format set to 2 decimal points.")
        process_ratio("C1C5", "MTHA", "NPNA")
        update_progress("Methane/Normal Pentane (C1/C5) ratio is being processed...\n  Gas ratio format set to 2 decimal points.")
        return data_buffer
    data_half_meter = process_single_buffer(data_buffer0_5, curve_index_map, apply_npd=False)
    data_five_meter = process_single_buffer(data_buffer5, curve_index_map, apply_npd=False)

    # For 1m, create two versions:
    # Always process the 1m data if available
    if data_buffer1 is not None:
        data_one_meter_las = process_single_buffer(data_buffer1.copy(), curve_index_map, apply_npd=True)
        data_one_meter_ascii = process_single_buffer(data_buffer1.copy(), curve_index_map, apply_npd=False)
    else:
        data_one_meter_las = np.empty((0, 0))  # Empty array instead of None
        data_one_meter_ascii = np.empty((0, 0))  # Empty array instead of None




    return data_half_meter, data_one_meter_las, data_one_meter_ascii, data_five_meter

def format_data(data_subset, las, use_ascii_delimiter=False, ascii_output=False):
    """Format data rows."""
    formatted_lines = []
    COLUMN_WIDTHS = [9, 11, 12, 11, 11, 11, 11, 11, 11, 13, 13, 11, 11, 13, 11, 13, 13, 12, 12, 13, 11, 11, 12, 11, 13, 15, 11, 11, 11, 11, 11, 11, 11, 11, 11, 16, 16, 16, 16, 16, 11, 11, 11, 11]
    ASCII_COLUMN_WIDTHS = [10, 11, 12, 11, 11, 11, 11, 11, 11, 13, 13, 11, 11, 13, 11, 13, 13, 12, 12, 13, 11, 11, 12, 11, 13, 15, 11, 11, 11, 11, 11, 11, 11, 11, 11, 16, 16, 16, 16, 16, 11, 11, 11, 11]
    widths = ASCII_COLUMN_WIDTHS if ascii_output else COLUMN_WIDTHS
    for row in data_subset:
        formatted_row = []
        for j, value in enumerate(row):
            mnemonic = las[j].mnemonic.upper()
            if value == NULL_VALUE or np.isnan(value):
                formatted_value = str(NULL_VALUE)
            else:
                if mnemonic == "DXC":
                    formatted_value = f"{value:.5f}"
                elif mnemonic in ["GASX", "MDIA", "MDOA", "ECDT", "BDTI", "BDDI", "BRVC", "LITH"]:
                    formatted_value = f"{value:.3f}"
                elif mnemonic in ["C1C2", "C1C3", "C1C4", "C1C5", "Depth", "DVER", "ROPA", "TQA", "TQX", "TVA", "MFIA", "TCTI", "BDIA"]:
                    formatted_value = f"{value:.2f}"
                elif mnemonic in ["HKLA", "HKLX", "WOBA", "SPPA", "MTIA", "MTOA"]:
                    formatted_value = f"{value:.1f}"
                elif mnemonic in ["RPMA", "RPMB", "HSX", "MTHA", "ETHA", "PRPA", "IBTA", "NBTA", "IPNA", "NPNA"]:
                    formatted_value = f"{value:.0f}"
                else:
                    formatted_value = f"{value:.2f}"
            formatted_row.append(formatted_value)
        if use_ascii_delimiter:
            formatted_line = ASCII_SEPARATOR.join(formatted_row)
        else:
            if ascii_output:
                formatted_line = formatted_row[0].rjust(widths[0]) + "".join(
                    f"\t{v:>{widths[i] - 1}}" for i, v in enumerate(formatted_row[1:], start=1)
                )
            else:
                formatted_line = "".join(f"{v:>{widths[i]}}" for i, v in enumerate(formatted_row))

        formatted_lines.append(formatted_line + "\n")
    return formatted_lines

def update_step_header(header_lines, step_value):
    """Update the STEP value in the LAS header."""
    return [line.replace("XX", f"{step_value:.1f}", 1) if line.strip().startswith("STEP") else line for line in header_lines]

def generate_output_files(selected_options, las_dir, ascii_dir, data_buffer, data_one_meter_las, data_one_meter_ascii, data_five_meter, las,
                          modified_header_lines0_5, modified_header_lines1, modified_header_lines5, update_progress):
    """Generate selected output files."""
    update_progress("Output files are being processed and saved...")
    for option in selected_options:
        if option.startswith("LAS") and las_dir:
            if "0.5m" in option:
                step, step_name, data_subset = 0.5, "0.5m", data_buffer
                header_lines = modified_header_lines0_5
                update_progress("LAS 0.5m components prepared for generation\n Please wait...")
                use_delimiter = False
            elif "1m" in option:
                # Fix: Define step, step_name, and header_lines for LAS 1m
                step, step_name, data_subset = 1.0, "1m", data_one_meter_las
                header_lines = modified_header_lines1
                update_progress("LAS 1m components prepared for generation\n Please wait...")
                use_delimiter = True
            elif "5m" in option:
                step, step_name, data_subset = 5.0, "5m", data_five_meter
                header_lines = modified_header_lines5
                update_progress("LAS 5m components prepared for generation\n Please wait...")
                use_delimiter = False
            else:
                continue
            las_header = update_step_header(header_lines.copy(), step)
            formatted_data = format_data(data_subset, las, use_ascii_delimiter=use_delimiter, ascii_output=False)
            if formatted_data:
                formatted_data[-1] = formatted_data[-1].rstrip("\n")
            content = las_header + formatted_data
            filename = f"MUD_LOG_{step_name}.las"
            save_path = os.path.join(las_dir, filename)
            try:
                with open(save_path, 'w', encoding="utf-8") as f:
                    f.writelines(content)
                update_progress(f"{filename} generated and saved successfully.")
            except Exception as e:
                update_progress(f"Error saving {filename}: {e}")

        elif option.startswith("ASCII") and ascii_dir:
            if "0.5m" in option:
                data_subset = data_buffer
                step_name = "0.5m"
                update_progress("ASCII 0.5 components prepared for generation\n Please wait...")
            elif "1m" in option:
                data_subset = data_one_meter_ascii
                step_name = "1m"  # Fix: Assign step_name for ASCII 1m
                update_progress("ASCII 1m components prepared for generation\n Please wait...")
            elif "5m" in option:
                data_subset = data_five_meter
                step_name = "5m"
                update_progress("ASCII 5m components prepared for generation\n Please wait...")
            else:
                continue
            ascii_header = [ASCII_HEADER]
            formatted_data = format_data(data_subset, las, use_ascii_delimiter=False, ascii_output=True)
            if formatted_data:
                formatted_data[-1] = formatted_data[-1].rstrip("\n")
            content = ascii_header + formatted_data
            filename = f"MUD_LOG_{step_name}.asc"
            save_path = os.path.join(ascii_dir, filename)
            try:
                with open(save_path, 'w') as f:
                    f.writelines(content)
                update_progress(f"{filename} generated and saved successfully.")
            except Exception as e:
                update_progress(f"Error saving {filename}: {e}")


# ----------------- MAIN FUNCTION WITH STEP NAVIGATION -----------------#
def main():
    root = tk.Tk()
    root.title("EOWR LAS/ASCII Generator")
    root.configure(bg=UI_BG)
    def on_closing():
        root.destroy()
        os._exit(0)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    paned = tk.PanedWindow(root, orient=tk.VERTICAL, bg=UI_BG)
    paned.pack(fill=tk.BOTH, expand=True)
    workflow_frame = tk.Frame(paned, bg=UI_BG)
    paned.add(workflow_frame, stretch="always")
    progress_frame = tk.Frame(paned, height=150, bg=UI_BG)
    paned.add(progress_frame)
    progress_text = tk.Text(progress_frame, height=8, font=UI_FONT, bg="white", fg=UI_FG)
    progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    left_label = tk.Label(progress_frame, text="SLB WCM, Geoservices", font=("Arial", 8), fg="grey", bg=UI_BG)
    left_label.pack(side=tk.LEFT, padx=5, pady=2)
    watermark_label = tk.Label(progress_frame, text="Developed by Faraz Zand", font=("Arial", 8), fg="grey", bg=UI_BG)
    watermark_label.pack(side=tk.BOTTOM, anchor="e", padx=5, pady=2)
    def update_progress(message):
        progress_text.insert(tk.END, message + "\n")
        progress_text.see(tk.END)
        root.update_idletasks()
    update_progress("Application started.")
    results = {}

    # Helper function to reset results from a given step
    def reset_results_from(step):
        keys_by_step = {
            1: ['selected_options', 'selected_files', 'las_data_buffers', 'curve_index_map', 'las_object', 'header_answers', 'actual_depths', 'npd_result', 'data_half_meter', 'data_one_meter', 'data_five_meter', 'modified_header_lines0_5', 'modified_header_lines1', 'modified_header_lines5', 'las_dir', 'ascii_dir'],
            2: ['selected_files', 'las_data_buffers', 'curve_index_map', 'las_object', 'header_answers', 'actual_depths', 'npd_result', 'data_half_meter', 'data_one_meter', 'data_five_meter', 'modified_header_lines0_5', 'modified_header_lines1', 'modified_header_lines5', 'las_dir', 'ascii_dir'],
            3: ['header_answers', 'actual_depths', 'npd_result', 'data_half_meter', 'data_one_meter', 'data_five_meter', 'modified_header_lines0_5', 'modified_header_lines1', 'modified_header_lines5', 'las_dir', 'ascii_dir'],
            4: ['actual_depths', 'npd_result', 'data_half_meter', 'data_one_meter', 'data_five_meter', 'modified_header_lines0_5', 'modified_header_lines1', 'modified_header_lines5', 'las_dir', 'ascii_dir'],
            5: ['npd_result', 'data_half_meter', 'data_one_meter', 'data_five_meter', 'modified_header_lines0_5', 'modified_header_lines1', 'modified_header_lines5', 'las_dir', 'ascii_dir'],
            6: ['data_half_meter', 'data_one_meter', 'data_five_meter', 'modified_header_lines0_5', 'modified_header_lines1', 'modified_header_lines5', 'las_dir', 'ascii_dir'],
            7: ['modified_header_lines0_5', 'modified_header_lines1', 'modified_header_lines5', 'las_dir', 'ascii_dir'],
            8: ['las_dir', 'ascii_dir']
        }
        for key in keys_by_step.get(step, []):
            if key in results:
                del results[key]

    step = 1
    while True:
        if step == 1:
            selected_options = select_output_options(workflow_frame, update_progress)
            results['selected_options'] = selected_options
            step = 2
        elif step == 2:
            selected_files = select_las_file(workflow_frame, update_progress, results['selected_options'])
            if selected_files == "BACK":
                reset_results_from(2)
                step = 1
                continue
            results['selected_files'] = selected_files
            las_data_buffers = {}
            counter = 0
            las_object = None
            for s, file_path in selected_files.items():
                try:
                    las = lasio.read(file_path)
                    las_data_buffers[s] = np.array(las.data.copy())
                    update_progress(f"LAS input file for {s} m imported.")
                    if counter == 0:
                        curve_index_map = {curve.mnemonic.upper(): idx for idx, curve in enumerate(las.curves)}
                        las_object = las
                        counter += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read LAS file for {s} m.\nError: {str(e)}")
                    sys.exit(1)
            results['las_data_buffers'] = las_data_buffers
            results['curve_index_map'] = curve_index_map
            results['las_object'] = las_object
            step = 3
        elif step == 3:
            header_answers = collect_header_info(workflow_frame, update_progress)
            if header_answers == "BACK":
                reset_results_from(3)
                step = 2
                continue
            results['header_answers'] = header_answers
            step = 4
        elif step == 4:
            if "LAS 1m" in results['selected_options']:
                actual_depths = collect_depth_info(workflow_frame, update_progress)
                if actual_depths == "BACK":
                    reset_results_from(4)
                    step = 3
                    continue
                results['actual_depths'] = actual_depths
            else:
                results['actual_depths'] = None
            step = 5

        elif step == 5:
            if "LAS 1m" in results['selected_options']:
                npd_result = select_npd_file(workflow_frame, update_progress)
                if npd_result == "BACK":
                    reset_results_from(5)
                    step = 4
                    continue
                results['npd_result'] = npd_result
            else:
                results['npd_result'] = (False, None)
            step = 6
        elif step == 6:
            # Use fresh copies of the raw data for processing
            db0_5 = results['las_data_buffers'].get(0.5, np.empty((0,0))).copy()
            db1 = results['las_data_buffers'].get(1.0, np.empty((0,0))).copy()
            db5 = results['las_data_buffers'].get(5.0, np.empty((0,0))).copy()
            data_half_meter, data_one_meter_las, data_one_meter_ascii, data_five_meter = process_data_buffer(
                db0_5, db1, db5,
                results['curve_index_map'], results['npd_result'], update_progress,
                results['selected_options']
            )
            if results['actual_depths'] is not None and data_one_meter_las is not None:
                if data_one_meter_las.shape[0] > 0 and data_one_meter_las[-1, 0] > float(results['actual_depths'][1]):
                    update_progress("Detected: Last row of 1m LAS depth > actual TD")
                    data_one_meter_las[-1, 3:] = NULL_VALUE
                if data_one_meter_las.shape[0] > 0 and data_one_meter_las[0, 0] < float(results['actual_depths'][0]):
                    update_progress("Detected: First row of 1m LAS depth < actual start depth")
                    data_one_meter_las[0, 3:] = NULL_VALUE

            results['data_half_meter'] = data_half_meter
            results['data_one_meter_las'] = data_one_meter_las
            results['data_one_meter_ascii'] = data_one_meter_ascii
            if "LAS 1m" in results['selected_options']:
                results['data_one_meter'] = data_one_meter_las  # Assign LAS version (with NPD codes & depth fix)
            elif "ASCII 1m" in results['selected_options']:
                results['data_one_meter'] = data_one_meter_ascii  # Assign ASCII version (without NPD codes)
            else:
                results['data_one_meter'] = None  # Avoids errors if neither is selected
            results['data_five_meter'] = data_five_meter
            step = 7
        elif step == 7:
            today = datetime.now()
            date_string = today.strftime("%m/%d/%Y")
            if "LAS 0.5m" in results['selected_options']:
                field_mapping0_5 = {
                    "COMP": results['header_answers'][0], "WELL": results['header_answers'][1],
                    "STRT": str(results['las_data_buffers'][0.5][0, 0]), "STOP": str(results['las_data_buffers'][0.5][-1, 0]),
                    "FLD": results['header_answers'][2], "RIGN": results['header_answers'][3],
                    "RIGTYP": results['header_answers'][4], "CREA.": date_string
                }
                header_lines0_5 = HEADER_TEMPLATE.splitlines(keepends=True)
                modified_header_lines0_5 = header_lines0_5.copy()
                for field, new_value in field_mapping0_5.items():
                    for i, line in enumerate(modified_header_lines0_5):
                        if field in line.split():
                            padded_value = new_value + " " * (20 - len(new_value)) if len(new_value) < 21 else new_value + " "
                            modified_header_lines0_5[i] = line.replace("XX", padded_value, 1)
                            break
                results['modified_header_lines0_5'] = modified_header_lines0_5
            else:
                results['modified_header_lines0_5'] = None
            if "LAS 1m" in results['selected_options']:
                field_mapping1 = {
                    "COMP": results['header_answers'][0], "WELL": results['header_answers'][1],
                    "STRT": str(results['las_data_buffers'][1.0][0, 0]), "STOP": str(results['las_data_buffers'][1.0][-1, 0]),
                    "FLD": results['header_answers'][2], "RIGN": results['header_answers'][3],
                    "RIGTYP": results['header_answers'][4], "CREA.": date_string
                }
                header_lines1 = HEADER_TEMPLATE.splitlines(keepends=True)
                modified_header_lines1 = header_lines1.copy()
                for field, new_value in field_mapping1.items():
                    for i, line in enumerate(modified_header_lines1):
                        if field in line.split():
                            padded_value = new_value + " " * (20 - len(new_value)) if len(new_value) < 21 else new_value + " "
                            modified_header_lines1[i] = line.replace("XX", padded_value, 1)
                            break
                results['modified_header_lines1'] = modified_header_lines1
            else:
                results['modified_header_lines1'] = None
            if "LAS 5m" in results['selected_options']:
                field_mapping5 = {
                    "COMP": results['header_answers'][0], "WELL": results['header_answers'][1],
                    "STRT": str(results['las_data_buffers'][5.0][0, 0]), "STOP": str(results['las_data_buffers'][5.0][-1, 0]),
                    "FLD": results['header_answers'][2], "RIGN": results['header_answers'][3],
                    "RIGTYP": results['header_answers'][4], "CREA.": date_string
                }
                header_lines5 = HEADER_TEMPLATE.splitlines(keepends=True)
                modified_header_lines5 = header_lines5.copy()
                for field, new_value in field_mapping5.items():
                    for i, line in enumerate(modified_header_lines5):
                        if field in line.split():
                            padded_value = new_value + " " * (20 - len(new_value)) if len(new_value) < 21 else new_value + " "
                            modified_header_lines5[i] = line.replace("XX", padded_value, 1)
                            break
                results['modified_header_lines5'] = modified_header_lines5
            else:
                results['modified_header_lines5'] = None
            step = 8
        elif step == 8:
            output_dirs = select_output_directories(workflow_frame, results['selected_options'])
            if output_dirs == "BACK":
                reset_results_from(8)
                step = 5 if "LAS 1m" in results['selected_options'] else 3
                continue
            results['las_dir'], results['ascii_dir'] = output_dirs
            step = 9
        elif step == 9:
            generate_output_files(results['selected_options'], results['las_dir'], results['ascii_dir'],
                                  results['data_half_meter'], results['data_one_meter_las'], results['data_one_meter_ascii'], results['data_five_meter'],
                                  results['las_object'].curves, results['modified_header_lines0_5'],
                                  results['modified_header_lines1'], results['modified_header_lines5'], update_progress)

            update_progress("LAS/ASCII Processing completed. Please find the output file(s) in the selected path(s). \n Click 'Close' to exit.")
            close_button = tk.Button(workflow_frame, text="Close", font=("Arial", 12, "bold"),
                                       bg=UI_BUTTON_BG, fg=UI_BUTTON_FG,
                                       command=lambda: (root.destroy(), sys.exit(0)))
            close_button.pack(pady=20)
            break
    root.mainloop()

if __name__ == "__main__":
    main()
