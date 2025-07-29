# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
Internationalization, i.e. translation and similar tasks.
"""
import typing as t

import annize.flow.run_context
import annize.data
import annize.i18n


class ProjectDefinedTranslationProvider(annize.i18n.TranslationProvider):

    def __init__(self):
        self.__translations = {}

    def __translations_for_stringname(self, stringname: str) -> dict[str, str]:
        result = self.__translations[stringname] = self.__translations.get(stringname) or {}
        return result

    def translate(self, stringname, *, culture):
        return self.__translations_for_stringname(stringname).get(culture.iso_639_1_lang_code)

    def add_translations(self, stringname: str, variants: dict[str, str]) -> None:
        self.__translations_for_stringname(stringname).update(variants)


_translationprovider = ProjectDefinedTranslationProvider()

annize.i18n.add_translation_provider(_translationprovider, priority=-100_000) # TODO who unloads it?!


class String(annize.i18n.ProvidedTrStr):

    def __init__(self, *, stringname: str|None, stringtr: str|None, **variants: str):
        if stringtr:
            stringtr = stringtr.strip()
            if not stringtr.endswith(")"):
                raise ValueError("stringtr specification must end with ')'")
            istart = stringtr.find("(")
            if istart == -1:
                raise ValueError("stringtr specification must contain a '('")
            inrstr = stringtr[istart+1:-1].strip()
            if (len(inrstr) < 3) or (inrstr[0] != inrstr[-1]) or (inrstr[0] not in ["'", '"']):
                raise ValueError("stringtr specification must contain a gettext text id inside quotes")
            stringname = inrstr[1:-1]
        if not stringname:
            stringname = annize.data.UniqueId().long_str
        super().__init__(stringname)
        if variants:
            _translationprovider.add_translations(stringname, variants)


class Culture(annize.i18n.Culture):

    def __init__(self, *, iso_639_1_lang_code: str, subcode: str|None,
                 fallback_cultures: list[annize.i18n.Culture]):
        # TODO weird
        TODO = annize.i18n.get_culture(iso_639_1_lang_code).english_lang_name  # TODO subcode
        super().__init__(TODO, iso_639_1_lang_code=iso_639_1_lang_code, subcode=subcode,
                         fallback_cultures=fallback_cultures)


class UnspecifiedCulture(annize.i18n.UnspecifiedCulture):
    pass


class IdCulture(annize.i18n.IdCulture):
    pass


class ProjectCultures(list):

    def __init__(self, *, cultures: list[annize.i18n.Culture]):
        super().__init__(cultures)


def project_cultures() -> list[annize.i18n.Culture]:
    result = []
    for pcults in annize.flow.run_context.objects_by_type(ProjectCultures):
        result += pcults
    return result
