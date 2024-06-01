import os
import random
import numpy as np
from datetime import date, timedelta

import pandas as pd

import data_importer
import radar


class Generator:
    def __init__(self, sample_size: int, ordered_elements: dict, city_data: str = None, names_data: str = None,
                 last_names_data: str = None):
        self.sample_size = sample_size
        self.ordered_elements = ordered_elements
        self.data_storage = data_importer.DataBank()
        self.used_pesel_base = []
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

    def get_random_name(self, year, gender, p=True):
        if p:
            min_year = self.data_storage.first_name['Year'].min()
            max_year = self.data_storage.first_name['Year'].max()

            if year < min_year:
                year = min_year
            elif year > max_year:
                year = max_year
            names = self.data_storage.first_name[
                    (self.data_storage.first_name['Year'] == year) & (self.data_storage.first_name['Gender'] == gender)]
            if not names.empty:
                return np.random.choice(names['Name'], p=names['Number'] / names['Number'].sum())
            return None
        else:
            names = self.data_storage.first_name[
                (self.data_storage.first_name['Gender'] == gender)]
            if not names.empty:
                return np.random.choice(names['Name'])
            return None

    def get_random_pesel(self, birth_date, gender):
        pesel_digits = []
        month_pesel_start = 80
        start_century = 18

        if birth_date.year < start_century*100:
            raise ValueError("Provided birth_date doesn't allow to generate pesel number")

        # add first two digits
        pesel_digits.append(str(birth_date.year)[-2])
        pesel_digits.append(str(birth_date.year)[-1])

        # add third and fourth digits
        pesel_month = \
            month_pesel_start + (((birth_date.year // 100) - start_century) * 20) % 100 + birth_date.month
        if pesel_month < 10:
            pesel_digits.append(0)
        else:
            pesel_digits.append(str(pesel_month)[-2])
        pesel_digits.append(pesel_month % 10)

        # add fifth and sixth digits
        if birth_date.day < 10:
            pesel_digits.append(0)
        else:
            pesel_digits.append(str(birth_date.day)[-2])
        pesel_digits.append(birth_date.day % 10)

        # add rest of digits
        while True:
            # add seventh, eight, ninth digits
            pesel_digits.append(random.randint(0, 9))
            pesel_digits.append(random.randint(0, 9))
            pesel_digits.append(random.randint(0, 9))

            # add tenth digit
            if gender == "M":
                pesel_digits.append(random.choice([1, 3, 5, 7, 9]))
            elif gender == "K":
                pesel_digits.append(random.choice([0, 2, 4, 6, 8]))
            else:
                raise ValueError("Wrong Gender value provided to pesel generator!")

            # calculate control number
            controle_digit_wage = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 1]
            controle_sum = 0

            for number in range(10):
                controle_sum += int(pesel_digits[number]) * controle_digit_wage[number]
            controle_modulo = controle_sum % 10
            if controle_modulo == 0:
                pesel_digits.append(0)
            else:
                pesel_digits.append(10 - controle_modulo)

            if len(pesel_digits) != 11:
                raise ValueError("Generated pesel is longer then 11 digits!!!")
            final_pesel = ''.join(map(str, pesel_digits))
            if final_pesel not in self.used_pesel_base:
                self.used_pesel_base.append(final_pesel)
                return final_pesel

    def generate_persons(self):

        start_date = date(self.ordered_elements["person"]["year_range"][0], 1, 1)
        end_date = date(self.ordered_elements["person"]["year_range"][1], 12, 31)

        # generate gender, birth_date and last_name
        basic_data = {
            'Birth Date': np.array(
                [radar.random_datetime(start=start_date, stop=end_date) for x in range(self.sample_size)]),
            'Gender': np.random.choice(['M', 'K'], self.sample_size, p=[0.5, 0.5]),
            'Last Name': np.random.choice(self.data_storage.last_name['last_names'], self.sample_size)
        }
        df = pd.DataFrame(basic_data)

        # generate Name
        df['Name'] = \
            df.apply(lambda row:
                     self.get_random_name(row['Birth Date'].year, row['Gender'],
                                          self.ordered_elements["person"]["name_weighted_probability"]), axis=1)

        # generate Second Name
        df['Second Name'] = \
            df.apply(lambda row:
                     self.get_random_name(row['Birth Date'].year, row['Gender'],
                                          self.ordered_elements["person"]["name_weighted_probability"])
                     if np.random.rand() < 0.4 else None, axis=1)

        # generate Pesel
        df['Pesel Number'] = \
            df.apply(lambda row: self.get_random_pesel(row['Birth Date'], row['Gender']), axis=1)

        return df

    def generate_localisations(self):
        if self.ordered_elements["localisation"]["weighted_probability"]:
            weights = self.data_storage.localisation["population"] / self.data_storage.localisation["population"].sum()
            result_df = self.data_storage.localisation.sample(n=self.sample_size, weights=weights, replace=True)
            result_df["postal_code"] = result_df["postal_code"].apply(lambda x: random.choice(x) if x else None)
            return result_df
        else:
            result_df = self.data_storage.localisation.sample(n=self.sample_size, replace=True)
            result_df["postal_code"] = result_df["postal_code"].apply(lambda x: random.choice(x) if x else None)
            return result_df


if __name__ == "__main__":
    order = {
        "localisation": {
            "weighted_probability": True
        },
        "person": {
            "year_range": [1950, 2015],
            "name_weighted_probability": True
        },
    }
    lol = Generator(1000, order)
    # print(lol.data_storage.first_name.info())
    dupa = lol.generate_persons()
    print(dupa.info())