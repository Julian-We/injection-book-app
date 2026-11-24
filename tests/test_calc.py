import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import injection  # noqa: E402


def test_no_dilution_needed():
    # F362 (aug06 cell): calculate_injection(100, 150) - already above the 0.25 uL
    # pipetting floor without any dilution, so dil_fac should stay at 1 (conc unchanged).
    vol, conc, amount = injection.calculate_injection(100, 150)
    assert conc == 150
    assert amount == 100
    assert vol > 0.25


def test_matches_historical_notebook_output_d545():
    # jan22b cell output, captured verbatim in the notebook: 0.336 uL, 668.75 ng/uL, 150 pg
    vol, conc, amount = injection.calculate_injection(150, 1337.5)
    assert round(vol, 3) == 0.336
    assert conc == 668.75
    assert amount == 150


def test_inject_volume_override_dilution_bug_is_reproduced():
    # oct13a/b/c B465 line: calculate_injection(80, 952, 6) - explicit inject_volume=6.
    # This falls into the auto-dilution branch, whose retry loop silently ignores the
    # caller's inject_volume/mix_volume and uses func()'s defaults (iv=2, mv=3) instead.
    # We assert the *actual* (buggy) historical behavior, not a hypothetically-fixed one.
    vol, conc, amount = injection.calculate_injection(80, 952, 6)
    assert conc == 476.0  # 952 / dil_fac=2
    assert round(vol, 3) == 0.252
    assert amount == 80


def test_calc_injectionmix_adds_phr_and_hepes_rows():
    table = injection.calc_injectionmix({"X | 1": (1.0, 500, 100)}, mix_vol=3, phr=True)
    assert "PhR" in table
    assert "HEPES" in table


def test_calc_injectionmix_hepes_tops_up_to_mix_volume():
    # 1 uL RNA line + 0.3 uL PhR (10% of 3) -> HEPES should be 3 - 1 - 0.3 = 1.7
    table = injection.calc_injectionmix({"X | 1": (1.0, 500, 100)}, mix_vol=3, phr=True)
    hepes_line = [l for l in table.splitlines() if l.startswith("|HEPES")][0]
    assert "1.7" in hepes_line


def test_calc_injectionmix_custom_phr_volume():
    table = injection.calc_injectionmix({"X | 1": (1.0, 500, 100)}, mix_vol=3, phr=True, phr_vol=0.5)
    assert "|PhR| - |     \t 0.5|" in table
    assert "|HEPES| - |    \t 1.5|" in table


def test_calc_injectionmix_default_phr_is_ten_percent():
    table = injection.calc_injectionmix({"X | 1": (1.0, 500, 100)}, mix_vol=3, phr=True)
    assert "|PhR| - |     \t 0.3|" in table
    assert "|HEPES| - |    \t 1.7|" in table
