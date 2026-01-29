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

"""Unit tests for the model and editor of the `acct_gather.conf` configuration file."""

from constants import EXAMPLE_ACCT_GATHER_CONFIG
from pyfakefs.fake_filesystem_unittest import TestCase

from slurmutils import AcctGatherConfig, ModelError, acctgatherconfig

EXPECTED_ACCT_GATHER_DUMPS_OUTPUT = """
energyipmifrequency=1
energyipmicalcadjustment=yes
energyipmipowersensors=node=16,19;socket1=19,26;knc=16,19
energyipmiusername=testipmiusername
energyipmipassword=testipmipassword
energyipmitimeout=10
profilehdf5dir=/mydir
profilehdf5default=all
profileinfluxdbdatabase=acct_gather_db
profileinfluxdbdefault=all
profileinfluxdbhost=testhostname
profileinfluxdbpass=testpassword
profileinfluxdbrtpolicy=testpolicy
profileinfluxdbuser=testuser
profileinfluxdbtimeout=10
infinibandofedport=0
sysfsinterfaces=enp0s1
""".strip()


class TestAcctGatherConfigEditor(TestCase):
    """Unit tests for the model and editor of the `acct_gather.conf` configuration file."""

    def setUp(self) -> None:
        self.setUpPyfakefs()
        self.fs.create_file("/etc/slurm/acct_gather.conf", contents=EXAMPLE_ACCT_GATHER_CONFIG)

    def test_loads(self) -> None:
        """Test `loads` method of the `acct_gather.conf` model editor."""
        config = acctgatherconfig.loads(EXAMPLE_ACCT_GATHER_CONFIG)
        self.assertEqual(config.energy_ipmi_frequency, 1)
        self.assertTrue(config.energy_ipmi_calc_adjustment)
        self.assertDictEqual(
            config.energy_ipmi_power_sensors,
            {"node": [16, 19], "socket1": [19, 26], "knc": [16, 19]},
        )
        self.assertEqual(config.energy_ipmi_username, "testipmiusername")
        self.assertEqual(config.energy_ipmi_password, "testipmipassword")
        self.assertEqual(config.energy_ipmi_timeout, 10)
        self.assertEqual(config.profile_hdf5_dir, "/mydir")
        self.assertListEqual(config.profile_hdf5_default, ["all"])
        self.assertEqual(config.profile_influxdb_database, "acct_gather_db")
        self.assertListEqual(config.profile_influxdb_default, ["all"])
        self.assertEqual(config.profile_influxdb_host, "testhostname")
        self.assertEqual(config.profile_influxdb_pass, "testpassword")
        self.assertEqual(config.profile_influxdb_rt_policy, "testpolicy")
        self.assertEqual(config.profile_influxdb_user, "testuser")
        self.assertEqual(config.profile_influxdb_timeout, 10)
        self.assertEqual(config.infiniband_ofed_port, 0)
        self.assertListEqual(config.sysfs_interfaces, ["enp0s1"])

    def test_dumps(self) -> None:
        """Test `dumps` method of the `acct_gather.conf` model editor."""
        config = acctgatherconfig.loads(EXAMPLE_ACCT_GATHER_CONFIG)
        # Check if output matches expected output.
        self.assertEqual(acctgatherconfig.dumps(config), EXPECTED_ACCT_GATHER_DUMPS_OUTPUT)
        # New config and old config should not be equal since the editor strips all comments.
        self.assertNotEqual(acctgatherconfig.dumps(config), EXAMPLE_ACCT_GATHER_CONFIG)

    def test_edit(self) -> None:
        """Test `edit` context manager from the acctgatherconfig module."""
        with acctgatherconfig.edit("/etc/slurm/acct_gather.conf") as config:
            config.energy_ipmi_frequency = 2
            config.energy_ipmi_calc_adjustment = False
            config.energy_ipmi_power_sensors = {
                "node": [20, 21],
                "socket1": [10, 26],
                "knc": [16, 19],
            }
            config.energy_ipmi_username = "testipmiusername1"
            config.energy_ipmi_password = "testipmipassword1"
            config.energy_ipmi_timeout = 20
            config.profile_hdf5_dir = "/mydir1234"
            config.profile_hdf5_default = ["none"]
            config.profile_influxdb_database = "test_acct_gather_db"
            config.profile_influxdb_default = ["none"]
            config.profile_influxdb_host = "testhostname1"
            config.profile_influxdb_pass = "testpassword1"
            config.profile_influxdb_rt_policy = "testpolicy1"
            config.profile_influxdb_user = "testuser1"
            config.profile_influxdb_timeout = 20
            config.infiniband_ofed_port = 1
            config.sysfs_interfaces = ["enp0s2"]

        config = acctgatherconfig.load("/etc/slurm/acct_gather.conf")
        self.assertEqual(config.energy_ipmi_frequency, 2)
        self.assertFalse(config.energy_ipmi_calc_adjustment)
        (
            self.assertDictEqual(
                config.energy_ipmi_power_sensors,
                {"node": [20, 21], "socket1": [10, 26], "knc": [16, 19]},
            ),
        )
        self.assertEqual(config.energy_ipmi_username, "testipmiusername1")
        self.assertEqual(config.energy_ipmi_password, "testipmipassword1")
        self.assertEqual(config.energy_ipmi_timeout, 20)
        self.assertEqual(config.profile_hdf5_dir, "/mydir1234")
        self.assertEqual(config.profile_hdf5_default, ["none"])
        self.assertEqual(config.profile_influxdb_database, "test_acct_gather_db")
        self.assertEqual(config.profile_influxdb_default, ["none"])
        self.assertEqual(config.profile_influxdb_host, "testhostname1")
        self.assertEqual(config.profile_influxdb_pass, "testpassword1")
        self.assertEqual(config.profile_influxdb_rt_policy, "testpolicy1")
        self.assertEqual(config.profile_influxdb_user, "testuser1")
        self.assertEqual(config.profile_influxdb_timeout, 20)
        self.assertEqual(config.infiniband_ofed_port, 1)
        self.assertEqual(config.sysfs_interfaces, ["enp0s2"])

    def test_load_fail(self) -> None:
        """Test that bogus values are automatically caught when loading a new model."""
        # Catch if field value is unexpected. e.g. not a boolean value.
        with self.assertRaises(ValueError):
            AcctGatherConfig.from_str(
                """
                energyipmicalcadjustment=totally
                """
            )

        # Catch if field is unexpected or in the incorrect syntax.
        with self.assertRaises(ModelError):
            AcctGatherConfig.from_str(
                """
                observe_the_jobs=totally
                """
            )

        # Catch if field value is invalid when checking against the model schema.
        with self.assertRaises(ModelError):
            AcctGatherConfig.from_str(
                """
                EnergyIPMIFrequency=ALL THE TIME!!
                """
            )

    def test_edit_fail(self) -> None:
        """Test that bogus attributes are handled when editing a loaded model."""
        # Catch if user tries to edit a non-existent attribute.
        with self.assertRaises(AttributeError):
            config = acctgatherconfig.loads(EXAMPLE_ACCT_GATHER_CONFIG)
            config.profile_influxdbrt_policy = "newtestpolicy"

        # Catch if user tries to access a non-existent attribute.
        with self.assertRaises(AttributeError):
            config = acctgatherconfig.loads(EXAMPLE_ACCT_GATHER_CONFIG)
            _ = config.profile_influxdbrt_policy
