import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import pytest

from psygen.trait.utils.probability_helpers import ProbabilityHelper as P


def test_normalise_basic():
    arr = [0.2, 0.3, 0.5]
    norm = P.normalise(arr)
    assert pytest.approx(sum(norm)) == 1.0
    assert norm == arr  # already normalised


def test_normalise_handles_negatives():
    arr = [-1, 1]
    norm = P.normalise(arr)
    assert norm[0] == 0.0
    assert norm[1] == 1.0


def test_shift():
    probs = [0.2, 0.3, 0.5]
    P.shift(probs, 2, 0, 0.1)
    assert pytest.approx(probs) == [0.3, 0.3, 0.4]


def test_cap():
    probs = [0.1, 0.8, 0.1]
    P.cap(probs, 1, 0.5)
    assert pytest.approx(probs) == [0.25, 0.5, 0.25]


def test_shift_equal():
    probs = [0.3, 0.3, 0.4]
    P.shift_equal(probs, 1, [0, 2], 0.2)
    assert pytest.approx(probs) == [0.2, 0.5, 0.3]


def test_shift_from_to():
    probs = [0.3, 0.3, 0.4]
    P.shift_from_to(probs, [0, 1], 2, 0.2)
    assert pytest.approx(probs) == [0.2, 0.2, 0.6]


def test_multiply():
    probs = [0.1, 0.2, 0.3]
    P.multiply(probs, [0, 2], 2)
    assert probs == [0.2, 0.2, 0.6]
