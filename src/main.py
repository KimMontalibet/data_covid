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
import ssl
from urllib.request import urlopen



# Import additional library for loading bar
from utils import generate_dict_formula, generate_rapport_incoherence_genre_wide, generate_rapport_incoherence_long
# Set the logger
logging.basicConfig(filename="./logs/incoherence_report.log", level=logging.INFO)


if __name__ == "__main__":

    #output_folder_path = sys.argv[1]
    output_folder_path = "./output/"

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    # =============================================================================
    # data sursaud covid quot
    # =============================================================================
    try:
        url = "https://www.data.gouv.fr/fr/datasets/r/941ff2b4-ea24-4cdf-b0a7-655f2a332fb2"
        df = pd.read_excel(url)
        file_name = urlopen(url).url.split("/")[-1].split(".")[0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} could not be fetched".format(e, file_name))
        file_name = None

    if file_name:
        logging.info("processing file {}".format(file_name))

        list_cols = list(df.columns)
        df["numero_ligne"] = df.index + 1
        df = df[["numero_ligne"] + list_cols]

        # save dataframe for second report on classe d'âge
        df0 = df.copy(deep = True)

        list_dict_formules = generate_dict_formula(df)
        path = output_folder_path + "incoherences_{0}.xlsx".format(file_name)
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

    try:
        url = "https://www.data.gouv.fr/fr/datasets/r/c67aebf7-9883-49ef-a654-c4af5fdf5206"
        df0 = pd.read_csv(url, sep = ";")
        file_name = urlopen(url).url.split("/")[-1].split(".")[0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} could not be fetched".format(e, file_name))
        file_name = None

    if file_name:
        logging.info("processing file {}".format(file_name))
        list_cols = list(df0.columns)
        df0["numero_ligne"] = df0.index + 1
        df0 = df0[["numero_ligne"] + list_cols]

        var_groupby = ["dep", "semaine"]
        path =  output_folder_path + "incoherences_{0}.xlsx".format(file_name)
        res, sub_df = generate_rapport_incoherence_long(df0, "sursaud_cl_age_corona", var_groupby, path)


    # =============================================================================
    # data covid hospit
    # =============================================================================

    try:
        url = "https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7"
        df = pd.read_csv(url, sep=";")
        file_name = urlopen(url).url.split("/")[-1].split(".")[0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} could not be fetched".format(e, file_name))
        file_name = None

    if file_name:
        logging.info("processing file {}".format(file_name))

        list_cols = list(df.columns)
        df["numero_ligne"] = df.index + 1
        df = df[["numero_ligne"] + list_cols]


        path = output_folder_path + "incoherences_{0}.xlsx".format(file_name)

        var_groupby = ["dep", "jour"]
        df0 = df.copy(deep = True)
        res_genre, sub_df_genre = generate_rapport_incoherence_long(df0, "sexe", var_groupby, path, write = False)


        ## check the cumulated number of dc

        df["jour"] = pd.to_datetime(df["jour"])
        #df["dep_sexe"] = df.apply(lambda row: str(row["dep"]) + "_" + str(row["sexe"]), axis = 1)
        df["dc_lag"] = df.groupby(["dep", "sexe"])["dc"].shift(1)
        df["diff"] = df["dc"] - df["dc_lag"]



        df.sort_values(by=["dep", "sexe", "jour"], inplace=True)
        df["id"] = [x for x in range(1, len(df) + 1)]

        sub_df = df.loc[df["diff"] < 0]
        sub_df2 = df[df.id.isin([x - 1 for x in sub_df.id.values])]

        sub_df_concat = pd.concat([sub_df, sub_df2], sort=True)

        sub_df_concat.sort_values(by="id", inplace=True)
        sub_df_concat.drop(["id"], axis=1, inplace=True)


        res2 = pd.DataFrame({"Metrique": ["Nombre de lignes total", "Nombre de lignes avec incohérence"],
                             "Nombre": [len(df), len(sub_df)]})

        ## check the cumulated number of rad
        #df["dep_sexe"] = df.apply(lambda row: str(row["dep"]) + "_" + str(row["sexe"]), axis = 1)

        df["rad_lag"] = df.groupby(["dep", "sexe"])["rad"].shift(1)
        df["diff_rad"] = df["rad"] - df["rad_lag"]


        sub_df_rad = df.loc[df["diff_rad"] < 0]
        sub_df2_rad = df[df.id.isin([x - 1 for x in sub_df_rad.id.values])]

        sub_df_concat_rad = pd.concat([sub_df_rad, sub_df2_rad], sort=True)

        sub_df_concat_rad.sort_values(by="id", inplace=True)
        sub_df_concat_rad.drop(["id"], axis=1, inplace=True)


        res2_rad = pd.DataFrame({"Metrique": ["Nombre de lignes total", "Nombre de lignes avec incohérence"],
                             "Nombre": [len(df), len(sub_df_rad)]})


        writer = pd.ExcelWriter(path)
        res_genre.to_excel(writer, 'synthese_genre', index=False)
        sub_df_genre.to_excel(writer, 'lignes_erreur_genre', index=False)
        res2.to_excel(writer, 'synthese_dc_cumules', index=False)
        sub_df_concat.to_excel(writer, 'lignes_erreur_dc_cumules', index=False)
        res2_rad.to_excel(writer, 'synthese_rad_cumules', index=False)
        sub_df_concat_rad.to_excel(writer, 'lignes_erreur_rad_cumules', index=False)
        writer.save()

    # =============================================================================
    # data covid hospit etablissements
    # =============================================================================
    try:
        url = "https://www.data.gouv.fr/fr/datasets/r/41b9bd2a-b5b6-4271-8878-e45a8902ef00"
        hosp_cum = pd.read_csv(url, sep = ";")
        file_name = urlopen(url).url.split("/")[-1].split(".")[0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} not could not be fetched".format(e, file_name))
        file_name = None

    if file_name:
        logging.info("processing file {}".format(file_name))
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

        path = output_folder_path + "incoherences_{0}.xlsx".format(file_name)

        res = pd.DataFrame({"Metrique": ["Nombre de lignes total", "Nombre de lignes avec incohérence"],
                            "Nombre": [len(hosp_cum), len(sub_df)]})

        writer = pd.ExcelWriter(path)
        res.to_excel(writer, 'synthese', index=False)
        sub_df_concat.to_excel(writer, 'lignes_erreur', index=False)
        writer.save()

    # =============================================================================
    # covid trois laba quot
    # =============================================================================
    try:
        url = "https://www.data.gouv.fr/fr/datasets/r/b4ea7b4b-b7d1-4885-a099-71852291ff20"
        df = pd.read_csv(url, sep = ";")
        file_name = urlopen(url).url.split("/")[-1].split(".")[0]
    except Exception as e:
        logging.warning("Error : {0}. File corresponding to {1} not could not be fetched".format(e, file_name))
        file_name = None

    if file_name:
        logging.info("processing file {}".format(file_name))

        list_cols = list(df.columns)
        df["numero_ligne"] = df.index + 1
        df = df[["numero_ligne"] + list_cols]

        # save dataframe for second report on classe d'âge
        df0 = df.copy(deep = True)

        list_dict_formules = generate_dict_formula(df)
        path = output_folder_path + "incoherences_{0}.xlsx".format(file_name)
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
        try:
            url = "https://www.data.gouv.fr/fr/datasets/r/72050bc8-9959-4bb1-88a0-684ff8db5fb5"
            df = pd.read_csv(url, sep=";")
            file_name = urlopen(url).url.split("/")[-1].split(".")[0]
        except Exception as e:
            logging.warning("Error : {0}. File corresponding to {1} could not be fetched".format(e, file_name))
            file_name = None

        if file_name:
            logging.info("processing file {}".format(file_name))
            list_cols = list(df.columns)
            df["numero_ligne"] = df.index + 1
            df = df[["numero_ligne"] + list_cols]

            # save dataframe for second report on classe d'âge
            df0 = df.copy(deep=True)

            list_dict_formules = generate_dict_formula(df)
            path = output_folder_path + "incoherences_{0}.xlsx".format(file_name)
            res, sub_df = generate_rapport_incoherence_genre_wide(df, list_dict_formules, path, write=False)

            var_groupby = ["dep", "week"]
            res2, sub_df2 = generate_rapport_incoherence_long(df0, "clage_covid", var_groupby, path, write=False)

            writer = pd.ExcelWriter(path)
            res.to_excel(writer, 'synthese_genre', index=False)
            sub_df.to_excel(writer, 'lignes_erreur_genre', index=False)
            res2.to_excel(writer, 'synthese_cl_age', index=False)
            sub_df2.to_excel(writer, 'lignes_cl_age', index=False)
            writer.save()
