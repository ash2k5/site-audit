from site_audit.pdf_generator import _grade_color, _level_color, _score_color, render_html


def test_score_color_thresholds():
    assert _score_color(85) == "#22c55e"
    assert _score_color(65) == "#f59e0b"
    assert _score_color(45) == "#f97316"
    assert _score_color(20) == "#ef4444"


def test_grade_and_level_colors():
    assert _grade_color("A") == "#22c55e"
    assert _grade_color("Z") == "#6b7280"
    assert _level_color("High") == "#ef4444"
    assert _level_color("Unknown") == "#6b7280"


def test_render_html(report):
    html = render_html(report)
    assert "Example Inc" in html
    assert "https://example.com" in html
    assert "Improve LCP" in html
    assert "Add alt text to images" in html
    assert "Mobile Score" in html
