# Group 17 - Created 13/04/2026 - Martinelli, Requeut

import json
import argparse
import statistics
from tqdm import tqdm
from model import RobotMission

def run_simulation(params: dict, max_steps: int) -> dict:
    """Runs a single model instance and returns performance metrics."""
    model = RobotMission(**params)
    for _ in range(max_steps):
        model.step()
        last = model.datacollector.get_model_vars_dataframe().iloc[-1]
        
        # Stop condition: no more possible transformations or collections
        if not (last["Green Waste"] >= 2 or last["Yellow Waste"] >= 2 or last["Red Waste"] > 0):
            break

    df = model.datacollector.get_model_vars_dataframe()
    final = df.iloc[-1]
    
    return {
        "steps": int(len(df)),
        "initial_score": float(df.iloc[0]["Waste Score"]),
        "final_score": float(final["Waste Score"]),
        "disposed_score": float(final["Disposed"] * 4) # 1 Red waste = 4 value units
    }

def aggregate(runs: list[dict]) -> dict:
    """Aggregates multiple runs into statistical summaries."""
    disposed = [r["disposed_score"] for r in runs]
    steps = [r["steps"] for r in runs]
    initials = [r["initial_score"] for r in runs]

    avg_initial = statistics.mean(initials)
    avg_disposed = statistics.mean(disposed)
    
    return {
        "avg_steps": round(statistics.mean(steps), 1),
        "efficiency": round((avg_disposed / avg_initial * 100), 2) if avg_initial > 0 else 0.0,
        "score_stats": {
            "mean": round(avg_disposed, 1), 
            "std": round(statistics.stdev(disposed), 1) if len(disposed) > 1 else 0.0
        }
    }

def run_batch(n_runs, max_steps, base_params, output_path):
    """Executes experiments comparing communication effectiveness."""
    results = {}
    print(f"\n{'='*60}")
    print(f"{'EXPERIMENT: WASTE COLLECTION PERFORMANCE':^60}")
    print(f"{'='*60}")

    for com in [True, False]:
        mode = "WITH Communication" if com else "WITHOUT Communication"
        print(f"\nTarget: {mode}")
        
        # Progress bar
        runs = []
        for _ in tqdm(range(n_runs), desc="Simulating", unit="run"):
            runs.append(run_simulation({**base_params, "can_communicate": com}, max_steps))
            
        agg = aggregate(runs)
        results[f"comms_{com}"] = agg

        # Summary Output
        print(f"  > Efficiency Score : {agg['efficiency']}% (Waste value disposed)")
        print(f"  > Avg Completion   : {agg['avg_steps']} steps")
        print(f"  > Value Cleared    : {agg['score_stats']['mean']} ± {agg['score_stats']['std']} pts")

    # Final Comparison
    diff = results["comms_True"]["efficiency"] - results["comms_False"]["efficiency"]
    print(f"\n{'='*60}")
    print(f"ANALYSIS: Communication improved efficiency by {diff:+.2f} percentage points.")
    print(f"{'='*60}\n")

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=50)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--output", type=str, default="results.json")
    args, _ = parser.parse_known_args()

    config = {
        "number_of_green_robots": 5, "number_of_yellow_robots": 5, "number_of_red_robots": 5,
        "initial_waste_density_green": 0.1, "initial_waste_density_yellow": 0.1, "initial_waste_density_red": 0.1
    }

    run_batch(args.runs, args.steps, config, args.output)