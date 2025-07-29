# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
gettext-based internationalization.
"""
import os
import subprocess

import annize.features.base
import annize.fs


class UpdatePOs:

    def __init__(self, *, po_directory: annize.fs.TInputPath):
        self.__po_directory = annize.fs.content(po_directory)

    def __call__(self, *args, **kwargs):
        #import time; time.sleep(5)#TODO
        #import annize.user_feedback; xx= annize.user_feedback.message_dialog("fuh!", ["bar", "baz"], config_key="füze");yy= annize.user_feedback.input_dialog(f"describ {xx}", suggested_answer=str(xx));annize.user_feedback.message_dialog(f"you has {yy}!", ["oke"]) #TODO

        po_directory = self.__po_directory.path()
        srcdir = annize.fs.Path(annize.features.base.project_directory())
        allfiles = []
        for dirtup in os.walk(srcdir):
            for f in dirtup[2]:
                ff = f"{dirtup[0]}/{f}"
                if [suf for suf in [".py", ".ui", ".xml"] if ff.endswith(suf)]:
                    allfiles.append(ff)  # TODO  arg list gets very long
        with annize.fs.fresh_temp_directory() as tmpdir:
            pot_file = tmpdir("pot.pot")
            subprocess.check_call(["xgettext", "--keyword=tr", "--add-comments", "--from-code", "utf-8", "--sort-output", "-o", pot_file, *allfiles])
            for fpofile in os.listdir(po_directory):  # TODO zz only *.po ?!
                subprocess.check_call(["msgmerge", "--no-fuzzy-matching", "--backup=none", "--update", f"{po_directory}/{fpofile}", pot_file])


class GenerateMOs:

    def __init__(self, *, po_directory: annize.fs.TFilesystemContent, mo_directory: annize.fs.TInputPath):
        self.__po_directory = annize.fs.content(po_directory)
        self.__mo_directory = annize.fs.content(mo_directory)

    def __call__(self, *args, **kwargs):
        # TODO zz
        podir = self.__po_directory.path()
        mosdir = self.__mo_directory.path()
        for pofile in os.listdir(podir):
            outdir = f"{mosdir}/{pofile[:-3]}/LC_MESSAGES"
            os.makedirs(outdir, exist_ok=True)
            subprocess.check_call(["msgfmt", f"--output-file={outdir}/annize.mo", f"{podir}/{pofile}"])  # TODO zz hardcoded annize.mo
