import pandas as pd
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity

class FingerprintVacancyAssigner:
    """
    Compara fingerprints desde un archivo query con una base de datos,
    asignando el número de vacancias del archivo más similar.
    Se añade un peso personalizable para la característica 'N'.
    """
    def __init__(self, base_csv_path: str, query_csv_path: str, weight_N: float = 2.0):
        self.df_base = pd.read_csv(base_csv_path)
        self.df_query = pd.read_csv(query_csv_path)
        self.weight_N = weight_N

        # Columnas de features: histogramas + estadísticos + N
        self.feature_cols = (
            [col for col in self.df_base.columns if col.startswith("hist_bin_")] +
            ["mean", "std", "skewness", "kurtosis", "Q1", "median", "Q3", "IQR", "N"]
        )

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
        del fingerprint más similar de la base, aplicando peso a 'N'.
        """
        # Copiar matrices de características
        X_base = self.df_base[self.feature_cols].copy()
        X_query = self.df_query[self.feature_cols].copy()

        # Aplicar peso a la columna N
        X_base["N"] = X_base["N"] * self.weight_N
        X_query["N"] = X_query["N"] * self.weight_N

        # Calcular similitud y matches
        sim = cosine_similarity(X_query.values, X_base.values)
        best_idx = sim.argmax(axis=1)

        matched_files = self.df_base.iloc[best_idx]["file_name"].values
        matched_vacancies = [self.extract_vacancy_from_filename(f) for f in matched_files]

        self.df_query["matched_file"] = matched_files
        self.df_query["assigned_vacancy"] = matched_vacancies
        return self.df_query

# Ejemplo de uso
if __name__ == "__main__":
    assigner = FingerprintVacancyAssigner(
        base_csv_path="outputs/csv/finger_data.csv",
        query_csv_path="outputs/csv/finger_key_files.csv",
        weight_N=3.0  # peso mayor para 'N'
    )
    df_result = assigner.assign()
    df_result.to_csv("outputs/csv/finger_key_files_clasificado.csv", index=False)
    print("✅ Resultado guardado con peso_N =", assigner.weight_N)
