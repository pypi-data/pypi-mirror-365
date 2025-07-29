# SPDX-FileCopyrightText: © 2021 Josef Hahn
# SPDX-License-Identifier: AGPL-3.0-only
"""
TODO.

See :py:func:`tr`.
"""
import abc
import locale
import os
import subprocess
import threading
import typing as t

import annize.asset


CultureSpec = "Culture|str|None"


class TranslationProvider(abc.ABC):

    @abc.abstractmethod
    def translate(self, stringname: str, *, culture: "Culture") -> str|None:
        pass


class GettextTranslationProvider(TranslationProvider):

    def __init__(self, mopath):
        self.__mopath = mopath
        self.__gettexttrs = {}

    def translate(self, stringname: str, *, culture: "Culture"):
        culture = get_culture(culture)
        import gettext # TODO
        gettexttr = self.__gettexttrs.get(culture.iso_639_1_lang_code, None)
        if not gettexttr:
            gettexttr = gettext.translation("annize", self.__mopath, languages=[culture.iso_639_1_lang_code],
                                            fallback=True)
            class Failfallback(gettext.NullTranslations):
                def __getattribute__(self, name: str):
                    def afct(*_, **__):
                        return None
                    return afct
            gettexttr.add_fallback(Failfallback())
            self.__gettexttrs[culture.iso_639_1_lang_code] = gettexttr
        return gettexttr.gettext(stringname)


_providers = []


def add_translation_provider(provider: TranslationProvider, *, priority: int = 0) -> None:
    _providers.append((priority, provider))
    _providers.sort(key=lambda prtup: prtup[0])


def translation_providers() -> list[TranslationProvider]:
    return [prtup[1] for prtup in _providers]


add_translation_provider(GettextTranslationProvider(annize.asset.data.mo_dir), priority=100_000) #TODO


def tr(stringname: str, *, culture: CultureSpec = None) -> str:  # TODO ?!
    return ProvidedTrStr(stringname).translate(culture)


class TrStr(abc.ABC):

    @staticmethod
    def tr(stringname: str) -> "TrStr":
        return ProvidedTrStr(stringname)

    def translate(self, culture: CultureSpec = None) -> str:
        culture = get_culture(culture)
        acultures = [culture]
        while acultures:
            #TODO add fallbacks
            cculture = acultures.pop(0)
            result = self.get_variant(cculture) if (not isinstance(cculture, IdCulture)) else self.stringname  # TODO
            if result is not None:
                return result
            acultures += cculture.fallback_cultures
        raise TranslationUnavailableError(self.stringname, culture.english_lang_name)

    @abc.abstractmethod
    def get_variant(self, culture: "Culture") -> str:
        pass

    @property
    def stringname(self) -> str:
        return repr(self)

    def format(self_, *args, **kwargs) -> "TrStr":
        if "self" in kwargs:
            kwargs.pop("self")  # TODO weg?!
        class ATrStr(TrStr):
            def get_variant(self, culture):
                oresult = self_.get_variant(culture)
                return oresult.format(*args, **kwargs) if (oresult is not None) else None
        return ATrStr()

    def __str__(self):
        return self.translate()


class ProvidedTrStr(TrStr):

    def __init__(self, stringname: str):
        super().__init__()
        self.__stringname = stringname

    @property
    def stringname(self):
        return self.__stringname

    def get_variant(self, culture):
        culture = get_culture(culture)
        for provider in translation_providers():
            result = provider.translate(self.__stringname, culture=culture)
            if result is not None:
                return result
        return None


#: Type annotation for something that can be either a :samp:`str` or a :py:class:`TrStr`.
TrStrOrStr = TrStr|str


def tr_if_trstr(txt: TrStrOrStr, culture: CultureSpec = None) -> str:  # TODO
    if (not txt) or isinstance(txt, str):
        return txt
    return txt.translate(culture=culture)


def to_trstr(txt: TrStrOrStr) -> TrStr:
    if isinstance(txt, str):
        class ATrStr(TrStr):
            def get_variant(self, culture):
                return txt
        return ATrStr()
    return txt


