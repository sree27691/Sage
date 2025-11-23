from typing import List, Dict, Any
from sage.models.schemas import TCSComponents, JudgeOutput, TrustSummary, EvidenceUnit

class TCSEngine:
    def calculate_tcs(
        self,
        judge_output: JudgeOutput,
        trust_summary: TrustSummary,
        evidence_units: List[Dict[str, Any]],
        aspect_ontology: List[str],
        injected_conflicts: int = 0,
        expected_conflicts_estimate: int = 2 # Default heuristic
    ) -> TCSComponents:
        
        # 1. Groundedness (G)
        # G = grounded_claims / total_claims
        total_claims = len(judge_output.claims_judgement)
        grounded_claims = 0
        supported_claims = 0
        
        for judgement in judge_output.claims_judgement:
            is_grounded = (len(judgement.evidence_ids) > 0) and \
                          (judgement.judge_label in ["Supported", "PartiallySupported"])
            if is_grounded:
                grounded_claims += 1
            
            if judgement.judge_label == "Supported":
                supported_claims += 1
                

                
        G = grounded_claims / total_claims if total_claims > 0 else 0.0
        
        # 2. Accuracy (A)
        # A = supported_claims / total_claims
        # Fix: If total_claims is 0, Accuracy is technically undefined, but let's assume 0 or 1 depending on context.
        # If no claims were made, maybe that's good (no lies)? But usually it means failure to summarize.
        # Let's stick to 0.0 if no claims.
        A = supported_claims / total_claims if total_claims > 0 else 0.0
        
        # 3. Aspect Coverage (C)
        # C = covered_aspects / total_required_aspects
        covered_aspects = set()
        for judgement in judge_output.claims_judgement:
            if judgement.judge_label in ["Supported", "PartiallySupported"]:
                # In a real system, we'd map claims to aspects via NLP or metadata.
                # Here we assume the claim text or associated metadata might link to aspects.
                # For this implementation, we'll look at the TrustSummary aspects that have claims.
                # Or better, we check if the claim text contains the aspect name (simple heuristic).
                for aspect in aspect_ontology:
                    if aspect.lower() in judgement.claim_text.lower():
                        covered_aspects.add(aspect)
        
        C = len(covered_aspects) / len(aspect_ontology) if aspect_ontology else 0.0
        
        # 4. Conflict Score (D) - Higher is better (fewer conflicts)
        # D = 1.0 / (1 + detected_conflicts)
        detected_conflicts = len(judge_output.conflicts)
        D = 1.0 / (1.0 + detected_conflicts)
            
        # 5. Uncertainty Score (U) - Higher is better (fewer uncertainties)
        # U = 1.0 - (uncertain_aspects / total_aspects)
        total_aspects = len(aspect_ontology) if aspect_ontology else 1
        uncertain_aspects_count = len(trust_summary.uncertainties)
        # Also include judge flagged ones
        uncertain_aspects_count += len(judge_output.uncertainty_aspects)
        # Dedup if needed, but simple count is fine for heuristic
        
        U = max(0.0, 1.0 - (uncertain_aspects_count / total_aspects))
        
        # Final TCS
        # TCS = 0.35G + 0.25A + 0.20C + 0.15D + 0.05U
        TCS = (0.35 * G) + (0.25 * A) + (0.20 * C) + (0.15 * D) + (0.05 * U)
        
        # Band
        if TCS >= 0.90:
            band = "Elite"
        elif TCS >= 0.80:
            band = "Production Safe"
        elif TCS >= 0.60:
            band = "Pilot"
        else:
            band = "Unsafe"
            
        return TCSComponents(
            groundedness=round(G, 2),
            accuracy=round(A, 2),
            coverage=round(C, 2),
            conflict_detection=round(D, 2),
            uncertainty=round(U, 2),
            tcs_score=round(TCS, 2),
            band=band
        )
