"""
Main application entry point for the Bridge Plan Generator.

This script provides a command-line interface for generating bridge plans
at different aggregation levels (CID, Alias, Mgr, Team).
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

# Add src directory to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import bridge_config
import bridge_models
from bridge_plan_generator import data_loader
from bridge_plan_generator import sourcing_processor
from bridge_plan_generator import target_processor
from bridge_plan_generator import suppression_processor
from bridge_plan_generator import hierarchy_processor
from bridge_plan_generator import promotion_ops_calculator
from bridge_plan_generator import sourcing_plan_generator
from bridge_plan_generator import suppression_plan_generator
from bridge_plan_generator import bridge_plan_orchestrator
from bridge_plan_generator import report_generator


def main():
    """Main application entry point."""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Bridge Plan Generator - Generate strategic sales bridge plans',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate plans at CID level
  python src/run_bridge_plan.py --level CID --config config/bridge_config.json --output output/

  # Generate plans at Alias level
  python src/run_bridge_plan.py --level Alias --config config/bridge_config.json --output output/

  # Generate plans at Manager level
  python src/run_bridge_plan.py --level Mgr --config config/bridge_config.json --output output/

  # Generate plans at Team level
  python src/run_bridge_plan.py --level Team --config config/bridge_config.json --output output/
        """
    )
    
    parser.add_argument(
        '--level',
        type=str,
        required=True,
        choices=['CID', 'Alias', 'Mgr', 'Team'],
        help='Aggregation level for bridge plan generation'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        required=True,
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for generated reports'
    )
    
    parser.add_argument(
        '--entity',
        type=str,
        default=None,
        help='Specific entity ID to generate plan for (optional, generates for all if not specified)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        print(f"📋 Loading configuration from {args.config}...")
        config = bridge_config.Config.load_from_file(args.config)
        
        # Validate configuration
        is_valid, error_msg = config.validate()
        if not is_valid:
            print(f"❌ Configuration validation failed: {error_msg}")
            sys.exit(1)
        
        print("✅ Configuration loaded successfully")
        
        # Initialize components
        print("\n🔧 Initializing components...")
        data_loader_obj = data_loader.DataLoader()
        sourcing_processor_obj = sourcing_processor.SourcingProcessor()
        target_processor_obj = target_processor.TargetProcessor()
        suppression_processor_obj = suppression_processor.SuppressionProcessor()
        hierarchy_processor_obj = hierarchy_processor.HierarchyProcessor()
        
        # Load data files
        print("\n📂 Loading data files...")
        
        print(f"  Loading sourcing data from {config.sourcing_data_path}...")
        sourcing_df = data_loader_obj.load_sourcing_data(config.sourcing_data_path)
        print(f"  ✅ Loaded {len(sourcing_df)} sourcing records")
        
        print(f"  Loading target data from {config.target_data_path}...")
        target_df = data_loader_obj.load_target_data(config.target_data_path)
        print(f"  ✅ Loaded {len(target_df)} target records")
        
        print(f"  Loading suppression benchmark from {config.suppression_benchmark_path}...")
        benchmark_df = data_loader_obj.load_suppression_benchmark(config.suppression_benchmark_path)
        print(f"  ✅ Loaded suppression benchmark data")
        
        print(f"  Loading CID mapping from {config.cid_mapping_path}...")
        mapping_df = data_loader_obj.load_cid_mapping(config.cid_mapping_path, config.cid_mapping_sheet)
        print(f"  ✅ Loaded {len(mapping_df)} CID mappings")
        
        # Validate required columns
        print("\n🔍 Validating data columns...")
        
        sourcing_required = ['ASIN', 'CID', 'total_t30d_gms_BAU', 'suppression_category_large'] + config.event_flag_priority
        is_valid, error_msg = data_loader_obj.validate_required_columns(sourcing_df, sourcing_required, 'sourcing data')
        if not is_valid:
            print(f"❌ {error_msg}")
            sys.exit(1)
        
        target_required = ['CID', 't30_gms_target']
        is_valid, error_msg = data_loader_obj.validate_required_columns(target_df, target_required, 'target data')
        if not is_valid:
            print(f"❌ {error_msg}")
            sys.exit(1)
        
        mapping_required = ['CID', 'Alias', 'Mgr', 'Team']
        is_valid, error_msg = data_loader_obj.validate_required_columns(mapping_df, mapping_required, 'CID mapping')
        if not is_valid:
            print(f"❌ {error_msg}")
            sys.exit(1)
        
        print("✅ All data columns validated")
        
        # Process data
        print("\n⚙️  Processing data...")
        
        # Extract T30 GMS BAU
        t30_gms_df = sourcing_processor_obj.extract_t30_gms_bau(sourcing_df)
        
        # Aggregate by CID
        cid_aggregated = sourcing_processor_obj.aggregate_by_cid(t30_gms_df)
        
        # Extract targets
        targets_df = target_processor_obj.extract_targets(target_df)
        
        # Calculate gaps
        gaps_df = target_processor_obj.calculate_gaps(cid_aggregated, targets_df)
        
        # Build hierarchy map
        hierarchy_map = hierarchy_processor_obj.build_hierarchy_map(mapping_df)
        
        # Extract suppression benchmark
        benchmark_percentages = suppression_processor_obj.extract_benchmark_percentages(benchmark_df)
        
        # Calculate current suppression by CID
        current_suppression_df = suppression_processor_obj.calculate_current_suppression(sourcing_df)
        
        # Convert to dictionary format with percentages by category name
        current_suppression_dict = {}
        for _, row in current_suppression_df.iterrows():
            current_suppression_dict[row['suppression_category_name']] = row['percentage']
        
        print("✅ Data processing complete")
        
        # Aggregate to requested level
        print(f"\n📊 Aggregating data to {args.level} level...")
        
        if args.level == 'CID':
            aggregated_df = gaps_df
        elif args.level == 'Alias':
            aggregated_df = hierarchy_processor_obj.aggregate_by_alias(gaps_df, hierarchy_map)
        elif args.level == 'Mgr':
            aggregated_df = hierarchy_processor_obj.aggregate_by_manager(gaps_df, hierarchy_map)
        elif args.level == 'Team':
            aggregated_df = hierarchy_processor_obj.aggregate_by_team(gaps_df, hierarchy_map)
        
        print(f"✅ Aggregated to {len(aggregated_df)} {args.level} entities")
        
        # Filter to specific entity if requested
        if args.entity:
            aggregated_df = aggregated_df[aggregated_df[args.level] == args.entity]
            if aggregated_df.empty:
                print(f"❌ Entity '{args.entity}' not found at {args.level} level")
                sys.exit(1)
            print(f"  Filtered to entity: {args.entity}")
        
        # Initialize plan generators
        print("\n🎯 Initializing plan generators...")
        promotion_ops_calc = promotion_ops_calculator.PromotionOPSCalculator(config.suppression_coefficients)
        sourcing_generator = sourcing_plan_generator.SourcingPlanGenerator()
        suppression_generator = suppression_plan_generator.SuppressionPlanGenerator(config.suppression_coefficients)
        orchestrator = bridge_plan_orchestrator.BridgePlanOrchestrator(sourcing_generator, suppression_generator)
        report_generator_obj = report_generator.ReportGenerator()
        
        # Generate bridge plans
        print(f"\n🚀 Generating bridge plans for {len(aggregated_df)} entities...")
        
        all_plans = []
        
        for idx, row in aggregated_df.iterrows():
            entity_id = str(row[args.level])
            current_t30_gms = row.get('t30_gms_bau_total', 0)
            target_t30_gms = row.get('t30_gms_target', 0)
            gap = row.get('gap', 0)
            
            print(f"\n  Processing {entity_id}...")
            print(f"    Current: {current_t30_gms:.0f}, Target: {target_t30_gms:.0f}, Gap: {gap:.0f}")
            
            # Get sourcing data for this entity
            if args.level == 'CID':
                entity_sourcing = sourcing_df[sourcing_df['CID'] == entity_id].copy()
            else:
                # Get all CIDs for this entity
                if args.level == 'Alias':
                    entity_cids = [cid for cid, alias in hierarchy_map.cid_to_alias.items() if alias == entity_id]
                elif args.level == 'Mgr':
                    entity_aliases = [alias for alias, mgr in hierarchy_map.alias_to_manager.items() if mgr == entity_id]
                    entity_cids = [cid for cid, alias in hierarchy_map.cid_to_alias.items() if alias in entity_aliases]
                elif args.level == 'Team':
                    entity_mgrs = [mgr for mgr, team in hierarchy_map.manager_to_team.items() if team == entity_id]
                    entity_aliases = [alias for alias, mgr in hierarchy_map.alias_to_manager.items() if mgr in entity_mgrs]
                    entity_cids = [cid for cid, alias in hierarchy_map.cid_to_alias.items() if alias in entity_aliases]
                
                entity_sourcing = sourcing_df[sourcing_df['CID'].isin(entity_cids)].copy()
            
            # Add participation scores to sourcing data
            entity_sourcing['participation_score'] = entity_sourcing.apply(
                lambda row: sourcing_processor_obj.calculate_participation_score({
                    flag: row[flag] for flag in config.event_flag_priority
                }),
                axis=1
            )
            
            # Add t30_gms_bau column (rename from total_t30d_gms_BAU)
            entity_sourcing['t30_gms_bau'] = entity_sourcing['total_t30d_gms_BAU']
            
            # Get current suppression for this entity
            # For now, use the overall suppression distribution
            # (In a real implementation, you'd calculate per-entity suppression)
            current_suppression = current_suppression_dict.copy()
            
            # Generate all patterns
            patterns = orchestrator.generate_all_patterns(
                entity_id=entity_id,
                aggregation_level=args.level,
                current_t30_gms=current_t30_gms,
                target_t30_gms=target_t30_gms,
                gap=gap,
                sourcing_data=entity_sourcing,
                current_suppression=current_suppression,
                benchmark_suppression=benchmark_percentages
            )
            
            print(f"    ✅ Generated {len(patterns)} pattern(s)")
            all_plans.extend(patterns)
        
        # Export reports
        print(f"\n📝 Exporting reports to {args.output}...")
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export summary CSV
        summary_csv = output_dir / f"bridge_plan_summary_{args.level}.csv"
        report_generator_obj.export_to_csv(all_plans, str(summary_csv))
        print(f"  ✅ Exported summary to {summary_csv}")
        
        # Export detailed Excel
        excel_file = output_dir / f"bridge_plan_detailed_{args.level}.xlsx"
        report_generator_obj.export_to_excel(all_plans, str(excel_file))
        print(f"  ✅ Exported detailed report to {excel_file}")
        
        # Export detailed sourcing CSV
        sourcing_csv = output_dir / f"bridge_plan_sourcing_{args.level}.csv"
        report_generator_obj.export_detailed_sourcing_csv(all_plans, str(sourcing_csv))
        print(f"  ✅ Exported sourcing details to {sourcing_csv}")
        
        # Export detailed suppression CSV
        suppression_csv = output_dir / f"bridge_plan_suppression_{args.level}.csv"
        report_generator_obj.export_detailed_suppression_csv(all_plans, str(suppression_csv))
        print(f"  ✅ Exported suppression details to {suppression_csv}")
        
        print(f"\n✨ Bridge plan generation complete! Generated {len(all_plans)} plans.")
        print(f"📁 Reports saved to: {output_dir}")
        
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"\n❌ Missing required column: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
