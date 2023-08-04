import types

parameters = types.SimpleNamespace(
    borough="LYON_8EME",
    pattern="BATI",
    experiment_output_dir="junk",
    vintage="2012",
    persistedVolume="/within-container-mount-point",
    database=types.SimpleNamespace(
        port="5432",
        name="citydb-lyon-2012",
        user="postgres",
        password="postgres",
        keep_database=True,
    ),
)
