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
        # FIXME: for 2015 split buildings produces an empty output (no
        # buildings at all) !
        vintages=["2009", "2012"],
    ),
)
