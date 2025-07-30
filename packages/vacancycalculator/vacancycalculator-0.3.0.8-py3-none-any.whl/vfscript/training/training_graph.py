import json
import copy
import os
import numpy as np
from scipy.spatial import ConvexHull
from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier,
    ConstructSurfaceModifier,
    InvertSelectionModifier
)
from vfscript.training.training_fingerstyle import DumpProcessor, StatisticsCalculator  # ajusta la ruta según tu proyecto
from vfscript.training.utils import resolve_input_params_path

class AtomicGraphGenerator:
    def __init__(self, json_params_path: str = None):
        if json_params_path is None:
            json_params_path = resolve_input_params_path("input_params.json")
        with open(json_params_path, "r", encoding="utf-8") as f:
            all_params = json.load(f)
        cfg = all_params["CONFIG"][0]
        self.input_path = cfg['relax']
        self.cutoff = cfg['cutoff']
        self.radius = cfg['radius']
        self.smoothing = cfg['smoothing_level_training']
        self.num_iterations = cfg['max_graph_variations']
        self.max_nodes = cfg['max_graph_size']
        self.pipeline = import_file(self.input_path, multiple_frames=True)

        # Preparamos el dict de metrics con todos los campos que queremos
        self.metrics = {
            'surface_area': [],
            'filled_volume': [],
            'vacancys': [],
            'cluster_size': [],
            # ahora todos los stats de norms:
            'N': [], 'mean': [], 'std': [], 'skewness': [], 'kurtosis': [],
            'Q1': [], 'median': [], 'Q3': [], 'IQR': [],
            **{f'hist_bin_{i}': [] for i in range(1,11)}
        }

    def run(self):
        for _ in range(self.num_iterations):
            for length in range(2, self.max_nodes + 1):
                ids, coords = self._generate_graph(length)
                expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)
                area, volume, count, stats = self._export_graph(expr)
                # guardamos metrics básicas
                self.metrics['surface_area'].append(area)
                self.metrics['filled_volume'].append(volume)
                self.metrics['vacancys'].append(len(ids))
                self.metrics['cluster_size'].append(count)
                # y todas las stats extraídas
                for key, val in stats.items():
                    self.metrics[key].append(val)

        os.makedirs("outputs/json", exist_ok=True)
        with open('outputs/json/training_graph.json', 'w') as f:
            json.dump(self.metrics, f, indent=4)
        print('✔️ Exported metrics to outputs/json/training_graph.json')

    def _generate_graph(self, length: int):
        data = self.pipeline.compute()
        pos = data.particles.positions.array
        ids_arr = data.particles['Particle Identifier'].array
        N = len(pos)
        start = np.random.choice(N)
        coords, ids = [pos[start]], [int(ids_arr[start])]
        current = coords[0]
        remaining = set(range(N)) - {start}

        while len(coords) < length and remaining:
            rem = np.array(list(remaining))
            dists = np.linalg.norm(pos[rem] - current, axis=1)
            order = np.argsort(dists)
            top2 = order[:2] if len(order) >= 2 else order
            choice = np.random.choice(rem[top2])
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current = pos[choice]
            remaining.remove(choice)

        return ids, coords

    def _export_graph(self, expr: str):
        # 1) exportar el dump
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
        data = p.compute()
        points = data.particles.positions.array
        count = len(points)

        if count >= 4:
            hull = ConvexHull(points)
            area, volume = hull.area, hull.volume
        else:
            area, volume = 0.0, 0.0

        dump_path = f'outputs/dump/graph_{count}.dump'
        os.makedirs("outputs/dump", exist_ok=True)
        export_file(
            p,
            dump_path,
            'lammps/dump',
            columns=[
                'Particle Identifier', 'Particle Type',
                'Position.X','Position.Y','Position.Z'
            ]
        )
        p.modifiers.clear()

        # 2) extraer características del nuevo dump
        processor = DumpProcessor(dump_path)
        processor.read_and_translate()
        processor.compute_norms()
        stats = StatisticsCalculator.compute_statistics(processor.norms)
        return area, volume, count, stats


if __name__ == '__main__':
    generator = AtomicGraphGenerator()
    generator.run()
