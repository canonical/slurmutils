#!/usr/bin/env python3
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

"""Unit tests for models and editor representing the `slurm.conf` configuration file."""

from constants import EXAMPLE_SLURM_CONFIG
from pyfakefs.fake_filesystem_unittest import TestCase

from slurmutils import (
    DownNodes,
    FrontendNode,
    Node,
    NodeSet,
    Partition,
    SlurmConfig,
    slurmconfig,
)

EXPECTED_SLURM_DUMPS_OUTPUT = """
slurmctldhost=juju-c9fc6f-0(10.152.28.20)
slurmctldhost=juju-c9fc6f-1(10.152.28.100)
clustername=charmed-hpc
authtype=auth/munge
epilog=/usr/local/slurm/epilog
prolog=/usr/local/slurm/prolog
firstjobid=65536
inactivelimit=120
jobcomptype=jobcomp/filetxt
jobcomploc=/var/log/slurm/jobcomp
killwait=30
maxjobcount=10000
minjobage=3600
plugindir=/usr/local/lib:/usr/local/slurm/lib
returntoservice=0
schedulertype=sched/backfill
slurmctldlogfile=/var/log/slurm/slurmctld.log
slurmdlogfile=/var/log/slurm/slurmd.log
slurmctldport=7002
slurmdport=7003
slurmdspooldir=/var/spool/slurmd.spool
statesavelocation=/var/spool/slurm.state
tmpfs=/tmp
waittime=30
nodename=juju-c9fc6f-2 nodeaddr=10.152.28.48 cpus=1 realmemory=1000 tmpdisk=10000
nodename=juju-c9fc6f-3 nodeaddr=10.152.28.49 cpus=1 realmemory=1000 tmpdisk=10000
nodename=juju-c9fc6f-4 nodeaddr=10.152.28.50 cpus=1 realmemory=1000 tmpdisk=10000
nodename=juju-c9fc6f-5 nodeaddr=10.152.28.51 cpus=1 realmemory=1000 tmpdisk=10000
downnodes=juju-c9fc6f-5 state=down reason="Maintenance Mode"
partitionname=DEFAULT maxtime=30 maxnodes=10 state=up
partitionname=batch nodes=juju-c9fc6f-2,juju-c9fc6f-3,juju-c9fc6f-4,juju-c9fc6f-5 minnodes=4 maxtime=120 allowgroups=admin
""".strip()


