from site_audit.pdf_generator import _grade_color, _level_color, _score_color, render_html


def test_score_color_thresholds():
    assert _score_color(85) == "#2e7d52"
    assert _score_color(65) == "#9a6b12"
    assert _score_color(45) == "#ba1a1a"
    assert _score_color(20) == "#ba1a1a"


def test_grade_and_level_colors():
    assert _grade_color("A") == "#2e7d52"
    assert _grade_color("Z") == "#747878"
    assert _level_color("High") == "#ba1a1a"
    assert _level_color("Unknown") == "#747878"


def test_render_html(report):
    html = render_html(report)
    assert "Example Inc" in html
    assert "https://example.com" in html
    assert "Improve LCP" in html
    assert "Add alt text to images" in html
    assert "Mobile score" in html
