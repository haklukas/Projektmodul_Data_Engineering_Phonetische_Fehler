from enum import Enum

class Textclasses(Enum):
    NUMBER = 0
    NAME = 1
    COUNTRY = 2
    COMPANY = 3
    NATURAL_TEXT = 4

PARAMS = {
    Textclasses.NUMBER: {
        "noise_layers": 3,
        "volumes": [0.7, 1.0],
        "speeds": [1.0, 2.0],
        "num_interrupts": 2,
        "len_interrupts": 0.2,
        "snr_lower": 10.0,
        "snr_upper": 20.0,
        "total_snrlevels": 2
    },
    Textclasses.NAME: {
        "noise_layers": 1,
        "volumes": [0.7, 1.0],
        "speeds": [1.0, 2.0],
        "num_interrupts": 1,
        "len_interrupts": 0.2,
        "snr_lower": 10.0,
        "snr_upper": 20.0,
        "total_snrlevels": 2

    },
    Textclasses.COUNTRY: {
        "noise_layers": 2,
        "volumes": [1.0],
        "speeds": [1.0],
        "num_interrupts": 3,
        "len_interrupts": 0.2,
        "snr_lower": 10.0,
        "snr_upper": 20.0,
        "total_snrlevels": 2

    },
    Textclasses.COMPANY: {
        "noise_layers": 2,
        "volumes": [1.0],
        "speeds": [1.0],
        "num_interrupts": 3,
        "len_interrupts": 0.2,
        "snr_lower": 10.0,
        "snr_upper": 20.0,
        "total_snrlevels": 2

    },
    Textclasses.NATURAL_TEXT: {
        "noise_layers": 2,
        "volumes": [1.0],
        "speeds": [1.0],
        "num_interrupts": 3,
        "len_interrupts": 0.2,
        "snr_lower": 10.0,
        "snr_upper": 20.0,
        "total_snrlevels": 2

    }
}

"""
for t in Textclasses:
    print(t)
    print(PARAMS[t]["num_interrupts"])

original_texts=[
            ("Bosnien und Herzegowina", Textclasses.COUNTRY),
            ("Maria Sklodowska-Curie", Textclasses.NAME),
            ("L'arc de Triomphe", Textclasses.COUNTRY),
            ("Samsung", Textclasses.COMPANY),
            ("17543", Textclasses.NUMBER),
            ("siebzehntausendfünfhundertfünfundfünfzig", Textclasses.NUMBER),
            ("ein heißer Mittwochabend mit vielen Eiswürfeln", Textclasses.NATURAL_TEXT)
]

print([x[0] for x in original_texts])"""

audios_by_class = [[]] * len(Textclasses)
print(audios_by_class)