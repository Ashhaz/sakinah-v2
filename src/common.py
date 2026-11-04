# Shared helpers for the content files.

SURAHS = {
    2: "Al-Baqarah", 3: "Āl ʿImrān", 4: "An-Nisāʾ", 5: "Al-Māʾidah", 6: "Al-Anʿām", 7: "Al-Aʿrāf", 9: "At-Tawbah", 10: "Yūnus",
    11: "Hūd", 12: "Yūsuf", 13: "Ar-Raʿd", 14: "Ibrāhīm", 15: "Al-Ḥijr", 16: "An-Naḥl", 17: "Al-Isrāʾ",
    18: "Al-Kahf", 19: "Maryam", 20: "Ṭā-Hā", 21: "Al-Anbiyāʾ", 22: "Al-Ḥajj", 23: "Al-Muʾminūn",
    24: "An-Nūr", 25: "Al-Furqān", 28: "Al-Qaṣaṣ", 29: "Al-ʿAnkabūt", 30: "Ar-Rūm", 31: "Luqmān", 33: "Al-Aḥzāb", 39: "Az-Zumar",
    41: "Fuṣṣilat", 42: "Ash-Shūrā", 49: "Al-Ḥujurāt", 50: "Qāf", 51: "Adh-Dhāriyāt", 53: "An-Najm", 57: "Al-Ḥadīd",
    62: "Al-Jumuʿah", 63: "Al-Munāfiqūn", 64: "At-Taghābun", 65: "At-Ṭalāq", 67: "Al-Mulk",
    78: "An-Nabaʾ", 82: "Al-Infiṭār", 90: "Al-Balad", 93: "Aḍ-Ḍuḥā", 91: "Ash-Shams", 94: "Ash-Sharḥ", 95: "At-Tīn",
    71: "Nūḥ", 102: "At-Takāthur", 103: "Al-ʿAṣr", 112: "Al-Ikhlāṣ", 113: "Al-Falaq", 114: "An-Nās",
}

COLLECTIONS = {
    "bukhari": "Sahih al-Bukhari",
    "muslim": "Sahih Muslim",
    "tirmidhi": "Jami‘ at-Tirmidhi",
    "abudawud": "Sunan Abi Dawud",
}


def ra(name, f=False):
    return f"{name} (may Allah be pleased with {'her' if f else 'him'})"


def ra2(a, b):
    return f"{a} and {b} (may Allah be pleased with them)"


def Q(ref, ayahs, en, why="", arabic=True, note=""):
    """A Qur'an verse card. `ayahs` = list of 'surah:ayah' keys whose Arabic is loaded live.
    arabic=False -> the translation is only PART of the verse, so the Arabic is not shown inline
    (the reader is sent to the full verse instead)."""
    return dict(ref=ref, ayahs=ayahs, en=en, why=why, arabic=arabic, note=note)


def H(en, by, srcs, why="", grade=None):
    """A hadith card. srcs = list of (collection_key, number) or (None, 'free text label')."""
    return dict(en=en, by=by, srcs=srcs, why=why, grade=grade)


def B(n):
    return ("bukhari", n)


def M(n):
    return ("muslim", n)


def T(n):
    return ("tirmidhi", n)


def D(n):
    return ("abudawud", n)
