# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
pylint testing.
"""
import subprocess

import annize.features.testing.common
import annize.fs


class Test(annize.features.testing.common.Test):

    def __init__(self, *, source: annize.fs.FilesystemContent):
        super().__init__()
        self.__source = source

    def run(self):
        srcpath = self.__source.path()
        subprocess.check_call(["pylint", srcpath], cwd=srcpath)
