from __future__ import annotations

ACTION_LIBRARY = {
    "temperature_c": "Verify heater control, thermocouple calibration and thermal setpoint window.",
    "pressure_bar": "Check pressure regulator, leaks and recipe setpoint; confirm control-loop stability.",
    "speed_mpm": "Review line-speed setpoint against validated process window and downstream capacity.",
    "vibration_mm_s": "Inspect spindle/bearing condition, fixturing and imbalance before continued release.",
    "tool_wear_pct": "Inspect or replace tooling and verify tool-life standard / preventive replacement interval.",
    "material_hardness": "Quarantine suspect material lot and verify incoming-material certification / sampling.",
    "humidity_pct": "Verify environmental control and material conditioning requirements.",
    "operator_experience_y": "Review standardized work, training qualification and error-proofing at the operation.",
}


def corrective_actions(root_causes: list[dict]) -> list[dict]:
    actions = []
    for item in root_causes:
        feature = item["feature"]
        actions.append({
            "feature": feature,
            "signed_contribution": float(item["signed_contribution"]),
            "recommended_check": ACTION_LIBRARY.get(feature, "Perform structured process investigation."),
        })
    return actions