class Culture:

    @staticmethod
    def get_from_iso_639_1_lang_code(iso_639_1_lang_code: str, subcode: str|None = None,
                                     fallback_cultures: t.Iterable["Culture"] = ()):
        import pycountry  # TODO dependency
        language = pycountry.languages.get(alpha_2=iso_639_1_lang_code.upper())
        return Culture(language.name, iso_639_1_lang_code, subcode, fallback_cultures)

    def __init__(self, english_lang_name: str, iso_639_1_lang_code: str, subcode: str|None,
                 fallback_cultures: t.Iterable["Culture"]):
        self.__english_lang_name = english_lang_name
        self.__iso_639_1_lang_code = iso_639_1_lang_code.lower()
        self.__subcode = subcode.upper() if subcode else None
        self.__fallback_cultures = fallback_cultures

    @property
    def english_lang_name(self) -> str:
        return self.__english_lang_name

    @property
    def iso_639_1_lang_code(self) -> str:
        return self.__iso_639_1_lang_code

    @property
    def subcode(self) -> str:
        return self.__subcode

    @property
    def fullname(self) -> str:
        result = self.iso_639_1_lang_code
        if self.subcode:
            result += f"_{self.subcode}"
        return result

    @property
    def fallback_cultures(self) -> t.Iterable["Culture"]:
        return tuple(self.__fallback_cultures)

    def __find_lcall(self):
        iso_639_1_lang_code = self.iso_639_1_lang_code or "en"
        for lcode in [lcc.strip() for lcc in subprocess.check_output(["locale", "-a"]).decode().split("\n")]:
            if lcode.lower().startswith(iso_639_1_lang_code):
                if (not self.subcode) or lcode[3:].startswith(self.subcode):
                    return lcode
        raise RuntimeError(f"Unable to find a locale that matches {self.iso_639_1_lang_code!r}")

    @staticmethod
    def __get_env():
        try:
            locale_lc_all = ".".join(locale.getlocale(locale.LC_ALL))
        except TypeError:
            locale_lc_all = None
        return os.environ.get("LC_ALL", None), os.environ.get("LANGUAGE", None), locale_lc_all

    @staticmethod
    def __set_env(lc_all, language, locale_lc_all):
        def setenv(ekey, evalue):
            if evalue is None:
                if ekey in os.environ:
                    os.environ.pop(ekey)
            else:
                os.environ[ekey] = evalue
        setenv("LC_ALL", lc_all)
        setenv("LANGUAGE", language)
        locale.setlocale(locale.LC_ALL, locale_lc_all or "")

    def __enter__(self):
        _culturestack.stack = stack = getattr(_culturestack, "stack", [])
        stack.append((self, Culture.__get_env()))
        lcall = self.__find_lcall()
        Culture.__set_env(lcall, self.iso_639_1_lang_code, lcall)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _, lenv = _culturestack.stack.pop()
        if len(_culturestack.stack) == 0:
            delattr(_culturestack, "stack")
        Culture.__set_env(*lenv)


class UnspecifiedCulture(Culture):  # TODO

    def __init__(self):
        super().__init__(english_lang_name="Unspecified", iso_639_1_lang_code="", subcode=None, fallback_cultures=())


unspecified_culture = UnspecifiedCulture()


class IdCulture(Culture):

    def __init__(self):
        super().__init__(english_lang_name="IDs", iso_639_1_lang_code="", subcode=None, fallback_cultures=())


class _CultureFence(Culture):  # TODO just use `None` instead?

    def __init__(self):
        super().__init__(english_lang_name="", iso_639_1_lang_code="", subcode=None, fallback_cultures=())


def get_culture(culture: CultureSpec, *, fallback_cultures: t.Iterable[Culture] = ()) -> Culture|None:#TODO
    if culture is None:
        if fallback_cultures:
            raise ValueError("`fallback_cultures` must not be specified without `culture`")
        return current_culture()
    if isinstance(culture, str):
        cultureparts = culture.replace("-", "_").split("_")
        if len(cultureparts) == 1:
            culturecode, culturesubcode = cultureparts[0], None
        elif len(cultureparts) == 2:
            culturecode, culturesubcode = cultureparts
        else:
            raise ValueError(f"Invalid culture string '{culture}'")
        culture = Culture.get_from_iso_639_1_lang_code(culturecode, culturesubcode, fallback_cultures=fallback_cultures)
    return culture


_culturestack = threading.local()


def current_culture() -> Culture:
    stack = getattr(_culturestack, "stack", None)
    if stack:
        stacklast = stack[-1][0]
        if not isinstance(stacklast, _CultureFence):
            return stacklast
    raise NoCurrentCultureError()


def annize_user_interaction_culture() -> Culture:
    return get_culture(os.environ.get("LANGUAGE")[:2] or "en")  # TODO


def friendly_join_string_list(strlist: list[TrStrOrStr]) -> TrStr:
    tstrlist = [to_trstr(txt) for txt in strlist]
    class ATrStr(TrStr):
        def get_variant(self, culture):
            trand = tr("an_And")
            sstrlist = [txt.get_variant(culture) for txt in tstrlist]
            return ", ".join(sstrlist[:-1]) + (f" {trand} " if len(sstrlist) > 1 else "") + sstrlist[-1]
    return ATrStr()


class NoCurrentCultureError(TypeError):

    def __init__(self):
        super().__init__("There is no current Annize i18n culture")


class TranslationUnavailableError(TypeError):

    def __init__(self, stringname: str, language: str):
        super().__init__(f"There is no translation for '{stringname}' in language '{language}'")
