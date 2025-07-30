# main.py

from .core import *  
from .config_loader import cargar_json_usuario
from pathlib import Path
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')

def VacancyAnalysis():
    
    base = "outputs"
    for sub in ("csv", "dump", "json"):
        os.makedirs(os.path.join(base, sub), exist_ok=True)

    
    processor = TrainingProcessor()
    processor.run()

    
    CONFIG = cargar_json_usuario()
    
    if "CONFIG" not in CONFIG or not isinstance(CONFIG["CONFIG"], list) or len(CONFIG["CONFIG"]) == 0:
        raise ValueError("input_params.json debe contener una lista 'CONFIG' con al menos un objeto.")

    configuracion = CONFIG["CONFIG"][0]
    defect_file = configuracion['defect']

    cs_out_dir = Path("inputs")
    cs_generator = CrystalStructureGenerator(configuracion, cs_out_dir)
    dump_path = cs_generator.generate()
    print(f"Estructura relajada generada en: {dump_path}")

    processor = ClusterProcessor(defect_file)
    processor.run()
    separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
    separator.run()

    # 3. Procesar dumps críticos
    clave_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
    for archivo in clave_criticos:
        try:
            dump_proc = ClusterDumpProcessor(archivo, decimals=5)
            dump_proc.load_data()
            dump_proc.process_clusters()
            dump_proc.export_updated_file(f"{archivo}_actualizado.txt")
        except Exception as e:
            print(f"Error procesando {archivo}: {e}")

    # 4. Subdivisión iterativa
    lista_criticos = ClusterDumpProcessor.cargar_lista_archivos_criticos("outputs/json/key_archivos.json")
    for archivo in lista_criticos:
        machine_proc = ClusterProcessorMachine(archivo, configuracion['cluster tolerance'], configuracion['iteraciones_clusterig'])
        machine_proc.process_clusters()
        machine_proc.export_updated_file()

    # 5. Separar archivos finales vs críticos
    separator = KeyFilesSeparator(configuracion, os.path.join("outputs/json", "clusters.json"))
    separator.run()

    # 6. Generar nuevos dumps por cluster
    export_list = ExportClusterList("outputs/json/key_archivos.json")
    export_list.process_files()

    # 7. Calcular superficies de dump
    surf_proc = SurfaceProcessor(configuracion)
    surf_proc.process_all_files()
    surf_proc.export_results()



    exporter = ClusterFeatureExporter("outputs/json/key_archivos.json")
    exporter.export()


    #Calcular categoria de defect_file.csv
    model = BehaviorTreeModel(weight_cluster_size=2.0, max_depth=5)
    model.train('outputs/json/training_graph.json')

    df_resultado = model.classify_csv(
        csv_path='outputs/csv/defect_data.csv',
        output_path='outputs/csv/finger_data_clasificado.csv'
    )

    print(df_resultado[['archivo', 'grupo_predicho']])


    #ETAPA DE PREDICCIONES


    trainer = VacancyModelTrainer(json_path='outputs/json/training_graph.json')
    trainer.load_data()
    trainer.train_all_models()
    #
    #  Predecir en lote desde archivo CSV
# Ejecutar comparación con peso en 'N'
    assigner = FingerprintVacancyAssigner(
        base_csv_path="outputs/csv/finger_data.csv",
        query_csv_path="outputs/csv/finger_key_files.csv",
        weight_N=0.05
    )
    df_result = assigner.assign()

    # 1) Imprimir en consola
    print(df_result)

    # 2) O guardar en CSV
    import os
    os.makedirs("outputs/csv", exist_ok=True)
    df_result.to_csv("outputs/csv/finger_key_files_clasificado.csv", index=False)
    print("✅ Resultado guardado en outputs/csv/finger_key_files_clasificado.csv")

if __name__ == "__main__":
    VacancyAnalysis()
    print("Script ejecutado correctamente.")



