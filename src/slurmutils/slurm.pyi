# Copyright 2025 Canonical Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

from .core.base import Mode, Model, ModelList, ModelMapping, classproperty
from .core.callback import Callback
from .core.editor import BaseEditor

MCSParametersCallback: Callback = ...

class DownNodes(Model):
    down_nodes: list[str] | None
    reason: str | None
    state: str | None
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_mode__(cls) -> Mode: ...  # noqa N804

class FrontendNode(Model):
    frontend_name: str | None
    frontend_addr: str | None
    allow_groups: list[str] | None
    allow_users: list[str] | None
    deny_groups: list[str] | None
    deny_users: list[str] | None
    port: int | None
    reason: str | None
    state: str | None
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_mode__(cls) -> Mode: ...  # noqa N804

class Node(Model):
    node_name: str | None
    node_hostname: str | None
    node_addr: str | None
    bcast_addr: str | None
    boards: int | None
    core_spec_count: int | None
    cores_per_socket: int | None
    cpu_bind: str | None
    cpus: int | None
    cpu_spec_list: list[int] | None
    features: list[str] | None
    gres: list[str] | None
    mem_spec_limit: int | None
    port: int | None
    procs: int | None
    real_memory: int | None
    reason: str | None
    sockets: int | None
    sockets_per_board: int | None
    state: str | None
    threads_per_core: int | None
    tmp_disk: int | None
    weight: int | None
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_mode__(cls) -> Mode: ...  # noqa N804

class NodeSet(Model):
    node_set: str | None
    feature: str | None
    nodes: list[str] | None
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_mode__(cls) -> Mode: ...  # noqa N804

class Partition(Model):
    partition_name: str | None
    alloc_nodes: list[str] | None
    allow_accounts: list[str] | None
    allow_groups: list[str] | None
    allow_qos: list[str] | None
    alternate: str | None
    cpu_bind: str | None
    default: bool | None
    default_time: int | str | None
    def_cpu_per_gpu: int | None
    def_mem_per_cpu: int | None
    def_mem_per_gpu: int | None
    def_mem_per_node: int | None
    deny_accounts: list[str] | None
    deny_qos: list[str] | None
    disable_root_jobs: bool | None
    exclusive_topo: bool | None
    exclusive_user: bool | None
    grace_time: int | None
    hidden: bool | None
    lln: bool | None
    max_cpus_per_node: int | None
    max_cpus_per_socket: int | None
    max_mem_per_cpu: int | None
    max_mem_per_node: int | None
    max_nodes: int | str | None
    max_time: int | str | None
    min_nodes: int | None
    nodes: list[str] | None
    over_subscribe: str | None
    over_time_limit: int | str | None
    power_down_on_idle: bool | None
    preempt_mode: str | None
    priority_job_factor: int | None
    priority_tier: int | None
    qos: str | None
    req_resv: bool | None
    resume_timeout: int | None
    root_only: bool | None
    select_type_parameters: list[str] | None
    state: str | None
    suspend_time: int | str | None
    suspend_timeout: int | None
    tres_billing_weights: dict[str, str] | None
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_mode__(cls) -> Mode: ...  # noqa N804

class DownNodesList(ModelList[DownNodes]):
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]: ...  # noqa N804

class FrontendNodeMapping(ModelMapping[str, FrontendNode]):
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]: ...  # noqa N804

class NodeMapping(ModelMapping[str, Node]):
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]: ...  # noqa N804

class NodeSetMapping(ModelMapping[str, NodeSet]):
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]: ...  # noqa N804

class PartitionMapping(ModelMapping[str, Partition]):
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]: ...  # noqa N804

