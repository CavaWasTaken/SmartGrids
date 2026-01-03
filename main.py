"""
Main entry point for the prosumer community simulator
"""
import os
import sys
import config
from simulator import CommunitySimulator
from visualization import save_results, generate_plots


def main():
    """Main function to run the simulation"""
    try:
        # Create simulator
        simulator = CommunitySimulator()
        
        # Run simulation
        simulator.run_simulation()
        
        # Get simulation data
        simulation_data = simulator.get_simulation_data()
        
        # Save results if configured
        if config.SAVE_RESULTS:
            print(f"\n{'='*70}")
            print("SAVING RESULTS")
            print(f"{'='*70}")
            save_results(simulation_data, config.RESULTS_DIR)
        
        # Generate plots if configured
        if config.GENERATE_PLOTS:
            print(f"\n{'='*70}")
            print("GENERATING VISUALIZATIONS")
            print(f"{'='*70}")
            generate_plots(simulation_data, config.RESULTS_DIR)
        
        print(f"\n{'='*70}")
        print("✓ SIMULATION COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
