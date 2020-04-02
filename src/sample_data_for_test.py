# save sample on the code repo in order to make test

path = "/Users/kimmontalibet/Desktop/data_spf/spf-27032020-16h13/"
path_sample = "/Users/kimmontalibet/PycharmProjects/data_covid/data/"
os.listdir(path)

for file in os.listdir(path):
    if file.split(".")[-1] == "xlsx":
        list_sheets = pd.ExcelFile(path + file).sheet_names
        print(list_sheets)
        writer = pd.ExcelWriter(path_sample + file)

        for sheet in list_sheets:
            df = pd.read_excel(path + file, sheet_name=sheet).head(10)
            df.to_excel(writer, sheet, index=False)
        writer.save()

    elif file.split(".")[-1] == "csv":
        df = pd.read_csv(path + file, sep=";").head(10)
        df.to_csv(path_sample + file, sep=";", index=False)

