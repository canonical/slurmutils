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

uv := require("uv")

project_dir := justfile_directory()
tests_dir := project_dir / "tests"

export PY_COLORS := "1"
export PYTHONBREAKPOINT := "pdb.set_trace"

uv_run := "uv run --frozen --extra dev"

[private]
default:
    @just help

# Regenerate uv.lock
lock:
    uv lock

# Create a development environment
env: lock
    uv sync --extra dev

# Upgrade uv.lock with the latest dependencies
upgrade:
    uv lock --upgrade

# Apply coding style standards to code
fmt: lock
    {{uv_run}} ruff format
    {{uv_run}} ruff check --fix

# Check code against coding style standards
lint: lock
    {{uv_run}} codespell --skip uv.lock
    {{uv_run}} ruff check

# Run static type checker on code
typecheck: lock
    {{uv_run}} pyright

# Run unit tests
unit *args: lock
    {{uv_run}} coverage run -m pytest --tb native -v -s {{args}} {{tests_dir / "unit"}}
    {{uv_run}} coverage report
    {{uv_run}} coverage xml -o {{project_dir / "cover" / "coverage.xml"}}

# Publish new release to PyPI
publish:
    @UV_PUBLISH_TOKEN=${UV_PUBLISH_TOKEN} uv publish

# Show available recipes
help:
    @just --list --unsorted
