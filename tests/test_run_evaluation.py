import pytest
from ai_evaluation.run_evaluation import AIEvaluator

def test_aievaluator_initialization():
    """Test that the AIEvaluator class can be initialized."""
    evaluator = AIEvaluator()
    assert evaluator is not None
