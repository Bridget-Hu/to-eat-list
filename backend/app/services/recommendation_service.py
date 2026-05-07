from dataclasses import dataclass
from datetime import datetime, timezone
from math import inf

from app.services.recommendation_rules import (
    AVOID_KEYWORD_EXPANSIONS,
    BUDGET_CONTROL_PRICE_RATIO,
    DEFAULT_HEALTH_GOAL,
    HEALTH_GOAL_ALIASES,
    HEALTH_GOAL_RULES,
    KEYWORD_SYNONYMS,
    MAX_RECOMMENDATIONS,
    MEAL_BUDGET_SHARE,
    MEAL_TYPE_KEYWORDS,
    MILK_TEA_KEYWORDS,
    MIN_RECOMMENDABLE_SCORE,
    SCORE_WEIGHTS,
    SEVERE_AVOID_KEYWORDS,
)
from app.utils.keyword_normalizer import normalize_keywords


FOOD_TEXT_FIELDS = (
    "name",
    "store",
    "category",
    "taste_tags",
    "taste",
    "health_tags",
    "tags",
    "note",
)

MEAL_TYPES = ("早餐", "午餐", "晚餐")


@dataclass(frozen=True)
class RecommendationContext:
    budget: float
    taste_keywords: list[str]
    avoid_keywords: list[str]
    health_goal: str
    craving_keywords: list[str]
    has_milk_tea: bool


def _unique_keywords(keywords):
    result = []
    seen = set()

    for keyword in keywords:
        if keyword and keyword not in seen:
            seen.add(keyword)
            result.append(keyword)

    return result


def normalize_health_goal(goal):
    cleaned = str(goal or "").strip()
    mapped_goal = HEALTH_GOAL_ALIASES.get(cleaned, cleaned)

    if mapped_goal not in HEALTH_GOAL_RULES:
        return DEFAULT_HEALTH_GOAL

    return mapped_goal


def expand_avoid_keywords(keywords):
    expanded = []

    for keyword in keywords:
        expanded.append(keyword)
        expanded.extend(normalize_keywords(
            AVOID_KEYWORD_EXPANSIONS.get(keyword, []),
            KEYWORD_SYNONYMS,
        ))

    return _unique_keywords(expanded)


def build_context(data):
    budget = getattr(data, "budget", 60)

    if budget is None:
        budget = 60

    taste_keywords = normalize_keywords(getattr(data, "taste", ""), KEYWORD_SYNONYMS)
    avoid_keywords = normalize_keywords(getattr(data, "dislike", ""), KEYWORD_SYNONYMS)
    craving_keywords = normalize_keywords(getattr(data, "want", ""), KEYWORD_SYNONYMS)

    return RecommendationContext(
        budget=float(budget or 0),
        taste_keywords=taste_keywords,
        avoid_keywords=expand_avoid_keywords(avoid_keywords),
        health_goal=normalize_health_goal(getattr(data, "goal", "")),
        craving_keywords=craving_keywords,
        has_milk_tea=bool(getattr(data, "hadMilkTea", False)),
    )


def food_text(food):
    return " ".join(str(food.get(field) or "") for field in FOOD_TEXT_FIELDS).lower()


def _all_rule_keywords():
    keywords = set(KEYWORD_SYNONYMS.keys()) | set(KEYWORD_SYNONYMS.values())
    keywords.update(MILK_TEA_KEYWORDS)
    keywords.update(SEVERE_AVOID_KEYWORDS)

    for rule in HEALTH_GOAL_RULES.values():
        keywords.update(rule.get("positive", []))
        keywords.update(rule.get("negative", []))

    for meal_keywords in MEAL_TYPE_KEYWORDS.values():
        keywords.update(meal_keywords)

    return tuple(sorted((keyword for keyword in keywords if keyword), key=len, reverse=True))


ALL_RULE_KEYWORDS = _all_rule_keywords()


