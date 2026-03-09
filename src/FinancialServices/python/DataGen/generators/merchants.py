from __future__ import annotations

import pandas as pd
from faker import Faker

from DataGen.generators.helpers import weighted_choice


COUNTRIES = ["USA", "CAN", "MEX", "GBR", "DEU", "AUS"]
COUNTRY_WEIGHTS = [0.78, 0.07, 0.05, 0.04, 0.03, 0.03]


def _generate_countries(count: int, rng) -> list[str]:
    countries = rng.choice(COUNTRIES, size=count, p=COUNTRY_WEIGHTS).tolist()
    if count >= len(COUNTRIES):
        for idx, country in enumerate(COUNTRIES[1:], start=1):
            countries[idx] = country
        countries[0] = "USA"
        perm = rng.permutation(count)
        countries = [countries[i] for i in perm]
    return countries


def _generate_merchant_names(count: int, rng) -> list[str]:
    faker = Faker("en_US")
    faker.seed_instance(int(rng.integers(0, 2**31 - 1)))
    return [faker.company() for _ in range(count)]


def generate_merchants(config: dict, rng) -> pd.DataFrame:
    count = config["resolved_counts"]["merchants"]
    behavior = config["behavior"]["merchants"]
    category_weights = behavior["category_weights"]
    risk_weights = behavior["risk_tier_weights"]
    categories = list(category_weights.keys())
    risks = list(risk_weights.keys())

    merchant_ids = pd.Series(range(1, count + 1), name="MerchantId")
    category = weighted_choice(rng, categories, category_weights, count)
    risk_tier = weighted_choice(rng, risks, risk_weights, count)
    alpha = float(behavior.get("popularity_pareto_alpha", 2.0))
    popularity = rng.pareto(alpha, size=count) + 1.0
    merchant_names = _generate_merchant_names(count, rng)
    countries = _generate_countries(count, rng)

    df = pd.DataFrame(
        {
            "MerchantId": merchant_ids,
            "MerchantName": merchant_names,
            "Category": category,
            "RiskTier": risk_tier,
            "PopularityWeight": popularity,
            "Country": countries,
        }
    )
    return df
