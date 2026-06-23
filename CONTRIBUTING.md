# Contributing to `slurmutils`

Do you want to contribute to the `slurmutils` repository? You've come to the right place then!
__Here is how you can get involved.__

Before you start working on your contribution, please familiarize yourself with the [Charmed
HPC project's contributing guide]. After you've gone through the main contributing guide,
you can use this guide for specific information on contributing to the `slurmutils` repository.

Have any questions? Feel free to ask them in the [Ubuntu High-Performance Computing Matrix chat].

[Charmed HPC project's contributing guide]: https://github.com/canonical/docs/blob/main/CONTRIBUTING.md
[Ubuntu High-Performance Computing Matrix chat]: https://matrix.to/#/#hpc:ubuntu.com


## Hacking on `slurmutils`


This repository uses [just](https://github.com/casey/just) and [uv](https://github.com/astral-sh/uv) for development
which provide some useful commands that will help you while hacking on `slurmutils`:

```shell
# Create a developer environment
just env

# Upgrade uv.lock with the latest dependencies
just upgrade
```

Run `just help` to view the full list of available recipes.

### Before opening a pull request on the `slurmutils` repository

Ensure that your changes pass all the existing tests, and that you have added tests
for any new features you're introducing in this changeset.

Your proposed changes will not be reviewed until your changes pass all the
required tests. You can run the required tests locally using `just`:

```shell
# Apply formatting standards to code
just fmt

# Check code against coding style standards
just lint

# Run static type checks
just typecheck

# Run unit tests
just unit
```

## License information

By contributing to `slurmutils`, you agree to license your contribution under
the GNU Lesser General Public License v3.0 only license.

### Adding a new file to `slurmutils`

If you add a new source code file to the repository, add the following license header
as a comment to the top of the file with the copyright owner set to the organization
you are contributing on behalf of and the current year set as the copyright year.

```text
Copyright (C) [year] [name of author]

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

### Updating an existing file in `slurmutils`

If you are making changes to an existing file, and the copyright year is not the current year,
update the year range to include the current year. For example, if a file's copyright year is:

```text
Copyright 2023 Canonical Ltd.
```

and you make changes to that file in 2025, update the copyright year in the file to:

```text
Copyright 2023-2025 Canonical Ltd.
```

