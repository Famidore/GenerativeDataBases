import pandas as pd
import os
import unidecode
import logging

# Setting the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("generator.log")
    ]
)
logger = logging.getLogger(__name__)


def normalize_text(text: str):
    """
    Normalize text by removing Polish diacritical marks and converting to lowercase.

    :param text: The input text to be normalized.
    :type text: str
    :return: Normalized text.
    :rtype: str
    """
    return unidecode.unidecode(text).lower()


class DataBank:
    """
    A class to manage and load various datasets related to names and localizations (by default in Poland).
    """

    def __init__(self):
        """
        Initialize the DataBank class with attributes for first names, last names, and localizations.
        """
        self.first_name = None
        self.last_name = None
        self.localisation = None
        logger.info("DataBank instance created.")

    def load_built_in_localisation_data(self):
        """
        Load built-in localization data for Polish cities and their postal codes.

        This method reads city and postal code data from predefined CSV files, normalizes the city names,
        and associates each city with its respective postal codes.
        """
        data_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        logger.info("Loading built-in localization data from %s", data_dir_path)

        try:
            city_list = pd.read_csv(os.path.join(data_dir_path, "Poland_cities", "pl.csv"))
            regions_admin_info = pd.read_csv(os.path.join(data_dir_path, "Poland_postal_codes",
                                                          "Poland_complete_postal_codes_admin_div.csv"))

            city_list["city"] = city_list["city"].apply(normalize_text)
            regions_admin_info["Administrative Division"] = \
                regions_admin_info["Administrative Division"].apply(normalize_text)
            city_list['postal_code'] = [[] for _ in range(len(city_list))]

            for idx, row in city_list.iterrows():
                city = row['city']
                postal_codes = \
                    regions_admin_info[regions_admin_info['Administrative Division'] == city]['Postal Code'].tolist()
                city_list.at[idx, 'postal_code'] = postal_codes

            self.localisation = city_list   # .apply(normalize_text)
            logger.info("Localization data loaded successfully.")
        except Exception as e:
            logger.error("Error loading localization data: %s", str(e))

    def load_built_in_names_data(self):
        """
        Load built-in first names data for Poland.

        This method reads first names data from a predefined CSV file.
        """
        data_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        logger.info("Loading built-in names data from %s", data_dir_path)

        try:
            self.first_name = pd.read_csv(os.path.join(data_dir_path, "Poland_all_first_last_names",
                                                       "Imiona_nadane_wPolsce_w_latach_2000-2019.csv"))
            self.first_name = self.first_name.apply(normalize_text)
            logger.info("First names data loaded successfully.")
        except Exception as e:
            logger.error("Error loading first names data: %s", str(e))

    def load_built_in_last_name_data(self):
        """
        Load built-in last names data for Poland.

        This method reads last names data from a predefined text file.
        """
        data_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
        logger.info("Loading built-in last names data from %s", data_dir_path)

        try:
            self.last_name = pd.read_csv(os.path.join(data_dir_path, "Poland_all_first_last_names",
                                                      "polish_surnames.txt"), header=None, names=['last_names'])
            self.last_name = self.last_name.apply(normalize_text)
            logger.info("Last names data loaded successfully.")
        except Exception as e:
            logger.error("Error loading last names data: %s", str(e))

    def load_csv_data(self, path: str):
        """
        Load data from a specified CSV file.

        :param path: The path to the CSV file.
        :type path: str
        :raises NameError: If the file is not in CSV format.
        :return: Data loaded from the CSV file.
        :rtype: pd.DataFrame
        """
        logger.info("Loading CSV data from %s", path)

        if not path.endswith(".csv"):
            logger.error("File %s is not in 'csv' format!", path)
            raise NameError(f"File {path} should be saved in 'csv' format!")

        try:
            data = pd.read_csv(os.path.abspath(path))
            data = data.apply(normalize_text)
            logger.info("CSV data loaded successfully from %s", path)
            return data
        except Exception as e:
            logger.error("Error loading CSV data from %s: %s", path, str(e))
            raise
