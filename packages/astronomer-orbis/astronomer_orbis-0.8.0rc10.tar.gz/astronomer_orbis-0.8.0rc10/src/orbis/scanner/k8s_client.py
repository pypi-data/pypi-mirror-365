import base64
import hashlib
import logging
import os
import shlex
import time
from pathlib import Path
from typing import cast

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

from orbis.scanner.models import JobStatus, ScannerConfig
from orbis.utils.logger import get_early_logger


class K8sClient:
    """Kubernetes operations for scanner using Python client."""

    def __init__(self, kubeconfig_path: str | None = None, logger: logging.Logger | None = None):
        # Use provided logger or fallback to early logger for backwards compatibility
        self.logger = logger if logger else get_early_logger()
        self._load_config(kubeconfig_path)

        # Initialize API clients
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
        self.rbac_v1 = client.RbacAuthorizationV1Api()

    def _load_config(self, kubeconfig_path: str | None = None):
        """Load Kubernetes configuration with priority order."""
        try:
            if kubeconfig_path:
                # 1. Explicit path provided
                config.load_kube_config(config_file=kubeconfig_path)
                self.logger.info(f"Loaded config from: {kubeconfig_path}")
            elif os.getenv("KUBECONFIG"):
                # 2. KUBECONFIG environment variable
                config.load_kube_config(config_file=os.getenv("KUBECONFIG"))
                self.logger.info(f"Loaded config from KUBECONFIG: {os.getenv('KUBECONFIG')}")
            elif Path.home().joinpath(".kube/config").exists():
                # 3. Default location
                config.load_kube_config()
                self.logger.info("Loaded config from ~/.kube/config")
            else:
                # 4. In-cluster config (for pods)
                config.load_incluster_config()
                self.logger.info("Loaded in-cluster config")
        except Exception as e:
            raise RuntimeError(f"Failed to load Kubernetes config: {e}")

    def create_service_account(self, config: ScannerConfig) -> bool:
        """Create service account using Python client."""
        try:
            sa_body = client.V1ServiceAccount(metadata=client.V1ObjectMeta(name=config.service_account_name, namespace=config.namespace, labels={"app": "support-bundle", "component": "scanner"}))

            self.core_v1.create_namespaced_service_account(namespace=config.namespace, body=sa_body)
            self.logger.info(f"Created ServiceAccount: {config.service_account_name}")
            return True

        except ApiException as e:
            if e.status == 409:  # Already exists
                self.logger.info(f"ServiceAccount {config.service_account_name} already exists")
                return True
            else:
                self.logger.error(f"Failed to create ServiceAccount: {e}")
                raise

    def create_cluster_role_binding(self, config: ScannerConfig) -> bool:
        """Create cluster role and cluster role binding."""
        try:
            # First, create the custom ClusterRole
            cluster_role_body = client.V1ClusterRole(
                metadata=client.V1ObjectMeta(name="read-support-bundle", labels={"app": "support-bundle", "component": "scanner"}),
                rules=[
                    client.V1PolicyRule(
                        api_groups=[""],
                        resources=[
                            "namespaces",
                            "pods",
                            "pods/log",
                            "pods/status",
                            "pods/ephemeralcontainers",
                            "configmaps",
                            "secrets",
                            "services",
                            "persistentvolumes",
                            "persistentvolumeclaims",
                            "endpoints",
                            "events",
                            "resourcequotas",
                            "limitranges",
                            "replicationcontrollers",
                            "nodes",
                        ],
                        verbs=["get", "list", "watch"],
                    ),
                    client.V1PolicyRule(api_groups=["apps"], resources=["deployments", "daemonsets", "statefulsets", "replicasets"], verbs=["get", "list", "watch"]),
                    client.V1PolicyRule(api_groups=["batch"], resources=["jobs", "cronjobs"], verbs=["get", "list", "watch"]),
                    client.V1PolicyRule(api_groups=["networking.k8s.io"], resources=["ingresses", "networkpolicies"], verbs=["get", "list", "watch"]),
                    client.V1PolicyRule(api_groups=["apiextensions.k8s.io"], resources=["customresourcedefinitions"], verbs=["get", "list", "watch"]),
                    client.V1PolicyRule(api_groups=["operators.coreos.com"], resources=["*"], verbs=["get", "list", "watch"]),
                ],
            )

            try:
                self.rbac_v1.create_cluster_role(body=cluster_role_body)
                self.logger.info("Created ClusterRole: read-support-bundle")
            except ApiException as e:
                if e.status == 409:
                    self.logger.info("ClusterRole read-support-bundle already exists")
                else:
                    self.logger.error(f"Failed to create ClusterRole: {e}")
                    raise

            # Now create the ClusterRoleBinding
            crb_body = client.V1ClusterRoleBinding(
                metadata=client.V1ObjectMeta(name=config.role_binding_name, labels={"app": "support-bundle", "component": "scanner"}),
                role_ref=client.V1RoleRef(
                    api_group="rbac.authorization.k8s.io",
                    kind="ClusterRole",
                    name="read-support-bundle",  # Changed from cluster-admin to custom role
                ),
                subjects=[client.RbacV1Subject(kind="ServiceAccount", name=config.service_account_name, namespace=config.namespace)],
            )

            self.rbac_v1.create_cluster_role_binding(body=crb_body)
            self.logger.info(f"Created ClusterRoleBinding: {config.role_binding_name}")
            return True

        except ApiException as e:
            if e.status == 409:
                self.logger.info(f"ClusterRoleBinding {config.role_binding_name} already exists")
                return True
            else:
                self.logger.error(f"Failed to create ClusterRoleBinding: {e}")
                raise

    def create_job(self, config: ScannerConfig) -> str:
        """Create scanner job with proper resource definitions."""
        scanner_args = config.build_scanner_command_args()
        scanner_command = f"scanner.py {' '.join(scanner_args)} && cp /data/*.tar.gz /results/"

        job_body = client.V1Job(
            metadata=client.V1ObjectMeta(name=config.job_name, namespace=config.namespace, labels={"app": "support-bundle", "component": "scanner"}),
            spec=client.V1JobSpec(
                backoff_limit=0,
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": "support-bundle", "component": "scanner"}),
                    spec=client.V1PodSpec(
                        service_account_name=config.service_account_name,
                        restart_policy="Never",
                        init_containers=[
                            client.V1Container(
                                name="scanner-init",
                                image=config.image,
                                command=["/bin/bash", "-c"],
                                args=[scanner_command],
                                volume_mounts=[client.V1VolumeMount(name="results-file", mount_path="/results")],
                                resources=client.V1ResourceRequirements(limits={"memory": config.memory, "cpu": config.cpu}, requests={"memory": "200Mi", "cpu": "200m"}),
                            )
                        ],
                        containers=[
                            client.V1Container(
                                name="main",
                                image=config.image,
                                command=["/bin/bash", "-c"],
                                args=[f"echo 'Data collection complete. Sleeping for {config.validated_sleep_duration} seconds' && sleep {config.validated_sleep_duration}"],
                                volume_mounts=[client.V1VolumeMount(name="results-file", mount_path="/results")],
                                resources=client.V1ResourceRequirements(limits={"memory": "200Mi", "cpu": "200m"}, requests={"memory": "100Mi", "cpu": "100m"}),
                            )
                        ],
                        volumes=[client.V1Volume(name="results-file", empty_dir=client.V1EmptyDirVolumeSource())],
                    ),
                ),
            ),
        )

        try:
            job = cast(client.V1Job, self.batch_v1.create_namespaced_job(namespace=config.namespace, body=job_body))
            if job.metadata and job.metadata.name:
                self.logger.info(f"Created job: {job.metadata.name}")
                return job.metadata.name
            else:
                raise RuntimeError("Job created but metadata is missing")

        except ApiException as e:
            self.logger.error(f"Failed to create job: {e}")
            raise

    def get_job_status(self, job_name: str, namespace: str) -> JobStatus:
        """Get comprehensive job status with rich information."""
        try:
            job = cast(client.V1Job, self.batch_v1.read_namespaced_job_status(name=job_name, namespace=namespace))

            if not job.metadata or not job.status:
                raise RuntimeError("Job metadata or status is missing")

            status = JobStatus(
                name=job.metadata.name or "",
                namespace=job.metadata.namespace or "",
                creation_time=job.metadata.creation_timestamp,
                start_time=job.status.start_time,
                completion_time=job.status.completion_time,
                active=job.status.active or 0,
                succeeded=job.status.succeeded or 0,
                failed=job.status.failed or 0,
            )

            if job.status.conditions:
                for condition in job.status.conditions:
                    status.conditions.append({
                        "type": condition.type,
                        "status": condition.status,
                        "reason": condition.reason,
                        "message": condition.message,
                        "last_transition_time": condition.last_transition_time,
                    })

                    if condition.type == "Complete" and condition.status == "True":
                        status.ready = True

            # Get pod information
            pod_name = self.find_scanner_pod(namespace)
            if pod_name:
                status.pod_name = pod_name
                pod = cast(client.V1Pod, self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace))
                if pod.status:
                    status.pod_status = pod.status.phase

                    init_statuses = getattr(pod.status, "init_container_statuses", []) or []
                    for init_cs in init_statuses:
                        if init_cs.name == "scanner-init":
                            state = getattr(init_cs, "state", None)
                            if state and state.terminated and state.terminated.exit_code == 0:
                                if not status.ready:
                                    self.logger.info("Init container 'scanner-init' has terminated successfully - setting status.ready = True for early Data Ready indication.")
                                status.ready = True

            return status

        except ApiException as e:
            self.logger.error(f"Failed to get job status: {e}")
            raise

    def find_scanner_pod(self, namespace: str) -> str | None:
        """Find scanner pod by label selector."""
        try:
            pods = cast(client.V1PodList, self.core_v1.list_namespaced_pod(namespace=namespace, label_selector="component=scanner"))

            if not pods.items:
                self.logger.error(f"No scanner pods found in namespace {namespace} with label component=scanner")
                return None

            if len(pods.items) > 1:
                self.logger.warning(f"Found {len(pods.items)} scanner pods, using the first one: {pods.items[0].metadata.name}")

            selected_pod = pods.items[0]
            pod_name = selected_pod.metadata.name
            pod_status = selected_pod.status.phase if selected_pod.status else "Unknown"

            self.logger.info(f"Selected scanner pod: {pod_name} (status: {pod_status})")

            if pod_status not in ["Running", "Succeeded"]:
                self.logger.warning(f"Pod {pod_name} is in {pod_status} state, file copy may fail")

            return pod_name

        except ApiException as e:
            self.logger.error(f"Failed to find scanner pod: {e}")
            return None

    def _check_init_container_completion(self, pod_name: str, namespace: str, remote_bundle_path: str) -> bool:
        """Check if scanner-init container has completed and bundle file exists.

        Returns True if init container completed successfully and bundle exists.
        """
        try:
            pod = self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            init_statuses = pod.status.init_container_statuses or []

            for ics in init_statuses:
                if ics.name == "scanner-init":
                    state = ics.state
                    # Check if terminated with exit code 0
                    if state and state.terminated and state.terminated.exit_code == 0:
                        terminated_at = state.terminated.finished_at
                        self.logger.info(f"Init container 'scanner-init' completed successfully at {terminated_at}.")

                        # Check if support bundle file exists
                        return self._verify_bundle_file_exists(pod_name, namespace, remote_bundle_path)
            return False
        except Exception as e:
            self.logger.error(f"Error checking init container completion: {e}")
            return False

    def _is_init_container_running(self, pod_name: str, namespace: str) -> bool:
        """Check if scanner-init container is currently running.

        Returns True if init container is in running state.
        """
        try:
            pod = self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            init_statuses = pod.status.init_container_statuses or []

            for ics in init_statuses:
                if ics.name == "scanner-init":
                    state = ics.state
                    if state and state.running:
                        self.logger.info("Init container 'scanner-init' is currently running.")
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking init container running state: {e}")
            return False

    def _verify_bundle_file_exists(self, pod_name: str, namespace: str, remote_bundle_path: str) -> bool:
        """Verify that the support bundle file exists in the pod."""
        try:
            # Use a compound command: test existence and get file info if it exists
            sanitized_path = shlex.quote(remote_bundle_path)
            exec_command = ["sh", "-c", f"test -f {sanitized_path} && ls -l {sanitized_path}"]
            resp = stream(
                self.core_v1.connect_get_namespaced_pod_exec,
                pod_name,
                namespace,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )

            # If file exists, ls will output file details; if not, empty response
            if resp.strip():
                file_info = resp.strip().splitlines()
                self.logger.info(f"Support bundle file confirmed: {file_info[-1]}")
                self.logger.info("EARLY JOB EXIT: Detected support bundle present and init container done. Returning success.")
                return True
            else:
                self.logger.warning(f"Init container done, but support bundle file does not exist at '{remote_bundle_path}' yet.")
                return False

        except Exception as e:
            self.logger.error(f"Error checking for support bundle after init container: {e}")
            return False

    def _discover_and_log_pod(self, job_name: str, namespace: str, status: JobStatus) -> str | None:
        """Discover scanner pod and log it once when first found."""
        pod_name = status.pod_name or self.find_scanner_pod(namespace)
        if pod_name:
            self.logger.info(f"Monitoring pod for init container completion: {pod_name}")
        return pod_name

    def wait_for_job_completion(self, job_name: str, namespace: str, config: ScannerConfig, timeout: int | None = None) -> tuple[bool, bool]:
        """Wait for job completion or early readiness after scanner-init is finished.

        Returns:
            tuple[bool, bool]: (job_completed, init_container_running)
            - job_completed: True if job completed successfully
            - init_container_running: True if init container is still running (relevant when job_completed=False)

        Will return (True, False) when:
            - The scanner-init init container has terminated successfully (exit_code == 0)
            - The expected support bundle file exists in the pod

        Will return (False, True) when:
            - The job times out but init container is still running

        Will return (False, False) when:
            - The pod/job fails before completion
            - The bundle is not found or init container fails
            - The job times out and init container is not running
        """
        start_time = time.time()
        last_status = None
        discovered_pod_name = None
        self.logger.info("Entering custom job wait: will detect init container completion to trigger early exit.")

        # Use configurable timeout and polling intervals
        timeout = timeout or config.poll_timeout
        poll_interval = config.poll_interval
        error_retry_interval = config.error_retry_interval
        remote_bundle_path = config.remote_tar_path

        while time.time() - start_time < timeout:
            try:
                status = self.get_job_status(job_name, namespace)
                # Log job progress if changed
                current_status_str = f"Active={status.active}, Succeeded={status.succeeded}, Failed={status.failed}"
                if current_status_str != last_status:
                    self.logger.info(f"Job {job_name}: {current_status_str}")
                    last_status = current_status_str

                if status.succeeded and status.succeeded > 0:
                    self.logger.info("Job completed successfully (via Job .status.succeeded).")
                    return True, False
                elif status.failed and status.failed > 0:
                    self.logger.error("Job failed.")
                    self._log_failed_job_details(job_name, namespace)
                    return False, False

                # Discover and log pod name once when first found
                if not discovered_pod_name:
                    discovered_pod_name = self._discover_and_log_pod(job_name, namespace, status)

                # Check init container status for early completion
                current_pod_name = status.pod_name or discovered_pod_name
                if current_pod_name:
                    if self._check_init_container_completion(current_pod_name, namespace, remote_bundle_path):
                        return True, False

                # sleep before next poll using configurable interval
                time.sleep(poll_interval)

            except ApiException as e:
                self.logger.warning(f"Error checking job status: {e}")
                time.sleep(error_retry_interval)
            except Exception as exc:
                self.logger.error(f"Unexpected error in wait_for_job_completion: {exc}")
                time.sleep(error_retry_interval)

        # Timeout reached - check if init container is still running
        current_pod_name = discovered_pod_name or self.find_scanner_pod(namespace)
        init_container_running = False
        if current_pod_name:
            init_container_running = self._is_init_container_running(current_pod_name, namespace)

        self._log_job_timeout(job_name, namespace, timeout, discovered_pod_name, remote_bundle_path, init_container_running)
        return False, init_container_running

    def _log_job_timeout(self, job_name: str, namespace: str, timeout: int, discovered_pod_name: str | None, remote_bundle_path: str, init_container_running: bool = False) -> None:
        """Log job timeout scenarios with appropriate error messages."""
        if not discovered_pod_name:
            self.logger.error(f"Job {job_name} timed out after {timeout} seconds. Could not find associated pod.")
            return

        if init_container_running:
            self.logger.warning(f"Job {job_name} monitoring timed out after {timeout} seconds, but init container is still running.")
            self.logger.warning("Init container may still be making progress. Leaving resources intact for manual retrieval later.")
            self.logger.warning(f"To check progress: kubectl logs {discovered_pod_name} -n {namespace} -c scanner-init")
            self.logger.warning(f"To retrieve when ready: orbis scanner retrieve -a {namespace}")
        elif not self._check_init_container_completion(discovered_pod_name, namespace, remote_bundle_path):
            self.logger.error(f"Job {job_name} timed out after {timeout} seconds. Init container did not complete successfully.")
        else:
            self.logger.error(f"Job {job_name} timed out after {timeout} seconds. Bundle file was not found at {remote_bundle_path}.")

    def _log_failed_job_details(self, job_name: str, namespace: str):
        """Log details about failed job for debugging."""
        try:
            pod_name = self.find_scanner_pod(namespace)
            if pod_name:
                self.logger.error(f"Job '{job_name}' failed. Check pod logs: kubectl logs {pod_name} -n {namespace} -c scanner-init")
            else:
                self.logger.error(f"Job '{job_name}' failed but could not find associated pod")
        except Exception as e:
            self.logger.error(f"Could not get failed job details for '{job_name}': {e}")

    def copy_file_from_pod(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        """Copy file from pod using base64 encoding to avoid binary data corruption."""
        try:
            self.logger.info(f"Starting file copy from pod {pod_name}:{remote_path} to {local_path}")

            if not self._validate_remote_file_exists(pod_name, namespace, remote_path):
                return False

            if not self._validate_pod_readiness(pod_name, namespace):
                return False

            # Use base64 encoding to safely stream binary data
            exec_command = ["base64", remote_path]
            self.logger.info(f"Executing copy command on pod {pod_name}: {' '.join(exec_command)}")

            # Execute command and get base64 stream
            resp = stream(self.core_v1.connect_get_namespaced_pod_exec, pod_name, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False, _preload_content=False)

            # Collect base64 data from stream
            base64_data = self._collect_base64_data_from_stream(resp)
            if not base64_data:
                return False

            # Decode and write file
            if not self._decode_and_write_file(base64_data, local_path):
                return False

            # Verify file was copied successfully
            return self._verify_copied_file(local_path)

        except Exception as e:
            self.logger.error(f"Failed to copy file from pod {pod_name}:{remote_path} to {local_path}: {e}")
            # Log additional debug information
            self.logger.debug(f"Pod: {pod_name}, Namespace: {namespace}, Remote: {remote_path}, Local: {local_path}")

            self._log_detailed_error_context(pod_name, namespace, remote_path, str(e))
            return False

    def _collect_base64_data_from_stream(self, resp) -> str:
        """Collect base64 data from kubernetes stream response."""
        base64_data = ""
        stderr_output = []

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                stdout_data = resp.read_stdout()
                if stdout_data:
                    # Convert bytes to string if needed
                    if isinstance(stdout_data, bytes):
                        stdout_data = stdout_data.decode("utf-8", errors="replace")
                    base64_data += stdout_data

            if resp.peek_stderr():
                stderr_data = resp.read_stderr()
                if isinstance(stderr_data, bytes):
                    stderr_data = stderr_data.decode("utf-8", errors="replace")
                stderr_output.append(stderr_data)
                self.logger.warning(f"stderr: {stderr_data}")

        resp.close()

        # Log any collected stderr for debugging
        if stderr_output:
            full_stderr = "".join(stderr_output)
            self.logger.error(f"Command stderr output: {full_stderr}")

        # Clean up base64 data (remove newlines/whitespace)
        clean_base64 = "".join(base64_data.split())
        if not clean_base64:
            self.logger.error("No base64 data received from pod")
            return ""

        return clean_base64

    def _decode_and_write_file(self, base64_data: str, local_path: str) -> bool:
        """Decode base64 data and write to local file."""
        try:
            binary_data = base64.b64decode(base64_data)
            with open(local_path, "wb") as local_file:
                local_file.write(binary_data)
            return True
        except Exception as decode_error:
            self.logger.error(f"Failed to decode base64 data: {decode_error}")
            return False

    def _verify_copied_file(self, local_path: str) -> bool:
        """Verify that the copied file exists and has content."""
        if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
            file_size = os.path.getsize(local_path)
            self.logger.info(f"File copied successfully: {local_path} ({file_size} bytes)")
            return True
        else:
            if not os.path.exists(local_path):
                self.logger.error(f"File copy verification failed: {local_path} does not exist")
            else:
                self.logger.error(f"File copy verification failed: {local_path} has zero size")
            return False

    def verify_file_checksum(self, pod_name: str, namespace: str, remote_path: str, local_path: str) -> bool:
        """Verify file integrity using checksums."""
        try:
            # Get remote checksum
            exec_command = ["sha256sum", remote_path]
            resp = stream(self.core_v1.connect_get_namespaced_pod_exec, pod_name, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False)
            remote_checksum = resp.split()[0]

            # Calculate local checksum
            with open(local_path, "rb") as f:
                local_checksum = hashlib.sha256(f.read()).hexdigest()

            if remote_checksum == local_checksum:
                self.logger.info("File checksum verification passed")
                return True
            else:
                self.logger.error("File checksum verification failed")
                return False

        except Exception as e:
            self.logger.error(f"Checksum verification failed: {e}")
            return False

    def cleanup_scanner_resources(self, namespace: str) -> None:
        """Clean up scanner resources: Jobs, Pods, ServiceAccount, ClusterRoleBinding, and ClusterRole."""
        self.logger.info(f"Cleaning up scanner resources in namespace: {namespace}")

        try:
            # Delete jobs
            jobs = self.batch_v1.list_namespaced_job(namespace=namespace, label_selector="component=scanner")
            for job in jobs.items:
                self.batch_v1.delete_namespaced_job(name=job.metadata.name, namespace=namespace)
                self.logger.info(f"Deleted job: {job.metadata.name}")

            # Delete pods
            pods = self.core_v1.list_namespaced_pod(namespace=namespace, label_selector="component=scanner")
            for pod in pods.items:
                self.core_v1.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
                self.logger.info(f"Deleted pod: {pod.metadata.name}")

            # Delete service account
            config = ScannerConfig(namespace=namespace)
            try:
                self.core_v1.delete_namespaced_service_account(name=config.service_account_name, namespace=namespace)
                self.logger.info("Deleted service account")
            except ApiException as e:
                if e.status != 404:
                    self.logger.warning(f"Failed to delete service account: {e}")

            # Delete cluster role binding
            try:
                self.rbac_v1.delete_cluster_role_binding(name=config.role_binding_name)
                self.logger.info("Deleted cluster role binding")
            except ApiException as e:
                if e.status != 404:
                    self.logger.warning(f"Failed to delete cluster role binding: {e}")

            # Delete custom cluster role (if it exists)
            try:
                self.rbac_v1.delete_cluster_role(name="read-support-bundle")
                self.logger.info("Deleted cluster role: read-support-bundle")
            except ApiException as e:
                if e.status != 404:
                    self.logger.warning(f"Failed to delete cluster role: {e}")

        except ApiException as e:
            self.logger.error(f"Error during cleanup: {e}")
            raise

    def _validate_remote_file_exists(self, pod_name: str, namespace: str, remote_path: str) -> bool:
        """Validate that the remote file exists before attempting copy."""
        try:
            self.logger.debug(f"Checking if remote file exists: {remote_path}")

            sanitized_path = shlex.quote(remote_path)
            exec_command = ["sh", "-c", f"test -f {sanitized_path} && ls -la {sanitized_path}"]
            resp = stream(self.core_v1.connect_get_namespaced_pod_exec, pod_name, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False)

            # If file exists, ls will output file details; if not, empty response
            if resp.strip():
                self.logger.info(f"Remote file exists: {remote_path}")
                self.logger.debug(f"File details: {resp.strip()}")
                return True
            else:
                self.logger.error(f"Remote file does not exist: {remote_path}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to validate remote file existence: {e}")
            return False

    def _validate_pod_readiness(self, pod_name: str, namespace: str) -> bool:
        """Validate that the pod is ready for file operations."""
        try:
            pod = cast(client.V1Pod, self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace))

            if not pod.status:
                self.logger.error(f"Pod {pod_name} has no status information")
                return False

            pod_phase = pod.status.phase
            self.logger.debug(f"Pod {pod_name} phase: {pod_phase}")

            if pod_phase == "Succeeded":
                # Pod has completed - cannot exec into containers, but files may still be accessible
                self.logger.warning(f"Pod {pod_name} is in 'Succeeded' state. Cannot exec into containers.")
                self.logger.warning("The scanner has completed but the main container has exited.")
                self.logger.warning("To retrieve the support bundle manually, run:")
                self.logger.warning(f"kubectl cp {pod_name}:/results/scanner-*.tar.gz ./scanner-bundle.tar.gz -n {namespace}")
                return False

            if pod_phase != "Running":
                self.logger.error(f"Pod {pod_name} is not in a ready state. Current phase: {pod_phase}")
                return False

            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    container_name = container_status.name
                    if not container_status.ready:
                        self.logger.warning(f"Container {container_name} in pod {pod_name} is not ready")

            self.logger.debug(f"Pod {pod_name} is ready for file operations")
            return True

        except Exception as e:
            self.logger.error(f"Failed to validate pod readiness: {e}")
            return False

    def _log_detailed_error_context(self, pod_name: str, namespace: str, remote_path: str, error_message: str) -> None:
        """Log detailed error context for debugging."""
        try:
            self.logger.error(f"=== Detailed Error Context for Pod {pod_name} ===")

            # Get pod status
            try:
                pod = cast(client.V1Pod, self.core_v1.read_namespaced_pod(name=pod_name, namespace=namespace))
                if pod.status:
                    self.logger.error(f"Pod phase: {pod.status.phase}")
                    if pod.status.container_statuses:
                        for cs in pod.status.container_statuses:
                            self.logger.error(f"Container {cs.name}: ready={cs.ready}, restartCount={cs.restart_count}")
                            if cs.state and cs.state.waiting:
                                self.logger.error(f"Container {cs.name} waiting: {cs.state.waiting.reason} - {cs.state.waiting.message}")
                            if cs.state and cs.state.terminated:
                                self.logger.error(f"Container {cs.name} terminated: {cs.state.terminated.reason} - {cs.state.terminated.message}")
            except Exception as e:
                self.logger.error(f"Could not get pod status: {e}")

            try:
                exec_command = ["ls", "-la", "/results"]
                resp = stream(self.core_v1.connect_get_namespaced_pod_exec, pod_name, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False)
                self.logger.error(f"Contents of /results directory: {resp}")
            except Exception as e:
                self.logger.error(f"Could not list /results directory: {e}")

            try:
                exec_command = ["find", "/results", "/data", "/tmp", "-name", "*.tar.gz", "-type", "f"]
                resp = stream(self.core_v1.connect_get_namespaced_pod_exec, pod_name, namespace, command=exec_command, stderr=True, stdin=False, stdout=True, tty=False)
                self.logger.error(f"All .tar.gz files in pod: {resp}")
            except Exception as e:
                self.logger.error(f"Could not search for .tar.gz files: {e}")

            self.logger.error(f"Original error: {error_message}")
            self.logger.error("=== End Error Context ===")

        except Exception as e:
            self.logger.error(f"Failed to gather error context: {e}")
