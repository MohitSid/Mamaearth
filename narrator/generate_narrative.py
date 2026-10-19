import os
import json
from pathlib import Path
from google import genai

def generate_scr_narrative(findings: dict) -> dict:
    """
    Generate a Situation-Complication-Resolution business narrative.
    Returns a dictionary on both success and failure.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "narrative": None,
            "tokens": 0,
            "message": "GEMINI_API_KEY is not configured."
        }

    system_instruction = """
    You are a senior data analyst writing for Mamaearth's Growth Analytics team.
    Write a concise business report using Situation, Complication, and Resolution.
    Use only the supplied findings. Do not invent numbers or unsupported facts.
    Explain what the data suggests without claiming correlation proves causation.
    """

    prompt = f"""
    Write a business narrative using these verified findings:
    {json.dumps(findings, indent=2)}

    Include these sections:
    Situation:
    Complication:
    Resolution:

    Include the key revenue, return-rate, segment, reconciliation, and monthly
    trend figures. Keep the report between 250 and 350 words.
    """

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.0,
                "max_output_tokens": 800,
                "http_options": {"timeout": 10000}
            }
        )

        narrative = response.text

        if not narrative:
            raise ValueError("Gemini returned an empty narrative.")

        return {
            "status": "success",
            "narrative": narrative,
            "tokens": getattr(
                getattr(response, "usage_metadata", None),
                "total_token_count",
                0
            ),
            "message": None
        }

    except Exception as exc:
        return {
            "status": "error",
            "narrative": None,
            "tokens": 0,
            "message": str(exc)
        }


def generate_scr_narrative_offline(findings: dict) -> dict:
    """Generate a deterministic SCR report without an API call."""

    revenue = findings["cleaned_total_revenue_inr"]
    raw_revenue = findings["raw_total_revenue_inr"]
    delta = findings["duplicate_reconciliation_delta_inr"]

    rates = findings["return_rate_by_payment_method"]
    cod_rate = rates["COD"]
    card_rate = rates["CARD"]
    upi_rate = rates["UPI"]

    segment = findings["highest_risk_segment"]
    segment_rate = segment["return_rate_pct"]
    segment_method = segment["payment_method"]
    city_tier = segment["city_tier"]

    peak = findings["true_peak_month"]
    jan = findings["outlier_inflated_month"]

    narrative = f"""
SITUATION
Mamaearth's Growth Analytics team analyzed customer orders and revenue.
After cleaning and deduplicating the data, total revenue was ₹{revenue:,.2f}.
The raw order data initially reported ₹{raw_revenue:,.2f}.

COMPLICATION
The removal of duplicate orders explains ₹{delta:,.2f} of the revenue
difference between the raw and cleaned reports. Return rates also differ
substantially by payment method: COD is {cod_rate:.1f}%, compared with
{card_rate:.1f}% for Card and {upi_rate:.1f}% for UPI.

The highest-risk segment identified was {segment_method}, City Tier
{city_tier}, with a return rate of {segment_rate:.1f}%.

January's apparent revenue was ₹{jan['apparent_revenue_inr']:,.2f},
but after excluding the quantity outliers it was
₹{jan['corrected_revenue_inr']:,.2f}. The corrected peak month was
{peak['month']}, with revenue of ₹{peak['revenue_inr']:,.2f}.

RESOLUTION
The team should investigate the COD return process, particularly in
the highest-risk city tier, and validate the causes before implementing
policy changes. Revenue reporting should use the deduplicated dataset,
while retaining a reconciliation trail to the raw figures. Monthly
performance reviews should use the outlier-corrected series alongside
the uncorrected figures so exceptional orders are visible without
distorting the underlying trend.
""".strip()

    return {
        "status": "success",
        "narrative": narrative,
        "tokens": 0,
        "message": None
    }



def generate_narrative(findings: dict) -> dict:
    """Try Gemini; use the deterministic fallback on any failure."""

    result = generate_scr_narrative(findings)

    if result["status"] == "success":
        return result

    offline_result = generate_scr_narrative_offline(findings)
    offline_result["message"] = (
        "Offline fallback used. Gemini: " + str(result["message"])
    )
    return offline_result



import json
from pathlib import Path

ROOT = Path.cwd()

# If your notebook is inside the analysis folder, use:
# ROOT = Path.cwd().parent

findings_path = ROOT / "narrator" / "findings.json"

with open(findings_path, "r", encoding="utf-8") as f:
    findings = json.load(f)

print("Findings loaded successfully!")
print(findings.keys())


offline_result = generate_scr_narrative_offline(findings)

print("Status:", offline_result["status"])
print(offline_result["narrative"])



import re

def check_narrative_accuracy(narrative: str, findings: dict) -> dict:
    """Check the five required figures in the generated narrative."""

    normalized = narrative.replace(",", "")
    normalized = re.sub(r"\s+", " ", normalized).lower()

    checks = {
        "cleaned revenue": bool(
            re.search(r"97358\.30\b", normalized)
        ),
        "COD return rate": bool(
            re.search(r"44\.4\s*%", normalized)
        ),
        "COD Tier 2 return rate": bool(
            re.search(r"54\.5\s*%", normalized)
        ),
        "duplicate reconciliation": bool(
            re.search(r"2501\.90\b", normalized)
        ),
        "peak month": (
            (
                "march 2026" in normalized
                or "2026-03" in normalized
            )
            and bool(re.search(r"20318\.90\b", normalized))
        ),    
    }

    for label, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {label}")

    return {
        "passed": all(checks.values()),
        "checks": checks
    }



accuracy = check_narrative_accuracy(
    offline_result["narrative"],
    findings
)

print("Overall:", "PASS" if accuracy["passed"] else "FAIL")
