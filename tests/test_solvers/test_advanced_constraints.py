"""Tests for advanced constraint functionality in optimization solvers.

This module verifies that advanced constraints (skills, precedence, exclusion,
grouping) are properly implemented and enforced by the solver.
"""

import logging

import pytest

from mcp_optimizer.solvers.ortools_solver import AdvancedConstraints, ORToolsSolver

logger = logging.getLogger(__name__)


class TestAdvancedConstraints:
    """Test suite for advanced constraint implementation."""

    @pytest.fixture
    def ortools_solver(self):
        """Create OR-Tools solver instance."""
        return ORToolsSolver()

    def test_skill_based_assignment_basic(self, ortools_solver):
        """Test basic skill-based assignment functionality."""
        workers = ["alice", "bob", "charlie"]
        tasks = ["python_task", "java_task", "database_task"]
        costs = [[1, 10, 5], [10, 1, 8], [3, 7, 2]]

        worker_skills = {
            "alice": ["python", "database"],
            "bob": ["java", "database"],
            "charlie": ["python", "java", "database"],
        }

        task_requirements = {
            "python_task": ["python"],
            "java_task": ["java"],
            "database_task": ["database"],
        }

        result = ortools_solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            worker_skills=worker_skills,
            task_requirements=task_requirements,
        )

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        # Verify skill constraints are enforced
        assignments = result.get("assignments", [])
        assert len(assignments) == 3

        for assignment in assignments:
            worker = assignment["worker"]
            task = assignment["task"]

            required_skills = set(task_requirements[task])
            worker_skill_set = set(worker_skills[worker])

            assert required_skills.issubset(worker_skill_set), (
                f"Worker {worker} lacks required skills for {task}"
            )

    def test_skill_based_assignment_complex(self, ortools_solver):
        """Test complex skill-based assignment with multiple skill requirements."""
        workers = ["dev1", "dev2", "dev3", "dev4"]
        tasks = ["frontend", "backend", "devops", "fullstack"]
        costs = [[2, 8, 9, 4], [7, 1, 6, 3], [9, 5, 2, 8], [4, 3, 7, 1]]

        worker_skills = {
            "dev1": ["html", "css", "javascript"],  # Frontend specialist
            "dev2": ["python", "sql", "api"],  # Backend specialist
            "dev3": ["docker", "kubernetes", "aws"],  # DevOps specialist
            "dev4": ["html", "python", "docker"],  # Generalist
        }

        task_requirements = {
            "frontend": ["html", "javascript"],
            "backend": ["python", "sql"],
            "devops": ["docker", "kubernetes"],
            "fullstack": ["html", "python"],
        }

        result = ortools_solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            worker_skills=worker_skills,
            task_requirements=task_requirements,
        )

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        assignments = result.get("assignments", [])

        # Verify correct skill matching
        assignment_map = {a["task"]: a["worker"] for a in assignments}

        # Check that assignments respect skill requirements
        for task, worker in assignment_map.items():
            required_skills = set(task_requirements[task])
            worker_skill_set = set(worker_skills[worker])
            assert required_skills.issubset(worker_skill_set)

    def test_precedence_constraints(self, ortools_solver):
        """Test precedence constraint functionality."""
        workers = ["w1", "w2", "w3"]
        tasks = ["setup", "execute", "cleanup"]
        costs = [[1, 2, 3], [2, 1, 2], [3, 3, 1]]

        constraints = AdvancedConstraints()
        constraints.add_precedence_constraint("setup", "execute")
        constraints.add_precedence_constraint("execute", "cleanup")

        result = ortools_solver.solve_assignment_problem(
            workers=workers, tasks=tasks, costs=costs, advanced_constraints=constraints
        )

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        # For precedence constraints in assignment problems,
        # we simplified to prevent same-worker assignment
        assignments = result.get("assignments", [])
        assignment_map = {a["task"]: a["worker"] for a in assignments}

        # Verify precedence constraint (simplified implementation)
        # Tasks with precedence should not be assigned to same worker
        if "setup" in assignment_map and "execute" in assignment_map:
            assert assignment_map["setup"] != assignment_map["execute"]
        if "execute" in assignment_map and "cleanup" in assignment_map:
            assert assignment_map["execute"] != assignment_map["cleanup"]

    def test_exclusion_constraints(self, ortools_solver):
        """Test exclusion constraint functionality."""
        workers = ["w1", "w2", "w3"]
        tasks = ["task_a", "task_b", "task_c", "task_d"]
        costs = [[1, 2, 3, 4], [2, 1, 4, 3], [3, 4, 1, 2]]

        constraints = AdvancedConstraints()
        # Tasks A and B cannot be assigned to the same worker
        constraints.add_exclusion_constraint(["task_a", "task_b"])
        # Tasks C and D cannot be assigned to the same worker
        constraints.add_exclusion_constraint(["task_c", "task_d"])

        result = ortools_solver.solve_assignment_problem(
            workers=workers, tasks=tasks, costs=costs, advanced_constraints=constraints
        )

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        assignments = result.get("assignments", [])
        worker_tasks = {}

        for assignment in assignments:
            worker = assignment["worker"]
            task = assignment["task"]
            if worker not in worker_tasks:
                worker_tasks[worker] = []
            worker_tasks[worker].append(task)

        # Verify exclusion constraints
        for worker, tasks_assigned in worker_tasks.items():
            # Check that task_a and task_b are not both assigned to same worker
            if "task_a" in tasks_assigned:
                assert "task_b" not in tasks_assigned, (
                    f"Exclusion violated: {worker} has both task_a and task_b"
                )

            # Check that task_c and task_d are not both assigned to same worker
            if "task_c" in tasks_assigned:
                assert "task_d" not in tasks_assigned, (
                    f"Exclusion violated: {worker} has both task_c and task_d"
                )

    def test_grouping_constraints_same_worker(self, ortools_solver):
        """Test grouping constraint (tasks must be assigned to same worker)."""
        workers = ["team1", "team2", "team3"]
        tasks = ["design", "implement", "test", "deploy"]
        costs = [[1, 2, 3, 4], [3, 1, 2, 5], [5, 4, 1, 2]]

        constraints = AdvancedConstraints()
        # Design and implement must be done by same worker
        constraints.add_grouping_constraint(["design", "implement"], same_worker=True)

        result = ortools_solver.solve_assignment_problem(
            workers=workers, tasks=tasks, costs=costs, advanced_constraints=constraints
        )

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        assignments = result.get("assignments", [])
        assignment_map = {a["task"]: a["worker"] for a in assignments}

        # Verify grouping constraint
        if "design" in assignment_map and "implement" in assignment_map:
            assert assignment_map["design"] == assignment_map["implement"], (
                "Grouping constraint violated: design and implement assigned to different workers"
            )

    def test_combined_constraints(self, ortools_solver):
        """Test combination of multiple constraint types."""
        workers = ["senior_dev", "junior_dev", "qa_engineer", "devops_engineer"]
        tasks = ["architecture", "coding", "testing", "deployment"]
        costs = [
            [1, 3, 8, 6],  # senior_dev
            [8, 1, 5, 7],  # junior_dev
            [9, 4, 1, 8],  # qa_engineer
            [5, 6, 3, 1],  # devops_engineer
        ]

        # Skills
        worker_skills = {
            "senior_dev": ["architecture", "coding", "leadership"],
            "junior_dev": ["coding", "basic_testing"],
            "qa_engineer": ["testing", "automation", "quality"],
            "devops_engineer": ["deployment", "infrastructure", "monitoring"],
        }

        task_requirements = {
            "architecture": ["architecture"],
            "coding": ["coding"],
            "testing": ["testing"],
            "deployment": ["deployment"],
        }

        # Advanced constraints
        constraints = AdvancedConstraints()
        constraints.add_precedence_constraint("architecture", "coding")
        constraints.add_precedence_constraint("coding", "testing")
        constraints.add_exclusion_constraint(["architecture", "deployment"])

        result = ortools_solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            worker_skills=worker_skills,
            task_requirements=task_requirements,
            advanced_constraints=constraints,
        )

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        assignments = result.get("assignments", [])
        assignment_map = {a["task"]: a["worker"] for a in assignments}

        # Verify skill constraints
        for task, worker in assignment_map.items():
            if task in task_requirements:
                required_skills = set(task_requirements[task])
                worker_skill_set = set(worker_skills[worker])
                assert required_skills.issubset(worker_skill_set)

        # Verify precedence constraints (simplified as exclusion)
        if "architecture" in assignment_map and "coding" in assignment_map:
            assert assignment_map["architecture"] != assignment_map["coding"]
        if "coding" in assignment_map and "testing" in assignment_map:
            assert assignment_map["coding"] != assignment_map["testing"]

        # Verify exclusion constraints
        if "architecture" in assignment_map and "deployment" in assignment_map:
            assert assignment_map["architecture"] != assignment_map["deployment"]

    def test_constraint_validation_comprehensive(self, ortools_solver):
        """Test comprehensive constraint validation."""
        workers = ["w1", "w2", "w3"]
        tasks = ["t1", "t2", "t3"]
        costs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        # Test valid skills configuration
        worker_skills = {"w1": ["skill1"], "w2": ["skill2"], "w3": ["skill1", "skill2"]}
        task_requirements = {"t1": ["skill1"], "t2": ["skill2"]}

        result = ortools_solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            worker_skills=worker_skills,
            task_requirements=task_requirements,
        )
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        # Test valid advanced constraints
        constraints = AdvancedConstraints()
        constraints.add_precedence_constraint("t1", "t2")
        constraints.add_exclusion_constraint(["t2", "t3"])

        result = ortools_solver.solve_assignment_problem(
            workers=workers, tasks=tasks, costs=costs, advanced_constraints=constraints
        )
        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

    def test_capacity_with_skills(self, ortools_solver):
        """Test capacity constraints combined with skill requirements."""
        workers = ["specialist", "generalist"]
        tasks = ["task1", "task2", "task3", "task4"]
        costs = [[1, 2, 3, 4], [2, 3, 4, 5]]

        worker_skills = {
            "specialist": ["special_skill"],
            "generalist": ["general_skill", "special_skill"],
        }

        task_requirements = {
            "task1": ["special_skill"],
            "task2": ["general_skill"],
            "task3": ["general_skill"],
            "task4": ["special_skill"],
        }

        result = ortools_solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            max_tasks_per_worker=2,
            worker_skills=worker_skills,
            task_requirements=task_requirements,
        )

        assert result is not None
        assert result.get("status").value in ["optimal", "feasible"]

        if result.get("status").value in ["optimal", "feasible"]:
            assignments = result.get("assignments", [])

            # Verify capacity constraints
            worker_task_counts = {}
            for assignment in assignments:
                worker = assignment["worker"]
                worker_task_counts[worker] = worker_task_counts.get(worker, 0) + 1

            for worker, count in worker_task_counts.items():
                assert count <= 2, f"Worker {worker} assigned {count} tasks, exceeding limit of 2"

            # Verify skill constraints
            for assignment in assignments:
                worker = assignment["worker"]
                task = assignment["task"]
                if task in task_requirements:
                    required_skills = set(task_requirements[task])
                    worker_skill_set = set(worker_skills[worker])
                    assert required_skills.issubset(worker_skill_set)

    def test_optimization_with_constraints(self, ortools_solver):
        """Test that solver finds optimal solution respecting constraints."""
        workers = ["cheap_worker", "expensive_worker"]
        tasks = ["simple_task", "complex_task"]

        # Expensive worker is better at complex tasks, cheap worker at simple tasks
        costs = [[1, 10], [5, 2]]  # [cheap_worker costs, expensive_worker costs]

        worker_skills = {"cheap_worker": ["basic"], "expensive_worker": ["basic", "advanced"]}

        task_requirements = {
            "simple_task": ["basic"],
            "complex_task": ["advanced"],  # Only expensive worker can do this
        }

        result = ortools_solver.solve_assignment_problem(
            workers=workers,
            tasks=tasks,
            costs=costs,
            worker_skills=worker_skills,
            task_requirements=task_requirements,
        )

        assert result is not None
        assert result.get("status").value == "optimal"

        assignments = result.get("assignments", [])
        assignment_map = {a["task"]: a["worker"] for a in assignments}

        # Complex task must go to expensive worker (skill constraint)
        assert assignment_map["complex_task"] == "expensive_worker"
        # Simple task should go to cheap worker (cost optimization)
        assert assignment_map["simple_task"] == "cheap_worker"

        # Total cost should be 1 + 2 = 3
        assert result.get("total_cost") == 3.0

    def test_infeasible_constraint_combinations_detailed(self, ortools_solver):
        """Test detailed scenarios of infeasible constraint combinations."""
        workers = ["w1", "w2"]
        tasks = ["t1", "t2", "t3"]
        costs = [[1, 2, 3], [4, 5, 6]]

        # Scenario 1: Impossible skill requirements
        worker_skills = {"w1": ["skill1"], "w2": ["skill2"]}
        task_requirements = {"t1": ["skill3"]}  # No worker has skill3

        with pytest.raises(ValueError, match="No worker has all required skills"):
            ortools_solver.solve_assignment_problem(
                workers,
                tasks,
                costs,
                worker_skills=worker_skills,
                task_requirements=task_requirements,
            )

        # Scenario 2: Max capacity too low with skill requirements
        worker_skills = {"w1": ["skill1"], "w2": ["skill1"]}  # Both can do the tasks
        task_requirements = {"t1": ["skill1"], "t2": ["skill1"], "t3": ["skill1"]}

        with pytest.raises(ValueError, match="Insufficient total capacity"):
            ortools_solver.solve_assignment_problem(
                workers,
                tasks,
                costs,
                max_tasks_per_worker=1,  # 2*1 = 2 < 3 tasks
                worker_skills=worker_skills,
                task_requirements=task_requirements,
            )
