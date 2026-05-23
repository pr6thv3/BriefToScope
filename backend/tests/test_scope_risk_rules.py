from app.services.scope_risk_rules import RISK_RULES, detect_rule_based_risks


def test_required_paid_beta_risk_rules_are_present():
    ids = {rule.id for rule in RISK_RULES}
    assert {
        "unlimited_revisions_implied",
        "seo_mentioned_not_scoped",
        "copywriting_responsibility_unclear",
        "client_assets_missing",
        "timeline_dependency_missing",
        "third_party_tools_unspecified",
        "custom_animation_complexity_unclear",
        "payment_milestone_missing",
        "acceptance_criteria_missing",
        "ownership_ip_unclear",
    }.issubset(ids)


def test_unlimited_revisions_rule():
    risks = detect_rule_based_risks(["Client wants unlimited revisions and to keep tweaking until everyone is happy."])
    assert any(risk.id == "rule_unlimited_revisions_implied" for risk in risks)


def test_seo_rule():
    risks = detect_rule_based_risks(["They want SEO and to rank on Google, but no SEO scope was defined."])
    assert any(risk.id == "rule_seo_mentioned_not_scoped" for risk in risks)


def test_copywriting_rule():
    risks = detect_rule_based_risks(["We may need website copy for all pages and copywriting help."])
    assert any(risk.id == "rule_copywriting_responsibility_unclear" for risk in risks)


def test_client_assets_rule():
    risks = detect_rule_based_risks(["Client will send photos later and brand assets later."])
    assert any(risk.id == "rule_client_assets_missing" for risk in risks)


def test_timeline_dependency_rule():
    risks = detect_rule_based_risks(["They need it soon, but launch depends on approval and feedback."])
    assert any(risk.id == "rule_timeline_dependency_missing" for risk in risks)


def test_third_party_tools_rule():
    risks = detect_rule_based_risks(["The site needs to connect to HubSpot and maybe Zapier."])
    assert any(risk.id == "rule_third_party_tools_unspecified" for risk in risks)


def test_animation_rule():
    risks = detect_rule_based_risks(["They asked for custom animation, parallax, and motion on the homepage."])
    assert any(risk.id == "rule_custom_animation_complexity_unclear" for risk in risks)


def test_payment_milestone_rule():
    risks = detect_rule_based_risks(["The budget is approved but payment and deposit timing were not discussed."])
    assert any(risk.id == "rule_payment_milestone_missing" for risk in risks)


def test_acceptance_criteria_rule():
    risks = detect_rule_based_risks(["Final approval and sign off will happen, but no done criteria exist."])
    assert any(risk.id == "rule_acceptance_criteria_missing" for risk in risks)


def test_ownership_ip_rule():
    risks = detect_rule_based_risks(["Client asked if they own the files, source files, and Figma files."])
    assert any(risk.id == "rule_ownership_ip_unclear" for risk in risks)
