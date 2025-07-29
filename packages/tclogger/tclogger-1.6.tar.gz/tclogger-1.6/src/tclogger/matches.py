import re

from copy import deepcopy
from rapidfuzz import fuzz
from typing import Literal, Union, Protocol

KeyType = Union[str, int, list[Union[str, int]]]


class MatchFuncType(Protocol):

    def __call__(self, key: KeyType, pattern: KeyType, **kwargs) -> bool:
        """Match key with pattern."""
        ...


def match_val(
    val: str,
    vals: list[str],
    ignore_case: bool = True,
    spaces_to: Literal["keep", "ignore" "merge"] = "merge",
    use_fuzz: bool = False,
) -> tuple[str, int, float]:
    """
    Return:
        - closest val
        - index of the closest val in the list
        - similarity score (0-1)

    score = (1 – d/L)
    * d: distance by insert(1)/delete(1)/replace(2)
    * L: length sum of both strings
    """
    if not vals:
        return None, None, 0

    xval = deepcopy(val)
    xvals = deepcopy(vals)

    if spaces_to == "ignore":
        xval = re.sub(r"\s+", "", val.strip())
        xvals = [re.sub(r"\s+", "", v.strip()) for v in vals]
    elif spaces_to == "merge":
        xval = re.sub(r"\s+", " ", val.strip())
        xvals = [re.sub(r"\s+", " ", v.strip()) for v in vals]
    else:
        pass

    if ignore_case:
        xval = xval.lower()
        xvals = [v.lower() for v in xvals]

    if use_fuzz:
        scores = [fuzz.ratio(xval, v) / 100.0 for v in xvals]
    else:
        scores = [1 if xval == v else 0 for v in xvals]

    midx, max_score = None, 0.0
    for i, s in enumerate(scores):
        if s > max_score:
            midx = i
            max_score = s
    if midx is None:
        mval = None
    else:
        mval = vals[midx]
    return mval, midx, max_score


def unify_key_to_list(
    key: KeyType, ignore_case: bool = False, sep: str = "."
) -> list[Union[str, int]]:
    xkey = deepcopy(key)
    if isinstance(xkey, str):
        # split "a.b.c" to ["a", "b", "c"]
        xkey = xkey.split(sep)
    elif isinstance(xkey, (list, tuple)):
        # split case like ["a.b", "c"]
        xkey = [k.split(sep) if isinstance(k, str) else k for k in xkey]
        xkey = [item for sublist in xkey for item in sublist]
    if ignore_case:
        xkey = [k.lower() if isinstance(k, str) else k for k in xkey]
    return xkey


def unify_key_to_str(key: KeyType, ignore_case: bool = False, sep: str = ".") -> str:
    """Compared to `unitfy_key_to_list()`, this would enable match_key to accept str-format list idx in as key part.
    This means that "a.0.x" is same to ["a", 0, "x"] and ["a", "0", "x"].
    """
    xkey = deepcopy(key)
    if isinstance(xkey, (list, tuple)):
        xkey = sep.join(str(k) for k in xkey)
    if ignore_case:
        xkey = xkey.lower()
    return xkey


def match_key(
    key: KeyType,
    pattern: KeyType,
    ignore_case: bool = False,
    use_regex: bool = False,
    sep: str = ".",
) -> bool:
    unify_params = {"ignore_case": ignore_case, "sep": sep}
    xkey = unify_key_to_str(key, **unify_params)
    xpattern = unify_key_to_str(pattern, **unify_params)
    if use_regex:
        return re.match(xpattern, xkey) is not None
    else:
        return xkey == xpattern
