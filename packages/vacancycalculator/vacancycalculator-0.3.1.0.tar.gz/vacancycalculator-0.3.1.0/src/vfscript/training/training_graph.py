import json
import copy
import os
import numpy as np
import pandas as pd                           # ← para el CSV
from scipy.spatial import ConvexHull
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
        if json_params_path is None:
            json_params_path = resolve_input_params_path("input_params.json")
        with open(json_params_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)["CONFIG"][0]

        self.input_path  = cfg['relax']
        self.cutoff      = cfg['cutoff']
        self.radius      = cfg['radius']
        self.smoothing   = cfg['smoothing_level_training']
        self.iterations  = cfg['max_graph_variations']
        self.max_nodes   = cfg['max_graph_size']
        self.pipeline    = import_file(self.input_path, multiple_frames=True)

        # Prepara estructura para acumular todo
        self.records = []

    def run(self):
        for _ in range(self.iterations):
            for length in range(2, self.max_nodes + 1):
                ids, _ = self._generate_graph(length)
                expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)

                # 1) exportar dump y calcular area/volumen
                area, volume, count, dump_path = self._export_and_dump(expr)

                # 2) procesar ese dump para extraer normas y estadísticas
                proc = DumpProcessor(dump_path)
                proc.read_and_translate()
                proc.compute_norms()
                stats = StatisticsCalculator.compute_statistics(proc.norms)

                # 3) agregar un registro completo
                rec = {
                    "surface_area": area,
                    "filled_volume": volume,
                    "vacancys": len(ids),
                    "cluster_size": count,
                    **stats
                }
                self.records.append(rec)

        # Guardar JSON
        os.makedirs("outputs/json", exist_ok=True)
        with open("outputs/json/training_graph.json","w") as f:
            json.dump(self.records, f, indent=4)
        print("✔️ JSON guardado en outputs/json/training_graph.json")

        # Guardar CSV
        os.makedirs("outputs/csv", exist_ok=True)
        df = pd.DataFrame(self.records)
        df.to_csv("outputs/csv/finger_data.csv", index=False)
        print("✔️ CSV guardado en outputs/csv/finger_data.csv")

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
            rem   = np.array(list(rem_set))
            dists = np.linalg.norm(pos[rem] - current, axis=1)
            order = np.argsort(dists)
            cands = rem[order[:2]] if len(order)>1 else rem[order]
            choice= np.random.choice(cands)
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current = pos[choice]
            rem_set.remove(choice)

        return ids, coords

    def _export_and_dump(self, expr: str):
        p = copy.deepcopy(self.pipeline)
        p.modifiers.append(ExpressionSelectionModifier(expression=expr))
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(ConstructSurfaceModifier(
            radius=self.radius,
            smoothing_level=self.smoothing,
            select_surface_particles=True
        ))
        p.modifiers.append(InvertSelectionModifier())
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(ClusterAnalysisModifier(cutoff=self.cutoff, unwrap_particles=True))

        data   = p.compute()
        pts    = data.particles.positions.array
        count  = len(pts)
        if count >= 4:
            hull   = ConvexHull(pts)
            area   = hull.area
            volume = hull.volume
        else:
            area, volume = 0.0, 0.0

        dump_dir  = "outputs/dump"
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
