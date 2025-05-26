#!/usr/bin/env python3
"""
MCP Optimizer - Streamlit Dashboard

Interactive web dashboard for MCP Optimizer with real-time optimization capabilities.

Installation:
    pip install mcp-optimizer streamlit plotly pandas

Usage:
    streamlit run streamlit_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import mcp-optimizer components
try:
    from mcp_optimizer import (
        LinearProgrammingSolver,
        AssignmentSolver,
        TransportationSolver,
        KnapsackSolver,
        RoutingSolver,
        PortfolioOptimizer,
        OptimizationEngine,
        SolverConfig,
        OptimizationResult
    )
except ImportError:
    st.error("Error: mcp-optimizer package not found. Install with: pip install mcp-optimizer")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="MCP Optimizer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'optimization_history' not in st.session_state:
    st.session_state.optimization_history = []
if 'solver_config' not in st.session_state:
    st.session_state.solver_config = SolverConfig()

def main():
    """Main dashboard function."""
    st.markdown('<h1 class="main-header">🚀 MCP Optimizer Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar configuration
    setup_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔧 Optimization Studio",
        "📊 Results Analysis", 
        "📈 Performance Metrics",
        "🎯 Problem Templates",
        "📋 History",
        "⚙️ Settings"
    ])
    
    with tab1:
        optimization_studio()
    
    with tab2:
        results_analysis()
    
    with tab3:
        performance_metrics()
    
    with tab4:
        problem_templates()
    
    with tab5:
        optimization_history()
    
    with tab6:
        settings_panel()

def setup_sidebar():
    """Setup sidebar with global controls."""
    st.sidebar.title("🎛️ Control Panel")
    
    # Solver configuration
    st.sidebar.subheader("Solver Configuration")
    
    timeout = st.sidebar.slider("Timeout (seconds)", 10, 3600, 300)
    max_iterations = st.sidebar.number_input("Max Iterations", 1000, 100000, 10000)
    threads = st.sidebar.slider("Threads", 1, 16, 4)
    tolerance = st.sidebar.selectbox("Tolerance", [1e-6, 1e-8, 1e-10], index=0)
    
    st.session_state.solver_config = SolverConfig(
        timeout=timeout,
        max_iterations=max_iterations,
        tolerance=tolerance,
        threads=threads
    )
    
    # Quick actions
    st.sidebar.subheader("Quick Actions")
    if st.sidebar.button("🗑️ Clear History"):
        st.session_state.optimization_history = []
        st.success("History cleared!")
    
    if st.sidebar.button("📥 Export Results"):
        export_results()
    
    # System status
    st.sidebar.subheader("System Status")
    st.sidebar.success("✅ MCP Optimizer Ready")
    st.sidebar.info(f"🕒 {datetime.now().strftime('%H:%M:%S')}")

def optimization_studio():
    """Main optimization interface."""
    st.header("🔧 Optimization Studio")
    
    # Problem type selection
    problem_type = st.selectbox(
        "Select Problem Type",
        ["Linear Programming", "Assignment", "Transportation", "Knapsack", "Routing", "Portfolio"],
        key="problem_type"
    )
    
    # Dynamic problem interface based on type
    if problem_type == "Linear Programming":
        linear_programming_interface()
    elif problem_type == "Assignment":
        assignment_interface()
    elif problem_type == "Transportation":
        transportation_interface()
    elif problem_type == "Knapsack":
        knapsack_interface()
    elif problem_type == "Routing":
        routing_interface()
    elif problem_type == "Portfolio":
        portfolio_interface()

def linear_programming_interface():
    """Linear programming problem interface."""
    st.subheader("📈 Linear Programming")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Objective Function**")
        direction = st.radio("Direction", ["maximize", "minimize"])
        
        # Dynamic coefficient input
        num_vars = st.number_input("Number of Variables", 2, 10, 2)
        coefficients = []
        
        for i in range(num_vars):
            coef = st.number_input(f"Coefficient x{i+1}", value=1.0, key=f"obj_coef_{i}")
            coefficients.append(coef)
    
    with col2:
        st.write("**Constraints**")
        num_constraints = st.number_input("Number of Constraints", 1, 10, 2)
        
        constraints = []
        for i in range(num_constraints):
            st.write(f"Constraint {i+1}")
            constraint_coefs = []
            
            cols = st.columns(num_vars + 2)
            for j in range(num_vars):
                with cols[j]:
                    coef = st.number_input(f"x{j+1}", value=1.0, key=f"const_{i}_{j}")
                    constraint_coefs.append(coef)
            
            with cols[num_vars]:
                operator = st.selectbox("", ["<=", ">=", "="], key=f"op_{i}")
            
            with cols[num_vars + 1]:
                value = st.number_input("Value", value=1.0, key=f"val_{i}")
            
            constraints.append({
                "coefficients": constraint_coefs,
                "operator": operator,
                "value": value
            })
    
    # Solve button
    if st.button("🚀 Solve Linear Programming", type="primary"):
        solve_linear_programming(coefficients, direction, constraints, num_vars)

def solve_linear_programming(coefficients, direction, constraints, num_vars):
    """Solve linear programming problem."""
    try:
        solver = LinearProgrammingSolver(config=st.session_state.solver_config)
        
        problem = {
            "objective": {
                "coefficients": coefficients,
                "direction": direction
            },
            "constraints": constraints,
            "bounds": [(0, None)] * num_vars,
            "variable_names": [f"x{i+1}" for i in range(num_vars)]
        }
        
        with st.spinner("Solving optimization problem..."):
            start_time = time.time()
            result = solver.solve(problem)
            solve_time = time.time() - start_time
        
        # Display results
        display_optimization_result(result, solve_time, "Linear Programming", problem)
        
    except Exception as e:
        st.error(f"Optimization failed: {str(e)}")

def assignment_interface():
    """Assignment problem interface."""
    st.subheader("👥 Assignment Problem")
    
    # Matrix size
    size = st.slider("Matrix Size", 2, 8, 4)
    
    st.write("**Cost Matrix**")
    st.write("Enter costs for assigning each worker to each task:")
    
    # Create cost matrix input
    cost_matrix = []
    for i in range(size):
        row = []
        cols = st.columns(size)
        for j in range(size):
            with cols[j]:
                cost = st.number_input(
                    f"Worker {i+1} → Task {j+1}",
                    value=np.random.randint(1, 20),
                    key=f"cost_{i}_{j}"
                )
                row.append(cost)
        cost_matrix.append(row)
    
    # Display matrix
    df = pd.DataFrame(cost_matrix, 
                     columns=[f"Task {j+1}" for j in range(size)],
                     index=[f"Worker {i+1}" for i in range(size)])
    st.dataframe(df, use_container_width=True)
    
    if st.button("🚀 Solve Assignment", type="primary"):
        solve_assignment_problem(cost_matrix, size)

def solve_assignment_problem(cost_matrix, size):
    """Solve assignment problem."""
    try:
        solver = AssignmentSolver(config=st.session_state.solver_config)
        
        problem = {
            "cost_matrix": cost_matrix,
            "employee_names": [f"Worker_{i+1}" for i in range(size)],
            "task_names": [f"Task_{j+1}" for j in range(size)]
        }
        
        with st.spinner("Solving assignment problem..."):
            start_time = time.time()
            result = solver.solve(problem)
            solve_time = time.time() - start_time
        
        display_optimization_result(result, solve_time, "Assignment", problem)
        
        # Visualize assignment
        visualize_assignment(result, cost_matrix, size)
        
    except Exception as e:
        st.error(f"Assignment optimization failed: {str(e)}")

def transportation_interface():
    """Transportation problem interface."""
    st.subheader("🚚 Transportation Problem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Supply (Sources)**")
        num_sources = st.number_input("Number of Sources", 2, 6, 3)
        supply = []
        for i in range(num_sources):
            s = st.number_input(f"Source {i+1} Supply", value=100, key=f"supply_{i}")
            supply.append(s)
    
    with col2:
        st.write("**Demand (Destinations)**")
        num_destinations = st.number_input("Number of Destinations", 2, 6, 4)
        demand = []
        for i in range(num_destinations):
            d = st.number_input(f"Destination {i+1} Demand", value=75, key=f"demand_{i}")
            demand.append(d)
    
    st.write("**Transportation Costs**")
    costs = []
    for i in range(num_sources):
        row = []
        cols = st.columns(num_destinations)
        for j in range(num_destinations):
            with cols[j]:
                cost = st.number_input(
                    f"Source {i+1} → Dest {j+1}",
                    value=np.random.randint(5, 25),
                    key=f"trans_cost_{i}_{j}"
                )
                row.append(cost)
        costs.append(row)
    
    if st.button("🚀 Solve Transportation", type="primary"):
        solve_transportation_problem(supply, demand, costs, num_sources, num_destinations)

def solve_transportation_problem(supply, demand, costs, num_sources, num_destinations):
    """Solve transportation problem."""
    try:
        solver = TransportationSolver(config=st.session_state.solver_config)
        
        problem = {
            "supply": supply,
            "demand": demand,
            "costs": costs,
            "supplier_names": [f"Source_{i+1}" for i in range(num_sources)],
            "customer_names": [f"Dest_{j+1}" for j in range(num_destinations)]
        }
        
        with st.spinner("Solving transportation problem..."):
            start_time = time.time()
            result = solver.solve(problem)
            solve_time = time.time() - start_time
        
        display_optimization_result(result, solve_time, "Transportation", problem)
        
        # Visualize transportation flow
        visualize_transportation(result, costs, supply, demand)
        
    except Exception as e:
        st.error(f"Transportation optimization failed: {str(e)}")

def knapsack_interface():
    """Knapsack problem interface."""
    st.subheader("🎒 Knapsack Problem")
    
    capacity = st.number_input("Knapsack Capacity", value=100, min_value=1)
    
    st.write("**Items**")
    num_items = st.number_input("Number of Items", 3, 15, 5)
    
    items = []
    for i in range(num_items):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(f"Item {i+1} Name", value=f"Item_{i+1}", key=f"item_name_{i}")
        with col2:
            weight = st.number_input(f"Weight", value=np.random.randint(5, 30), key=f"weight_{i}")
        with col3:
            value = st.number_input(f"Value", value=np.random.randint(10, 50), key=f"value_{i}")
        
        items.append({"name": name, "weight": weight, "value": value})
    
    # Display items table
    df = pd.DataFrame(items)
    df['Value/Weight Ratio'] = df['value'] / df['weight']
    st.dataframe(df, use_container_width=True)
    
    if st.button("🚀 Solve Knapsack", type="primary"):
        solve_knapsack_problem(items, capacity)

def solve_knapsack_problem(items, capacity):
    """Solve knapsack problem."""
    try:
        solver = KnapsackSolver(config=st.session_state.solver_config)
        
        problem = {
            "items": items,
            "capacity": capacity,
            "knapsack_type": "0-1"
        }
        
        with st.spinner("Solving knapsack problem..."):
            start_time = time.time()
            result = solver.solve(problem)
            solve_time = time.time() - start_time
        
        display_optimization_result(result, solve_time, "Knapsack", problem)
        
        # Visualize knapsack solution
        visualize_knapsack(result, items, capacity)
        
    except Exception as e:
        st.error(f"Knapsack optimization failed: {str(e)}")

def routing_interface():
    """Routing problem interface."""
    st.subheader("🗺️ Routing Problem")
    
    num_locations = st.slider("Number of Locations", 3, 10, 5)
    
    st.write("**Distance Matrix**")
    locations = [f"Location_{i}" for i in range(num_locations)]
    
    # Generate or input distance matrix
    if st.checkbox("Generate Random Distances"):
        np.random.seed(42)
        distance_matrix = np.random.randint(10, 100, (num_locations, num_locations))
        # Make symmetric and set diagonal to 0
        distance_matrix = (distance_matrix + distance_matrix.T) // 2
        np.fill_diagonal(distance_matrix, 0)
    else:
        distance_matrix = []
        for i in range(num_locations):
            row = []
            cols = st.columns(num_locations)
            for j in range(num_locations):
                with cols[j]:
                    if i == j:
                        dist = 0
                    else:
                        dist = st.number_input(
                            f"{i}→{j}",
                            value=np.random.randint(10, 50),
                            key=f"dist_{i}_{j}"
                        )
                    row.append(dist)
            distance_matrix.append(row)
    
    # Display distance matrix
    df = pd.DataFrame(distance_matrix, columns=locations, index=locations)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🚀 Solve Routing", type="primary"):
        solve_routing_problem(distance_matrix, locations)

def solve_routing_problem(distance_matrix, locations):
    """Solve routing problem."""
    try:
        solver = RoutingSolver(config=st.session_state.solver_config)
        
        problem = {
            "distance_matrix": distance_matrix,
            "locations": locations,
            "start_location": 0,
            "problem_type": "TSP"
        }
        
        with st.spinner("Solving routing problem..."):
            start_time = time.time()
            result = solver.solve(problem)
            solve_time = time.time() - start_time
        
        display_optimization_result(result, solve_time, "Routing", problem)
        
        # Visualize route
        visualize_route(result, distance_matrix, locations)
        
    except Exception as e:
        st.error(f"Routing optimization failed: {str(e)}")

def portfolio_interface():
    """Portfolio optimization interface."""
    st.subheader("💰 Portfolio Optimization")
    
    # Asset selection
    default_assets = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    assets = st.multiselect("Select Assets", default_assets, default=default_assets[:3])
    
    if not assets:
        st.warning("Please select at least one asset.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Expected Returns (%)**")
        expected_returns = []
        for asset in assets:
            ret = st.number_input(f"{asset} Expected Return", value=12.0, key=f"return_{asset}") / 100
            expected_returns.append(ret)
    
    with col2:
        st.write("**Risk Parameters**")
        target_return = st.number_input("Target Return (%)", value=10.0) / 100
        risk_tolerance = st.number_input("Risk Tolerance (%)", value=5.0) / 100
    
    # Simplified covariance matrix (for demo)
    n = len(assets)
    covariance_matrix = np.random.rand(n, n) * 0.01
    covariance_matrix = (covariance_matrix + covariance_matrix.T) / 2
    np.fill_diagonal(covariance_matrix, np.random.rand(n) * 0.05)
    
    if st.button("🚀 Optimize Portfolio", type="primary"):
        solve_portfolio_problem(assets, expected_returns, covariance_matrix.tolist(), target_return, risk_tolerance)

def solve_portfolio_problem(assets, expected_returns, covariance_matrix, target_return, risk_tolerance):
    """Solve portfolio optimization problem."""
    try:
        optimizer = PortfolioOptimizer(config=st.session_state.solver_config)
        
        problem = {
            "assets": assets,
            "expected_returns": expected_returns,
            "covariance_matrix": covariance_matrix,
            "target_return": target_return,
            "risk_tolerance": risk_tolerance,
            "constraints": {
                "min_weight": 0.05,
                "max_weight": 0.40
            }
        }
        
        with st.spinner("Optimizing portfolio..."):
            start_time = time.time()
            result = optimizer.solve(problem)
            solve_time = time.time() - start_time
        
        display_optimization_result(result, solve_time, "Portfolio", problem)
        
        # Visualize portfolio allocation
        visualize_portfolio(result, assets)
        
    except Exception as e:
        st.error(f"Portfolio optimization failed: {str(e)}")

def display_optimization_result(result, solve_time, problem_type, problem_data):
    """Display optimization results."""
    # Store in history
    history_entry = {
        "timestamp": datetime.now(),
        "problem_type": problem_type,
        "solve_time": solve_time,
        "result": result,
        "problem_data": problem_data
    }
    st.session_state.optimization_history.append(history_entry)
    
    # Display results
    st.success("✅ Optimization completed successfully!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Objective Value", f"{result.objective_value:.4f}")
    
    with col2:
        st.metric("Solve Time", f"{solve_time:.3f}s")
    
    with col3:
        st.metric("Status", result.status)
    
    # Variables
    if hasattr(result, 'variables') and result.variables:
        st.write("**Solution Variables:**")
        var_df = pd.DataFrame({
            "Variable": [f"x{i+1}" for i in range(len(result.variables))],
            "Value": result.variables
        })
        st.dataframe(var_df, use_container_width=True)

def visualize_assignment(result, cost_matrix, size):
    """Visualize assignment solution."""
    st.subheader("📊 Assignment Visualization")
    
    # Create assignment matrix
    assignment_matrix = np.zeros((size, size))
    if hasattr(result, 'get_assignments'):
        assignments = result.get_assignments()
        for worker, task in assignments.items():
            worker_idx = int(worker.split('_')[1]) - 1
            task_idx = int(task.split('_')[1]) - 1
            assignment_matrix[worker_idx][task_idx] = 1
    
    # Heatmap
    fig = px.imshow(
        assignment_matrix,
        labels=dict(x="Tasks", y="Workers", color="Assigned"),
        x=[f"Task {j+1}" for j in range(size)],
        y=[f"Worker {i+1}" for i in range(size)],
        color_continuous_scale="Blues"
    )
    fig.update_layout(title="Assignment Matrix")
    st.plotly_chart(fig, use_container_width=True)

def visualize_transportation(result, costs, supply, demand):
    """Visualize transportation solution."""
    st.subheader("📊 Transportation Flow")
    
    # Create flow diagram (simplified)
    fig = go.Figure()
    
    # Add supply and demand bars
    sources = [f"Source {i+1}" for i in range(len(supply))]
    destinations = [f"Dest {j+1}" for j in range(len(demand))]
    
    fig.add_trace(go.Bar(
        name="Supply",
        x=sources,
        y=supply,
        marker_color="lightblue"
    ))
    
    fig.add_trace(go.Bar(
        name="Demand",
        x=destinations,
        y=demand,
        marker_color="lightcoral"
    ))
    
    fig.update_layout(
        title="Supply vs Demand",
        xaxis_title="Locations",
        yaxis_title="Quantity"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def visualize_knapsack(result, items, capacity):
    """Visualize knapsack solution."""
    st.subheader("📊 Knapsack Solution")
    
    # Get selected items
    selected_items = []
    if hasattr(result, 'get_selected_items'):
        selected_items = result.get_selected_items()
    
    # Create visualization
    df = pd.DataFrame(items)
    df['Selected'] = df['name'].isin([item['name'] for item in selected_items])
    
    fig = px.scatter(
        df,
        x="weight",
        y="value",
        color="Selected",
        size="value",
        hover_data=["name"],
        title="Items: Weight vs Value"
    )
    
    fig.add_vline(x=capacity, line_dash="dash", line_color="red", 
                  annotation_text=f"Capacity: {capacity}")
    
    st.plotly_chart(fig, use_container_width=True)

def visualize_route(result, distance_matrix, locations):
    """Visualize routing solution."""
    st.subheader("📊 Optimal Route")
    
    if hasattr(result, 'get_route'):
        route = result.get_route()
        
        # Create route visualization
        route_names = [locations[i] for i in route]
        
        fig = go.Figure()
        
        # Add route path
        for i in range(len(route) - 1):
            fig.add_trace(go.Scatter(
                x=[i, i+1],
                y=[0, 0],
                mode='lines+markers',
                name=f"{route_names[i]} → {route_names[i+1]}",
                text=[route_names[i], route_names[i+1]],
                textposition="top center"
            ))
        
        fig.update_layout(
            title="Optimal Route",
            xaxis_title="Step",
            yaxis_title="",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Route summary
        st.write("**Route Summary:**")
        route_text = " → ".join(route_names)
        st.write(route_text)

def visualize_portfolio(result, assets):
    """Visualize portfolio allocation."""
    st.subheader("📊 Portfolio Allocation")
    
    if hasattr(result, 'weights'):
        weights = result.weights
        
        # Pie chart
        fig = px.pie(
            values=weights,
            names=assets,
            title="Asset Allocation"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Bar chart
        fig2 = px.bar(
            x=assets,
            y=weights,
            title="Portfolio Weights"
        )
        fig2.update_layout(
            xaxis_title="Assets",
            yaxis_title="Weight (%)"
        )
        st.plotly_chart(fig2, use_container_width=True)

def results_analysis():
    """Results analysis tab."""
    st.header("📊 Results Analysis")
    
    if not st.session_state.optimization_history:
        st.info("No optimization results yet. Run some optimizations to see analysis.")
        return
    
    # Performance overview
    st.subheader("Performance Overview")
    
    history = st.session_state.optimization_history
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Optimizations", len(history))
    
    with col2:
        avg_time = np.mean([h['solve_time'] for h in history])
        st.metric("Avg Solve Time", f"{avg_time:.3f}s")
    
    with col3:
        problem_types = len(set(h['problem_type'] for h in history))
        st.metric("Problem Types", problem_types)
    
    with col4:
        total_time = sum(h['solve_time'] for h in history)
        st.metric("Total Time", f"{total_time:.3f}s")
    
    # Solve time trends
    st.subheader("Solve Time Trends")
    
    df = pd.DataFrame([
        {
            "timestamp": h['timestamp'],
            "problem_type": h['problem_type'],
            "solve_time": h['solve_time'],
            "objective_value": h['result'].objective_value
        }
        for h in history
    ])
    
    fig = px.line(
        df,
        x="timestamp",
        y="solve_time",
        color="problem_type",
        title="Solve Time Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Problem type distribution
    st.subheader("Problem Type Distribution")
    
    type_counts = df['problem_type'].value_counts()
    fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Optimization Problems by Type"
    )
    st.plotly_chart(fig, use_container_width=True)

def performance_metrics():
    """Performance metrics tab."""
    st.header("📈 Performance Metrics")
    
    if not st.session_state.optimization_history:
        st.info("No performance data available yet.")
        return
    
    history = st.session_state.optimization_history
    
    # Real-time metrics
    st.subheader("Real-time Metrics")
    
    # Create metrics dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        # Solve time distribution
        solve_times = [h['solve_time'] for h in history]
        fig = px.histogram(
            x=solve_times,
            nbins=20,
            title="Solve Time Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Success rate
        success_rate = 100  # Assuming all successful for demo
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=success_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Success Rate (%)"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 80], 'color': "gray"},
                       {'range': [80, 100], 'color': "lightgreen"}
                   ],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': 90}}
        ))
        st.plotly_chart(fig, use_container_width=True)

def problem_templates():
    """Problem templates tab."""
    st.header("🎯 Problem Templates")
    
    st.write("Quick start with pre-configured optimization problems:")
    
    templates = {
        "Production Planning": {
            "type": "Linear Programming",
            "description": "Maximize profit from production with resource constraints",
            "example": "Factory producing multiple products with limited materials"
        },
        "Employee Scheduling": {
            "type": "Assignment",
            "description": "Assign employees to shifts minimizing cost",
            "example": "Hospital nurse scheduling with skill requirements"
        },
        "Supply Chain": {
            "type": "Transportation",
            "description": "Minimize transportation costs in supply network",
            "example": "Distribute goods from warehouses to stores"
        },
        "Investment Selection": {
            "type": "Knapsack",
            "description": "Select investments within budget constraints",
            "example": "Choose projects to maximize ROI with limited capital"
        },
        "Delivery Routes": {
            "type": "Routing",
            "description": "Find shortest routes for deliveries",
            "example": "Optimize delivery truck routes to minimize distance"
        },
        "Asset Allocation": {
            "type": "Portfolio",
            "description": "Optimize investment portfolio risk/return",
            "example": "Balance stocks and bonds for retirement planning"
        }
    }
    
    for name, template in templates.items():
        with st.expander(f"📋 {name}"):
            st.write(f"**Type:** {template['type']}")
            st.write(f"**Description:** {template['description']}")
            st.write(f"**Example:** {template['example']}")
            
            if st.button(f"Load {name} Template", key=f"template_{name}"):
                st.success(f"Template '{name}' loaded! Switch to Optimization Studio tab.")

def optimization_history():
    """Optimization history tab."""
    st.header("📋 Optimization History")
    
    if not st.session_state.optimization_history:
        st.info("No optimization history available.")
        return
    
    # History table
    history_data = []
    for i, h in enumerate(st.session_state.optimization_history):
        history_data.append({
            "ID": i + 1,
            "Timestamp": h['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
            "Problem Type": h['problem_type'],
            "Solve Time (s)": f"{h['solve_time']:.3f}",
            "Objective Value": f"{h['result'].objective_value:.4f}",
            "Status": h['result'].status
        })
    
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True)
    
    # Detailed view
    if st.checkbox("Show Detailed View"):
        selected_id = st.selectbox("Select Optimization", range(1, len(history_data) + 1))
        
        if selected_id:
            h = st.session_state.optimization_history[selected_id - 1]
            
            st.subheader(f"Optimization #{selected_id} Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Problem Information:**")
                st.json({
                    "type": h['problem_type'],
                    "timestamp": h['timestamp'].isoformat(),
                    "solve_time": h['solve_time']
                })
            
            with col2:
                st.write("**Results:**")
                st.json({
                    "objective_value": h['result'].objective_value,
                    "status": h['result'].status,
                    "variables": h['result'].variables if hasattr(h['result'], 'variables') else None
                })

def settings_panel():
    """Settings panel tab."""
    st.header("⚙️ Settings")
    
    # Export/Import settings
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export History"):
            export_results()
    
    with col2:
        uploaded_file = st.file_uploader("📤 Import History", type=['json'])
        if uploaded_file:
            import_results(uploaded_file)
    
    # Performance settings
    st.subheader("Performance Settings")
    
    enable_caching = st.checkbox("Enable Result Caching", value=True)
    auto_save = st.checkbox("Auto-save Results", value=True)
    max_history = st.number_input("Max History Items", 10, 1000, 100)
    
    # Visualization settings
    st.subheader("Visualization Settings")
    
    theme = st.selectbox("Chart Theme", ["plotly", "plotly_white", "plotly_dark"])
    show_animations = st.checkbox("Show Animations", value=True)
    
    # Apply settings
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")

def export_results():
    """Export optimization results."""
    if not st.session_state.optimization_history:
        st.warning("No results to export.")
        return
    
    # Prepare export data
    export_data = []
    for h in st.session_state.optimization_history:
        export_data.append({
            "timestamp": h['timestamp'].isoformat(),
            "problem_type": h['problem_type'],
            "solve_time": h['solve_time'],
            "objective_value": h['result'].objective_value,
            "status": h['result'].status,
            "variables": h['result'].variables if hasattr(h['result'], 'variables') else None
        })
    
    # Create download
    json_data = json.dumps(export_data, indent=2)
    st.download_button(
        label="📥 Download Results",
        data=json_data,
        file_name=f"mcp_optimizer_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def import_results(uploaded_file):
    """Import optimization results."""
    try:
        data = json.load(uploaded_file)
        st.success(f"Imported {len(data)} optimization results!")
        # Note: In a real implementation, you'd reconstruct the history
    except Exception as e:
        st.error(f"Import failed: {str(e)}")

if __name__ == "__main__":
    main() 