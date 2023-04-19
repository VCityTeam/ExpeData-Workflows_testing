from hera import (
    ConfigMapEnvFrom,
    ImagePullPolicy,
    RetryStrategy,
    Task,
)


def send_command_to_postgres_db_task(cluster, command, limit=0):
    task = Task(
        "sendcommandtopostgresdb",
        retry_strategy=RetryStrategy(limit=limit),
        image=cluster.docker_registry + "vcity/postgres:15.2",
        image_pull_policy=ImagePullPolicy.IfNotPresent,
        env=[
            # Assumes the corresponding config map is defined in the k8s cluster
            ConfigMapEnvFrom(config_map_name=cluster.configmap, optional=False)
        ],
        command=["/bin/bash", "-c"],
        args=[command],
    )
    return task


def readinessProbe_task(cluster, parameters, host_ip, retry_limit):
    command = (
        "exec pg_isready -U "
        + parameters.database.user
        + " -h " + host_ip + " -p "
        + parameters.database.port
    )
    return send_command_to_postgres_db_task(cluster, command, retry_limit)


