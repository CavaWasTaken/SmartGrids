"""
Main entry point for the prosumer community simulator
"""
import sys
from simulator import CommunitySimulator

def main():
    """Main function to run the simulation"""
    try:
        # Create simulator
        simulator = CommunitySimulator()
        
        # Run simulation
        simulator.run_simulation()
        
        print(f"\n{'='*70}")
        print("SIMULATION COMPLETED SUCCESSFULLY")
        print(f"{'='*70}\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
