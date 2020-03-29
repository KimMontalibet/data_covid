import pandas as pd
import numpy as np


# generate formula automatically with the format xxx_tot = xxx_f + xxx_h
def generate_dict_formula(df):
    """takes as input a dataframe and generate the list of formulas"""
    list_var_with_gender = [x[:-2] for x in df.columns if x[-2:] == "_h"]
    list_var_no_gender = [x for x in df.columns if x[-2:] not in ["_h", "_f"]]
    list_dict_formules = []
    for var in list_var_with_gender:
        dict_temp = {}
        dict_temp["total"] = var
        dict_temp["list_variable_somme"] = [var + suffixe for suffixe in ["_h", "_f"]]
        list_dict_formules.append(dict_temp)

    return list_dict_formules

 def add_incoherence_metrics_to_df(df, list_dict_formules):
    # test if the diff between total and sum of variables are equal
    def test_total(row):
        if all([pd.isnull(row[x]) for x in [var_tot] + test["list_variable_somme"]]):
            return 0
        else:
            return 1 - int(bool(sum([row[x] for x in test["list_variable_somme"]]) == row[var_tot]))

    for test in list_dict_formules:
        var_tot = test["total"]
        df["test_" + var_tot] = df.apply(test_total, axis=1)

    # compute the diff between total and sum of variables
    def diff_total_sum(row):
        if all([pd.isnull(row[x]) for x in [var_tot] + test["list_variable_somme"]]):
            return np.nan
        else:
            return row[var_tot] - sum([row[x] for x in test["list_variable_somme"]])

    for test in list_dict_formules:
        var_tot = test["total"]
        df["diff_" + var_tot] = df.apply(diff_total_sum, axis=1)

    list_test_var = [x for x in df.columns if x[:5] == "test_"]

    list_diff_var = [x for x in df.columns if x[:5] == "diff_"]

    df["sum_test"] = df.apply(lambda row: sum([row[x] for x in list_test_var]), axis=1)

    return df



def generate_rapport_incoherence(df, list_dict_formules, date, path, write=True):
    """Inputs: dataframe and list_dict_formules
    outputs: 2 dataframes, one with synthethic error metrics and one with the rows
    errors """

    df0 = df.copy(deep = True)

    list_var = [x["total"] for x in list_dict_formules]
    df = add_incoherence_metrics_to_df(df, list_dict_formules)
    sub_df = df.loc[(df['sum_test'] > 0)]

    nb_ligne_err = len(sub_df)
    nb_ligne_total = len(df)

    list_metriques = ["Nombre total de lignes", "Lignes avec une erreur de cohérence"] + \
                     ["Lignes avec une erreur de cohérence pour la variable " + x for x in list_var]

    # colonnes: Nombre, Moyenne différence, Min diff, Max diff
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

    if write:
        writer = pd.ExcelWriter(path)
        res.to_excel(writer, 'synthese_genre', index=False)
        sub_df.to_excel(writer, 'lignes_erreur_genre', index=False)
        writer.save()

    return res, sub_df