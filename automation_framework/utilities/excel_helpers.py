import pandas as pd


class ExcelHelpers:
    def read_excel_data(self, file_path, sheet_name):
        data = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

        return data

    def get_city_country_list(self, file_path, sheet_name):
        data = self.read_excel_data(file_path, sheet_name)
        # Convert the dataframe to a list of tuples
        city_country_list = list(zip(data["name"].tolist(), data["country"].tolist()))
        return city_country_list

    # WIP
    def get_param_list(self, file_path, sheet_name, param_name):
        data = self.read_excel_data(file_path, sheet_name)
        # Convert the dataframe to a dictionary
        param_list = data[param_name].tolist()
        return param_list
