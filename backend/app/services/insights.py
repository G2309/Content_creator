"""Aprendizaje a partir de los resultados que la usuaria captura de Instagram.

Dos usos:
- La biblioteca muestra qué ganchos, pilares y objetivos traen más seguidores,
  y si la mezcla de contenido respeta la matriz 6/4/2.
- El generador recibe un resumen corto para inclinar los guiones nuevos hacia
  lo que ya funcionó en la cuenta.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import SavedTemplate
from app.objectives import OBJECTIVES

# Con menos publicaciones por grupo el promedio es ruido.
MIN_POSTS_PER_GROUP = 2
# Antes de este total no se le sugiere nada a la IA.
MIN_POSTS_FOR_LEARNINGS = 4

BALANCE_WINDOW_DAYS = 30
# Matriz inicial de la Arquitectura 2.0: 6 TOFU / 4 MOFU / 2 BOFU de 12.
TARGET_PCT = {"TOFU": 50, "MOFU": 33, "BOFU": 17}
FUNNEL_NAMES = {
    "TOFU": "descubrimiento o seguidores",
    "MOFU": "confianza",
    "BOFU": "conversión",
}

_FUNNEL_BY_OBJECTIVE = {o["id"]: o["funnel"] for o in OBJECTIVES}


def _has_results(t: SavedTemplate) -> bool:
    return t.views is not None or t.follows is not None


def _avg(values: list[int]) -> float:
    return round(sum(values) / len(values), 1) if values else 0.0


def _group(templates: list[SavedTemplate], key_attr: str, label_attr: str) -> list[dict]:
    groups: dict[str, list[SavedTemplate]] = defaultdict(list)
    for t in templates:
        key = getattr(t, key_attr)
        if key:
            groups[key].append(t)

    rows = []
    for key, items in groups.items():
        if len(items) < MIN_POSTS_PER_GROUP:
            continue
        retention = [t.retention_pct for t in items if t.retention_pct is not None]
        rows.append({
            "key": key,
            "label": getattr(items[0], label_attr) or key,
            "posts": len(items),
            "avg_follows": _avg([t.follows for t in items if t.follows is not None]),
            "avg_views": _avg([t.views for t in items if t.views is not None]),
            "avg_retention": _avg(retention) if retention else None,
        })
    rows.sort(key=lambda r: (r["avg_follows"], r["avg_views"]), reverse=True)
    return rows


def funnel_balance(templates: list[SavedTemplate]) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=BALANCE_WINDOW_DAYS)
    counts = {"TOFU": 0, "MOFU": 0, "BOFU": 0}
    for t in templates:
        created = t.created_at
        if created is not None and created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created is not None and created < since:
            continue
        funnel = _FUNNEL_BY_OBJECTIVE.get(t.objective_id)
        if funnel:
            counts[funnel] += 1

    total = sum(counts.values())
    actual = {k: round(v * 100 / total) if total else 0 for k, v in counts.items()}

    if total < 3:
        message = (
            "Guarda al menos 3 contenidos con objetivo para ver si tu mezcla está balanceada."
        )
    else:
        deficits = {k: TARGET_PCT[k] - actual[k] for k in counts}
        missing, gap = max(deficits.items(), key=lambda kv: kv[1])
        excess, over = min(deficits.items(), key=lambda kv: kv[1])
        if gap <= 10:
            message = "Tu mezcla está balanceada. Sigue así."
        elif excess == "BOFU" and over < -10:
            message = (
                "Estás publicando demasiado contenido de venta. Es la causa más común de "
                f"perder seguidores. Tu próximo contenido debería ser de {FUNNEL_NAMES[missing]}."
            )
        else:
            message = f"Te falta contenido de {FUNNEL_NAMES[missing]}. Haz el próximo de ese tipo."

    return {
        "window_days": BALANCE_WINDOW_DAYS,
        "counts": counts,
        "target_pct": TARGET_PCT,
        "actual_pct": actual,
        "message": message,
    }


def library_insights(db: Session, user_id: int) -> dict:
    templates = db.query(SavedTemplate).filter(SavedTemplate.user_id == user_id).all()
    with_results = [t for t in templates if _has_results(t)]
    return {
        "posts_with_results": len(with_results),
        "min_posts": MIN_POSTS_PER_GROUP,
        "by_hook": _group(with_results, "hook_id", "hook_label"),
        "by_pillar": _group(with_results, "pillar_id", "pillar_label"),
        "by_objective": _group(with_results, "objective_id", "objective_label"),
        "balance": funnel_balance(templates),
    }


def learnings_for_prompt(db: Session, user_id: int) -> str:
    """Resumen de lo que funcionó, para el prompt del guion. Vacío si no hay datos suficientes."""
    insights = library_insights(db, user_id)
    if insights["posts_with_results"] < MIN_POSTS_FOR_LEARNINGS:
        return ""

    lines = []
    for title, rows in (("Ganchos", insights["by_hook"]), ("Pilares", insights["by_pillar"])):
        if len(rows) >= 2:
            best, worst = rows[0], rows[-1]
            if best["avg_follows"] > worst["avg_follows"]:
                lines.append(
                    f"- {title}: «{best['label']}» promedia {best['avg_follows']:g} seguidores por "
                    f"publicación ({best['posts']} publicaciones); «{worst['label']}» promedia "
                    f"{worst['avg_follows']:g}."
                )
    if not lines:
        return ""

    return "\n".join([
        "RESULTADOS REALES DE ESTA CUENTA DE INSTAGRAM:",
        *lines,
        "Es una muestra pequeña: úsala como pista, no como regla. Si el gancho elegido para esta "
        "pieza es uno de los que rinden menos, ejecútalo con más cuidado en vez de cambiarlo.",
    ])
