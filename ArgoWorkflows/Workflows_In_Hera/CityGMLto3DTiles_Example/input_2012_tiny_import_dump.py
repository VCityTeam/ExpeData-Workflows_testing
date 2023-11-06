import types

inputs = types.SimpleNamespace(
    constants=types.SimpleNamespace(
        # Constants (a.k.a. fixed parameters): such parameter values are not
        # sweeped (in other terms they are unique values). and are thus shared by all the computations.
        pattern="BATI",
        experiment_output_dir="junk",
    ),
    parameters=types.SimpleNamespace(
        # Parameters vary independently from one another
        boroughs=["LYON_1ER", "LYON_8EME"],
        vintages=["2012", "2015"],
        # FIXME: debug entries (to be removed when loops are effective):
        borough="LYON_8EME",
        vintage="2012",
    ),
    database_generic=types.SimpleNamespace(
        port="5432",
        name="citydb-lyon-",
        user="postgres",
        password="postgres",
        keep_database=True,
    ),
    # Technical variables derived from vintages (as many databases as vintages)
    database_2012=types.SimpleNamespace(
        port="5432",
        name="citydb-lyon-2012",
        user="postgres",
        password="postgres",
        keep_database=True,
    ),
    database_2015=types.SimpleNamespace(
        port="5432",
        name="citydb-lyon-2015",
        user="postgres",
        password="postgres",
        keep_database=True,
    ),
)
