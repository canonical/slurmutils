# slurmutils

![PyPI - Version](https://img.shields.io/pypi/v/slurmutils)
![PyPI - Downloads](https://img.shields.io/pypi/dm/slurmutils)
![GitHub License](https://img.shields.io/github/license/canonical/slurmutils)
[![Matrix](https://img.shields.io/matrix/ubuntu-hpc%3Amatrix.org?logo=matrix&label=ubuntu-hpc)](https://matrix.to/#/#hpc:ubuntu.com)

Utilities and APIs for interfacing with the Slurm workload manager.

slurmutils is a collection of various utilities that make it easier 
for you and your friends to interface with the Slurm workload manager, especially if you 
are orchestrating deployments of new and current Slurm clusters. Gone are the days of
seething over incomplete Jinja2 templates. Current utilities shipped in the 
slurmutils package include:

#### `from slurmutils import ...`

* `calculate_rs`: A function for calculating the ranges and strides of an iterable with
  unique elements. This function can be used to help convert arrays of node hostnames,
  device file ids, etc into a Slurm hostname specification.
* `acctgatherconfig`: An editor for _acct_gather.conf_ configuration files.
* `cgroupconfig`: An editor for _cgroup.conf_ configuration files.
* `gresconfig`: An editor for _gres.conf_ configuration files.
* `ociconfig`: An editor for _oci.conf_ configuration files.
* `slurmconfig`: An editor for _slurm.conf_ configuration files.
* `slurmdbdconfig`: An editor for _slurmdbd.conf_ configuration files.

For more information on how to use or contribute to slurmutils, 
check out the [Getting Started](#-getting-started) and [Development](#-development) 
sections below 👇

## ✨ Getting Started

### Installation

#### Option 1: Install from PyPI

```shell
$ python3 -m pip install slurmutils
```

#### Option 2: Install from source

```shell
$ pip install .
```

### Usage

#### `slurmutils`

The top-level provides access to some utilities that streamline common Slurm-related
operations such as calculating the ranges and strides for a Slurm hostname specification
or editing configuration files in-place. Here's some example operations you can perform 
with these utilities:

##### `calculate_rs`

###### Calculate a range and/or stride from a list of node hostnames

```python3
from os.path import commonprefix

from slurmutils import calculate_rs

nodes = ["juju-abc654-1", "juju-abc654-2", "juju-abc654-4"]
prefix = commonprefix(nodes)
nums = [int(n.partition(prefix)[2]) for n in nodes]
slurm_host_spec = prefix + calculate_rs(nums)  # "juju-abc654-[1-2,4]"
```

###### Calculate a device file range for Nvidia GPUs

```python3
from pathlib import Path

from slurmutils import calculate_rs

device_files = [file for file in Path("/dev").iterdir() if "nvidia" in file.name]
prefix = "/dev/nvidia"
nums = [int(n.partition(prefix)[2]) for n in device_files]
file_spec = prefix + calculate_rs(nums)  # "/dev/nvidia[0-4]"
```

##### `acctgatherconfig`

###### Edit a pre-existing _acct_gather.conf_ configuration file

```python
from slurmutils import acctgatherconfig

with acctgatherconfig.edit("/etc/slurm/acct_gather.conf") as config:
    config.profile_influxdb_database = "test_acct_gather_db"
    config.profile_influxdb_default = ["none"]
    config.profile_influxdb_host = "testhostname1"
    config.profile_influxdb_pass = "testpassword1"
    config.profile_influxdb_rt_policy = "testpolicy1"
    config.profile_influxdb_user = "testuser1"
    config.profile_influxdb_timeout = 20
```

##### `cgroupconfig`

###### Edit a pre-existing _cgroup.conf_ configuration file

```python
from slurmutils import cgroupconfig

with cgroupconfig.edit("/etc/slurm/cgroup.conf") as config:
    config.constrain_cores = True
    config.constrain_devices = True
    config.constrain_ram_space = True
    config.constrain_swap_space = True
```

##### `gresconfig`

###### Edit a pre-existing _gres.conf_ configuration file

```python
from slurmutils import Gres, GresList, gresconfig

with gresconfig.edit("/etc/slurm/gres.conf") as config:
    gres1 = Gres(
        name="gpu",
        type="epyc",
        file="/dev/amd4",
        cores=[0, 1],
    )
    gres2 = Gres(
        name="gpu",
        nodename="juju-abc654-[1-20]",
        type="epyc",
        file="/dev/amd[0-3]",
        count="12G",
    )
    config.auto_detect = "rsmi"
    config.gres["gpu"] = GresList(gres1, gres2)
```

##### `ociconfig`

###### Edit a pre-existing _oci.conf_ configuration file

```python
from slurmutils import ociconfig

with ociconfig.edit("/etc/slurm/oci.conf") as config:
    config.ignore_file_config_json = False
    config.env_exclude = "^(SLURM_CONF|SLURM_CONF_SERVER|SLURM_JWT)="
    config.create_env_file = "newline"
    config.std_io_debug = "debug"
    config.syslog_debug = "debug"
```

##### `slurmconfig`

###### Edit a pre-existing _slurm.conf_ configuration file

```python
from slurmutils import slurmconfig

with slurmconfig.edit("/etc/slurm/slurm.conf") as config:
    del config.inactive_limit
    config.max_job_count = 20000
    config.proctrack_type = "proctrack/linuxproc"
```

###### Add a new node to the _slurm.conf_ file

```python
from slurmutils import Node, slurmconfig

with slurmconfig.edit("/etc/slurm/slurm.conf") as config:
    node = Node(
        nodename="batch-[0-25]",
        nodeaddr="12.34.56.78",
        cpus=1,
        realmemory=1000,
        tmpdisk=10000,
    )
    config.nodes[node.node_name] = node
```

##### `slurmdbdconfig`

###### Edit a pre-existing _slurmdbd.conf_ configuration file

```python
from slurmutils import slurmdbdconfig

with slurmdbdconfig.edit("/etc/slurm/slurmdbd.conf") as config:
    config.archive_usage = True
    config.log_file = "/var/spool/slurmdbd.log"
    config.debug_flags = ["db_event", "db_job", "db_usage"]
    del config.auth_alt_types
    del config.auth_alt_parameters
```

## 🤔 What's next?

If you want to learn more about all the things you can do with slurmutils, 
here are some further resources for you to explore:

* [Open an issue](https://github.com/canonical/slurmutils/issues/new?title=ISSUE+TITLE&body=*Please+describe+your+issue*)

## 🛠️ Development

The project uses [just](https://github.com/casey/just) and [uv](https://github.com/astral-sh/uv) 
for development, which provides some useful commands that will help you while hacking on slurmutils:

```shell
just fmt          # Apply formatting standards to code
just lint         # Check code against coding style standards
just typecheck    # Run static type checks
just unit         # Run unit tests
```

If you're interested in contributing your work to slurmutils, 
take a look at our [contributing guidelines](./CONTRIBUTING.md) for further details.

## 🤝 Project and community

slurmutils is a project of the [Ubuntu High-Performance Computing community](https://ubuntu.com/community/governance/teams/hpc).
Interested in contributing bug fixes, new editors, documentation, or feedback? Want to join the Ubuntu HPC community? You’ve come to the right place 🤩

Here’s some links to help you get started with joining the community:

* [Ubuntu Code of Conduct](https://ubuntu.com/community/ethos/code-of-conduct)
* [Contributing guidelines](./CONTRIBUTING.md)
* [Join the conversation on Matrix](https://matrix.to/#/#hpc:ubuntu.com)
* [Get the latest news on Discourse](https://discourse.ubuntu.com/c/hpc/151)

## 📋 License

slurmutils is free software, distributed under the GNU Lesser General Public License, v3.0.
See the [LGPL-3.0 LICENSE](./LICENSE) file for further details.
