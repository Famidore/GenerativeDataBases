import pandas as pd
import os
import unidecode


def normalize_text(text):
    return unidecode.unidecode(text).lower()


class DataBank:
    def __init__(self):
        self.first_name = None
        self.last_name = None
        self.localisation = None

    def load_built_in_localisation_data(self):
        data_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        city_list = pd.read_csv(
            os.path.join(data_dir_path, "Poland_cities", "pl.csv"))
        regions_admin_info = pd.read_csv(
            os.path.join(data_dir_path, "Poland_postal_codes", "Poland_complete_postal_codes_admin_div.csv"))

        city_list["city"] = city_list["city"].apply(normalize_text)
        regions_admin_info["Administrative Division"] = regions_admin_info["Administrative Division"].apply(
            normalize_text)
        city_list['postal_code'] = [[] for _ in range(len(city_list))]
        for idx, row in city_list.iterrows():
            city = row['city']
            postal_codes =\
                regions_admin_info[regions_admin_info['Administrative Division'] == city]['Postal Code'].tolist()
            city_list.at[idx, 'postal_code'] = postal_codes
        self.localisation = city_list

    def load_built_in_names_data(self):
        data_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        self.first_name = pd.read_csv(
            os.path.join(data_dir_path, "Poland_all_first_last_names", "Imiona_nadane_wPolsce_w_latach_2000-2019.csv"))

    def load_built_in_last_name_data(self):
        data_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        self.last_name = pd.read_csv(
            os.path.join(data_dir_path, "Poland_all_first_last_names", "polish_surnames.txt"),
            header=None, names=['last_names'])

    def load_csv_data(self, path: str):
        if ".csv" not in path:
            raise NameError(f"File {path} should be saved in 'csv' format!")
        return pd.read_csv(os.path.abspath(path))
