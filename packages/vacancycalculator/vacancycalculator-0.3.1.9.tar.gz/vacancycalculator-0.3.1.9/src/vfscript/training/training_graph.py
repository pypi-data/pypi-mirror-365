import json
import copy
import os
import csv
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
from vfscript.training.training_fingerstyle import DumpProcessor, StatisticsCalculator
from vfscript.training.utils import resolve_input_params_path

class AtomicGraphGenerator:
    def __init__(self,
                 json_params_path: str = None,
                 sphere_radius: float = 10.0  # radio de la esfera central
    ):
        # --- Parámetros de input_params.json -------------
        if json_params_path is None:
            json_params_path = resolve_input_params_path("input_params.json")
        cfg = json.load(open(json_params_path))["CONFIG"][0]
        self.input_path = cfg['relax']
        self.cutoff    = cfg['cutoff']
        self.radius    = cfg['smoothing_level_training']
        self.smoothing = cfg['smoothing_level_training']
        self.iterations= cfg['max_graph_variations']
        self.max_nodes = cfg['max_graph_size']
        # -------------------------------------------------

        # Cargar pipeline y computar una vez para obtener el centro
        self.pipeline = import_file(self.input_path, multiple_frames=True)
        data0 = self.pipeline.compute()
        pos0  = data0.particles.positions.array
        # Centro geométrico global
        self.cx, self.cy, self.cz = pos0.mean(axis=0)

        # Radio de la región central donde permitiremos borrar
        self.sphere_radius = cfg['radius_training']

        # Prepara CSV y JSON como antes...
        self.records = []
        self.csv_path = "outputs/csv/finger_data.csv"
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        header = ["vacancys","N","mean","std","skewness",
                  "kurtosis","Q1","median","Q3","IQR"
                 ] + [f"hist_bin_{i}" for i in range(1,11)]
        if not os.path.exists(self.csv_path) or os.path.getsize(self.csv_path)==0:
            with open(self.csv_path,'w',newline='',encoding='utf-8') as f:
                csv.writer(f).writerow(header)

    def run(self):
        for _ in range(self.iterations):
            for length in range(2, self.max_nodes+1):
                ids, _ = self._generate_graph(length)
                expr_ids = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)

                area, volume, count, dump_path = self._export_and_dump(expr_ids)

                proc = DumpProcessor(dump_path)
                proc.read_and_translate()
                proc.compute_norms()
                stats = StatisticsCalculator.compute_statistics(proc.norms)

                rec = {
                    "surface_area": area,
                    "filled_volume": volume,
                    "vacancys":     len(ids),
                    "cluster_size": count,
                    **stats
                }
                self.records.append(rec)

                row = [length, stats['N'], stats['mean'], stats['std'],
                       stats['skewness'],stats['kurtosis'],stats['Q1'],
                       stats['median'],stats['Q3'],stats['IQR']
                      ] + [stats[f"hist_bin_{i}"] for i in range(1,11)]
                with open(self.csv_path,'a',newline='',encoding='utf-8') as f:
                    csv.writer(f).writerow(row)

        os.makedirs("outputs/json",exist_ok=True)
        with open("outputs/json/training_graph.json","w",encoding='utf-8') as f:
            json.dump(self.records,f,indent=4)
        print("✔️ JSON y CSV actualizados.")

    def _generate_graph(self, length: int):
        data    = self.pipeline.compute()
        pos     = data.particles.positions.array
        ids_arr = data.particles['Particle Identifier'].array
        N       = len(pos)
        start   = np.random.choice(N)
        coords  = [pos[start]]; ids=[int(ids_arr[start])]
        current = coords[0]
        rem_set = set(range(N))-{start}

        while len(coords)<length and rem_set:
            rem   = np.array(list(rem_set))
            dists = np.linalg.norm(pos[rem]-current,axis=1)
            order = np.argsort(dists)
            cands = rem[order[:2]] if len(order)>1 else rem[order]
            choice= np.random.choice(cands)
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current=pos[choice]
            rem_set.remove(choice)

        return ids, coords

    def _export_and_dump(self, expr_ids: str):
        p = copy.deepcopy(self.pipeline)
        # 1) seleccionar IDs a eliminar y limitar al centro
        sphere_expr = (
            f"(Position.X - {self.cx})*(Position.X - {self.cx}) + (Position.Y - {self.cy})*(Position.Y - {self.cy}) + "
            f"(Position.Z - {self.cz})*(Position.Z - {self.cz}) <= {self.sphere_radius*self.sphere_radius}"
        )
        combined = f"({expr_ids}) && ({sphere_expr})"
        p.modifiers.append(ExpressionSelectionModifier(expression=combined))
        p.modifiers.append(DeleteSelectedModifier())

        # 2) construir superficie, invertir, eliminar fuera
        p.modifiers.append(ConstructSurfaceModifier(
            radius=self.radius,
            smoothing_level=self.smoothing,
            select_surface_particles=True
        ))
        p.modifiers.append(InvertSelectionModifier())
        p.modifiers.append(DeleteSelectedModifier())

        # 3) cluster analysis
        p.modifiers.append(ClusterAnalysisModifier(
            cutoff=self.cutoff, unwrap_particles=True
        ))

        data = p.compute()
        pts  = data.particles.positions.array
        count= len(pts)
        if count>=4:
            hull=ConvexHull(pts)
            area,volume = hull.area, hull.volume
        else:
            area=volume=0.0

        dump_dir = "outputs/dump"
        os.makedirs(dump_dir,exist_ok=True)
        dump_path = os.path.join(dump_dir, f"graph_{count}.dump")
        export_file(p,dump_path,'lammps/dump',
                    columns=['Particle Identifier',
                             'Particle Type',
                             'Position.X','Position.Y','Position.Z']
        )
        p.modifiers.clear()
        return area, volume, count, dump_path

if __name__=="__main__":
    gen = AtomicGraphGenerator(sphere_radius=5.0)
    gen.run()
