# Copyright 2026 Canonical Ltd.
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

"""Unit tests for schema value normalization."""

from unittest import TestCase

from slurmutils import CGroupConfig, DownNodes, Node, Partition
from slurmutils.core.normalize import normalize_for_schema
from slurmutils.core.schema import (
    CGROUP_CONFIG_MODEL_SCHEMA,
    NODE_MODEL_SCHEMA,
    PARTITION_MODEL_SCHEMA,
)


class TestNormalizeForSchema(TestCase):
    """Unit tests for normalize_for_schema."""

    def test_lowercases_enum_values(self) -> None:
        """Enum strings are normalized to lowercase."""
        normalized = normalize_for_schema({"state": "DOWN"}, NODE_MODEL_SCHEMA)
        self.assertEqual(normalized["state"], "down")

    def test_coerces_boolean_strings(self) -> None:
        """Boolean schema fields accept yes/no and true/false in any case."""
        normalized = normalize_for_schema(
            {"constraincores": "YES", "constraindevices": "NO"},
            CGROUP_CONFIG_MODEL_SCHEMA,
        )
        self.assertTrue(normalized["constraincores"])
        self.assertFalse(normalized["constraindevices"])

    def test_lowercases_enum_in_oneof(self) -> None:
        """Enum strings inside oneOf branches are normalized."""
        normalized = normalize_for_schema({"maxnodes": "UNLIMITED"}, PARTITION_MODEL_SCHEMA)
        self.assertEqual(normalized["maxnodes"], "unlimited")

    def test_lowercases_yes_no_string_enums(self) -> None:
        """String enum fields that include yes/no accept uppercase input."""
        normalized = normalize_for_schema({"oversubscribe": "YES"}, PARTITION_MODEL_SCHEMA)
        self.assertEqual(normalized["oversubscribe"], "yes")


class TestCaseInsensitiveModelValues(TestCase):
    """Integration tests for case-insensitive enum and boolean values."""

    def test_node_state_from_str(self) -> None:
        """Node state accepts Slurm-style uppercase values."""
        node = Node.from_str("nodename=compute-1 state=DOWN")
        self.assertEqual(node.state, "down")
        self.assertIn("state=down", str(node))

    def test_node_state_from_dict(self) -> None:
        """Node state accepts uppercase values via direct construction."""
        node = Node({"nodename": "compute-1", "state": "DOWN"})
        self.assertEqual(node.state, "down")

    def test_down_nodes_state_from_str(self) -> None:
        """DownNodes state accepts uppercase values."""
        down_nodes = DownNodes.from_str('downnodes=node1 state=DOWN reason="Maintenance"')
        self.assertEqual(down_nodes.state, "down")

    def test_partition_oversubscribe_from_str(self) -> None:
        """Partition oversubscribe accepts YES/NO enum values."""
        partition = Partition.from_str("partitionname=batch oversubscribe=YES state=UP")
        self.assertEqual(partition.over_subscribe, "yes")
        self.assertEqual(partition.state, "up")

    def test_cgroup_boolean_from_str(self) -> None:
        """Cgroup boolean fields accept YES/NO when parsing configuration."""
        config = CGroupConfig.from_str(
            """
            constraincores=YES
            constraindevices=NO
            """
        )
        self.assertTrue(config.constrain_cores)
        self.assertFalse(config.constrain_devices)

    def test_cgroup_boolean_from_dict(self) -> None:
        """Cgroup boolean fields accept YES/NO via direct construction."""
        config = CGroupConfig({"constraincores": "YES", "constraindevices": "NO"})
        self.assertTrue(config.constrain_cores)
        self.assertFalse(config.constrain_devices)

    def test_cgroup_boolean_from_json(self) -> None:
        """Cgroup boolean fields accept YES/NO via from_json."""
        config = CGroupConfig.from_json('{"constraincores": "YES", "constraindevices": "NO"}')
        self.assertTrue(config.constrain_cores)
        self.assertFalse(config.constrain_devices)