def food_keywords(food):
    raw_text = food_text(food)
    keywords = []

    for field in FOOD_TEXT_FIELDS:
        keywords.extend(normalize_keywords(food.get(field), KEYWORD_SYNONYMS))

    # Tags and notes may contain descriptive phrases instead of clean tags.
    # Infer known rule keywords from the full text to keep matching stable.
    for keyword in ALL_RULE_KEYWORDS:
        if keyword.lower() in raw_text:
            keywords.extend(normalize_keywords(keyword, KEYWORD_SYNONYMS))

    return set(keywords)


def _find_matches(raw_text, keyword_set, target_keywords, synonym_map=KEYWORD_SYNONYMS):
    matches = []

    for keyword in target_keywords:
        normalized = normalize_keywords(keyword, synonym_map)
        candidate = normalized[0] if normalized else keyword

        if candidate in keyword_set or candidate in raw_text:
            matches.append(candidate)

    return _unique_keywords(matches)


def _limited_score(weight, matches, per_match_ratio):
    if not matches:
        return 0

    return min(weight, round(weight * per_match_ratio * len(matches), 2))


def _budget_target(context, meal_type=None):
    if context.budget <= 0:
        return 0

    if meal_type in MEAL_BUDGET_SHARE:
        return context.budget * MEAL_BUDGET_SHARE[meal_type]

    return context.budget


def _score_budget(food, context, meal_type):
    price = food.get("price")
    target_budget = _budget_target(context, meal_type)

    if price is None or target_budget <= 0:
        return 0, inf, []

    price = float(price)
    ratio = price / target_budget
    distance = abs(target_budget - price)
    weight = SCORE_WEIGHTS["budget"]

    if ratio <= 0.5:
        return round(weight * 0.25, 2), distance, ["价格明显低于预算，获得少量加分"]

    if ratio <= 0.85:
        return round(weight * 0.6, 2), distance, ["价格在预算范围内"]

    if ratio <= 1:
        return weight, distance, ["价格接近预算且未超出"]

    if ratio <= 1.25:
        return -round(weight * 0.45, 2), distance, ["价格略超预算，已小幅降分"]

    if ratio <= 1.6:
        return -weight, distance, ["价格超出预算较多，已明显降分"]

    return -round(weight * 1.5, 2), distance, ["价格远超预算，已强烈降分"]


def _score_avoid(context, raw_text, keyword_set):
    matches = _find_matches(raw_text, keyword_set, context.avoid_keywords)

    if not matches:
        return 0, False, []

    severe_matches = [keyword for keyword in matches if keyword in SEVERE_AVOID_KEYWORDS]

    if severe_matches:
        return (
            SCORE_WEIGHTS["avoid_exclusion"],
            True,
            [f"命中严重忌口，已排除：{'、'.join(severe_matches)}"],
        )

    penalty = SCORE_WEIGHTS["avoid_penalty"] * len(matches)
    return penalty, False, [f"命中忌口关键词，已强烈降分：{'、'.join(matches)}"]


def _score_taste(context, raw_text, keyword_set):
    matches = _find_matches(raw_text, keyword_set, context.taste_keywords)
    score = _limited_score(SCORE_WEIGHTS["taste"], matches, 0.5)
    reasons = [f"命中口味偏好：{'、'.join(matches)}"] if matches else []

    return score, reasons


def _score_craving(context, raw_text, keyword_set):
    matches = _find_matches(raw_text, keyword_set, context.craving_keywords)
    score = _limited_score(SCORE_WEIGHTS["craving"], matches, 0.6)
    reasons = [f"命中今天想吃：{'、'.join(matches)}"] if matches else []

    return score, reasons


