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
        # BUG: for 2015 split buildings produces an empty output (no
        # buildings at all). This might be due to the fact that 2015 buildings
        # are already nicely split and only a copy to the targer directory is
        # required (but not done?)...
        vintages=["2009", "2012"],
    ),
)
