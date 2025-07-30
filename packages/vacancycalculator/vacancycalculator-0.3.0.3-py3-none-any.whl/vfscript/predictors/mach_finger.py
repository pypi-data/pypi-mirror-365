import pandas as pd
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity

class FingerprintVacancyAssigner:
    """
    Compara fingerprints desde un archivo query con una base de datos,
    y asigna el número de vacancias del archivo más similar.
    """
    def __init__(self, base_csv_path: str, query_csv_path: str):
        self.df_base = pd.read_csv(base_csv_path)
        self.df_query = pd.read_csv(query_csv_path)

        # Columnas de features que se comparan
        self.feature_cols = [col for col in self.df_base.columns if col.startswith("hist_bin_")] + [
            "mean", "std", "skewness", "kurtosis", "Q1", "median", "Q3", "IQR"
        ]

    def extract_vacancy_from_filename(self, filename: str):
        """
        Extrae el número de vacancias del nombre de archivo, por ejemplo:
        'vacancy_4_training.dump' → 4
        """
        match = re.search(r'vacancy_(\d+)_', filename)
        return int(match.group(1)) if match else None

    def assign(self):
        """
        Asigna a cada fingerprint del query el número de vacancias
        del fingerprint más similar de la base.
        """
        X_base = self.df_base[self.feature_cols].values
        X_query = self.df_query[self.feature_cols].values

        similarity = cosine_similarity(X_query, X_base)
        best_match_idx = similarity.argmax(axis=1)

        matched_files = self.df_base.iloc[best_match_idx]["file_name"].values
        matched_vacancies = [self.extract_vacancy_from_filename(name) for name in matched_files]

        self.df_query["matched_file"] = matched_files
        self.df_query["assigned_vacancy"] = matched_vacancies
        return self.df_query