class SlurmConfig(Model):
    accounting_storage_backup_host: str | None
    accounting_storage_enforce: list[str] | None
    accounting_storage_external_host: str | None
    accounting_storage_host: str | None
    accounting_storage_parameters: dict[str, str | list[str]] | None
    accounting_storage_pass: str | None
    accounting_storage_port: int | None
    accounting_storage_tres: list[str] | None
    accounting_storage_type: str | None
    accounting_storage_user: str | None
    accounting_store_flags: list[str] | None
    acct_gather_node_freq: int | None
    acct_gather_energy_type: str | None
    acct_gather_interconnect_type: str | None
    acct_gather_filesystem_type: str | None
    acct_gather_profile_type: str | None
    allow_spec_resources_usage: bool | None
    auth_alt_types: list[str] | None
    auth_alt_parameters: dict[str, bool | int | str] | None
    auth_info: dict[str, bool | int | str] | None
    auth_type: str | None
    batch_start_timeout: int | None
    bcast_exclude: list[str] | None
    bcast_parameters: dict[str, bool | str] | None
    burst_buffer_type: str | None
    cli_filter_plugins: list[str] | None
    cluster_name: str | None
    communication_parameters: dict[str, bool | int] | None
    complete_wait: int | None
    cpu_freq_def: str | None
    cpu_freq_governors: list[str] | None
    cred_type: str | None
    debug_flags: list[str] | None
    def_cpu_per_gpu: int | None
    def_mem_per_cpu: int | None
    def_mem_per_gpu: int | None
    def_mem_per_node: int | None
    dependency_parameters: dict[str, bool | int] | None
    disable_root_jobs: bool | None
    eio_timeout: int | None
    enforce_part_limits: str | None
    epilog: str | None
    epilog_msg_time: int | None
    epilog_slurmctld: str | None
    fair_share_dampening_factor: int | None
    federation_parameters: dict[str, bool] | None
    first_job_id: int | None
    get_env_timeout: int | None
    gres_types: list[str] | None
    group_update_force: bool | None
    group_update_time: int | None
    gpu_freq_def: int | str | None
    health_check_interval: int | None
    health_check_node_state: list[str] | None
    health_check_program: str | None
    inactive_limit: int | None
    include: list[str] | None
    interactive_step_options: str | None
    job_acct_gather_type: str | None
    job_acct_gather_frequency: dict[str, int] | None
    job_acct_gather_params: dict[str, bool] | None
    job_comp_host: str | None
    job_comp_loc: str | None
    job_comp_params: dict[str, bool | int | str] | None
    job_comp_pass: str | None
    job_comp_port: int | None
    job_comp_type: str | None
    job_comp_user: str | None
    job_file_append: bool | None
    job_requeue: bool | None
    job_submit_plugins: list[str] | None
    kill_on_bad_exit: bool | None
    kill_wait: int | None
    max_batch_requeue: int | None
    namespace_type: str | None
    node_features_plugins: list[str] | None
    launch_parameters: dict[str, bool] | None
    licenses: dict[str, bool | int] | None
    log_time_format: str | None
    mail_domain: str | None
    mail_prog: str | None
    max_array_size: int | None
    max_dbd_msgs: int | None
    max_job_count: int | None
    max_job_id: int | None
    max_mem_per_cpu: int | None
    max_mem_per_node: int | None
    max_node_count: int | None
    max_step_count: int | None
    max_tasks_per_node: int | None
    mcs_parameters: dict[str, bool | list[str]] | None
    mcs_plugin: str | None
    message_timeout: int | None
    metrics_type: str | None
    min_job_age: int | None
    mpi_default: str | None
    mpi_params: dict[str, bool | str] | None
    over_time_limit: int | str | None
    plugin_dir: list[str] | None
    plug_stack_config: str | None
    preempt_mode: str | None
    preempt_parameters: dict[str, bool | int] | None
    preempt_type: str | None
    preempt_exempt_time: int | str | None
    pr_ep_parameters: dict[str, Any] | None
    pr_ep_plugins: list[str] | None
    priority_calc_period: int
    priority_decay_half_life: int | str | None
    priority_favor_small: bool | None
    priority_flags: list[str] | None
    priority_max_age: int | str | None
    priority_parameters: str | None
    priority_site_factor_parameters: str | None
    priority_site_factor_plugin: str | None
    priority_type: str | None
    priority_usage_reset_period: str | None
    priority_weight_age: int | None
    priority_weight_assoc: int | None
    priority_weight_fairshare: int | None
    priority_weight_job_size: int | None
    priority_weight_partition: int | None
    priority_weight_qos: int | None
    priority_weight_tres: dict[str, int] | None
    private_data: list[str] | None
    proctrack_type: str | None
    prolog: str | None
    prolog_epilog_timeout: int | None
    prolog_flags: list[str] | None
    prolog_slurmctld: str | None
    propagate_prio_process: int | None
    propagate_resource_limits: list[str] | None
    propagate_resource_limits_except: list[str] | None
    reboot_program: str | None
    reconfig_flags: list[str] | None
    requeue_exit: list[str | int] | None
    requeue_exit_hold: list[str | int] | None
    resume_fail_program: str | None
    resume_program: str | None
    resume_rate: int | None
    resume_timeout: int | None
    resv_epilog: str | None
    resv_over_run: int | str | None
    resv_prolog: str | None
    return_to_service: int | None
    scheduler_parameters: dict[str, bool | int | str] | None
    scheduler_time_slice: int | None
    scheduler_type: str | None
    scron_parameters: dict[str, bool] | None
    select_type: str | None
    select_type_parameters: dict[str, bool] | None
    slurmctld_addr: str | None
    slurmctld_debug: str | None
    slurmctld_host: list[str] | None
    slurmctld_log_file: str | None
    slurmctld_parameters: dict[str, bool | int | str] | None
    slurmctld_pid_file: str | None
    slurmctld_port: int | str | None
    slurmctld_primary_off_prog: str | None
    slurmctld_primary_on_prog: str | None
    slurmctld_syslog_debug: str | None
    slurmctld_timeout: int | None
    slurmd_debug: str | None
    slurmd_log_file: str | None
    slurmd_parameters: dict[str, bool | int] | None
    slurmd_pid_file: str | None
    slurmd_port: int | None
    slurmd_spool_dir: str | None
    slurmd_syslog_debug: str | None
    slurmd_timeout: int | None
    slurmd_user: str | None
    slurm_sched_log_file: str | None
    slurm_sched_log_level: bool | None
    slurm_user: str | None
    srun_epilog: str | None
    srun_port_range: str | None
    srun_prolog: str | None
    state_save_location: str | None
    suspend_exc_nodes: dict[str, bool | int] | None
    suspend_exc_parts: list[str] | None
    suspend_exc_states: list[str] | None
    suspend_program: str | None
    suspend_rate: int | None
    suspend_time: int | str | None
    suspend_timeout: int | None
    switch_parameters: dict[str, bool | int | str | list[str]] | None
    switch_type: str | None
    task_epilog: str | None
    task_plugin: list[str] | None
    task_plugin_param: dict[str, bool | str] | None
    task_prolog: str | None
    tcp_timeout: int | None
    tmpfs: str | None
    topology_param: dict[str, bool | int] | None
    topology_plugin: str | None
    track_wc_key: bool | None
    tree_width: int | None
    unkillable_step_program: str | None
    unkillable_step_timeout: int | None
    use_pam: bool | None
    v_size_factor: int | None
    wait_time: int | None
    x11_parameters: dict[str, bool] | None
    down_nodes: DownNodesList
    frontend_nodes: FrontendNodeMapping
    nodes: NodeMapping
    nodesets: NodeSetMapping
    partitions: PartitionMapping
    @classproperty
    def __model_schema__(cls) -> dict[str, Any]: ...  # noqa N804
    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]: ...  # noqa N804

class SlurmConfigEditor(BaseEditor):
    @property
    def __model__(self) -> type[SlurmConfig]: ...
    def dump(
        self,
        obj: SlurmConfig,
        /,
        file: str | os.PathLike,
        *,
        mode: int = 0o644,
        user: str | int | None = None,
        group: str | int | None = None,
    ) -> None: ...
    def dumps(self, obj: SlurmConfig, /) -> str: ...
    def load(self, file: str | os.PathLike, /) -> SlurmConfig: ...
    def loads(self, s: str, /) -> SlurmConfig: ...
    @contextmanager
    def edit(
        self,
        file: str | os.PathLike,
        *,
        mode: int = 0o644,
        user: int | str | None = None,
        group: int | str | None = None,
    ) -> Iterator[SlurmConfig]: ...

_down_nodes_list_model_builder: Callable[[Any], Any] = ...
_frontend_node_mapping_model_builder: Callable[[Any], Any] = ...
_node_mapping_model_builder: Callable[[Any], Any] = ...
_nodeset_mapping_model_builder: Callable[[Any], Any] = ...
_partition_mapping_model_builder: Callable[[Any], Any] = ...
_slurm_config_model_builder: Callable[[Any], Any] = ...