class TestSlurmConfig(TestCase):
    """Unit tests for models and the editor representing the `slurm.conf` configuration file."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("/etc/slurm/slurm.conf", contents=EXAMPLE_SLURM_CONFIG)

    def test_loads(self) -> None:
        """Test `loads` method of `slurm.conf` model editor."""
        config = slurmconfig.loads(EXAMPLE_SLURM_CONFIG)
        self.assertListEqual(
            config.slurmctld_host,
            ["juju-c9fc6f-0(10.152.28.20)", "juju-c9fc6f-1(10.152.28.100)"],
        )

        self.assertEqual(config.slurmd_spool_dir, "/var/spool/slurmd.spool")
        self.assertEqual(config.scheduler_type, "sched/backfill")

        for name, node in config.nodes.items():
            self.assertIn(  # codespell:ignore
                name,
                {"juju-c9fc6f-2", "juju-c9fc6f-3", "juju-c9fc6f-4", "juju-c9fc6f-5"},
            )
            self.assertIn(  # codespell:ignore
                node.node_addr,
                {"10.152.28.48", "10.152.28.49", "10.152.28.50", "10.152.28.51"},
            )
            self.assertEqual(node.cpus, 1)
            self.assertEqual(node.real_memory, 1000)
            self.assertEqual(node.tmp_disk, 10000)

        for entry in config.down_nodes:
            self.assertEqual(entry.down_nodes[0], "juju-c9fc6f-5")
            self.assertEqual(entry.state, "down")
            self.assertEqual(entry.reason, "Maintenance Mode")

        for partition in config.partitions:
            self.assertIn(partition, {"DEFAULT", "batch"})  # codespell:ignore

        batch = config.partitions["batch"]
        self.assertListEqual(
            batch.nodes, ["juju-c9fc6f-2", "juju-c9fc6f-3", "juju-c9fc6f-4", "juju-c9fc6f-5"]
        )

    def test_dumps(self) -> None:
        """Test `dumps` method of the `slurm.conf` model editor."""
        config = slurmconfig.loads(EXAMPLE_SLURM_CONFIG)
        # Check if output matches expected output.
        self.assertEqual(slurmconfig.dumps(config), EXPECTED_SLURM_DUMPS_OUTPUT)
        # New config and old config should not be equal since the editor strips all comments.
        self.assertNotEqual(slurmconfig.dumps(config), EXAMPLE_SLURM_CONFIG)

    def test_edit(self) -> None:
        """Test `edit` context manager of the `slurm.conf` model editor."""
        with slurmconfig.edit("/etc/slurm/slurm.conf") as config:
            del config.inactive_limit
            config.reboot_program = "/usr/bin/systemctl reboot"
            config.max_job_count = 20000
            config.proctrack_type = "proctrack/linuxproc"
            config.plugin_dir.append("/snap/slurm/current/plugins")
            config.slurmctld_parameters = {"enable_configless": True}
            config.include = ["slurm.conf.overrides", "slurm.conf.profiling"]

            new_node = Node(**config.nodes["juju-c9fc6f-2"].dict())
            new_node.node_name = "batch-0"
            del config.nodes["juju-c9fc6f-2"]
            config.nodes[new_node.node_name] = new_node

        config = slurmconfig.load("/etc/slurm/slurm.conf")
        self.assertIsNone(config.inactive_limit)
        self.assertEqual(config.reboot_program, "/usr/bin/systemctl reboot")
        self.assertEqual(config.max_job_count, 20000)
        self.assertEqual(config.proctrack_type, "proctrack/linuxproc")
        self.assertListEqual(
            config.plugin_dir,
            ["/usr/local/lib", "/usr/local/slurm/lib", "/snap/slurm/current/plugins"],
        )
        self.assertDictEqual(config.slurmctld_parameters, {"enable_configless": True})
        self.assertListEqual(config.include, ["slurm.conf.overrides", "slurm.conf.profiling"])
        self.assertEqual(config.nodes["batch-0"].node_addr, "10.152.28.48")

        with slurmconfig.edit("/etc/slurm/slurm.conf") as config:
            del config.nodes
            del config.frontend_nodes
            del config.down_nodes
            del config.nodesets
            del config.partitions

        config = slurmconfig.load("/etc/slurm/slurm.conf")
        self.assertDictEqual(config.nodes.dict(), {})
        self.assertDictEqual(config.frontend_nodes.dict(), {})
        self.assertListEqual(config.down_nodes.list(), [])
        self.assertDictEqual(config.nodesets.dict(), {})
        self.assertDictEqual(config.partitions.dict(), {})

        new_nodes = [
            Node.from_dict(
                {
                    "nodename": "juju-c9fc6f-2",
                    "nodeaddr": "10.152.28.48",
                    "cpus": 1,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                }
            ),
            Node.from_dict(
                {
                    "nodename": "juju-c9fc6f-3",
                    "nodeaddr": "10.152.28.49",
                    "cpus": 1,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                }
            ),
            Node.from_dict(
                {
                    "nodename": "juju-c9fc6f-4",
                    "nodeaddr": "10.152.28.50",
                    "cpus": 1,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                }
            ),
            Node.from_dict(
                {
                    "nodename": "juju-c9fc6f-5",
                    "nodeaddr": "10.152.28.51",
                    "cpus": 1,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                }
            ),
        ]
        new_down_nodes = [
            DownNodes.from_dict(
                {
                    "downnodes": ["juju-c9fc6f-5"],
                    "state": "down",
                    "reason": "Maintenance Mode",
                }
            )
        ]
        new_partitions = [
            Partition.from_dict(
                {"partitionname": "DEFAULT", "maxtime": 30, "maxnodes": 10, "state": "up"}
            ),
            Partition.from_dict(
                {
                    "partitionname": "batch",
                    "nodes": [
                        "juju-c9fc6f-2",
                        "juju-c9fc6f-3",
                        "juju-c9fc6f-4",
                        "juju-c9fc6f-5",
                    ],
                    "minnodes": 4,
                    "maxtime": 120,
                    "allowgroups": ["admin"],
                }
            ),
        ]

        with slurmconfig.edit("/etc/slurm/slurm.conf") as config:
            for node in new_nodes:
                config.nodes[node.node_name] = node

            for down_node in new_down_nodes:
                config.down_nodes.append(down_node)

            for partition in new_partitions:
                config.partitions[partition.partition_name] = partition

    def test_update(self):
        """Test `update` method of the slurmconfig module."""
        config_updates = {
            "killwait": 10,
            "plugindir": ["/var/snap/slurm/usr/local/lib", "/var/snap/slurm/usr/local/slurm/lib"],
            "returntoservice": 0,
            "schedulertype": "sched/builtin",
            "switchtype": "switch/hpe_slingshot",
            "waittime": 30,
            "nodes": {
                "juju-c9fc6f-2": {
                    "nodeaddr": "10.152.28.98",
                    "cpus": 9,
                    "realmemory": 9000,
                    "tmpdisk": 90000,
                },
                "juju-c9fc6f-6": {
                    "nodeaddr": "10.152.28.52",
                    "cpus": 9,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                },
                "juju-c9fc6f-7": {
                    "nodeaddr": "10.152.28.53",
                    "cpus": 9,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                },
            },
            "downnodes": [
                {
                    "downnodes": ["juju-c9fc6f-6", "juju-c9fc6f-7"],
                    "state": "down",
                    "reason": "New nodes",
                }
            ],
            "partitions": {
                "DEFAULT": {
                    "maxtime": 10,
                    "maxnodes": 5,
                    "state": "up",
                },
                "new_batch": {
                    "nodes": ["juju-c9fc6f-6", "juju-c9fc6f-7"],
                    "minnodes": 1,
                    "maxtime": 120,
                    "allowgroups": ["admin"],
                },
            },
        }

        config = slurmconfig.loads(EXAMPLE_SLURM_CONFIG)
        updates = SlurmConfig.from_dict(config_updates)
        config.update(updates)

        self.assertEqual(config.kill_wait, 10)
        self.assertListEqual(
            config.plugin_dir,
            ["/var/snap/slurm/usr/local/lib", "/var/snap/slurm/usr/local/slurm/lib"],
        )
        self.assertEqual(config.scheduler_type, "sched/builtin")
        self.assertEqual(config.switch_type, "switch/hpe_slingshot")
        self.assertEqual(config.wait_time, 30)

        self.assertDictEqual(
            config.nodes.dict(),
            {
                "juju-c9fc6f-2": {
                    "nodeaddr": "10.152.28.98",
                    "cpus": 9,
                    "realmemory": 9000,
                    "tmpdisk": 90000,
                },
                "juju-c9fc6f-6": {
                    "nodeaddr": "10.152.28.52",
                    "cpus": 9,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                },
                "juju-c9fc6f-7": {
                    "nodeaddr": "10.152.28.53",
                    "cpus": 9,
                    "realmemory": 1000,
                    "tmpdisk": 10000,
                },
            },
        )
        self.assertListEqual(
            config.down_nodes.list(),
            [
                {
                    "downnodes": ["juju-c9fc6f-6", "juju-c9fc6f-7"],
                    "state": "down",
                    "reason": "New nodes",
                },
            ],
        )
        self.assertDictEqual(
            config.partitions.dict(),
            {
                "DEFAULT": {
                    "maxtime": 10,
                    "maxnodes": 5,
                    "state": "up",
                },
                "new_batch": {
                    "nodes": ["juju-c9fc6f-6", "juju-c9fc6f-7"],
                    "minnodes": 1,
                    "maxtime": 120,
                    "allowgroups": ["admin"],
                },
            },
        )

    def test_edit_fail(self) -> None:
        """Test that bogus attributes are handled when editing a loaded model."""
        # Catch if user tries to edit a non-existent attribute.
        with self.assertRaises(AttributeError):
            config = slurmconfig.loads(EXAMPLE_SLURM_CONFIG)
            config.auth = "slurm"

        # Catch if user tries to access a non-existent attribute.
        with self.assertRaises(AttributeError):
            config = slurmconfig.loads(EXAMPLE_SLURM_CONFIG)
            _ = config.auth

    def test_empty_config(self) -> None:
        """Test that the `slurm.conf` configuration file models correctly handle empty config."""
        config = SlurmConfig.from_str("")
        self.assertIsNone(config.accounting_storage_port)

        config = DownNodes.from_str("")
        self.assertIsNone(config.down_nodes)

        config = FrontendNode.from_str("")
        self.assertIsNone(config.deny_users)

        config = Node.from_str("")
        self.assertIsNone(config.node_addr)

        config = NodeSet.from_str("")
        self.assertIsNone(config.feature)

        config = Partition.from_str("")
        self.assertIsNone(config.partition_name)
