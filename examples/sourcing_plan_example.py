"""
Example usage of the SourcingPlanGenerator.

This example demonstrates how to use the SourcingPlanGenerator to create
sourcing-based bridge plans for closing sales gaps.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.bridge_plan_generator.sourcing_plan_generator import SourcingPlanGenerator
from src.bridge_plan_generator.sourcing_processor import SourcingProcessor


def main():
    """Demonstrate sourcing plan generation."""
    
    # Create sample sourcing data
    sourcing_data = pd.DataFrame({
        'ASIN': ['B001', 'B002', 'B003', 'B004', 'B005'],
        'CID': ['C001', 'C001', 'C002', 'C002', 'C003'],
        'total_t30d_gms_BAU': [50000, 30000, 80000, 20000, 10000],
        'sshve1_flag': ['Y', 'N', 'Y', 'N', 'N'],
        'fy26_mde2_flag': ['Y', 'Y', 'Y', 'N', 'N'],
        'nys26_flag': ['N', 'Y', 'Y', 'Y', 'N'],
        'bf25_flag': ['Y', 'N', 'N', 'Y', 'N'],
        'fy25_mde4_flag': ['N', 'N', 'Y', 'N', 'Y'],
        't365_flag': ['Y', 'Y', 'Y', 'Y', 'N']
    })
    
    # Process sourcing data
    processor = SourcingProcessor()
    
    # Extract T30 GMS BAU
    gms_data = processor.extract_t30_gms_bau(sourcing_data)
    
    # Extract event flags
    flags_data = processor.extract_event_flags(sourcing_data)
    
    # Calculate participation scores
    participation_scores = []
    for _, row in flags_data.iterrows():
        flags = {col: row[col] for col in processor.EVENT_FLAG_WEIGHTS.keys()}
        score = processor.calculate_participation_score(flags)
        participation_scores.append(score)
    
    # Combine data
    processed_data = gms_data.copy()
    processed_data['participation_score'] = participation_scores
    
    print("Processed Sourcing Data:")
    print(processed_data)
    print("\n" + "="*80 + "\n")
    
    # Generate sourcing plan
    generator = SourcingPlanGenerator()
    gap = 100000  # Target gap to close
    
    plan = generator.generate_plan(gap, processed_data)
    
    # Display plan results
    print(f"Sourcing Plan for Gap: ${gap:,.2f}")
    print(f"Total Gap: ${plan.total_gap:,.2f}")
    print(f"Gap Closable by Sourcing: ${plan.gap_closable_by_sourcing:,.2f}")
    print(f"Remaining Gap: ${plan.remaining_gap:,.2f}")
    print(f"\nRecommended ASINs: {len(plan.recommended_asins)}")
    print("\n" + "-"*80)
    
    for i, rec in enumerate(plan.recommended_asins, 1):
        print(f"\n{i}. ASIN: {rec.asin} (CID: {rec.cid})")
        print(f"   T30 GMS BAU: ${rec.t30_gms_bau:,.2f}")
        print(f"   Participation Score: {rec.participation_score:.2%}")
        print(f"   Expected Contribution: ${rec.expected_contribution:,.2f}")
        print(f"   Rationale: {rec.rationale}")
    
    print("\n" + "="*80)
    
    # Calculate coverage percentage
    if plan.total_gap > 0:
        coverage = (plan.gap_closable_by_sourcing / plan.total_gap) * 100
        print(f"\nGap Coverage: {coverage:.1f}%")
    
    if plan.remaining_gap > 0:
        print(f"Remaining gap of ${plan.remaining_gap:,.2f} may require suppression optimization.")
    else:
        print("Gap can be fully closed through sourcing!")


if __name__ == '__main__':
    main()
