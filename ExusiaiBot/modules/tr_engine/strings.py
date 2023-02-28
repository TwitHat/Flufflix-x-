#    Haruka Aya (A telegram bot project)
#    Copyright (C) 2017-2019 Paul Larsen
#    Copyright (C) 2019-2020 Akito Mizukito (Haruka Network Development)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import yaml
from codecs import encode, decode

from ExusiaiBot import LOGGER
from ExusiaiBot.modules.sql.locales_sql import prev_locale

LANGUAGES = ['en-US', 'en-GB', 'id', 'ru', 'es']

strings = {i: yaml.full_load(open(f"locales/{i}.yml", "r")) for i in LANGUAGES}


def tld(chat_id, t, show_none=True):
    if LANGUAGE := prev_locale(chat_id):
        LOCALE = LANGUAGE.locale_name
        if LOCALE in ('en-US') and t in strings['en-US']:
            return decode(
                encode(strings['en-US'][t], 'latin-1', 'backslashreplace'),
                'unicode-escape',
            )
        elif LOCALE in ('en-GB') and t in strings['en-GB']:
            return decode(
                encode(strings['en-GB'][t], 'latin-1', 'backslashreplace'),
                'unicode-escape',
            )
        elif LOCALE in ('id') and t in strings['id']:
            return decode(
                encode(strings['id'][t], 'latin-1', 'backslashreplace'),
                'unicode-escape',
            )
        elif LOCALE in ('ru') and t in strings['ru']:
            return decode(
                encode(strings['ru'][t], 'latin-1', 'backslashreplace'),
                'unicode-escape',
            )
        elif LOCALE in ('es') and t in strings['es']:
            return decode(
                encode(strings['es'][t], 'latin-1', 'backslashreplace'),
                'unicode-escape',
            )
    if t in strings['en-US']:
        return decode(
            encode(strings['en-US'][t], 'latin-1', 'backslashreplace'),
            'unicode-escape',
        )
    err = f"No string found for {t}.\nReport it in @exusiaisupport."
    LOGGER.warning(err)
    return err


def tld_list(chat_id, t):
    if LANGUAGE := prev_locale(chat_id):
        LOCALE = LANGUAGE.locale_name
        if LOCALE in ('en-US') and t in strings['en-US']:
            return strings['en-US'][t]
        elif LOCALE in ('en-GB') and t in strings['en-GB']:
            return strings['en-GB'][t]
        elif LOCALE in ('id') and t in strings['id']:
            return strings['id'][t]
        elif LOCALE in ('ru') and t in strings['ru']:
            return strings['ru'][t]
        elif LOCALE in ('es') and t in strings['es']:
            return strings['es'][t]

    if t in strings['en-US']:
        return strings['en-US'][t]

    LOGGER.warning(f"#NOSTR No string found for {t}.")
    return f"No string found for {t}.\nReport it in @exusiaisupport."


# def tld_help(chat_id, t):
#     LANGUAGE = prev_locale(chat_id)
#     print("tld_help ", chat_id, t)
#     if LANGUAGE:
#         LOCALE = LANGUAGE.locale_name

#         t = t + "_help"

#         print("Test2", t)

#         if LOCALE in ('ru') and t in RussianStrings:
#             return RussianStrings[t]
#         elif LOCALE in ('ua') and t in UkrainianStrings:
#             return UkrainianStrings[t]
#         elif LOCALE in ('es') and t in SpanishStrings:
#             return SpanishStrings[t]
#         elif LOCALE in ('tr') and t in TurkishStrings:
#             return TurkishStrings[t]
#         elif LOCALE in ('id') and t in IndonesianStrings:
#             return IndonesianStrings[t]
#         else:
#             return False
#     else:
#         return False
