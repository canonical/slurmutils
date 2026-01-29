# Copyright 2024-2025 Canonical Ltd.
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

"""Models representing the `slurm.conf` configuration file."""

__all__ = [
    "DownNodes",
    "DownNodesList",
    "FrontendNode",
    "FrontendNodeMapping",
    "Node",
    "NodeMapping",
    "NodeSet",
    "NodeSetMapping",
    "Partition",
    "PartitionMapping",
    "SlurmConfig",
    "SlurmConfigEditor",
]

from collections.abc import Callable, Iterable
from typing import Annotated, Any, cast

from .core.base import (
    Metadata,
    Mode,
    Model,
    ModelList,
    ModelMapping,
    classproperty,
    make_model_builder,
)
from .core.callback import (
    ColonSepCallback,
    CommaDictCallback,
    CommaDictColonArrayCallback,
    CommaDictColonPairCallback,
    CommaSepCallback,
    IntBoolCallback,
    MultilineCallback,
    QuoteCallback,
    StrBoolCallback,
    make_callback,
)
from .core.editor import BaseEditor
from .core.schema import (
    DOWN_NODES_LIST_MODEL_SCHEMA,
    DOWN_NODES_MODEL_SCHEMA,
    FRONTEND_NODE_MAPPING_MODEL_SCHEMA,
    FRONTEND_NODE_MODEL_SCHEMA,
    NODE_MAPPING_MODEL_SCHEMA,
    NODE_MODEL_SCHEMA,
    NODESET_MAPPING_MODEL_SCHEMA,
    NODESET_MODEL_SCHEMA,
    PARTITION_MAPPING_MODEL_SCHEMA,
    PARTITION_MODEL_SCHEMA,
    SLURM_CONFIG_MODEL_SCHEMA,
)


def _mcs_parameters_parser(value: str) -> dict[str, bool | list[str]]:
    params = value.split(":", maxsplit=1)
    result: dict[str, bool | list[str]] = dict.fromkeys(params[0].split(","), True)
    try:
        plugin_params = params[1]
        result["mcs_plugin_parameters"] = plugin_params.split("|")
    except IndexError:
        pass

    return result


def _mcs_parameters_marshaller(value: dict[str, bool | Iterable[str]]) -> str:
    plugin_params = "|".join(cast(Iterable[str], value.pop("mcs_plugin_parameters", [])))
    params = ",".join(k for k in value if value[k])
    if plugin_params:
        params += f":{plugin_params}"

    return params


MCSParametersCallback = make_callback(_mcs_parameters_parser, _mcs_parameters_marshaller)


class DownNodes(Model):
    """Model representing declared down nodes in the `slurm.conf` configuration file."""

    down_nodes: Annotated[list[str] | None, Metadata(primary=True, callback=CommaSepCallback)]
    reason: Annotated[str | None, Metadata(callback=QuoteCallback)]
    state: str | None

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return DOWN_NODES_MODEL_SCHEMA

    @classproperty
    def __model_mode__(cls) -> Mode:  # noqa N805
        return Mode.ONELINE


class FrontendNode(Model):
    """Model representing a frontend node in the `slurm.conf` configuration file."""

    frontend_name: Annotated[str | None, Metadata(primary=True)]
    frontend_addr: str | None
    allow_groups: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    allow_users: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    deny_groups: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    deny_users: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    port: int | None
    reason: Annotated[str | None, Metadata(callback=QuoteCallback)]
    state: str | None

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return FRONTEND_NODE_MODEL_SCHEMA

    @classproperty
    def __model_mode__(cls) -> Mode:  # noqa N805
        return Mode.ONELINE


class Node(Model):
    """Model representing a node in the `slurm.conf` configuration file."""

    node_name: Annotated[str | None, Metadata(primary=True)]
    node_hostname: str | None
    node_addr: str | None
    bcast_addr: str | None
    boards: int | None
    core_spec_count: int | None
    cores_per_socket: int | None
    cpu_bind: str | None
    cpus: int | None
    cpu_spec_list: Annotated[list[int] | None, Metadata(callback=CommaSepCallback)]
    features: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    gres: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    mem_spec_limit: int | None
    port: int | None
    procs: int | None
    real_memory: int | None
    reason: Annotated[str | None, Metadata(callback=QuoteCallback)]
    sockets: int | None
    sockets_per_board: int | None
    state: str | None
    threads_per_core: int | None
    tmp_disk: int | None
    weight: int | None

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return NODE_MODEL_SCHEMA

    @classproperty
    def __model_mode__(cls) -> Mode:  # noqa N805
        return Mode.ONELINE