def _score_health(context, food, raw_text, keyword_set, target_budget):
    goal = context.health_goal

    if goal == DEFAULT_HEALTH_GOAL:
        return 0, []

    rule = HEALTH_GOAL_RULES.get(goal, {})
    positive_keywords = normalize_keywords(rule.get("positive", []), KEYWORD_SYNONYMS)
    negative_keywords = normalize_keywords(rule.get("negative", []), KEYWORD_SYNONYMS)
    positive_matches = _find_matches(raw_text, keyword_set, positive_keywords)
    negative_matches = _find_matches(raw_text, keyword_set, negative_keywords)
    score = 0
    reasons = []

    if positive_matches:
        score += _limited_score(SCORE_WEIGHTS["health"], positive_matches, 0.5)
        reasons.append(f"符合健康目标：{goal}（{'、'.join(positive_matches)}）")

    if negative_matches:
        score -= _limited_score(SCORE_WEIGHTS["health"], negative_matches, 0.4)
        reasons.append(f"与健康目标稍冲突：{'、'.join(negative_matches)}")

    price = food.get("price")

    if goal == "控制预算" and price is not None and target_budget > 0:
        if float(price) <= target_budget * BUDGET_CONTROL_PRICE_RATIO:
            score += round(SCORE_WEIGHTS["health"] * 0.5, 2)

            if not positive_matches:
                reasons.append("符合健康目标：控制预算")

    return score, reasons


def _score_milk_tea(context, raw_text, keyword_set):
    milk_tea_keywords = normalize_keywords(MILK_TEA_KEYWORDS, KEYWORD_SYNONYMS)
    matches = _find_matches(raw_text, keyword_set, milk_tea_keywords)

    if not matches:
        return 0, []

    if context.has_milk_tea:
        return (
            -SCORE_WEIGHTS["milk_tea"],
            ["已喝奶茶，自动降低饮品类推荐"],
        )

    return (
        -round(SCORE_WEIGHTS["milk_tea"] * 0.3, 2),
        ["饮品/甜品类轻微降权，避免过度占据推荐"],
    )


def _score_meal_type(food, meal_type, raw_text, keyword_set):
    if not meal_type:
        return 0, []

    score = 0
    reasons = []
    category = str(food.get("category") or "").lower()

    if meal_type in category:
        score += round(SCORE_WEIGHTS["meal_type"] * 1.5, 2)
        reasons.append(f"分类匹配{meal_type}")

    meal_keywords = normalize_keywords(MEAL_TYPE_KEYWORDS.get(meal_type, []), {})
    matches = _find_matches(raw_text, keyword_set, meal_keywords, {})

    if matches:
        score += min(SCORE_WEIGHTS["meal_type"], round(SCORE_WEIGHTS["meal_type"] * 0.5 * len(matches), 2))
        reasons.append(f"适合{meal_type}：{'、'.join(matches)}")

    return score, reasons


def score_food(food, context, meal_type=None):
    raw_text = food_text(food)
    keyword_set = food_keywords(food)
    score = 0
    reasons = []

    avoid_score, excluded, avoid_reasons = _score_avoid(context, raw_text, keyword_set)
    score += avoid_score
    reasons.extend(avoid_reasons)

    if excluded:
        return {
            "food": food,
            "score": score,
            "budget_distance": inf,
            "reasons": reasons,
            "excluded": True,
        }

    budget_score, budget_distance, budget_reasons = _score_budget(food, context, meal_type)
    target_budget = _budget_target(context, meal_type)
    score += budget_score
    reasons.extend(budget_reasons)

    meal_score, meal_reasons = _score_meal_type(food, meal_type, raw_text, keyword_set)
    score += meal_score
    reasons.extend(meal_reasons)

    taste_score, taste_reasons = _score_taste(context, raw_text, keyword_set)
    score += taste_score
    reasons.extend(taste_reasons)

    craving_score, craving_reasons = _score_craving(context, raw_text, keyword_set)
    score += craving_score
    reasons.extend(craving_reasons)

    health_score, health_reasons = _score_health(
        context,
        food,
        raw_text,
        keyword_set,
        target_budget,
    )
    score += health_score
    reasons.extend(health_reasons)

    milk_tea_score, milk_tea_reasons = _score_milk_tea(context, raw_text, keyword_set)
    score += milk_tea_score
    reasons.extend(milk_tea_reasons)

    if not reasons:
        reasons.append("根据基础规则稳定排序")

    return {
        "food": food,
        "score": round(score, 2),
        "budget_distance": budget_distance,
        "reasons": reasons,
        "excluded": False,
    }


