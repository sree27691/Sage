from sage.engine.tcs import TCSEngine
from sage.models.schemas import JudgeOutput, TrustSummary, EvidenceUnit

def test_tcs():
    engine = TCSEngine()
    
    # Case 1: Perfect Grounding, No Conflicts, No Uncertainties
    judge_output = JudgeOutput(
        claims_judgement=[
            {"claim_text": "c1", "evidence_ids": ["e1"], "judge_label": "Supported", "reasoning": "r1"},
            {"claim_text": "c2", "evidence_ids": ["e2"], "judge_label": "Supported", "reasoning": "r2"}
        ],
        conflicts=[],
        uncertainty_aspects=[]
    )
    
    trust_summary = TrustSummary(
        product_id="test",
        overall_verdict="Good",
        aspects=[],
        claims=["c1", "c2"],
        conflicts=[],
        uncertainties=[]
    )
    
    evidence_units = [
        {"evidence_id": "e1", "aspect_tags": ["a1"], "source_type": "pdp"},
        {"evidence_id": "e2", "aspect_tags": ["a2"], "source_type": "pdp"}
    ]
    
    aspect_ontology = ["a1", "a2"]
    
    result = engine.calculate_tcs(judge_output, trust_summary, evidence_units, aspect_ontology)
    
    print("--- Test Case 1: Perfect Grounding, 0 Conflicts ---")
    print(f"G: {result.groundedness}")
    print(f"A: {result.accuracy}")
    print(f"C: {result.coverage}")
    print(f"D: {result.conflict_detection}")
    print(f"U: {result.uncertainty}")
    print(f"TCS: {result.tcs_score}")
    print(f"Band: {result.band}")

if __name__ == "__main__":
    test_tcs()
