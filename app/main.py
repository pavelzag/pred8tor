import argparse
import logging
import os
import pathlib
import platform
import sys
import time

from kubernetes import client, config

from k8s_client.api_client import K8sApiClient

if platform.system().upper() == 'DARWIN':
    log_file = pathlib.Path(os.getcwd(), 'pred8tor.log')
else:
    log_file = '/var/log/pred8tor.log'

# Configure the logger to write to the log file and stdout
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.getLogger().addHandler(stdout_handler)

POD = 'pod'
DEPLOYMENT = 'deployment'
SERVICE = 'service'
NAMESPACE = 'namespace'
EXPIRATION_TIME = 'expiration_time'


def has_time_passed(epoch_time: int) -> bool:
    current_time = time.time()
    if current_time > epoch_time:
        return True
    else:
        return False


def delete_object(object_type: str, namespace: str, object_name: str, apps_api, core_api) -> None:
    try:
        if object_type == DEPLOYMENT:

            apps_api.delete_namespaced_deployment(
                name=object_name,
                namespace=namespace,
                body=client.V1DeleteOptions(
                    propagation_policy='Foreground',
                    grace_period_seconds=5
                )
            )
            logging.info(f"Deployment {object_name} deleted")
        elif object_type == POD:
            core_api.delete_namespaced_pod(name=object_name, namespace=namespace)
            logging.info(f"Pod {object_name} deleted")
        elif object_type == SERVICE:
            core_api.delete_namespaced_service(name=object_name, namespace=namespace)
            logging.info(f"Service {object_name} deleted")
        elif object_type == NAMESPACE:
            core_api.delete_namespace(name=object_name)
            logging.info(f"Namespace {object_name} deleted")
    except client.exceptions.ApiException as e:
        logging.error(f"Exception when deleting {object_type}: {e}")


def main():
    parser = argparse.ArgumentParser(description='Kubernetes object management script')
    parser.add_argument('--all-objects', action='store_true', help='Delete all objects', default=True)
    parser.add_argument('--delete-deployment', action='store_true', help='Delete deployments', default=False)
    parser.add_argument('--delete-pod', action='store_true', help='Delete pods', default=False)
    parser.add_argument('--delete-service', action='store_true', help='Delete services', default=False)
    parser.add_argument('--delete-namespace', action='store_true', help='Delete namespaces', default=False)
    parser.add_argument('--debug-mode', action='store_true', help='Debug Mode', default=True)
    parser.add_argument('--in-cluster-mode', action='store_true', help='InCluster Mode', default=True)
    parser.add_argument('--context-name', action='store_true', help='Cluster Name', default="default")

    args = parser.parse_args()
    k8s_api = K8sApiClient(in_cluster_mode=args.in_cluster_mode, context_name=args.context_name,
                           debug_mode=args.debug_mode)
    api_client = k8s_api.fetch_api_client()
    core_api = client.CoreV1Api(api_client=api_client)
    apps_api = client.AppsV1Api(api_client=api_client)

    if args.delete_deployment or args.all_objects:
        logging.info("\nChecking labels for Deployments to delete:")
        try:
            deployments = apps_api.list_deployment_for_all_namespaces(watch=False)
            for dep in deployments.items:
                if dep.metadata.labels is not None:
                    if EXPIRATION_TIME in dep.metadata.labels:
                        if dep.metadata.labels['expiration_time'].isdigit():
                            if has_time_passed(epoch_time=int(dep.metadata.labels['expiration_time'])):
                                logging.info(f'Expiration time is up for {dep.metadata.name} {DEPLOYMENT}')
                                delete_object(object_type=DEPLOYMENT, object_name=dep.metadata.name,
                                              namespace=dep.metadata.namespace, apps_api=apps_api, core_api=core_api)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch deployments due to {e}')

    if args.delete_pod or args.all_objects:
        logging.info("\nChecking labels for Namespace to delete:")
        try:
            pods = core_api.list_pod_for_all_namespaces(watch=False)
            for pod in pods.items:
                if pod.metadata.labels is not None:
                    if EXPIRATION_TIME in pod.metadata.labels:
                        if pod.metadata.labels['expiration_time'].isdigit():
                            if has_time_passed(epoch_time=int(pod.metadata.labels['expiration_time'])):
                                logging.info(f'Expiration time is up for {pod.metadata.name} {POD}')
                                delete_object(object_type=POD, namespace=pod.metadata.namespace,
                                              object_name=pod.metadata.name,
                                              apps_api=apps_api, core_api=core_api)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch pods due to {e}')

    if args.delete_service or args.all_objects:
        logging.info("\nChecking labels for Services to delete:")
        try:
            services = core_api.list_service_for_all_namespaces(watch=False)
            for svc in services.items:
                if svc.metadata.labels is not None:
                    if EXPIRATION_TIME in svc.metadata.labels:
                        if svc.metadata.labels['expiration_time'].isdigit():
                            if has_time_passed(epoch_time=int(svc.metadata.labels['expiration_time'])):
                                logging.info(f'Expiration time is up for {svc.metadata.name} {SERVICE}')
                                delete_object(object_type=SERVICE, namespace=svc.metadata.namespace,
                                              object_name=svc.metadata.name, apps_api=apps_api, core_api=core_api)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch services due to {e}')

    if args.delete_namespace or args.all_objects:
        logging.info("\nChecking labels for Namespaces to delete:")
        try:
            namespaces = core_api.list_namespace(watch=False)
            for ns in namespaces.items:
                if ns.metadata.labels is not None:
                    if EXPIRATION_TIME in ns.metadata.labels:
                        if ns.metadata.labels['expiration_time'].isdigit():
                            if has_time_passed(epoch_time=int(ns.metadata.labels['expiration_time'])):
                                logging.info(f'Expiration time is up for {ns.metadata.name} {NAMESPACE}')
                                delete_object(object_type=NAMESPACE, namespace=ns.metadata.name,
                                              object_name=ns.metadata.name, apps_api=apps_api, core_api=core_api)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch namespaces due to {e}')


if __name__ == '__main__':
    while True:
        main()
        logging.info(f'Taking a short nap')
        time.sleep(10)
