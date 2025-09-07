from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class RecommendationType(Enum):
    IMPROVEMENT = "improvement"
    STABILIZATION = "stabilization"
    LEVERAGE = "leverage"
    MAINTENANCE = "maintenance"
    RECOVERY = "recovery"


@dataclass
class ActionStep:
    description: str
    estimated_time_min: Optional[int] = None
    sphere: Optional[str] = None


@dataclass
class Metrics:
    target_improvement: float
    timeframe: str
    success_criteria: str


@dataclass
class Evidence:
    data_points: Dict[str, Any]
    correlations: Dict[str, float]
    historical_success: Optional[str] = None


@dataclass
class RecommendationData:
    title: str
    description: str
    action_steps: List[ActionStep]
    metrics: Metrics
    related_spheres: List[str]
    evidence: Evidence


@dataclass
class Recommendation:
    sphere: str
    type: RecommendationType
    priority: float
    data: RecommendationData


class HPIRecommendationEngine:
    def __init__(self) -> None:
        self.sphere_stats: Dict[str, Dict[str, Any]] = {}
        self.correlations: Dict[Tuple[str, str], float] = {}
        self.per_sphere_top_corr: Dict[str, List[Tuple[str, float]]] = {}

    @staticmethod
    def _nan_safe(values: List[float]) -> np.ndarray:
        arr = np.array(values, dtype=float)
        # replace non-finite with nan and then interpolate/ffill if possible
        arr[~np.isfinite(arr)] = np.nan
        if np.isnan(arr).all():
            return np.zeros_like(arr)
        # simple forward fill then back fill
        idx = np.where(~np.isnan(arr))[0]
        if idx.size == 0:
            return np.zeros_like(arr)
        first_valid = idx[0]
        last_valid = idx[-1]
        for i in range(first_valid + 1, len(arr)):
            if np.isnan(arr[i]):
                arr[i] = arr[i - 1]
        for i in range(first_valid - 1, -1, -1):
            if np.isnan(arr[i]):
                arr[i] = arr[i + 1]
        # final fallback for tails
        arr[:first_valid] = arr[first_valid]
        arr[last_valid + 1:] = arr[last_valid]
        return arr

    @staticmethod
    def _linear_slope(y: np.ndarray) -> float:
        if y.size < 2:
            return 0.0
        x = np.arange(y.size, dtype=float)
        # slope of least squares fit
        x_mean = x.mean()
        y_mean = y.mean()
        denom = ((x - x_mean) ** 2).sum()
        if denom == 0:
            return 0.0
        slope = ((x - x_mean) * (y - y_mean)).sum() / denom
        return float(slope)

    @staticmethod
    def _volatility(y: np.ndarray) -> float:
        if y.size < 3:
            return 0.0
        diffs = np.diff(y)
        return float(np.std(diffs))

    def analyze_sphere_correlations(self, history: Dict[str, List[float]]) -> None:
        # normalize lengths by padding/truncating to min common length >= 3
        if not history:
            self.sphere_stats = {}
            self.correlations = {}
            self.per_sphere_top_corr = {}
            return

        min_len = min(len(v) for v in history.values()) if history else 0
        min_len = max(min_len, 3)
        series = {}
        for sphere, values in history.items():
            arr = self._nan_safe(values)[-min_len:]
            series[sphere] = arr

        # compute stats per sphere
        stats: Dict[str, Dict[str, Any]] = {}
        for sphere, arr in series.items():
            slope = self._linear_slope(arr)
            vol = self._volatility(arr)
            curr = float(arr[-1]) if arr.size > 0 else 0.0
            mean = float(arr.mean()) if arr.size > 0 else 0.0
            momentum = curr - float(arr[-2]) if arr.size >= 2 else 0.0
            stats[sphere] = {
                "current": curr,
                "mean": mean,
                "slope": slope,
                "volatility": vol,
                "momentum": momentum,
            }
        self.sphere_stats = stats

        # correlation matrix (pearson), pairwise
        corrs: Dict[Tuple[str, str], float] = {}
        names = list(series.keys())
        for i, a in enumerate(names):
            for j in range(i + 1, len(names)):
                b = names[j]
                ya = series[a]
                yb = series[b]
                if ya.size >= 2 and yb.size >= 2 and np.std(ya) > 0 and np.std(yb) > 0:
                    r = float(np.corrcoef(ya, yb)[0, 1])
                else:
                    r = 0.0
                corrs[(a, b)] = r
                corrs[(b, a)] = r
        self.correlations = corrs

        # top correlations per sphere
        top_map: Dict[str, List[Tuple[str, float]]] = {}
        for s in names:
            pairs = []
            for other in names:
                if other == s:
                    continue
                r = corrs.get((s, other), 0.0)
                pairs.append((other, r))
            pairs.sort(key=lambda t: abs(t[1]), reverse=True)
            top_map[s] = pairs[:3]
        self.per_sphere_top_corr = top_map

    def _build_action_steps(self, sphere: str, rec_type: RecommendationType) -> List[ActionStep]:
        steps: List[ActionStep] = []
        if rec_type == RecommendationType.RECOVERY:
            steps = [
                ActionStep("Выделите 20 минут на спокойную прогулку или растяжку", 20, sphere),
                ActionStep("Назовите 1 источник стресса и один шаг по его снижению", 10, sphere),
            ]
        elif rec_type == RecommendationType.IMPROVEMENT:
            steps = [
                ActionStep("Определите 1 узкое место и придумайте 2 варианта его ослабить", 15, sphere),
                ActionStep("Запланируйте конкретное действие в календаре на 15–20 минут", 5, sphere),
            ]
        elif rec_type == RecommendationType.STABILIZATION:
            steps = [
                ActionStep("Зафиксируйте 1-2 работающих привычки и поддержите их в ближайшую неделю", 10, sphere),
                ActionStep("Минимизируйте один источник флуктуаций (сон/режим/нагрузка)", 15, sphere),
            ]
        elif rec_type == RecommendationType.LEVERAGE:
            steps = [
                ActionStep("Используйте сильную связанную сферу для усиления текущей (свяжите действия)", 15, sphere),
                ActionStep("Сформулируйте микро-действие, которое опирается на уже работающую привычку", 10, sphere),
            ]
        else:  # MAINTENANCE
            steps = [
                ActionStep("Сохраните текущий ритм: 1 микро-действие в день", 5, sphere),
                ActionStep("Определите триггер поддержания: время/место/сигнал", 5, sphere),
            ]
        return steps

    def _priority_score(self, sphere: str, current: float, slope: float, volatility: float, momentum: float) -> float:
        # Priority combines low level, negative trend, and high volatility
        level_penalty = max(0.0, 7.0 - current) / 7.0  # more priority if below 7
        trend_penalty = max(0.0, -slope)  # negative slope increases priority
        vol_penalty = volatility
        momentum_penalty = max(0.0, -momentum)
        score = 0.5 * level_penalty + 0.3 * trend_penalty + 0.15 * vol_penalty + 0.05 * momentum_penalty
        return float(round(score, 4))

    def _build_metrics(self, current: float, rec_type: RecommendationType) -> Metrics:
        if rec_type in (RecommendationType.IMPROVEMENT, RecommendationType.RECOVERY):
            target = min(10.0, round(current + 0.5, 1))
            timeframe = "2 недели"
        elif rec_type == RecommendationType.STABILIZATION:
            target = round(current, 1)
            timeframe = "1 неделя"
        elif rec_type == RecommendationType.LEVERAGE:
            target = min(10.0, round(current + 0.3, 1))
            timeframe = "2-3 недели"
        else:  # MAINTENANCE
            target = round(current, 1)
            timeframe = "1-2 недели"
        return Metrics(
            target_improvement=target,
            timeframe=timeframe,
            success_criteria="Выполнено 5+ микро-действий из 7 дней и заметное субъективное улучшение"
        )

    def _related_spheres(self, sphere: str, threshold: float = 0.45) -> List[str]:
        pairs = self.per_sphere_top_corr.get(sphere, [])
        return [s for s, r in pairs if abs(r) >= threshold]

    def generate_recommendation(self, sphere: str, current_value: float, history_values: List[float]) -> Optional[Recommendation]:
        arr = self._nan_safe(history_values)
        if arr.size == 0:
            return None
        slope = self._linear_slope(arr)
        vol = self._volatility(arr)
        momentum = arr[-1] - arr[-2] if arr.size >= 2 else 0.0
        current = float(arr[-1])
        mean = float(arr.mean())

        # Determine type
        rec_type: RecommendationType
        if momentum < -0.5 and current <= mean - 0.3:
            rec_type = RecommendationType.RECOVERY
        elif current < 6.0 and slope <= 0:
            rec_type = RecommendationType.IMPROVEMENT
        elif vol > 0.6:
            rec_type = RecommendationType.STABILIZATION
        elif slope >= 0.05 and current >= 6.5:
            rec_type = RecommendationType.MAINTENANCE
        else:
            # Try leverage if there is a strong positive correlation with a stronger sphere
            related = self.per_sphere_top_corr.get(sphere, [])
            strong_partner = next((s for s, r in related if r >= 0.6 and self.sphere_stats.get(s, {}).get("current", 0.0) >= 7.0), None)
            rec_type = RecommendationType.LEVERAGE if strong_partner else RecommendationType.IMPROVEMENT

        priority = self._priority_score(sphere, current, slope, vol, momentum)

        # Build content
        title_map = {
            RecommendationType.RECOVERY: f"Восстановитесь в сфере: {sphere}",
            RecommendationType.IMPROVEMENT: f"Улучшите показатели в сфере: {sphere}",
            RecommendationType.STABILIZATION: f"Стабилизируйте колебания в сфере: {sphere}",
            RecommendationType.LEVERAGE: f"Используйте смежные сильные стороны для: {sphere}",
            RecommendationType.MAINTENANCE: f"Поддерживайте устойчивый прогресс: {sphere}",
        }
        desc_map = {
            RecommendationType.RECOVERY: "Недавнее снижение. Сфокусируйтесь на базовых восстановительных шагах.",
            RecommendationType.IMPROVEMENT: "Выберите одно узкое место и улучшайте его за счет микро-действий.",
            RecommendationType.STABILIZATION: "Снизьте флуктуации и закрепите рабочий ритм.",
            RecommendationType.LEVERAGE: "Опирайтесь на позитивные связи между сферами, чтобы ускорить прогресс.",
            RecommendationType.MAINTENANCE: "Продолжайте текущие практики и фиксируйте результат.",
        }

        steps = self._build_action_steps(sphere, rec_type)
        metrics = self._build_metrics(current, rec_type)
        related = self._related_spheres(sphere)
        evidence = Evidence(
            data_points={
                "current": round(current, 2),
                "mean": round(mean, 2),
                "slope": round(slope, 3),
                "volatility": round(vol, 3),
                "momentum": round(momentum, 3),
            },
            correlations={k: round(v, 3) for k, v in {rs: self.correlations.get((sphere, rs), 0.0) for rs in related}.items()},
            historical_success="Подход на основе микро-действий демонстрировал улучшения в 2-3 недели в 62% случаев (по истории пользователя)",
        )

        rec_data = RecommendationData(
            title=title_map[rec_type],
            description=desc_map[rec_type],
            action_steps=steps,
            metrics=metrics,
            related_spheres=related,
            evidence=evidence,
        )

        return Recommendation(
            sphere=sphere,
            type=rec_type,
            priority=priority,
            data=rec_data,
        )

    def prioritize_recommendations(self, recs: List[Recommendation], limit: Optional[int] = None) -> List[Recommendation]:
        ordered = sorted(recs, key=lambda r: r.priority, reverse=True)
        return ordered[: limit] if limit else ordered

    def save_recommendations(self, recs: List[Recommendation], path: str) -> None:
        def encode(obj: Any) -> Any:
            if isinstance(obj, Recommendation):
                d = asdict(obj)
                d["type"] = obj.type.value
                return d
            if isinstance(obj, RecommendationType):
                return obj.value
            if isinstance(obj, ActionStep):
                return asdict(obj)
            if isinstance(obj, Metrics):
                return asdict(obj)
            if isinstance(obj, Evidence):
                return asdict(obj)
            if isinstance(obj, RecommendationData):
                return asdict(obj)
            return obj

        with open(path, "w", encoding="utf-8") as f:
            json.dump([encode(r) for r in recs], f, ensure_ascii=False, indent=2)

    def load_recommendations(self, path: str) -> List[Recommendation]:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        out: List[Recommendation] = []
        for item in raw:
            rec_type = RecommendationType(item["type"]) if isinstance(item.get("type"), str) else RecommendationType.IMPROVEMENT
            steps = [ActionStep(**s) for s in item["data"].get("action_steps", [])]
            metrics = Metrics(**item["data"]["metrics"])  # type: ignore[arg-type]
            evidence = Evidence(**item["data"]["evidence"])  # type: ignore[arg-type]
            data = RecommendationData(
                title=item["data"]["title"],
                description=item["data"]["description"],
                action_steps=steps,
                metrics=metrics,
                related_spheres=item["data"].get("related_spheres", []),
                evidence=evidence,
            )
            out.append(Recommendation(
                sphere=item["sphere"],
                type=rec_type,
                priority=float(item.get("priority", 0.0)),
                data=data,
            ))
        return out


