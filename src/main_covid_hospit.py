#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# This scripts generate the incoherence report for the covid data
# =============================================================================



# Import standard libraries
import sys
import logging
import pandas as pd
import numpy as np
import xlrd
import openpyxl
import os

# Import additional library for loading bar
from functions import generate_dict_formula, add_incoherence_metrics_to_df

# Set the logger
logging.basicConfig(filename="incoherence_report.log", level=logging.INFO)


if __name__ == "__main__":
    # Set the directory paths

    input_folder_path = sys.argv[1]
    output_folder_path = sys.argv[2]
    date = sys.argv[3]
    file_name_extension = sys.argv[4]
    df = pd.read_csv(os.path.join(input_folder_path, file_name_extension), sep = ";")
    list_cols = list(df.columns)
    df["numero_ligne"] = df.index + 1
    df = df[["numero_ligne"] + list_cols]

    # save dataframe for second report on classe d'âge
    df0 = df.copy(deep = True)


    def generate_rapport_incoherence_long_hosp(df0, var_groupby, path, write=True):
        df_tot = df0[df0.sexe == 0]
        df_cl = df0[df0.sexe != 0]
        list_var = [x for x in df0.dtypes[df0.dtypes != "object"].index if x not in ["numero_ligne", "sexe"]]
        df_agg = df_cl.groupby(var_groupby)[list_var].apply(lambda x: x.sum(min_count=1)).reset_index()
        df_agg.columns = var_groupby + [x + "_sum" for x in list_var]
        df = pd.merge(df_tot, df_agg, on=var_groupby)
        list_dict_formules = [{"total": x, "list_variable_somme": [x + "_sum"]} for x in list_var]
        df = add_incoherence_metrics_to_df(df, list_dict_formules)

        sub_df = df.loc[(df['sum_test'] > 0)]

        nb_ligne_err = len(sub_df)
        nb_ligne_total = len(df0)

        list_metriques = ["Nombre total de lignes", "Lignes avec une erreur de cohérence"] + \
                         ["Lignes avec une erreur de cohérence pour la variable " + x for x in list_var]

        # colonnes: Nombre, Moyenne différence, Min diff, Max diff
        list_test_var = [x for x in df.columns if x[:5] == "test_"]
        list_diff_var = [x for x in df.columns if x[:5] == "diff_"]
        list_nombre = [nb_ligne_total, nb_ligne_err] + list(sub_df[list_test_var].sum().values)
        list_moyenne_diff = [np.nan, np.nan] + list(sub_df[list_diff_var].replace(0, np.nan).mean().values)
        list_min_diff = [np.nan, np.nan] + list(sub_df[list_diff_var].replace(0, np.nan).min().values)
        list_max_diff = [np.nan, np.nan] + list(sub_df[list_diff_var].replace(0, np.nan).max().values)

        res = pd.DataFrame({"Metrique": list_metriques,
                            "Nombre de lignes": list_nombre,
                            "% de Lignes": [x * 100 / nb_ligne_total for x in list_nombre],
                            "Moyenne de la différence": list_moyenne_diff,
                            "Min de la différence": list_min_diff,
                            "Max de la différence": list_max_diff})



        sub_df2 = pd.merge(sub_df[var_groupby], df_cl, on=var_groupby)
        sub_df_concat = pd.concat([sub_df, sub_df2], sort=False)
        sub_df_concat = sub_df_concat.sort_values(by="numero_ligne")

        if write:
            writer = pd.ExcelWriter(path)
            res.to_excel(writer, 'synthese', index=False)
            sub_df_concat.to_excel(writer, 'lignes_erreur', index=False)
            writer.save()

        return res, sub_df_concat

    path = output_folder_path + "covid_hospit_{}.xlsx".format(date)

    var_groupby = ["dep", "jour"]
    res, sub_df = generate_rapport_incoherence_long_hosp(df0, var_groupby, path, write = True)