class NodeSet(Model):
    """Model representing a node set in the `slurm.conf` configuration file."""

    node_set: Annotated[str | None, Metadata(primary=True)]
    feature: str | None
    nodes: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return NODESET_MODEL_SCHEMA

    @classproperty
    def __model_mode__(cls) -> Mode:  # noqa N805
        return Mode.ONELINE


class Partition(Model):
    """Model representing a partition in the `slurm.conf` configuration file."""

    partition_name: Annotated[str | None, Metadata(primary=True)]
    alloc_nodes: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    allow_accounts: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    allow_groups: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    allow_qos: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    alternate: str | None
    cpu_bind: str | None
    default: bool | None
    default_time: int | str | None
    def_cpu_per_gpu: int | None
    def_mem_per_cpu: int | None
    def_mem_per_gpu: int | None
    def_mem_per_node: int | None
    deny_accounts: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    deny_qos: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
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
    nodes: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
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
    select_type_parameters: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    state: str | None
    suspend_time: int | str | None
    suspend_timeout: int | None
    tres_billing_weights: Annotated[dict[str, str] | None, Metadata(callback=CommaDictCallback)]

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return PARTITION_MODEL_SCHEMA

    @classproperty
    def __model_mode__(cls) -> Mode:  # noqa N805
        return Mode.ONELINE


class DownNodesList(ModelList[DownNodes]):
    """List of down nodes entries in the `slurm.conf` configuration file."""

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return DOWN_NODES_LIST_MODEL_SCHEMA

    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]:  # noqa N805
        return _down_nodes_list_model_builder


class FrontendNodeMapping(ModelMapping[str, FrontendNode]):
    """Mapping of frontend node names to corresponding frontend nodes."""

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return FRONTEND_NODE_MAPPING_MODEL_SCHEMA

    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]:  # noqa N805
        return _frontend_node_mapping_model_builder


class NodeMapping(ModelMapping[str, Node]):
    """Mapping of node names to corresponding nodes."""

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return NODE_MAPPING_MODEL_SCHEMA

    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]:  # noqa N805
        return _node_mapping_model_builder


class NodeSetMapping(ModelMapping[str, NodeSet]):
    """Mapping of node set names to corresponding node sets."""

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return NODESET_MAPPING_MODEL_SCHEMA

    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]:  # noqa N805
        return _nodeset_mapping_model_builder


class PartitionMapping(ModelMapping[str, Partition]):
    """Mapping of partition names to corresponding partitions."""

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return PARTITION_MAPPING_MODEL_SCHEMA

    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]:  # noqa N805
        return _partition_mapping_model_builder


