"""
Report generator module for the Bridge Plan Generator.

This module handles generation of summary reports and export to CSV/Excel formats
with Japanese language support.
"""

import pandas as pd
from typing import List
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

import bridge_models


class ReportGenerator:
    """Generates summary reports and exports bridge plans."""
    
    def generate_summary_report(self, plan: 'bridge_models.BridgePlan') -> dict:
        """
        Generate a summary report for a bridge plan.
        
        Args:
            plan: BridgePlan to summarize
            
        Returns:
            Dictionary containing all report fields
        """
        report = {
            'Pattern': plan.pattern_name,
            'Aggregation Level': plan.aggregation_level,
            'Entity ID': plan.entity_id,
            'Current T30 GMS': plan.current_t30_gms,
            'Target T30 GMS': plan.target_t30_gms,
            'Gap': plan.total_gap,
            'Feasibility Score': plan.feasibility_score,
            'Recommendations': '\n'.join(plan.recommendations)
        }
        
        # Add sourcing details if present
        if plan.sourcing_plan:
            report['Sourcing Gap Closable'] = plan.sourcing_plan.gap_closable_by_sourcing
            report['Sourcing ASINs Count'] = len(plan.sourcing_plan.recommended_asins)
            report['Sourcing Remaining Gap'] = plan.sourcing_plan.remaining_gap
        
        # Add suppression details if present
        if plan.suppression_plan:
            report['Suppression Gap Closable'] = plan.suppression_plan.gap_closable_by_suppression
            report['Suppression Opportunities Count'] = len(plan.suppression_plan.opportunities)
            report['Suppression Remaining Gap'] = plan.suppression_plan.remaining_gap
        
        return report
    
    def export_to_csv(self, plans: List['bridge_models.BridgePlan'], output_path: str) -> None:
        """
        Export bridge plans to CSV format with UTF-8 encoding for Japanese support.
        
        Args:
            plans: List of BridgePlan objects to export
            output_path: Path where CSV file should be saved
        """
        # Generate summary reports for all plans
        reports = [self.generate_summary_report(plan) for plan in plans]
        
        # Convert to DataFrame
        df = pd.DataFrame(reports)
        
        # Export to CSV with UTF-8 encoding
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    def export_to_excel(self, plans: List['bridge_models.BridgePlan'], output_path: str) -> None:
        """
        Export bridge plans to Excel format with formatted tables.
        
        Creates multiple sheets:
        - Summary: Overview of all patterns
        - Sourcing Details: Detailed ASIN recommendations
        - Suppression Details: Detailed suppression opportunities
        
        Args:
            plans: List of BridgePlan objects to export
            output_path: Path where Excel file should be saved
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_reports = [self.generate_summary_report(plan) for plan in plans]
            summary_df = pd.DataFrame(summary_reports)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Sourcing Details
            sourcing_details = []
            for plan in plans:
                if plan.sourcing_plan:
                    for asin_rec in plan.sourcing_plan.recommended_asins:
                        sourcing_details.append({
                            'Pattern': plan.pattern_name,
                            'Entity ID': plan.entity_id,
                            'ASIN': asin_rec.asin,
                            'CID': asin_rec.cid,
                            'Expected Contribution': asin_rec.expected_contribution,
                            'Participation Score': asin_rec.participation_score,
                            'Rationale': asin_rec.rationale
                        })
            
            if sourcing_details:
                sourcing_df = pd.DataFrame(sourcing_details)
                sourcing_df.to_excel(writer, sheet_name='Sourcing Details', index=False)
            
            # Sheet 3: Suppression Details
            suppression_details = []
            for plan in plans:
                if plan.suppression_plan:
                    for opp in plan.suppression_plan.opportunities:
                        suppression_details.append({
                            'Pattern': plan.pattern_name,
                            'Entity ID': plan.entity_id,
                            'Category': opp.category,
                            'Current %': opp.current_percentage,
                            'Target %': opp.target_percentage,
                            'Expected Impact': opp.expected_impact,
                            'Recommended Actions': '\n'.join(opp.recommended_actions)
                        })
            
            if suppression_details:
                suppression_df = pd.DataFrame(suppression_details)
                suppression_df.to_excel(writer, sheet_name='Suppression Details', index=False)
    
    def export_detailed_sourcing_csv(self, plans: List['bridge_models.BridgePlan'], output_path: str) -> None:
        """
        Export detailed sourcing recommendations to CSV.
        
        Args:
            plans: List of BridgePlan objects
            output_path: Path where CSV file should be saved
        """
        sourcing_details = []
        for plan in plans:
            if plan.sourcing_plan:
                for asin_rec in plan.sourcing_plan.recommended_asins:
                    sourcing_details.append({
                        'Pattern': plan.pattern_name,
                        'Aggregation Level': plan.aggregation_level,
                        'Entity ID': plan.entity_id,
                        'ASIN': asin_rec.asin,
                        'CID': asin_rec.cid,
                        'Expected Contribution': asin_rec.expected_contribution,
                        'Participation Score': asin_rec.participation_score,
                        'Rationale': asin_rec.rationale
                    })
        
        if sourcing_details:
            df = pd.DataFrame(sourcing_details)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    def export_detailed_suppression_csv(self, plans: List['bridge_models.BridgePlan'], output_path: str) -> None:
        """
        Export detailed suppression opportunities to CSV.
        
        Args:
            plans: List of BridgePlan objects
            output_path: Path where CSV file should be saved
        """
        suppression_details = []
        for plan in plans:
            if plan.suppression_plan:
                for opp in plan.suppression_plan.opportunities:
                    suppression_details.append({
                        'Pattern': plan.pattern_name,
                        'Aggregation Level': plan.aggregation_level,
                        'Entity ID': plan.entity_id,
                        'Category': opp.category,
                        'Current Percentage': opp.current_percentage,
                        'Target Percentage': opp.target_percentage,
                        'Expected Impact': opp.expected_impact,
                        'Recommended Actions': ' | '.join(opp.recommended_actions)
                    })
        
        if suppression_details:
            df = pd.DataFrame(suppression_details)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
