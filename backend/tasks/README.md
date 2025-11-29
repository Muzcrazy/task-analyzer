# Singularium — Smart Task Analyzer

## Summary
This project implements a mini Task Analyzer: a Django backend exposing two APIs and a small static frontend that submits a JSON array of tasks to the backend. The backend scores tasks using urgency, importance, estimated effort and dependency information and returns a sorted list plus explanations.

## How the scoring works (algorithm)
The scoring algorithm computes four components:

1. **Urgency** — derived from `due_date` relative to today's date. Values range roughly 0.2 (no due date / far future) up to >1.0 for past-due tasks (past-due tasks receive extra urgency). This encourages fixing overdue work first.

2. **Importance** — user-provided rating on a 1–10 scale, normalized to 0.1–1.0.

3. **Quick win** — computed as `1 / (1 + estimated_hours)`. This favors small-effort tasks when strategy emphasizes quick wins.

4. **Blocking** — counts how many other tasks depend on this one, normalized (caps applied). Tasks that unblock many others rank higher.

These components are combined using weighted sums. The API supports four strategies:

- **Smart Balance** (default): `0.4*urgency + 0.35*importance + 0.15*quick_win + 0.25*blocking`
- **Fastest Wins**: emphasizes quick_win
- **High Impact**: strongly favors importance
- **Deadline Driven**: strongly favors urgency

Circular dependencies are detected with DFS. When a cycle is found the algorithm flags it and applies a small penalty to involved tasks so they don't unfairly dominate results.

This design aims for readability, explainability, and predictable behavior for typical task lists.

## API Endpoints
- `POST /api/tasks/analyze/` — Accepts JSON array of tasks and returns tasks with `score` and `reason`.
- `GET /api/tasks/suggest/?tasks=<urlencoded-json>` — Returns top 3 tasks (with explanations).

Task JSON fields:
```json
{
  "title": "Example",
  "due_date": "2025-11-30",   // optional ISO date
  "estimated_hours": 2.5,
  "importance": 7,            // 1-10
  "dependencies": ["0","1"]   // optional, task indices as strings
}
