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

"""Unit tests for the model and editor of the `cgroup.conf` configuration file."""

from constants import EXAMPLE_CGROUP_CONFIG
from pyfakefs.fake_filesystem_unittest import TestCase

from slurmutils import CGroupConfig, ModelError, cgroupconfig

EXPECTED_CGROUP_DUMPS_OUTPUT = """
constraincores=yes
constraindevices=yes
constrainramspace=yes
constrainswapspace=yes
""".strip()


class TestCGroupConfig(TestCase):
    """Unit tests for model and editor of the `cgroup.conf` configuration file."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("/etc/slurm/cgroup.conf", contents=EXAMPLE_CGROUP_CONFIG)

    def test_loads(self) -> None:
        """Test `loads` method of the `cgroup.conf` model editor."""
        config = cgroupconfig.loads(EXAMPLE_CGROUP_CONFIG)
        self.assertTrue(config.constrain_cores)
        self.assertTrue(config.constrain_devices)
        self.assertTrue(config.constrain_ram_space)
        self.assertTrue(config.constrain_swap_space)

    def test_dumps(self) -> None:
        """Test `dumps` method of the `cgroup.conf` model editor."""
        config = cgroupconfig.loads(EXAMPLE_CGROUP_CONFIG)
        # Check if output matches expected output.
        self.assertEqual(cgroupconfig.dumps(config), EXPECTED_CGROUP_DUMPS_OUTPUT)
        # New config and old config should not be equal since the editor strips all comments.
        self.assertNotEqual(cgroupconfig.dumps(config), EXAMPLE_CGROUP_CONFIG)

    def test_edit(self) -> None:
        """Test `edit` context manager of the `cgroup.conf` model editor."""
        with cgroupconfig.edit("/etc/slurm/cgroup.conf") as config:
            config.constrain_cores = False
            config.constrain_devices = False
            config.constrain_ram_space = False
            config.constrain_swap_space = False

        config = cgroupconfig.load("/etc/slurm/cgroup.conf")
        self.assertFalse(config.constrain_cores)
        self.assertFalse(config.constrain_devices)
        self.assertFalse(config.constrain_ram_space)
        self.assertFalse(config.constrain_swap_space)

    def test_load_fail(self) -> None:
        """Test that bogus values are automatically caught when loading a new model."""
        # Catch if field value is unexpected. e.g. not a boolean value.
        with self.assertRaises(ValueError):
            CGroupConfig.from_str(
                """
                constrainramspace=totally
                """
            )

        # Catch if field is unexpected or in the incorrect syntax.
        with self.assertRaises(ModelError):
            CGroupConfig.from_str(
                """
                constrain_ram_space=yes
                """
            )

        # Catch if field value is invalid when checking against the model schema.
        with self.assertRaises(ModelError):
            CGroupConfig.from_str(
                """
                cgroupplugin=yeahtotallyusecgroup
                """
            )

    def test_edit_fail(self) -> None:
        """Test that bogus attributes are handled when editing a loaded model."""
        # Catch if user tries to edit a non-existent attribute.
        with self.assertRaises(AttributeError):
            config = cgroupconfig.loads(CGroupConfig)
            config.constrain_ram = False

        # Catch if user tries to access a non-existent attribute.
        with self.assertRaises(AttributeError):
            config = cgroupconfig.loads(CGroupConfig)
            _ = config.constrain_ram
