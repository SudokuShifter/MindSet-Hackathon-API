from enum import Enum


DEFAULT_PUBLIC_JWT_KEY = """
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAmzt34d5Qj5i5T2YfvvpgnHJUAPLJSeEIDt5x4LRtzl0=
-----END PUBLIC KEY-----
"""

DEFAULT_PRIVATE_JWT_KEY = """
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIAyBvuOyXO5PW/EB+xFFV79K8aGWrqhYLNjH71ViIam8
-----END PRIVATE KEY-----
"""

E_KEYS = [
    1,
    3,
    -5,
    8,
    10,
    13,
    -15,
    17,
    -20,
    22,
    25,
    27,
    -29,
    -32,
    -34,
    -37,
    39,
    -41,
    44,
    46,
    49,
    -51,
    53,
    56,
]
N_KEYS = [
    2,
    4,
    7,
    9,
    11,
    14,
    16,
    19,
    21,
    23,
    26,
    28,
    31,
    33,
    35,
    38,
    40,
    43,
    45,
    47,
    50,
    52,
    55,
    57,
]
L_KEYS = [6, -12, -18, 24, -30, 36, -42, -48, -54]
