from privacheck.audit_engine import run_audit

def test_detects_purpose_and_legal_basis():
    text = "Les finalités du traitement sont la gestion du compte. La base légale est le consentement."
    result = run_audit(text, "test", "fr")
    ids = {x["id"] for x in result["details"] if x["evidence"]}
    assert "purpose" in ids
    assert "legal_basis" in ids

def test_empty_document_rejected():
    try:
        run_audit("   ")
    except ValueError:
        assert True
    else:
        assert False

def test_missing_is_not_declared_non_compliant():
    result = run_audit("Un texte suffisamment long mais sans les éléments attendus.", "test", "fr")
    assert all(x["status"] == "Non identifié" for x in result["details"])