class SlurmConfig(Model):
    """Model representing the `slurm.conf` configuration file."""

    accounting_storage_backup_host: str | None
    accounting_storage_enforce: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    accounting_storage_external_host: str | None
    accounting_storage_host: str | None
    accounting_storage_parameters: Annotated[
        dict[str, str | list[str]] | None,
        Metadata(callback=CommaDictCallback),
    ]
    accounting_storage_pass: str | None
    accounting_storage_port: int | None
    accounting_storage_tres: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    accounting_storage_type: str | None
    accounting_storage_user: str | None
    accounting_store_flags: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    acct_gather_node_freq: int | None
    acct_gather_energy_type: str | None
    acct_gather_interconnect_type: str | None
    acct_gather_filesystem_type: str | None
    acct_gather_profile_type: str | None
    allow_spec_resources_usage: bool | None
    auth_alt_types: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    auth_alt_parameters: Annotated[
        dict[str, bool | int | str] | None,
        Metadata(callback=CommaDictCallback),
    ]
    auth_info: Annotated[dict[str, bool | int | str] | None, Metadata(callback=CommaDictCallback)]
    auth_type: str | None
    batch_start_timeout: int | None
    bcast_exclude: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    bcast_parameters: Annotated[
        dict[str, bool | str] | None,
        Metadata(callback=CommaDictCallback),
    ]
    burst_buffer_type: str | None
    cli_filter_plugins: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    cluster_name: str | None
    communication_parameters: Annotated[
        dict[str, bool | int] | None, Metadata(callback=CommaDictCallback)
    ]
    complete_wait: int | None
    cpu_freq_def: str | None
    cpu_freq_governors: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    cred_type: str | None
    debug_flags: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    def_cpu_per_gpu: int | None
    def_mem_per_cpu: int | None
    def_mem_per_gpu: int | None
    def_mem_per_node: int | None
    dependency_parameters: Annotated[
        dict[str, bool | int] | None,
        Metadata(callback=CommaDictCallback),
    ]
    disable_root_jobs: bool | None
    eio_timeout: int | None
    enforce_part_limits: str | None
    epilog: str | None
    epilog_msg_time: int | None
    epilog_slurmctld: str | None
    fair_share_dampening_factor: int | None
    federation_parameters: Annotated[
        dict[str, bool] | None,
        Metadata(callback=CommaDictCallback),
    ]
    first_job_id: int | None
    get_env_timeout: int | None
    gres_types: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    group_update_force: Annotated[bool | None, Metadata(callback=IntBoolCallback)]
    group_update_time: int | None
    gpu_freq_def: int | str | None
    health_check_interval: int | None
    health_check_node_state: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    health_check_program: str | None
    inactive_limit: int | None
    include: Annotated[
        list[str] | None, Metadata(sep=" ", unique=False, callback=MultilineCallback)
    ]
    interactive_step_options: str | None
    job_acct_gather_type: str | None
    job_acct_gather_frequency: Annotated[
        dict[str, int] | None,
        Metadata(callback=CommaDictCallback),
    ]
    job_acct_gather_params: Annotated[
        dict[str, bool] | None,
        Metadata(callback=CommaDictCallback),
    ]
    job_comp_host: str | None
    job_comp_loc: str | None
    job_comp_params: Annotated[
        dict[str, bool | int | str] | None,
        Metadata(callback=CommaDictCallback),
    ]
    job_comp_pass: str | None
    job_comp_port: int | None
    job_comp_type: str | None
    job_comp_user: str | None
    job_container_type: str | None
    job_file_append: Annotated[bool | None, Metadata(callback=IntBoolCallback)]
    job_requeue: Annotated[bool | None, Metadata(callback=IntBoolCallback)]
    job_submit_plugins: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    kill_on_bad_exit: Annotated[bool | None, Metadata(callback=IntBoolCallback)]
    kill_wait: int | None
    max_batch_requeue: int | None
    node_features_plugins: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    launch_parameters: Annotated[
        dict[str, bool] | None,
        Metadata(callback=CommaDictCallback),
    ]
    licenses: Annotated[
        dict[str, bool | int] | None,
        Metadata(callback=CommaDictColonPairCallback),
    ]
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
    mcs_parameters: Annotated[
        dict[str, bool | list[str]] | None,
        Metadata(callback=MCSParametersCallback),
    ]
    mcs_plugin: str | None
    message_timeout: int | None
    metrics_type: str | None
    min_job_age: int | None
    mpi_default: str | None
    mpi_params: Annotated[
        dict[str, bool | str] | None,
        Metadata(callback=CommaDictCallback),
    ]
    over_time_limit: int | str | None
    plugin_dir: Annotated[list[str] | None, Metadata(callback=ColonSepCallback)]
    plug_stack_config: str | None
    preempt_mode: str | None
    preempt_parameters: Annotated[
        dict[str, bool | int] | None,
        Metadata(callback=CommaDictCallback),
    ]
    preempt_type: str | None
    preempt_exempt_time: int | str | None
    pr_ep_parameters: Annotated[
        dict[str, Any] | None,
        Metadata(callback=CommaDictCallback),
    ]
    pr_ep_plugins: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    priority_calc_period: int
    priority_decay_half_life: int | str | None
    priority_favor_small: Annotated[bool | None, Metadata(callback=StrBoolCallback)]
    priority_flags: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
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
    priority_weight_tres: Annotated[dict[str, int] | None, Metadata(callback=CommaDictCallback)]
    private_data: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    proctrack_type: str | None
    prolog: str | None
    prolog_epilog_timeout: int | None
    prolog_flags: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    prolog_slurmctld: str | None
    propagate_prio_process: int | None
    propagate_resource_limits: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    propagate_resource_limits_except: Annotated[
        list[str] | None,
        Metadata(callback=CommaSepCallback),
    ]
    reboot_program: Annotated[str | None, Metadata(callback=QuoteCallback)]
    reconfig_flags: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    requeue_exit: Annotated[list[str | int] | None, Metadata(callback=CommaSepCallback)]
    requeue_exit_hold: Annotated[list[str | int] | None, Metadata(callback=CommaSepCallback)]
    resume_fail_program: str | None
    resume_program: str | None
    resume_rate: int | None
    resume_timeout: int | None
    resv_epilog: str | None
    resv_over_run: int | str | None
    resv_prolog: str | None
    return_to_service: int | None
    scheduler_parameters: Annotated[
        dict[str, bool | int | str] | None,
        Metadata(callback=CommaDictCallback),
    ]
    scheduler_time_slice: int | None
    scheduler_type: str | None
    scron_parameters: Annotated[dict[str, bool] | None, Metadata(callback=CommaDictCallback)]
    select_type: str | None
    select_type_parameters: Annotated[
        dict[str, bool] | None,
        Metadata(callback=CommaDictCallback),
    ]
    slurmctld_addr: str | None
    slurmctld_debug: str | None
    slurmctld_host: Annotated[list[str] | None, Metadata(unique=False, callback=MultilineCallback)]
    slurmctld_log_file: str | None
    slurmctld_parameters: Annotated[
        dict[str, bool | int | str] | None,
        Metadata(callback=CommaDictCallback),
    ]
    slurmctld_pid_file: str | None
    slurmctld_port: int | str | None
    slurmctld_primary_off_prog: str | None
    slurmctld_primary_on_prog: str | None
    slurmctld_syslog_debug: str | None
    slurmctld_timeout: int | None
    slurmd_debug: str | None
    slurmd_log_file: str | None
    slurmd_parameters: Annotated[
        dict[str, bool | int] | None,
        Metadata(callback=CommaDictCallback),
    ]
    slurmd_pid_file: str | None
    slurmd_port: int | None
    slurmd_spool_dir: str | None
    slurmd_syslog_debug: str | None
    slurmd_timeout: int | None
    slurmd_user: str | None
    slurm_sched_log_file: str | None
    slurm_sched_log_level: Annotated[bool | None, Metadata(callback=IntBoolCallback)]
    slurm_user: str | None
    srun_epilog: str | None
    srun_port_range: str | None
    srun_prolog: str | None
    state_save_location: str | None
    suspend_exc_nodes: Annotated[
        dict[str, bool | int] | None,
        Metadata(callback=CommaDictColonPairCallback),
    ]
    suspend_exc_parts: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    suspend_exc_states: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    suspend_program: str | None
    suspend_rate: int | None
    suspend_time: int | str | None
    suspend_timeout: int | None
    switch_parameters: Annotated[
        dict[str, bool | int | str | list[str]] | None,
        Metadata(callback=CommaDictColonArrayCallback),
    ]
    switch_type: str | None
    task_epilog: str | None
    task_plugin: Annotated[list[str] | None, Metadata(callback=CommaSepCallback)]
    task_plugin_param: Annotated[
        dict[str, bool | str] | None,
        Metadata(callback=CommaDictCallback),
    ]
    task_prolog: str | None
    tcp_timeout: int | None
    tmpfs: str | None
    topology_param: Annotated[dict[str, bool | int] | None, Metadata(callback=CommaDictCallback)]
    topology_plugin: str | None
    track_wc_key: Annotated[bool | None, Metadata(callback=StrBoolCallback)]
    tree_width: int | None
    unkillable_step_program: str | None
    unkillable_step_timeout: int | None
    use_pam: Annotated[bool | None, Metadata(callback=IntBoolCallback)]
    v_size_factor: int | None
    wait_time: int | None
    x11_parameters: Annotated[dict[str, bool] | None, Metadata(callback=CommaDictCallback)]

    down_nodes: Annotated[
        DownNodesList, Metadata(unique=False, default_factory=lambda: DownNodesList())
    ]
    frontend_nodes: Annotated[
        FrontendNodeMapping,
        Metadata(
            origin="frontendnodes",
            alias="frontendnodename",
            unique=False,
            default_factory=lambda: FrontendNodeMapping(),
        ),
    ]
    nodes: Annotated[
        NodeMapping,
        Metadata(
            origin="nodes", alias="nodename", unique=False, default_factory=lambda: NodeMapping()
        ),
    ]
    nodesets: Annotated[
        NodeSetMapping,
        Metadata(
            origin="nodesets",
            alias="nodeset",
            unique=False,
            default_factory=lambda: NodeSetMapping(),
        ),
    ]
    partitions: Annotated[
        PartitionMapping,
        Metadata(
            origin="partitions",
            alias="partitionname",
            unique=False,
            default_factory=lambda: PartitionMapping(),
        ),
    ]

    @classproperty
    def __model_schema__(cls) -> dict[str, Any]:  # noqa N805
        return SLURM_CONFIG_MODEL_SCHEMA

    @classproperty
    def __model_builder__(cls) -> Callable[[Any], Any]:  # noqa N805
        return _slurm_config_model_builder


class SlurmConfigEditor(BaseEditor):
    """Editor for the `slurm.conf` configuration file."""

    @property
    def __model__(self) -> type[Model]:  # noqa D105
        return SlurmConfig


_down_nodes_list_model_builder = make_model_builder(DownNodes)
_frontend_node_mapping_model_builder = make_model_builder(FrontendNode)
_node_mapping_model_builder = make_model_builder(Node)
_nodeset_mapping_model_builder = make_model_builder(NodeSet)
_partition_mapping_model_builder = make_model_builder(Partition)
_slurm_config_model_builder = make_model_builder(
    DownNodesList,
    FrontendNodeMapping,
    NodeMapping,
    NodeSetMapping,
    PartitionMapping,
)
