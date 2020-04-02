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
from functions import generate_dict_formula, generate_rapport_incoherence_genre_wide, generate_rapport_incoherence_long
from functions import add_incoherence_metrics_to_df
# Set the logger
logging.basicConfig(filename="incoherence_report.log", level=logging.INFO)


if __name__ == "__main__":
    # Set the directory paths

    input_folder_path = sys.argv[1]
    output_folder_path = sys.argv[2]
    date = sys.argv[3]

    list_expected_files = ["sursaud-covid19-quotidien",
                           "sursaud-covid19-hebdomadaire",
                           "donnees-hospitalieres-covid19",
                           "donnees-hospitalieres-etablissements-covid19"]


    list_files = os.listdir(input_folder_path)

    # =============================================================================
    # data sursaud covid quot
    # =============================================================================
    file_name_short = "sursaud-covid19-quotidien"
    try:
        file = [x for x in list_files if file_name_short in x][0]
    except:
        print("File corresponding to {} not found".format(file_name_short))

    print("processing file sursaud-covid19-quotidien")

    df = pd.read_excel(os.path.join(input_folder_path, file))
    list_cols = list(df.columns)
    df["numero_ligne"] = df.index + 1
    df = df[["numero_ligne"] + list_cols]

    # save dataframe for second report on classe d'âge
    df0 = df.copy(deep = True)

    list_dict_formules = generate_dict_formula(df)
    path = output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)
    res, sub_df = generate_rapport_incoherence_genre_wide(df, list_dict_formules, path, write = False)

    var_groupby = ["dep", "date_de_passage"]
    res2, sub_df2 = generate_rapport_incoherence_long(df0, var_groupby, path, write = False)

    writer = pd.ExcelWriter(path)
    res.to_excel(writer, 'synthese_genre', index=False)
    sub_df.to_excel(writer, 'lignes_erreur_genre', index=False)
    res2.to_excel(writer, 'synthese_cl_age', index=False)
    sub_df2.to_excel(writer, 'lignes_cl_age', index=False)
    writer.save()

    # =============================================================================
    # data covid hospit hebdo
    # =============================================================================

    file_name_short = "sursaud-covid19-hebdomadaire"
    try:
        file = [x for x in list_files if file_name_short in x][0]
    except:
        print("File corresponding to {} not found".format(file_name_short))

    print("processing file sursaud-covid19-hebdomadaire")

    df0 = pd.read_csv(os.path.join(input_folder_path, file), sep = ";")
    list_cols = list(df0.columns)
    df0["numero_ligne"] = df0.index + 1
    df0 = df0[["numero_ligne"] + list_cols]

    var_groupby = ["dep", "semaine"]
    path =  output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)
    res, sub_df = generate_rapport_incoherence_long(df0, var_groupby, path)


    # =============================================================================
    # data covid hospit
    # =============================================================================

    file_name_short = "donnees-hospitalieres-covid19"
    try:
        file = [x for x in list_files if file_name_short in x][0]
    except:
        print("File corresponding to {} not found".format(file_name_short))

    print("processing file {}".format(file_name_short))

    df = pd.read_csv(os.path.join(input_folder_path, file), sep = ";")
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

    path = output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)

    var_groupby = ["dep", "jour"]
    res, sub_df = generate_rapport_incoherence_long_hosp(df0, var_groupby, path, write = True)


    # =============================================================================
    # data covid hospit
    # =============================================================================

    file_name_short = "donnees-hospitalieres-etablissements-covid19"
    try:
        file = [x for x in list_files if file_name_short in x][0]
    except:
        print("File corresponding to {} not found".format(file_name_short))

    print("processing file {}".format(file_name_short))
    hosp_cum = pd.read_csv(input_folder_path + file, sep = ";")

    hosp_cum = pd.read_csv(input_folder_path + file, sep=";")
    list_cols = list(hosp_cum.columns)
    # hosp_cum.sort_values(by = ["dep", "jour"], inplace = True)

    hosp_cum["numero_ligne"] = [x for x in range(1, len(hosp_cum) + 1)]

    hosp_cum = hosp_cum[["numero_ligne"] + list_cols]

    hosp_cum["jour"] = pd.to_datetime(hosp_cum["jour"])
    hosp_cum["nb_lag"] = hosp_cum.groupby("dep")["nb"].shift(1)
    hosp_cum["diff"] = hosp_cum["nb"] - hosp_cum["nb_lag"]

    hosp_cum.sort_values(by=["dep", "jour"], inplace=True)
    hosp_cum["id"] = [x for x in range(1, len(hosp_cum) + 1)]

    sub_df = hosp_cum.loc[hosp_cum["diff"] < 0]
    sub_df2 = hosp_cum[hosp_cum.id.isin([x - 1 for x in sub_df.id.values])]

    sub_df_concat = pd.concat([sub_df, sub_df2], sort=True)
    sub_df_concat.sort_values(by="id", inplace=True)
    sub_df_concat.drop("id", axis=1, inplace=True)

    path = output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)

    res = pd.DataFrame({"Metrique": ["Nombre de lignes total", "Nombre de lignes avec incohérence"],
                        "Nombre": [len(hosp_cum), len(sub_df)]})

    writer = pd.ExcelWriter(path)
    res.to_excel(writer, 'synthese', index=False)
    sub_df_concat.to_excel(writer, 'lignes_erreur', index=False)
    writer.save()




