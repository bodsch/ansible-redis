#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2022-2023, Bodo Schulz <bodo@boone-schulz.de>
# Apache-2.0 (see LICENSE or https://opensource.org/license/apache-2-0)
# SPDX-License-Identifier: Apache-2.0

"""
Ansible module: redis_version

This module detects the installed Redis or Valkey server version by executing
the respective server binary with ``--version`` and parsing the semantic
version (X.Y.Z) from stdout.

It is read-only and supports check mode.
"""

from __future__ import absolute_import, division, print_function

import re
from typing import List, Optional, Sequence, Tuple, TypedDict

from ansible.module_utils.basic import AnsibleModule

# ---------------------------------------------------------------------------------------

DOCUMENTATION = r"""
---
module: redis_version
short_description: Read the installed Redis or Valkey server version
version_added: "1.1.3"
author:
  - Bodo Schulz (@bodsch) <bodo@boone-schulz.de>

description:
  - Executes C(redis-server --version) (preferred) or C(valkey-server --version) on the target host.
  - Parses the semantic version (C(X.Y.Z)) from the output.
  - Returns the full stdout and stdout_lines for troubleshooting.

options: {}

notes:
  - This module is read-only and supports check mode.

requirements:
  - Redis server (C(redis-server)) or Valkey server (C(valkey-server)) installed on the target host.
"""

EXAMPLES = r"""
- name: Get Redis/Valkey version
  redis_version:
  register: redis

- name: Print parsed version
  ansible.builtin.debug:
    msg: "{{ redis.server }} version: {{ redis.version }}"

- name: Print raw stdout for troubleshooting
  ansible.builtin.debug:
    var: redis.stdout_lines
"""

RETURN = r"""
failed:
  description:
    - Indicates whether determining or parsing the version failed.
  returned: always
  type: bool

server:
  description:
    - Server identifier parsed from the version output (for example C(Redis server) or C(Valkey server)).
  returned: always
  type: str
  sample: "Redis server"

version:
  description:
    - Parsed Redis/Valkey version (C(X.Y.Z)) if found, otherwise C(unknown).
  returned: always
  type: str
  sample: "7.2.4"

stdout:
  description:
    - Raw stdout from the executed C(--version) command.
  returned: always
  type: str

stdout_lines:
  description:
    - Stdout split into lines.
  returned: always
  type: list
  elements: str
"""

# ---------------------------------------------------------------------------------------


class RedisVersionResult(TypedDict):
    """Result structure returned by :meth:`RedisVersion.run`."""

    stdout: str
    stdout_lines: List[str]
    failed: bool
    server: str
    version: str


class RedisVersion:
    """
    Redis/Valkey version detector.

    The module prefers ``redis-server`` when both Redis and Valkey are present,
    otherwise falls back to ``valkey-server``.
    """

    _VERSION_RE = re.compile(
        r"^(?P<server>.*server)\s+v=(?P<version>\d+\.\d+\.\d+)\b",
        re.MULTILINE,
    )

    def __init__(self, module: AnsibleModule) -> None:
        """
        Create a detector instance.

        Args:
            module: Ansible module instance used for binary discovery and command execution.
        """
        self._module = module
        self._redis_binary: Optional[str] = module.get_bin_path(
            "redis-server", required=False
        )
        self._valkey_binary: Optional[str] = module.get_bin_path(
            "valkey-server", required=False
        )

    def run(self) -> RedisVersionResult:
        """
        Execute the server binary with ``--version`` and parse the version.

        Returns:
            A dict compatible with ``module.exit_json``.
        """
        result: RedisVersionResult = {
            "stdout": "",
            "stdout_lines": [],
            "failed": True,
            "server": "unknown",
            "version": "unknown",
        }

        binary = self._redis_binary or self._valkey_binary
        if not binary:
            result["stdout"] = (
                "Neither redis-server nor valkey-server found on target host."
            )
            result["stdout_lines"] = [result["stdout"]]
            return result

        rc, out, err = self._exec([binary, "--version"])

        # Keep stdout for troubleshooting, even on non-zero rc.
        stdout = (out or "").rstrip()
        if not stdout and err:
            # Some builds may emit to stderr; preserve it as best-effort.
            stdout = err.rstrip()

        result["stdout"] = stdout
        result["stdout_lines"] = stdout.splitlines() if stdout else []

        if rc != 0:
            # Parsing might still succeed, but rc!=0 is generally a failure signal.
            self._module.log(
                msg=f"redis_version: command returned rc={rc} err='{err.rstrip()}'"
            )

        if stdout:
            match = self._VERSION_RE.search(stdout)
            if match:
                result["server"] = match.group("server")
                result["version"] = match.group("version")
                result["failed"] = False

        return result

    def _exec(self, argv: Sequence[str]) -> Tuple[int, str, str]:
        """
        Execute a command on the target.

        Args:
            argv: Command and arguments.

        Returns:
            Tuple of (rc, stdout, stderr).
        """
        rc, out, err = self._module.run_command(list(argv), check_rc=False)
        return int(rc), out, err


def main() -> None:
    """Module entrypoint."""
    module = AnsibleModule(
        argument_spec={},
        supports_check_mode=True,
    )

    detector = RedisVersion(module)
    module.exit_json(**detector.run())


if __name__ == "__main__":
    main()
