from __future__ import annotations

import pytest

import bibfmt


@pytest.mark.parametrize(
    ("string", "ref"),
    [
        pytest.param(
            "The Magnus expansion and some of its applications",
            "The {Magnus} expansion and some of its applications",
            id="name",
        ),
        pytest.param(
            "On generalized averaged Gaussian formulas, II",
            "On generalized averaged {Gaussian} formulas, {II}",
            id="roman_number",
        ),
        pytest.param(
            "Gaussian Hermitian Jacobian",
            "{Gaussian} {Hermitian} {Jacobian}",
            id="name_sequence",
        ),
        pytest.param(
            "VODE: a variable-coefficient ODE solver",
            "{VODE:} {A} variable-coefficient {ODE} solver",
            id="colon",
        ),
        pytest.param(
            "GMRES: A generalized minimal residual algorithm",
            "{GMRES:} {A} generalized minimal residual algorithm",
            id="captital_after_colon",
        ),
        pytest.param(
            "Peano's kernel theorem for vector-valued functions",
            "{Peano's} kernel theorem for vector-valued functions",
            id="name_with_apos",
        ),
        pytest.param(
            "Exponential Runge-Kutta methods for parabolic problems",
            "Exponential {Runge}-{Kutta} methods for parabolic problems",
            id="dashed_names",
        ),
        pytest.param(
            "Dash-Dash Double--Dash Triple---Dash",
            "Dash-Dash Double--Dash Triple---Dash",
            id="dashes",
        ),
        pytest.param("x: {X}", "x: {X}", id="colon_pre_fmt"),
        pytest.param(
            "{Aaa ${\\text{Pt/Co/AlO}}_{x}$ aaa bbb}",
            "{Aaa {${\\text{Pt/Co/AlO}}_{x}$} aaa bbb}",
            id="tex_math",
        ),
        pytest.param("z*", "z*", id="asterisk"),
        pytest.param("A \\LaTeX title", "A \\LaTeX title", id="macro"),
    ],
)
def test_translate_title(string, ref):
    assert bibfmt.tools._translate_title(string) == ref
