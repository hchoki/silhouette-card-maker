"""
Tests for create_pdf.py CLI.

Smoke test verifies the CLI runs end-to-end on local fixtures.
Output image tests render pages to PNG and do pixel-level comparison
against pre-generated expected images (see test/generate_expected_images.py).
"""
import os
import json
import tempfile
import zipfile
import pytest
from glob import glob
from click.testing import CliRunner
import numpy as np
from PIL import Image, ImageChops
from pathlib import Path
from create_pdf import cli
from utilities import generate_pdf, process_zip_decks, Registration, FitMode
from pdf_cases import IMAGES_DIR, BACK_DIR, DS_DIR, EXPECTED_DIR, TEST_CASES


# --- Smoke Test ---

def test_basic_create_pdf():
    """Verify the CLI runs without error and produces a PDF."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, 'game.pdf')
        result = runner.invoke(cli, [
            '--front_dir_path', 'test/basic/front',
            '--back_dir_path', 'test/basic/back',
            '--double_sided_dir_path', DS_DIR,
            '--output_path', output_path,
        ])
        assert result.exit_code == 0
        assert os.path.exists(output_path)


# --- Output Image Tests ---
# These tests invoke the CLI with --output_images, rendering each PDF page to
# PNG, then compare pixel-by-pixel against the expected images in EXPECTED_DIR.

def assert_images_match(actual_dir, expected_dir, max_diff_fraction=0.005):
    """Compare all PNG files in actual_dir against expected_dir pixel-by-pixel.

    max_diff_fraction: fraction of pixels allowed to differ (default 0.5%).
    A small tolerance is needed because JPEG decompression and image resampling
    can produce slightly different pixel values across platforms (e.g. Windows
    vs Linux libjpeg), even when the layout logic is identical.
    """
    actual_files = sorted(f for f in os.listdir(actual_dir) if f.endswith('.png'))
    expected_files = sorted(f for f in os.listdir(expected_dir) if f.endswith('.png'))

    assert actual_files == expected_files, (
        f"File mismatch.\n  Actual: {actual_files}\n  Expected: {expected_files}"
    )

    for filename in actual_files:
        with Image.open(os.path.join(actual_dir, filename)) as actual_img, \
             Image.open(os.path.join(expected_dir, filename)) as expected_img:

            assert actual_img.size == expected_img.size, (
                f"{filename}: size mismatch {actual_img.size} != {expected_img.size}"
            )

            # Convert both to same mode for comparison
            actual_rgb = actual_img.convert('RGB')
            expected_rgb = expected_img.convert('RGB')

        diff = ImageChops.difference(actual_rgb, expected_rgb)
        if diff.getbbox() is not None:
            # Calculate how many pixels differ (any channel non-zero)
            diff_pixels = int(np.any(np.array(diff) != 0, axis=2).sum())
            total_pixels = actual_rgb.size[0] * actual_rgb.size[1]
            diff_fraction = diff_pixels / total_pixels
            if diff_fraction > max_diff_fraction:
                raise AssertionError(
                    f"{filename}: images differ. "
                    f"{diff_pixels}/{total_pixels} pixels differ "
                    f"({diff_fraction:.2%} > {max_diff_fraction:.2%} tolerance)."
                )


def run_output_images_test(test_name, extra_args=None):
    """Helper to run a create_pdf --output_images test case."""
    runner = CliRunner()
    expected_dir = os.path.join(EXPECTED_DIR, test_name)

    assert os.path.isdir(expected_dir), (
        f"Expected images directory not found: {expected_dir}. "
        f"Run 'python test/generate_expected_images.py' first."
    )

    with tempfile.TemporaryDirectory() as output_dir:
        args = [
            '--front_dir_path', IMAGES_DIR,
            '--back_dir_path', BACK_DIR,
            '--double_sided_dir_path', DS_DIR,
            '--output_path', os.path.join(output_dir, 'output.pdf'),
            '--output_images',
        ]
        if extra_args:
            args += extra_args

        result = runner.invoke(cli, args)
        assert result.exit_code == 0, (
            f"CLI failed with exit code {result.exit_code}.\n"
            f"Output: {result.output}\n"
            f"Exception: {result.exception}"
        )

        assert_images_match(output_dir, expected_dir)


@pytest.mark.parametrize("test_name,extra_args", TEST_CASES, ids=[n for n, _ in TEST_CASES])
def test_output_images(test_name, extra_args):
    run_output_images_test(test_name, extra_args)


# --- Borderless Tests ---

def test_borderless_create_pdf():
    """Verify the CLI runs with --borderless and produces a PDF."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, 'game.pdf')
        result = runner.invoke(cli, [
            '--front_dir_path', 'test/basic/front',
            '--back_dir_path', 'test/basic/back',
            '--double_sided_dir_path', DS_DIR,
            '--output_path', output_path,
            '--borderless',
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
        assert os.path.exists(output_path)


def test_borderless_a4_create_pdf():
    """Verify --borderless works with explicit paper size."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, 'game.pdf')
        result = runner.invoke(cli, [
            '--front_dir_path', 'test/basic/front',
            '--back_dir_path', 'test/basic/back',
            '--double_sided_dir_path', DS_DIR,
            '--output_path', output_path,
            '--borderless',
            '--paper_size', 'a4',
        ])
        assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
        assert os.path.exists(output_path)


def test_borderless_with_specialty_errors():
    """--borderless with --specialty should raise an error."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as output_dir:
        output_path = os.path.join(output_dir, 'game.pdf')
        result = runner.invoke(cli, [
            '--front_dir_path', 'test/basic/front',
            '--back_dir_path', 'test/basic/back',
            '--output_path', output_path,
            '--borderless',
            '--specialty', 'letter-commander',
        ])
        assert result.exit_code != 0


# --- Mirror Registration Test ---

def _render_basic_pages(output_dir, extra_args=None):
    """Render test/basic to PNG pages in output_dir and return the page filenames."""
    runner = CliRunner()
    args = [
        '--front_dir_path', 'test/basic/front',
        '--back_dir_path', 'test/basic/back',
        '--double_sided_dir_path', 'test/basic/double_sided',
        '--output_path', os.path.join(output_dir, 'output.pdf'),
        '--output_images',
    ]
    if extra_args:
        args += extra_args
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, f"CLI failed: {result.output}\n{result.exception}"
    return sorted(f for f in os.listdir(output_dir) if f.endswith('.png'))


def _pages_differ(dir_a, dir_b, filename):
    """True if the named PNG differs between two output directories."""
    with Image.open(os.path.join(dir_a, filename)) as a, \
         Image.open(os.path.join(dir_b, filename)) as b:
        return ImageChops.difference(a.convert('RGB'), b.convert('RGB')).getbbox() is not None


def test_mirror_registration_flips_back_page_only():
    """--mirror_registration must mirror the back page's registration marks while
    leaving the front page byte-for-byte identical to a non-mirrored render."""
    with tempfile.TemporaryDirectory() as base_dir, \
         tempfile.TemporaryDirectory() as mirror_dir:
        base_pages = _render_basic_pages(base_dir)
        mirror_pages = _render_basic_pages(mirror_dir, ['--mirror_registration'])

        assert base_pages == mirror_pages
        assert len(base_pages) >= 2, f"expected front + back pages, got {base_pages}"

        front_page, back_page = base_pages[0], base_pages[-1]

        # Front page is unaffected by mirroring the registration marks.
        assert not _pages_differ(base_dir, mirror_dir, front_page), (
            "front page changed under --mirror_registration but must not"
        )
        # Back page's registration marks are mirrored/flipped -> it must change.
        assert _pages_differ(base_dir, mirror_dir, back_page), (
            "back page did not change under --mirror_registration"
        )


# --- Per-card config.json override layer ---

def _generate_basic(output_dir, card_overrides=None):
    """Render the rounded-corner card fixtures to PNG pages via generate_pdf,
    optionally with per-card overrides. Uses IMAGES_DIR so corner-fill is visible."""
    generate_pdf(
        front_dir_path=IMAGES_DIR,
        back_dir_path=BACK_DIR,
        ds_dir_path=DS_DIR,
        output_path=os.path.join(output_dir, 'out.pdf'),
        output_images=True,
        card_size='standard',
        paper_size='letter',
        registration=Registration.THREE.value,
        mirror_registration=False,
        only_fronts=False,
        fit=FitMode.STRETCH.value,
        crop_string=None,
        crop_backs_string=None,
        extend_edges=None,
        extend_corners=None,
        ppi=300,
        quality=100,
        skip_indices=[],
        load_offset=False,
        label=None,
        card_overrides=card_overrides,
    )
    return sorted(f for f in os.listdir(output_dir) if f.endswith('.png'))


def test_per_card_extend_corners_override_changes_front():
    """A per-card extend_corners override (config.json group) must alter the front page
    while a None override map leaves output identical to a plain render."""
    front_stems = [
        Path(f).stem for f in os.listdir(IMAGES_DIR)
        if not f.startswith('.')
    ]
    overrides = {stem: {"extend_corners": "5mm"} for stem in front_stems}

    with tempfile.TemporaryDirectory() as base_dir, \
         tempfile.TemporaryDirectory() as ovr_dir:
        base_pages = _generate_basic(base_dir)
        ovr_pages = _generate_basic(ovr_dir, card_overrides=overrides)

        assert base_pages == ovr_pages
        assert base_pages, "no pages rendered"
        # Corner-fill applied to every front -> front page must differ.
        assert _pages_differ(base_dir, ovr_dir, base_pages[0]), (
            "per-card extend_corners override did not change the front page"
        )


# --- Zip-deck batch workflow ---

def _make_deck_zip(zip_path, front_files, config=None):
    """Build a deck zip wrapped in a deck folder (front/ plus an optional config.json),
    mirroring how decks are normally zipped (a single top-level folder)."""
    deck = Path(zip_path).stem
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for fp in front_files:
            zf.write(fp, arcname=f"{deck}/front/{os.path.basename(fp)}")
        if config is not None:
            zf.writestr(f"{deck}/config.json", json.dumps(config))


_ZIP_PDF_KWARGS = dict(
    output_images=False,
    card_size='standard',
    paper_size='letter',
    registration=Registration.THREE.value,
    mirror_registration=False,
    only_fronts=True,
    fit=FitMode.STRETCH.value,
    crop_string=None,
    crop_backs_string=None,
    extend_edges=None,
    extend_corners=None,
    ppi=300,
    quality=100,
    skip_indices=[],
    load_offset=False,
    label=None,
)


def test_zip_decks_individual_produces_pdf_per_deck():
    """--zip_decks (individual mode) renders one PDF per zip."""
    fronts = sorted(glob(os.path.join(IMAGES_DIR, '*')))[:3]
    with tempfile.TemporaryDirectory() as zips_dir, \
         tempfile.TemporaryDirectory() as out_dir:
        _make_deck_zip(os.path.join(zips_dir, 'deck1.zip'), fronts)
        process_zip_decks(zip_decks_dir=zips_dir, output_dir=out_dir, **_ZIP_PDF_KWARGS)
        assert os.path.exists(os.path.join(out_dir, 'deck1.pdf'))


def test_zip_decks_individual_with_config_json():
    """A config.json group is parsed and applied without error, still producing a PDF."""
    fronts = sorted(glob(os.path.join(IMAGES_DIR, '*')))[:3]
    target_stem = Path(fronts[0]).stem
    config = {"groups": [{"files": [Path(fronts[0]).name], "extend_corners": "5mm"}]}
    with tempfile.TemporaryDirectory() as zips_dir, \
         tempfile.TemporaryDirectory() as out_dir:
        _make_deck_zip(os.path.join(zips_dir, 'cfg.zip'), fronts, config=config)
        process_zip_decks(zip_decks_dir=zips_dir, output_dir=out_dir, **_ZIP_PDF_KWARGS)
        assert os.path.exists(os.path.join(out_dir, 'cfg.pdf'))


def test_zip_decks_grouped_produces_single_pdf():
    """--group merges all decks into one group.pdf."""
    fronts = sorted(glob(os.path.join(IMAGES_DIR, '*')))[:3]
    with tempfile.TemporaryDirectory() as zips_dir, \
         tempfile.TemporaryDirectory() as out_dir:
        _make_deck_zip(os.path.join(zips_dir, 'deckA.zip'), fronts)
        _make_deck_zip(os.path.join(zips_dir, 'deckB.zip'), fronts)
        process_zip_decks(zip_decks_dir=zips_dir, output_dir=out_dir, group=True, **_ZIP_PDF_KWARGS)
        assert os.path.exists(os.path.join(out_dir, 'group.pdf'))
