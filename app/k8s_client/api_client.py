import logging
import os
import platform
import sys

import kubernetes.config
from kubernetes.client import ApiClient

LOG_FILE_NAME = 'pred8tor.log'
if 'macOS' in platform.platform():
    log_path = f'{os.getcwd()}'
else:
    log_path = '/var/log/'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{log_path}/{LOG_FILE_NAME}"),
        logging.StreamHandler(sys.stdout)
    ]
)


class K8sApiClient:
    def __init__(self, in_cluster_mode: bool = False, context_name: str = 'default', debug_mode: bool = True):
        self.in_cluster_mode = in_cluster_mode
        self.context_name = context_name
        self.debug_mode = debug_mode

    def fetch_api_client(self) -> ApiClient:
        if self.in_cluster_mode:
            try:
                kubernetes.config.load_incluster_config()
                return ApiClient()
            except kubernetes.config.ConfigException:
                logging.error(f'Error loading incluster configuration')
        else:
            clusters_contexts, _ = kubernetes.config.list_kube_config_contexts()
            for cluster_context in clusters_contexts:
                if cluster_context['name'] == self.context_name:
                    logging.info(f'Loading configuration for {self.context_name} context name')
                    api_client = kubernetes.config.new_client_from_config(context=self.context_name)
                    return api_client
