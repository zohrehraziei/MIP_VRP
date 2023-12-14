# Vehicle Routing Problem with Disruption

This repository contains a comprehensive suite of Python scripts for solving the Vehicle Routing Problem (VRP) with a focus on handling disruptions. The implementation is designed to demonstrate various approaches including callbacks for lazy constraints, cut generation, greedy heuristics, and valid inequalities.

## Overview

Leveraging the Gurobi Optimization Suite and the networkx library, these scripts address different aspects and strategies for solving VRP under normal and disrupted conditions.

## Scripts and Usage

### 1. CallbackLazyConstraints

- **Script**: `CallbackLazyConstraints.py`
- **Description**: Implements the VRP with lazy constraints using Gurobi's callback mechanism. Useful for dynamically adding constraints to the model during the optimization process.
- **Usage**:
  ```python
  model, vrp_callback = vrp(V, c, m, q, Q)
  model.optimize(vrp_callback)

 ### 2. CutGeneration

- **Script**: `CutGeneration.py`
- **Description**: Demonstrates the use of cut generation techniques in solving VRP. It iteratively adds cuts to the model to eliminate infeasible solutions.
- **Usage**:
  ```python
  model, vrp_cutgen = vrp2(V, c, m, q, Q)
  model.optimize(vrp_cutgen)

### 3. GreedyHeuristic

- **Script**: `GreedyHeuristic.py`
- **Description**: Provides a greedy heuristic approach for VRP, offering a quick, albeit less optimal, solution.
- **Usage**:
  ```python
  veh_set, obj = heuristic_greedy(V, c, m, q, Q)
  print("Heuristic objective: ", obj)

### 4. Valid-InequalitiesHeuristic

- **Script**: `Valid-InequalitiesHeuristic.py`
- **Description**: Incorporates valid inequalities into the VRP model, enhancing the solution space exploration with heuristic guidance.
- **Usage**:
  ```python
  model, vrp_callback = vrp(V, c, m, q, Q, veh_set, obj)
  model.optimize(vrp_callback)
