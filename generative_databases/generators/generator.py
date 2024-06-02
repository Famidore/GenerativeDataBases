import random
import numpy as np
from datetime import date
import pandas as pd
import logging
from generative_databases.generators import data_importer
from sqlalchemy import create_engine
import radar


# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("generator.log")],
)
logger = logging.getLogger(__name__)


class Generator:
    """
    Generator class for creating synthetic data.
    """

    def __init__(self, params_dict: dict):
        self.sample_size = params_dict["sample_size"]
        self.second_name_chance = params_dict["sec_name_prob"]
        self.data_storage = data_importer.DataBank()
        self.used_pesel_base = []
        city_data = params_dict["city_data"]
        names_data = params_dict["names_data"]
        last_names_data = params_dict["last_names_data"]
        self.params_dict = params_dict
        if city_data and city_data != " ":
            self.data_storage.localisation = self.data_storage.load_csv_data(city_data)
            logger.info(f"Loaded city data from {city_data}")
        else:
            self.data_storage.load_built_in_localisation_data()
            logger.info("Loaded built-in city data")

        if names_data and names_data != " ":
            self.data_storage.first_name = self.data_storage.load_csv_data(names_data)
            logger.info(f"Loaded names data from {names_data}")
        else:
            self.data_storage.load_built_in_names_data()
            logger.info("Loaded built-in names data")

        if last_names_data and last_names_data != " ":
            self.data_storage.last_name = self.data_storage.load_csv_data(
                last_names_data
            )
            logger.info(f"Loaded last names data from {last_names_data}")
        else:
            self.data_storage.load_built_in_last_name_data()
            logger.info("Loaded built-in last names data")

    def get_random_name(self, year: int, gender: str, p: bool = True):
        """
        Generate a random name based on the year and gender.

        :param year: Year of birth.
        :type year: int
        :param gender: Gender ('M' or 'K').
        :type gender: str
        :param p: Whether to use weighted probabilities.
        :type p: bool
        :return: Randomly selected name.
        :rtype: str
        """
        try:
            if p:
                min_year = self.data_storage.first_name["Year"].min()
                max_year = self.data_storage.first_name["Year"].max()

                if year < min_year:
                    year = min_year
                elif year > max_year:
                    year = max_year
                names = self.data_storage.first_name[
                    (self.data_storage.first_name["Year"] == year)
                    & (self.data_storage.first_name["Gender"] == gender)
                ]
                if not names.empty:
                    name = np.random.choice(
                        names["Name"], p=names["Number"] / names["Number"].sum()
                    )
                    logger.info(
                        f"Generated random name: {name} for year: {year} and gender: {gender}"
                    )
                    return name
                return None
            else:
                names = self.data_storage.first_name[
                    (self.data_storage.first_name["Gender"] == gender)
                ]
                if not names.empty:
                    name = np.random.choice(names["Name"])
                    logger.info(f"Generated random name: {name} for gender: {gender}")
                    return name
                return None
        except Exception as e:
            logger.error(f"Error in get_random_name: {e}")
            return None

    def get_random_pesel(self, birth_date: date, gender: str):
        """
        Generate a random PESEL number based on birthdate and gender.

        :param birth_date: Birthdate.
        :type birth_date: date
        :param gender: Gender ('M' or 'K').
        :type gender: str
        :return: Randomly generated PESEL number.
        :rtype: str
        """
        try:
            pesel_digits = []
            month_pesel_start = 80
            start_century = 18

            if birth_date.year < start_century * 100:
                raise ValueError(
                    "Provided birth_date doesn't allow to generate PESEL number"
                )

            # add first two digits
            pesel_digits.append(str(birth_date.year)[-2])
            pesel_digits.append(str(birth_date.year)[-1])

            # add third and fourth digits
            pesel_month = (
                month_pesel_start
                + (((birth_date.year // 100) - start_century) * 20) % 100
                + birth_date.month
            )
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
                # add seventh, eighth, ninth digits
                pesel_digits.append(random.randint(0, 9))
                pesel_digits.append(random.randint(0, 9))
                pesel_digits.append(random.randint(0, 9))

                # add tenth digit
                if gender == "M":
                    pesel_digits.append(random.choice([1, 3, 5, 7, 9]))
                elif gender == "K":
                    pesel_digits.append(random.choice([0, 2, 4, 6, 8]))
                else:
                    raise ValueError("Wrong Gender value provided to PESEL generator!")

                # calculate control number
                control_digit_weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 1]
                control_sum = 0

                for number in range(10):
                    control_sum += (
                        int(pesel_digits[number]) * control_digit_weights[number]
                    )
                control_modulo = control_sum % 10
                if control_modulo == 0:
                    pesel_digits.append(0)
                else:
                    pesel_digits.append(10 - control_modulo)

                if len(pesel_digits) != 11:
                    raise ValueError("Generated PESEL is longer than 11 digits!")
                final_pesel = "".join(map(str, pesel_digits))
                if final_pesel not in self.used_pesel_base:
                    self.used_pesel_base.append(final_pesel)
                    logger.info(f"Generated PESEL number: {final_pesel}")
                    return final_pesel
        except Exception as e:
            logger.error(f"Error in get_random_pesel: {e}")
            return None

    def generate_persons(self) -> pd.DataFrame:
        """
        Generate a DataFrame of synthetic persons' data.

        :return: DataFrame containing generated persons' data.
        :rtype: pd.DataFrame
        """
        try:
            logger.info(self.params_dict)
            start_date = date(self.params_dict["year_range"][0], 1, 1)
            end_date = date(self.params_dict["year_range"][1], 12, 31)

            # generate gender, birth_date and last_name
            basic_data = {
                "Birth Date": np.array(
                    [
                        radar.random_datetime(start=start_date, stop=end_date)
                        for _ in range(self.sample_size)
                    ]
                ),
                "Gender": np.random.choice(["M", "K"], self.sample_size, p=[0.5, 0.5]),
                "Last Name": np.random.choice(
                    self.data_storage.last_name["last_names"], self.sample_size
                ),
            }
            df = pd.DataFrame(basic_data)
            logger.info("Generated basic person data (Birth Date, Gender, Last Name)")

            # generate Name
            df["Name"] = df.apply(
                lambda row: self.get_random_name(
                    row["Birth Date"].year,
                    row["Gender"],
                    self.params_dict["names_w_prob"],
                ),
                axis=1,
            )
            logger.info("Generated Names")

            # generate Second Name
            df["Second Name"] = df.apply(
                lambda row: (
                    self.get_random_name(
                        row["Birth Date"].year,
                        row["Gender"],
                        self.params_dict["names_w_prob"],
                    )
                    if np.random.rand() < self.second_name_chance
                    else None
                ),
                axis=1,
            )
            logger.info("Generated Second Names")

            # generate PESEL
            df["Pesel Number"] = df.apply(
                lambda row: self.get_random_pesel(row["Birth Date"], row["Gender"]),
                axis=1,
            )
            logger.info("Generated PESEL numbers")

            return df
        except Exception as e:
            logger.error(f"Error in generate_persons: {e}")
            return pd.DataFrame()

    def generate_localisations(self) -> pd.DataFrame:
        """
        Generate a DataFrame of synthetic localisation data.

        :return: DataFrame containing generated localisation data.
        :rtype: pd.DataFrame
        """
        try:
            if self.params_dict["loc_w_prob"]:
                weights = (
                    self.data_storage.localisation["population"]
                    / self.data_storage.localisation["population"].sum()
                )
                result_df = self.data_storage.localisation.sample(
                    n=self.sample_size, weights=weights, replace=True
                )
                result_df["postal_code"] = result_df["postal_code"].apply(
                    lambda x: random.choice(x) if x else None
                )
                logger.info("Generated localisations with weighted probability")
                return result_df
            else:
                result_df = self.data_storage.localisation.sample(
                    n=self.sample_size, replace=True
                )
                result_df["postal_code"] = result_df["postal_code"].apply(
                    lambda x: random.choice(x) if x else None
                )
                logger.info("Generated localisations without weighted probability")
                return result_df
        except Exception as e:
            logger.error(f"Error in generate_localisations: {e}")
            return pd.DataFrame()

    def generate_and_save(self, kwargs: dict):
        """
        Generate synthetic data and save it to the specified formats.

        :param kwargs: Dictionary specifying output formats and file paths.
        :type kwargs: dict
        """
        try:
            persons_df = self.generate_persons()
            localisations_df = self.generate_localisations()

            localisations_df = localisations_df.reset_index(drop=True)
            persons_df = persons_df.reset_index(drop=True)

            result_df = pd.concat(
                [persons_df, localisations_df], axis=1, ignore_index=True
            )

            logger.info("Generated combined DataFrame of persons and localisations")

            for output_type, file_path in kwargs.items():
                if output_type == "csv":
                    result_df.to_csv(file_path, encoding="utf-8")
                    logger.info(f"Saved data to CSV file at {file_path}")
                elif output_type == "json":
                    result_df.to_json(file_path, orient="records", lines=True)
                    logger.info(f"Saved data to JSON file at {file_path}")
                elif output_type == "xml":
                    result_df.to_xml(file_path, index=False)
                    logger.info(f"Saved data to XML file at {file_path}")
                elif output_type == "excel":
                    result_df.to_excel(file_path, index=False)
                    logger.info(f"Saved data to Excel file at {file_path}")
                elif output_type == "html":
                    result_df.to_html(file_path, index=False)
                    logger.info(f"Saved data to HTML file at {file_path}")
                elif output_type == "hdf5":
                    result_df.to_hdf(file_path, key="df", mode="w")
                    logger.info(f"Saved data to HDF5 file at {file_path}")
                elif output_type == "parquet":
                    result_df.to_parquet(file_path)
                    logger.info(f"Saved data to Parquet file at {file_path}")
                elif output_type == "feather":
                    result_df.to_feather(file_path)
                    logger.info(f"Saved data to Feather file at {file_path}")
                elif output_type == "stata":
                    result_df.to_stata(file_path)
                    logger.info(f"Saved data to Stata file at {file_path}")
                elif output_type == "sql":
                    engine = create_engine(file_path)
                    result_df.to_sql(
                        "people", con=engine, if_exists="replace", index=False
                    )
                    logger.info(f"Saved data to SQL database at {file_path}")
                elif output_type == "pickle":
                    result_df.to_pickle(file_path)
                    logger.info(f"Saved data to Pickle file at {file_path}")
                else:
                    logger.warning(f"Unknown output type: {output_type}")

        except Exception as e:
            logger.error(f"Error in generate_and_save: {e}")


if __name__ == "__main__":
    order = {
        "localisation": {"weighted_probability": True},
        "person": {"year_range": [1950, 2015], "name_weighted_probability": True},
    }
    generator = Generator(1000, order)
    persons = generator.generate_persons()
    localisations = generator.generate_localisations()
