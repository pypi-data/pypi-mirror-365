# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
pyunit testing.
"""
import subprocess

import annize.features.testing.common


class Test(annize.features.testing.common.Test):

    def __init__(self, *, src: str):
        super().__init__()
        self.__src = src  # TODO use FsEntry instead

    def run(self):
        #TODO
        subprocess.check_call(["python3", "-m", "unittest", "discover", "-v", "-b", "-s", self.__src, "-p", "TODO.py"],
                              cwd="/home/pino/projects/annize")
