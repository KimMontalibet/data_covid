#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# This scripts runs generate the incoherence report for the covid data
# =============================================================================

# Import standard libraries
import sys
import logging
import pandas as pd
import xlrd
import openpyxl
import os

# Import additional library for loading bar
from functions import generate_dict_formula, generate_rapport_incoherence

# Set the logger
logging.basicConfig(filename="incoherence_report.log", level=logging.INFO)


if __name__ == "__main__":
    # Set the directory paths

    input_folder_path = sys.argv[1]
    output_folder_path = sys.argv[2]
    date = sys.argv[3]
    file_name_extension = sys.argv[4]
    df = pd.read_excel(os.path.join(input_folder_path, file_name_extension))
    list_cols = list(df.columns)
    df["numero_ligne"] = df.index + 1
    df = df[["numero_ligne"] + list_cols]
    df = df[df.sursaud_cl_age_corona == "0"]

    list_dict_formules = generate_dict_formula(df)
    path = output_folder_path + "sursaud_corona_quot_coherence_{}.xlsx".format(date)
    res, sub_df = generate_rapport_incoherence(df, list_dict_formules, date, path)








