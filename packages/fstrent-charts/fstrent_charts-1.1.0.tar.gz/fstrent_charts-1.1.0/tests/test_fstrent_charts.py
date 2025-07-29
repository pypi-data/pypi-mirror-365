"""Tests for the fstrent_charts module."""

import pytest
from io import StringIO
import sys
from fstrent_charts import CHRT

@pytest.fixture
def capture_stdout():
    """Capture stdout for testing chart output."""
    stdout = StringIO()
    old_stdout = sys.stdout
    sys.stdout = stdout
    yield stdout
    sys.stdout = old_stdout

def test_chart_initialization():
    """Test that a CHRT object initializes with default values."""
    chrt = CHRT()
    assert chrt.len_cnt == 220
    assert chrt.align == 'left'
    assert chrt.bold is True
    assert chrt.italic is False
    assert chrt.header_font_color == 'white'
    assert chrt.header_bg_color == 'blue'
    assert chrt.font_color == '#00FF00'
    assert chrt.bg_color == '#4B0082'
    assert chrt.border_font_color == '#00FF00'
    assert chrt.border_bg_color == '#4B0082'
    assert chrt.style == 2
    assert chrt.formatted is False
    assert chrt.in_json is None

def test_chart_top(capture_stdout):
    """Test the chart_top method outputs correctly."""
    chrt = CHRT()
    chrt.chart_top(in_str="Test Title")
    output = capture_stdout.getvalue()
    assert "Test Title" in output

def test_chart_row(capture_stdout):
    """Test the chart_row method outputs correctly."""
    chrt = CHRT()
    chrt.chart_row(in_str="Test Row", align='left', font_color='white', bg_color='blue')
    output = capture_stdout.getvalue()
    assert "Test Row" in output

def test_chart_bottom(capture_stdout):
    """Test the chart_bottom method outputs correctly."""
    chrt = CHRT()
    chrt.chart_bottom()
    output = capture_stdout.getvalue()
    assert "═" in output  # Assuming the bottom uses double-line characters

def test_chart_full(capture_stdout):
    """Test a full chart output."""
    chrt = CHRT()
    chrt.chart_top(in_str="Full Chart Test")
    chrt.chart_row(in_str="Row 1", align='left', font_color='white', bg_color='blue')
    chrt.chart_row(in_str="Row 2", align='left', font_color='white', bg_color='blue')
    chrt.chart_bottom()
    output = capture_stdout.getvalue()
    assert "Full Chart Test" in output
    assert "Row 1" in output
    assert "Row 2" in output
    assert "═" in output

# Add more tests as needed to cover additional functionality
  