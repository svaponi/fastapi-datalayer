import random

from app.domain.attribute.benefit import BenefitBasis, BenefitJurisdiction
from app.domain.attribute.tax import TaxBasis, TaxJurisdiction
from app.domain.attribute.time_adjustment import (
    TimeAdjustmentBasis,
    TimeAdjustmentJurisdiction,
)


def random_tax(i):
    return dict(
        title=f"test tax {i}",
        value=random.random() * 100,
        basis=random.choice(list(TaxBasis)),
        jurisdiction=random.choice(list(TaxJurisdiction)),
    )


def random_benefit(i):
    return dict(
        title=f"test benefit {i}",
        value=random.random() * 100,
        basis=random.choice(list(BenefitBasis)),
        jurisdiction=random.choice(list(BenefitJurisdiction)),
    )


def random_time_adjustment(i):
    return dict(
        title=f"test time-adjustments {i}",
        value=random.random() * 100,
        basis=random.choice(list(TimeAdjustmentBasis)),
        jurisdiction=random.choice(list(TimeAdjustmentJurisdiction)),
    )
