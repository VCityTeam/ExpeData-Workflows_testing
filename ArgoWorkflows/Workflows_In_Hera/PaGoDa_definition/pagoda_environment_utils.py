from hera.workflows import (
    ConfigMapEnvFrom,
    ExistingVolume,
    Parameter,
    script,
)


@script(
    env=[
        # Assumes the corresponding config map is defined at k8s level
        ConfigMapEnvFrom(
            config_map_name="{{inputs.parameters.config_map_name}}",
            optional=False,
        )
    ]
)
def print_pagoda_environment(
    # Implicit arguments refered above by the @script() decorator (and oddly
    # enough required by Hera altough not used by the function)
    config_map_name,
):
    import os
    import json

    print("Hera on PaGoDa can run python scripts...")
    print(
        "...and retrieve environment variables: ",
        json.dumps(dict(os.environ), indent=4),
    )
    print("Done.")


@script(
    inputs=[
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def list_pesistent_volume_files(
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    claim_name,
    mount_path,
):
    import os

    print(
        "Numerical experiment environment: persistent volume claim_name is ",
        claim_name,
    )
    print(
        "Numerical experiment environment: persistent volume mount path ",
        mount_path,
    )
    print(
        "Numerical experiment persistent volume directory list: ",
        os.listdir(mount_path),
    )
    print("Done.")