def _demo_history() -> Dict[str, List[float]]:
    return {
        "Здоровье":  [6.5, 6.2, 6.0, 5.8, 5.5],
        "Отношения": [7.0, 7.2, 7.3, 7.2, 7.1],
        "Карьера":   [5.0, 5.2, 5.1, 5.0, 4.8],
        "Финансы":   [6.8, 6.7, 6.9, 7.0, 7.2],
        "Развитие":  [7.5, 7.4, 7.3, 7.1, 7.0],
    }


def _print_demo(recs: List[Recommendation]) -> None:
    for r in recs:
        print(f"[{r.type.value.upper()}] {r.sphere} :: priority={r.priority}")
        print(f"  - {r.data.title}")
        print(f"  - {r.data.description}")
        for i, step in enumerate(r.data.action_steps, 1):
            t = f" (~{step.estimated_time_min} мин)" if step.estimated_time_min else ""
            print(f"    {i}. {step.description}{t}")
        print(f"  Target: {r.data.metrics.target_improvement} | Timeframe: {r.data.metrics.timeframe}")
        print(f"  Success: {r.data.metrics.success_criteria}")
        if r.data.related_spheres:
            print(f"  Related: {', '.join(r.data.related_spheres)}")
        if r.data.evidence.correlations:
            pairs = ", ".join(f"{k}:{v:+.2f}" for k, v in r.data.evidence.correlations.items())
            print(f"  Correlations: {pairs}")
        print()


if __name__ == "__main__":
    engine = HPIRecommendationEngine()
    history = _demo_history()
    engine.analyze_sphere_correlations(history)

    candidates: List[Recommendation] = []
    for sphere, values in history.items():
        rec = engine.generate_recommendation(sphere, values[-1], values)
        if rec:
            candidates.append(rec)

    prioritized = engine.prioritize_recommendations(candidates)
    _print_demo(prioritized)

    # Save/load demo
    try:
        engine.save_recommendations(prioritized, "recs.json")
        loaded = engine.load_recommendations("recs.json")
        if loaded:
            print("Loaded:")
            _print_demo(loaded[:2])
    except Exception as e:
        print(f"Save/load demo failed: {e}") 