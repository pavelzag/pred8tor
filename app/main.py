import argparse
import logging
import os
import pathlib
import platform
import sys
import time
from distutils import util

from kubernetes import client, dynamic

from k8s_client.api_client import K8sApiClient

LOG_FILE_NAME = 'pred8tor.log'
if platform.system().upper() == 'DARWIN':
    log_file = pathlib.Path(os.getcwd(), LOG_FILE_NAME)
else:
    log_file = f'/var/log/{LOG_FILE_NAME}'

# Configure the logger to write to the log file and stdout
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
if not logging.getLogger().hasHandlers():
    logging.getLogger().addHandler(stdout_handler)

POD = 'pod'
DEPLOYMENT = 'deployment'
DAEMONSET = 'daemonset'
APPLICATIONSET = 'applicationset'
SERVICE = 'service'
NAMESPACE = 'namespace'
EXPIRATION_TIME = 'expiration_time'


def has_time_passed(epoch_time: int) -> bool:
    current_time = time.time()
    if current_time > epoch_time:
        return True
    else:
        return False


def delete_object(object_type: str, namespace: str, object_name: str, apps_api, core_api, dyn_client) -> None:
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
        elif object_type == APPLICATIONSET:
            applicationset_resource = dyn_client.resources.get(api_version='argoproj.io/v1alpha1',
                                                               kind='ApplicationSet')
            dyn_client.delete(resource=applicationset_resource, name=object_name, namespace=namespace)
            logging.info(f"{object_type.capitalize()} {object_name} deleted")
        elif object_type == DAEMONSET:
            apps_api.delete_namespaced_daemon_set(name=object_name, namespace=namespace)
            logging.info(f"Daemonset {object_name} deleted")
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
    parser.add_argument('--all-objects', action='store', help='Delete all objects', default="true")
    parser.add_argument('--delete-applicationset', action='store', help='Delete applicationsets', default="false")
    parser.add_argument('--delete-daemonset', action='store', help='Delete daemonsets', default="false")
    parser.add_argument('--delete-deployment', action='store', help='Delete deployments', default="false")
    parser.add_argument('--delete-pod', action='store', help='Delete pods', default="false")
    parser.add_argument('--delete-service', action='store', help='Delete services', default="false")
    parser.add_argument('--delete-namespace', action='store', help='Delete namespaces', default="false")
    parser.add_argument('--debug-mode', action='store', help='Debug Mode', default="true")
    parser.add_argument('--in-cluster-mode', action='store', help='InCluster Mode', default="true")
    parser.add_argument('--context-name', action='store', help='Cluster Name', default="minikube")

    args = parser.parse_args()
    all_objects = bool(util.strtobool(args.all_objects))
    delete_deployment = bool(util.strtobool(args.delete_deployment))
    delete_daemonset = bool(util.strtobool(args.delete_daemonset))
    delete_applicationset = bool(util.strtobool(args.delete_applicationset))
    delete_pod = bool(util.strtobool(args.delete_pod))
    delete_service = bool(util.strtobool(args.delete_service))
    delete_namespace = bool(util.strtobool(args.delete_namespace))
    debug_mode = bool(util.strtobool(args.debug_mode))
    in_cluster_mode = bool(util.strtobool(args.in_cluster_mode))
    context_name = args.context_name

    k8s_api = K8sApiClient(in_cluster_mode, context_name,
                           debug_mode)
    api_client = k8s_api.fetch_api_client()
    core_api = client.CoreV1Api(api_client=api_client)
    apps_api = client.AppsV1Api(api_client=api_client)
    dyn_client = dynamic.DynamicClient(api_client)

    if delete_applicationset or all_objects:
        logging.info("\nChecking labels for Applicationsets to delete:")
        try:
            api_resource = dyn_client.resources.get(api_version='argoproj.io/v1alpha1',
                                                       kind='ApplicationSet')
            application_sets = api_resource.get()
            for appset in application_sets.items:
                if appset.metadata.labels is not None:
                    if EXPIRATION_TIME in appset.metadata.labels.to_dict():
                        if appset.metadata.labels['expiration_time'].isdigit():
                            if has_time_passed(epoch_time=int(appset.metadata.labels['expiration_time'])):
                                logging.info(f'Expiration time is up for {appset.metadata.name} {APPLICATIONSET}')
                                delete_object(object_type=APPLICATIONSET, object_name=appset.metadata.name,
                                              namespace=appset.metadata.namespace, apps_api=apps_api, core_api=core_api,
                                              dyn_client=dyn_client)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch deployments due to {e}')

    if delete_daemonset or all_objects:
        logging.info("\nChecking labels for Daemonsets to delete:")
        try:
            daemonsets = apps_api.list_daemon_set_for_all_namespaces(watch=False)
            for ds in daemonsets.items:
                if ds.metadata.labels is not None:
                    if EXPIRATION_TIME in ds.metadata.labels:
                        if ds.metadata.labels['expiration_time'].isdigit():
                            if has_time_passed(epoch_time=int(ds.metadata.labels['expiration_time'])):
                                logging.info(f'Expiration time is up for {ds.metadata.name} {DAEMONSET}')
                                delete_object(object_type=DAEMONSET, object_name=ds.metadata.name,
                                              namespace=ds.metadata.namespace, apps_api=apps_api, core_api=core_api,
                                              dyn_client=dyn_client)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch deployments due to {e}')
    if delete_deployment or all_objects:
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
                                              namespace=dep.metadata.namespace, apps_api=apps_api, core_api=core_api,
                                              dyn_client=dyn_client)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch deployments due to {e}')

    if delete_pod or all_objects:
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
                                              apps_api=apps_api, core_api=core_api, dyn_client=dyn_client)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch pods due to {e}')

    if delete_service or all_objects:
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
                                              object_name=svc.metadata.name, apps_api=apps_api, core_api=core_api,
                                              dyn_client=dyn_client)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch services due to {e}')

    if delete_namespace or all_objects:
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
                                              object_name=ns.metadata.name, apps_api=apps_api, core_api=core_api,
                                              dyn_client=dyn_client)
        except client.exceptions.ApiException as e:
            logging.error(f'Failed to fetch namespaces due to {e}')


if __name__ == '__main__':
    while True:
        main()
        logging.info(f'Taking a short nap')
        time.sleep(10)
