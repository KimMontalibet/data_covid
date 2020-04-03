#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# This script generates the incoherence report for the covid data
# data can be found on data gouv
# https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/
# https://www.data.gouv.fr/fr/datasets/donnees-des-urgences-hospitalieres-et-de-sos-medecins-relatives-a-lepidemie-de-covid-19/
# =============================================================================

# Import standard libraries
import sys
import logging
import pandas as pd
import os

# Import additional library for loading bar
from utils import generate_dict_formula, generate_rapport_incoherence_genre_wide, generate_rapport_incoherence_long
# Set the logger
logging.basicConfig(filename="./logs/incoherence_report.log", level=logging.INFO)


if __name__ == "__main__":

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
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} not found".format(e, file_name_short))
        file = None

    if file:
        logging.info("processing file {}".format(file_name_short))

        df = pd.read_excel(os.path.join(input_folder_path, file))
        #df = pd.read_csv(os.path.join(input_folder_path, file), sep = ",")
        list_cols = list(df.columns)
        df["numero_ligne"] = df.index + 1
        df = df[["numero_ligne"] + list_cols]

        # save dataframe for second report on classe d'âge
        df0 = df.copy(deep = True)

        list_dict_formules = generate_dict_formula(df)
        path = output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)
        res, sub_df = generate_rapport_incoherence_genre_wide(df, list_dict_formules, path, write = False)

        var_groupby = ["dep", "date_de_passage"]
        res2, sub_df2 = generate_rapport_incoherence_long(df0, "sursaud_cl_age_corona", var_groupby, path, write = False)

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
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} not found".format(e, file_name_short))
        file = None

    if file:
        logging.info("processing file {}".format(file_name_short))

        df0 = pd.read_csv(os.path.join(input_folder_path, file), sep = ";")
        list_cols = list(df0.columns)
        df0["numero_ligne"] = df0.index + 1
        df0 = df0[["numero_ligne"] + list_cols]

        var_groupby = ["dep", "semaine"]
        path =  output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)
        res, sub_df = generate_rapport_incoherence_long(df0, "sursaud_cl_age_corona", var_groupby, path)


    # =============================================================================
    # data covid hospit
    # =============================================================================

    file_name_short = "donnees-hospitalieres-covid19"
    try:
        file = [x for x in list_files if file_name_short in x][0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} not found".format(e, file_name_short))
        file = None

    if file:
        logging.info("processing file {}".format(file_name_short))

        df = pd.read_csv(os.path.join(input_folder_path, file), sep = ";")
        list_cols = list(df.columns)
        df["numero_ligne"] = df.index + 1
        df = df[["numero_ligne"] + list_cols]
        # save dataframe for second report on classe d'âge
        df0 = df.copy(deep = True)

        path = output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)

        var_groupby = ["dep", "jour"]
        res, sub_df = generate_rapport_incoherence_long(df0, "sexe", var_groupby, path, write = True)


    # =============================================================================
    # data covid hospit
    # =============================================================================

    file_name_short = "donnees-hospitalieres-etablissements-covid19"
    try:
        file = [x for x in list_files if file_name_short in x][0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} not found".format(e, file_name_short))
        file = None

    if file:
        logging.info("processing file {}".format(file_name_short))
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


    # =============================================================================
    # covid trois laba quot
    # =============================================================================

    file_name_short = "covid_troislabo_quot"
    try:
        file = [x for x in list_files if file_name_short in x][0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} not found".format(e, file_name_short))
        file = None

    if file:
        logging.info("processing file {}".format(file_name_short))
        df = pd.read_csv(input_folder_path + file, sep = ";")

        list_cols = list(df.columns)
        df["numero_ligne"] = df.index + 1
        df = df[["numero_ligne"] + list_cols]

        # save dataframe for second report on classe d'âge
        df0 = df.copy(deep = True)

        list_dict_formules = generate_dict_formula(df)
        path = output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)
        res, sub_df = generate_rapport_incoherence_genre_wide(df, list_dict_formules, path, write = False)

        var_groupby = ["dep", "jour"]
        res2, sub_df2 = generate_rapport_incoherence_long(df0, "clage_covid", var_groupby, path, write = False)

        writer = pd.ExcelWriter(path)
        res.to_excel(writer, 'synthese_genre', index=False)
        sub_df.to_excel(writer, 'lignes_erreur_genre', index=False)
        res2.to_excel(writer, 'synthese_cl_age', index=False)
        sub_df2.to_excel(writer, 'lignes_cl_age', index=False)
        writer.save()


        # =============================================================================
        # covid trois laba heb
        # =============================================================================

        file_name_short = "covid_troislabo_heb"
        try:
            file = [x for x in list_files if file_name_short in x][0]
        except Exception as e:
            logging.warning("Error : {0}. File corresponding to {1} not found".format(e, file_name_short))
            file = None

        if file:
            logging.info("processing file {}".format(file_name_short))
            df = pd.read_csv(input_folder_path + file, sep=";")

            list_cols = list(df.columns)
            df["numero_ligne"] = df.index + 1
            df = df[["numero_ligne"] + list_cols]

            # save dataframe for second report on classe d'âge
            df0 = df.copy(deep=True)

            list_dict_formules = generate_dict_formula(df)
            path = output_folder_path + "{0}_incoherence_{1}.xlsx".format(file_name_short, date)
            res, sub_df = generate_rapport_incoherence_genre_wide(df, list_dict_formules, path, write=False)

            var_groupby = ["dep", "week"]
            res2, sub_df2 = generate_rapport_incoherence_long(df0, "clage_covid", var_groupby, path, write=False)

            writer = pd.ExcelWriter(path)
            res.to_excel(writer, 'synthese_genre', index=False)
            sub_df.to_excel(writer, 'lignes_erreur_genre', index=False)
            res2.to_excel(writer, 'synthese_cl_age', index=False)
            sub_df2.to_excel(writer, 'lignes_cl_age', index=False)
            writer.save()
