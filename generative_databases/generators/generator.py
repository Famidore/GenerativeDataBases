import os
import random
import data_importer


class Generator:
    def __init__(self, sample_size: int, ordered_elements: dict, city_data: str = None, names_data: str = None,
                 last_names_data: str = None):
        self.sample_size = sample_size
        self.ordered_elements = ordered_elements
        self.data_storage = data_importer.DataBank()
        if city_data:
            self.data_storage.localisation = self.data_storage.load_csv_data(city_data)
        else:
            self.data_storage.load_built_in_localisation_data()
        if names_data:
            self.data_storage.first_name = self.data_storage.load_csv_data(names_data)
        else:
            self.data_storage.load_built_in_names_data()
        if last_names_data:
            self.data_storage.last_name = self.data_storage.load_csv_data(last_names_data)
        else:
            self.data_storage.load_built_in_last_name_data()

    def generate_persons(self):
        pass

    def generate_localisations(self):
        if True:  # ToDo add some chose option if generate with population as weight or just simple random
            weights = self.data_storage.localisation["population"] / self.data_storage.localisation["population"].sum()
            result_df = self.data_storage.localisation.sample(n=self.sample_size, weights=weights, replace=True)
            result_df["postal_code"] = result_df["postal_code"].apply(lambda x: random.choice(x) if x else None)
            return result_df
        else:
            result_df = self.data_storage.localisation.sample(n=self.sample_size, replace=True)
            result_df["postal_code"] = result_df["postal_code"].apply(lambda x: random.choice(x) if x else None)
            return result_df
        pass


if __name__ == "__main__":
    lol = Generator(1000, {"lol": 2})
    print(lol.data_storage.localisation.info())
    dupa = lol.generate_localisations()
    print(dupa)