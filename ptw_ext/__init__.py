import itertools
import numpy as np
from pathlib import Path
import pandas as pd


ptw_column_names = ['Worklist', 'Date', 'TreatmentUnit', 'Modality', 'Energy[MV/MeV]', 'Fieldsize[mm]', 'SDD[mm]', 'Gantry[deg]', 'Wedge[deg]', 'MU', 
                    'CAX', 'G10', 'L10', 'T10', 'R10', 'G20', 'L20', 'T20', 'R20', 'E1', 'E2', 'E3', 'E4', 
                    'Temp', 'Pressure', 'CAXRate', 'ExpTime', 'CAX_normed', 'Flatness', 'SymmetryGT', 'SymmetryLR', 'BQF', 'Wedge']

ptw_plotting_limits = {
    'CAX_normed': [95, 105, 100],
    'Flatness': [95, 105, 100],
    'SymmetryGT': [95, 105, 100],
    'SymmetryLR': [95, 105, 100],
    'BQF': [7.5, 8.5, 8],
}


def parse_qa_data_io(f):
    num_skip_rows = 5
    head_row_number = 2
    results = []

    lines = f.readlines()
    heads = lines[head_row_number].split(';')

    float_column_numbers = itertools.chain(range(37, 54), range(54, 66, 2))
    float_column_numbers = list(float_column_numbers)
    column_numbers = itertools.chain(range(3), range(4, 11), range(37, 54), range(54, 66, 2))
    column_numbers = list(column_numbers)
    # column_names = []
    # for i in column_numbers:
    #     column_names.append(heads[i])

    column_names = ptw_column_names

    print(column_names)
    for line_number, line in enumerate(lines):
        if line_number < num_skip_rows:
            continue
        values = []
        raw_values = line.split(';')
        for i in column_numbers:
            if i in float_column_numbers:
                values.append(float(raw_values[i]))
            else:
                values.append(raw_values[i])
        results.append(values)

    results = pd.DataFrame(results, columns=column_names)
    results['Date'] = pd.to_datetime(results['Date'])
    
    return results


def parse_qa_data(filename):
    num_skip_rows = 5
    head_row_number = 2
    results = []
    with open(filename) as f:
        lines = f.readlines()

    heads = lines[head_row_number].split(';')

    float_column_numbers = itertools.chain(range(37, 54), range(54, 66, 2))
    float_column_numbers = list(float_column_numbers)
    column_numbers = itertools.chain(range(3), range(4, 11), range(37, 54), range(54, 66, 2))
    column_numbers = list(column_numbers)
    column_names = []
    for i in column_numbers:
        column_names.append(heads[i])

    print(column_names)
    for line_number, line in enumerate(lines):
        if line_number < num_skip_rows:
            continue
        values = []
        raw_values = line.split(';')
        for i in column_numbers:
            if i in float_column_numbers:
                values.append(float(raw_values[i]))
            else:
                values.append(raw_values[i])
        results.append(values)

    results = pd.DataFrame(results, columns=column_names)
    results['Date'] = pd.to_datetime(results['Date'])
    
    return results