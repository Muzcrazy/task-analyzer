from datetime import date
from dateutil.parser import parse

def detect_cycle(tasks):
    visited = {}
    def dfs(node):
        if node in visited:
            return visited[node] == 1
        visited[node] = 1
        for nb in tasks.get(node, {}).get('dependencies', []):
            if nb not in tasks:
                continue
            if dfs(nb):
                return True
        visited[node] = 2
        return False

    for n in tasks:
        if n not in visited:
            if dfs(n):
                return True
    return False

def compute_scores(task_list, strategy='smart'):
    tasks = {}
    for i, t in enumerate(task_list):
        tid = str(i)
        tasks[tid] = {
            'id': tid,
            'title': t.get('title') or f'Untitled {i}',
            'due_date': t.get('due_date'),
            'estimated_hours': float(t.get('estimated_hours') or 1.0),
            'importance': int(t.get('importance') or 5),
            'dependencies': [str(x) for x in (t.get('dependencies') or [])]
        }

    cycle_present = detect_cycle(tasks)

    def urgency_score(due):
        if due is None:
            return 0.2
        if isinstance(due, str):
            try:
                due = parse(due).date()
            except Exception:
                return 0.2
        days = (due - date.today()).days
        if days < 0:
            return 1.0 + min(7, -days) * 0.1
        if days <= 1:
            return 1.0
        if days <= 7:
            return 0.8
        if days <= 30:
            return 0.5
        return 0.2

    dependents_count = {tid: 0 for tid in tasks}
    for t in tasks.values():
        for dep in t['dependencies']:
            if dep in dependents_count:
                dependents_count[dep] += 1

    results = []
    for tid, t in tasks.items():
        u = urgency_score(t['due_date'])
        imp = max(1, min(10, t['importance'])) / 10.0
        effort = t['estimated_hours']
        quick_win = 1.0 / (1.0 + effort)
        blocking = min(1.0, dependents_count.get(tid, 0) / 5.0)

        if strategy == 'fast':
            score = 0.2 * u + 0.2 * imp + 0.6 * quick_win + 0.1 * blocking
        elif strategy == 'impact':
            score = 0.1 * u + 0.7 * imp + 0.2 * quick_win + 0.2 * blocking
        elif strategy == 'deadline':
            score = 0.8 * u + 0.05 * imp + 0.15 * quick_win + 0.2 * blocking
        else:
            score = 0.4 * u + 0.35 * imp + 0.15 * quick_win + 0.25 * blocking

        if cycle_present and t['dependencies']:
            score *= 0.9

        score = max(0.0, min(score, 2.0))

        reason_parts = []
        reason_parts.append(f"urgency={u:.2f}")
        reason_parts.append(f"importance={imp:.2f}")
        reason_parts.append(f"quick_win={quick_win:.2f}")
        reason_parts.append(f"blocking={blocking:.2f}")
        if cycle_present:
            reason_parts.append('cycle_penalty')

        results.append({
            'id': tid,
            'title': t['title'],
            'due_date': t['due_date'],
            'estimated_hours': t['estimated_hours'],
            'importance': t['importance'],
            'dependencies': t['dependencies'],
            'score': round(float(score), 4),
            'reason': '; '.join(reason_parts)
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results