def _rank_scored_foods(scored_foods):
    return sorted(
        (item for item in scored_foods if not item["excluded"]),
        key=lambda item: (
            -item["score"],
            item["budget_distance"],
            item["food"].get("id") or inf,
        ),
    )


def _recommendation_payload(scored_food):
    food = scored_food["food"]

    return {
        "food_id": food.get("id"),
        "name": food.get("name") or "",
        "store": food.get("store") or "",
        "price": food.get("price"),
        "category": food.get("category") or "",
        "score": scored_food["score"],
        "reasons": scored_food["reasons"],
    }


def _reason_text(reasons):
    if not reasons:
        return "根据基础规则稳定排序。"

    return "；".join(reasons) + "。"


def _empty_meal_payload(meal_type):
    reasons = [
        f"暂无符合条件的{meal_type}菜品",
        "可以尝试放宽预算、减少忌口，或先导入更多菜品",
    ]

    return {
        "type": meal_type,
        "name": f"暂无合适{meal_type}",
        "reason": _reason_text(reasons),
        "price": None,
        "food_id": None,
        "store": "",
        "category": "",
        "score": None,
        "reasons": reasons,
    }


def _meal_payload(meal_type, scored_food):
    if scored_food is None:
        return _empty_meal_payload(meal_type)

    payload = _recommendation_payload(scored_food)

    return {
        "type": meal_type,
        "name": payload["name"],
        "reason": _reason_text(payload["reasons"]),
        "price": payload["price"],
        "food_id": payload["food_id"],
        "store": payload["store"],
        "category": payload["category"],
        "score": payload["score"],
        "reasons": payload["reasons"],
    }


def _choose_meal_food(foods, context, meal_type, used_ids):
    scored_foods = [
        score_food(food, context, meal_type)
        for food in foods
        if food.get("id") not in used_ids
    ]
    ranked_foods = _rank_scored_foods(scored_foods)

    if not ranked_foods:
        return None

    best_food = ranked_foods[0]

    if best_food["score"] <= MIN_RECOMMENDABLE_SCORE:
        return None

    food_id = best_food["food"].get("id")

    if food_id is not None:
        used_ids.add(food_id)

    return best_food


def generate_recommendations(data, foods):
    context = build_context(data)
    generated_at = datetime.now(timezone.utc).isoformat()
    scored_foods = [score_food(food, context) for food in foods]
    ranked_foods = _rank_scored_foods(scored_foods)
    recommendations = [
        _recommendation_payload(scored_food)
        for scored_food in ranked_foods[:MAX_RECOMMENDATIONS]
    ]
    used_ids = set()
    meals = [
        _meal_payload(meal_type, _choose_meal_food(foods, context, meal_type, used_ids))
        for meal_type in MEAL_TYPES
    ]
    total_price = round(sum(meal["price"] or 0 for meal in meals), 2)
    remaining_budget = round(context.budget - total_price, 2)

    if recommendations:
        summary = (
            f"本次推荐基于已导入的 {len(foods)} 个菜品生成，"
            f"健康目标为“{context.health_goal}”，"
            f"预计总价约 {total_price} 元，预算为 {context.budget} 元，"
            f"结余约 {remaining_budget} 元。"
            "排序已综合预算、口味、忌口、健康目标、今天想吃和奶茶状态。"
        )
    else:
        summary = (
            "暂无符合条件的菜品。"
            "可以尝试放宽预算、减少忌口，或先导入更多菜品。"
        )

    return {
        "budget": context.budget,
        "summary": summary,
        "totalPrice": total_price,
        "total_estimated_price": total_price,
        "remainingBudget": remaining_budget,
        "generated_at": generated_at,
        "meals": meals,
        "recommendations": recommendations,
    }


def build_recommendation(data, foods):
    return generate_recommendations(data, foods)
