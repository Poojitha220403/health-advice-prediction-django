import csv
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "health_prediction_app" / "data.csv"
SMOKING_AND_ALCOHOL = [
    "Average weekly alcohol consumption",
    "Current tobacco smoking",
    "Past tobacco smoking",
]


def all_attributes():
    with open(DATA_CSV, newline="") as f:
        return [row["Attribute"] for row in csv.DictReader(f)]


def test_form_lists_every_factor(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.content.decode()
    assert html.count('type="checkbox"') == len(all_attributes()) == 61


def test_post_returns_organ_scores_and_advice(client):
    response = client.post("/", {"selected_attributes": SMOKING_AND_ALCOHOL})
    assert response.status_code == 200
    averages = response.context["averages"]
    assert averages["Pulmonary"] == pytest.approx(2.6)
    assert averages["Body"] == pytest.approx(1.8)
    assert averages["Immune"] == pytest.approx(2.0)
    assert averages["Cardiac"] == pytest.approx(1.0)
    assert set(averages) == {
        "Body", "Cardiac", "Pulmonary", "Muscle", "Immune",
        "Renal", "Hepatic", "Metabolic", "Brain",
    }
    assert response.context["advice_results"], "expected advice for at least one organ system"


def test_empty_submission_rerenders_form(client):
    response = client.post("/", {})
    assert response.status_code == 200
    assert "averages" not in response.context
    assert 'type="checkbox"' in response.content.decode()


def test_settings_require_secret_key():
    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SECRET_KEY"}
    env["DJANGO_SETTINGS_MODULE"] = "health_advice_prediction.settings"
    result = subprocess.run(
        [sys.executable, "-c", "import django; django.setup()"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY" in result.stderr
