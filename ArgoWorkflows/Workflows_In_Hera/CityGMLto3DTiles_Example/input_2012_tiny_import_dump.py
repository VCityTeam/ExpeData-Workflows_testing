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
)
