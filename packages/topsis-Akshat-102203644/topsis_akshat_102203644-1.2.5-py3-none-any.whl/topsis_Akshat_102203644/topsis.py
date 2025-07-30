import sys
import pandas as pd
import numpy as np
import os

def calculate(matrix, weights, impacts):
    matrix = np.array(matrix, dtype=float)

    normalized_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))

    weighted_matrix = normalized_matrix * weights

    ideal_solution = []
    negative_ideal_solution = []
    for i in range(weighted_matrix.shape[1]):
        if impacts[i] == 1:
            ideal_solution.append(np.max(weighted_matrix[:, i]))
            negative_ideal_solution.append(np.min(weighted_matrix[:, i]))
        else:
            ideal_solution.append(np.min(weighted_matrix[:, i]))
            negative_ideal_solution.append(np.max(weighted_matrix[:, i]))

    ideal_solution = np.array(ideal_solution)
    negative_ideal_solution = np.array(negative_ideal_solution)

    distance_to_ideal = np.sqrt(((weighted_matrix - ideal_solution) ** 2).sum(axis=1))
    distance_to_negative_ideal = np.sqrt(((weighted_matrix - negative_ideal_solution) ** 2).sum(axis=1))

    scores = distance_to_negative_ideal / (distance_to_ideal + distance_to_negative_ideal)
    rankings = scores.argsort() + 1

    return scores, rankings


def main():
    if len(sys.argv) != 5:
        print("Usage: python topsis.py <InputDataSet.csv> <Weights> <Impacts> <Result.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    weights = sys.argv[2]
    impacts = sys.argv[3]
    result_file = sys.argv[4]

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    try:
        data = pd.read_csv(input_file)
        if data.shape[1] < 3:
            print("Error: Input file must contain at least three columns.")
            sys.exit(1)
        matrix = data.iloc[:, 1:].values
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    try:
        weights = list(map(float, weights.split(',')))
        impacts = list(map(float, impacts.split(',')))
        if not all(impact in [+1, -1] for impact in impacts):
            print("Error: Impacts must be +1 (benefit) or -1 (cost).")
            sys.exit(1)
    except ValueError:
        print("Error: Weights must be numeric values and impacts must be +1 or -1, separated by commas.")
        sys.exit(1)

    if len(weights) != matrix.shape[1] or len(impacts) != matrix.shape[1]:
        print("Error: Length of weights and impacts must match the number of criteria.")
        sys.exit(1)

    if not np.issubdtype(matrix.dtype, np.number):
        print("Error: All criteria columns must contain numeric values only.")
        sys.exit(1)

    scores, rankings = calculate(matrix, np.array(weights), np.array(impacts))

    try:
        data["Score"] = scores
        data["Rank"] = data["Score"].rank(ascending=False, method="min").astype(int)
        data.to_csv(result_file, index=False)
        print(f"Results saved to {result_file}")
    except Exception as e:
        print(f"Error writing results to file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()