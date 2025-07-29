import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from psygen.trait.human_abstract_profile import HumanAbstractTraitProfile
from psygen.trait.human_emergent_trait_profile import HumanEmergentTraitProfile


def test_abstract_profile_seed_determinism():
    profile1 = HumanAbstractTraitProfile(seed=42)
    profile2 = HumanAbstractTraitProfile(seed=42)
    assert profile1.to_dict() == profile2.to_dict()


def test_emergent_profile_generation_keys():
    base = HumanAbstractTraitProfile(seed=123)
    emergent = HumanEmergentTraitProfile(base)
    data = emergent.to_dict()
    expected_keys = {
        'Decision-Making Tempo',
        'Agency / Locus of Control',
        'Drive / Ambition',
        'Risk Appetite',
        'Impulse Expression',
        'Tonic Volatility',
        'Emotional Reactivity',
        'Empathy',
        'Attachment Style',
        'Dominance Orientation',
        'Social Boldness',
        'Curiosity / Openness',
        'Inventiveness / Creativity',
        'Strategic Foresight',
        'Adaptability / Resilience',
        'Stress-Coping Efficiency',
        'Norm Orientation',
        'Integrity',
        'Sense of Justice',
        'Value-Anchor Strength',
        'Competence Confidence'
    }
    assert set(data.keys()) == expected_keys
