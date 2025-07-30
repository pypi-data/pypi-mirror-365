from importlib.resources import files

PRIVELAGED_USERS = [
    'root',
    'administrator'
]

INVALID_PROCESSES = [
	'zombie'
]

# This will be overriden by process sensor
SYSTEM_USERS = []

SENSOR_CONFIG_PATH = files("slurm_top_python.config").joinpath("sensors.yml")
GENERAL_CONFIG_PATH = files("slurm_top_python.config").joinpath("general.yml")
