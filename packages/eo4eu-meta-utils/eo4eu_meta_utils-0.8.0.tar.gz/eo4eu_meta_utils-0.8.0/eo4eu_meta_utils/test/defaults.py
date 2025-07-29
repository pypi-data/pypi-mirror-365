
def default_kafka() -> dict:
    return {
        "image": "confluentinc/confluent-local:7.4.1",
        "hostname": "kafka",
        "container_name": "kafka",
        "ports": ["9092:9092"],
        "environment": {
            "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092",
            "KAFKA_CONTROLLER_QUORUM_VOTERS": "1@kafka:29093",
            "KAFKA_LISTENERS": "PLAINTEXT://kafka:29092,CONTROLLER://kafka:29093,PLAINTEXT_HOST://0.0.0.0:9092",
        },
        "healthcheck": {
            "test": ["CMD", "sleep", "1"],
            "retries": 0,
            "start_period": "15s",
            "start_interval": "0s"
        }
    }


def default_producer(
    config_dir: str,
    message_dir: str = "/var/kafka_messages",
    depends_on: dict|None = None
):
    if depends_on is None:
        depends_on = {}

    name = "at_prod"
    return {
        "hostname": name,
        "container_name": name,
        "image": "registry.apps.eo4eu.eu/eo4eu/eo4eu-provision-handler/utils/autotest-utils/autotest-producer:latest",
        "environment": [
            "BOOTSTRAP_SERVERS=kafka:29092",
            "GROUP_ID=at_prod",
            f"MESSAGE_DIR={message_dir}/*"
        ],
        "depends_on": {
            "at_serv": {"condition": "service_healthy"},
        } | depends_on,
        "volumes": [
            f"{config_dir}:{message_dir}"
        ]
    }


def default_service(config_dir: str):
    name = "at_serv"
    return {
        "hostname": name,
        "container_name": name,
        "image": "registry.apps.eo4eu.eu/eo4eu/eo4eu-provision-handler/utils/autotest-utils/autotest-service:latest",
        "environment": [
            "BOOTSTRAP_SERVERS=kafka:29092",
            "GROUP_ID=at_serv",
            "CONFIG_FILE=/var/config/autotest_service.json",
        ],
        "depends_on": {
            "kafka": {"condition": "service_healthy"},
        },
        "volumes": [
            f"{config_dir}:/var/config",
        ]
    }


def default_canary():
    return {
        "version": "0.1.4",
        "options": {
            "interval_sec": 2,
            "max_misses": 5,
            "initial_max_misses": 10,
        },
        "check": {
            "interval": "2s",
            "start_period": "0s",
            "start_interval": "0s"
        },
        "gitlab": {
            "username": "GITLAB_USERNAME",
            "token": "GITLAB_TOKEN",
        }
    }
