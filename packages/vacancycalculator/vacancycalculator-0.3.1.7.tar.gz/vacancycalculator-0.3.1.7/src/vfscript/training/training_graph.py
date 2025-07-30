import json
import copy
import os
import csv
import numpy as np
from scipy.spatial import ConvexHull
import pandas as pd
from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier,
    ConstructSurfaceModifier,
    InvertSelectionModifier
)
from vfscript.training.training_fingerstyle import DumpProcessor, StatisticsCalculator
from vfscript.training.utils import resolve_input_params_path

class AtomicGraphGenerator:
    def __init__(self, json_params_path: str = None):
        # --- Parámetros de input_params.json -------------
        if json_params_path is None:
            json_params_path = resolve_input_params_path("input_params.json")
        cfg = json.load(open(json_params_path))["CONFIG"][0]
        self.input_path = cfg['relax']
        self.cutoff    = cfg['cutoff']
        self.radius    = cfg['radius']
        self.radius_training=cfg['radius_training']
        self.smoothing = cfg['smoothing_level_training']
        self.iterations= cfg['max_graph_variations']
        self.max_nodes = cfg['max_graph_size']
        # -------------------------------------------------

        self.pipeline = import_file(self.input_path, multiple_frames=True)

        # Prepara JSON
        self.records = []

        # Rutas y header
        self.csv_path = "outputs/csv/finger_data.csv"
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

        header = [
            "vacancys",  # tú pusiste 'length', pon aquí el nombre real
            "N", "mean", "std",
            "skewness", "kurtosis", "Q1", "median", "Q3", "IQR"
        ] + [f"hist_bin_{i}" for i in range(1,11)]

        # Sólo escribir header si el archivo NO existe o está vacío
        if not os.path.exists(self.csv_path) or os.path.getsize(self.csv_path) == 0:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
    def run(self):
        for _ in range(self.iterations):
            for length in range(2, self.max_nodes + 1):
                ids, _ = self._generate_graph(length)
                expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)

                # 1) exportar dump y calcular área/volumen
                area, volume, count, dump_path = self._export_and_dump(expr)

                # 2) extraer normas y estadísticas
                proc = DumpProcessor(dump_path)
                proc.read_and_translate()
                proc.compute_norms()
                stats = StatisticsCalculator.compute_statistics(proc.norms)

                # 3) agregar al JSON interno
                rec = {
                    "surface_area": area,
                    "filled_volume": volume,
                    "vacancys":     len(ids),
                    "cluster_size": count,
                    **stats
                }
                self.records.append(rec)

                # 4) escribir línea en el CSV
                row = [
                    length,
                    stats['N'],
                    stats['mean'],
                    stats['std'],
                    stats['skewness'],
                    stats['kurtosis'],
                    stats['Q1'],
                    stats['median'],
                    stats['Q3'],
                    stats['IQR']
                ] + [stats[f"hist_bin_{i}"] for i in range(1,11)]
                with open(self.csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(row)

        # Guardar JSON completo
        os.makedirs("outputs/json", exist_ok=True)
        with open("outputs/json/training_graph.json", "w", encoding='utf-8') as f:
            json.dump(self.records, f, indent=4)
        print(f"✔️ JSON guardado en outputs/json/training_graph.json")
        print(f"✔️ CSV guardado en       {self.csv_path}")

    def _generate_graph(self, length: int):
        data    = self.pipeline.compute()
        pos     = data.particles.positions.array
        ids_arr = data.particles['Particle Identifier'].array
        N       = len(pos)
        start   = np.random.choice(N)
        coords  = [pos[start]]
        ids     = [int(ids_arr[start])]
        current = coords[0]
        rem_set = set(range(N)) - {start}

        while len(coords) < length and rem_set:
            rem    = np.array(list(rem_set))
            dists  = np.linalg.norm(pos[rem] - current, axis=1)
            order  = np.argsort(dists)
            cands  = rem[order[:2]] if len(order) > 1 else rem[order]
            choice = np.random.choice(cands)
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current = pos[choice]
            rem_set.remove(choice)

        return ids, coords

    def _export_and_dump(self, expr: str, sphere_radius: float):
        # Partimos de una copia
        p = copy.deepcopy(self.pipeline)

        # … tus selectores anteriores …

        # Antes de eliminar por cluster, calculo el centro a partir
        # de las posiciones actuales:
        data_tmp = p.compute()
        pos_all  = data_tmp.particles.positions.array
        # Centro geométrico de todos los átomos
        cx, cy, cz = pos_all.mean(axis=0)

        # Expresión esférica centrada en (cx,cy,cz)
        sphere_expr = (
            f"(Position.X - {cx})^2 + (Position.Y - {cy})^2 + "
            f"(Position.Z - {cz})^2 <= {sphere_radius**2}"
        )
        p.modifiers.append(ExpressionSelectionModifier(expression=sphere_expr))
        p.modifiers.append(DeleteSelectedModifier())

        # Ahora sí, cluster analysis sobre lo que queda
        p.modifiers.append(ClusterAnalysisModifier(cutoff=self.cutoff, unwrap_particles=True))

        data = p.compute()
        pts  = data.particles.positions.array
        count = len(pts)

        if count >= 4:
            hull = ConvexHull(pts)
            area, volume = hull.area, hull.volume
        else:
            area = volume = 0.0

        # 5) Exportar el dump resultante
        dump_dir = "outputs/dump"
        os.makedirs(dump_dir, exist_ok=True)
        dump_path = os.path.join(dump_dir, f"graph_{count}.dump")
        export_file(
            p, dump_path, 'lammps/dump',
            columns=[
                'Particle Identifier','Particle Type',
                'Position.X','Position.Y','Position.Z'
            ]
        )
        p.modifiers.clear()
        return area, volume, count, dump_path


if __name__ == "__main__":
    gen = AtomicGraphGenerator()
    gen.run()
