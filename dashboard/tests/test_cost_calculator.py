"""
Tests for Cost Calculator

Run with:
    cd dashboard
    source venv/bin/activate
    python -m pytest tests/test_cost_calculator.py -v
"""

import pytest
import sys
from pathlib import Path

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

from cost_calculator import CostCalculator


class TestCostCalculator:
    """Test suite for CostCalculator class."""
    
    @pytest.fixture
    def calculator(self):
        """Create a calculator instance for tests."""
        return CostCalculator()
    
    def test_calculator_initialization(self, calculator):
        """Test that calculator initializes correctly."""
        assert calculator is not None
        assert calculator.providers is not None
        assert calculator.limits is not None
    
    def test_local_rendering_cost(self, calculator):
        """Test local GPU rendering cost calculation."""
        cost = calculator.estimate_cost(
            provider='local',
            count=1
        )
        
        assert cost['provider'] == 'local'
        assert cost['count'] == 1
        assert cost['total'] > 0
        assert cost['per_image'] == cost['total']
        
        # Local should be very cheap (GPU time only)
        assert cost['per_image'] < 0.01  # Less than 1 cent per image
    
    def test_stability_ai_cost(self, calculator):
        """Test Stability AI API cost calculation."""
        cost = calculator.estimate_cost(
            provider='stability',
            resolution='1024x1024',
            steps=50,
            model='sdxl',
            count=10
        )
        
        assert cost['provider'] == 'stability'
        assert cost['count'] == 10
        assert cost['total'] == cost['per_image'] * 10
        
        # Should have breakdown
        assert 'breakdown' in cost
        assert cost['breakdown']['type'] == 'api'
    
    def test_dreamstudio_cost(self, calculator):
        """Test DreamStudio API cost calculation."""
        cost = calculator.estimate_cost(
            provider='dreamstudio',
            resolution='512x512',
            steps=30,
            model='sd_1_5',
            count=1
        )
        
        assert cost['provider'] == 'dreamstudio'
        assert cost['total'] > 0
    
    def test_resolution_scaling(self, calculator):
        """Test that higher resolutions cost more."""
        cost_512 = calculator.estimate_cost(
            provider='stability',
            resolution='512x512',
            steps=30,
            model='sd_1_5',
            count=1
        )
        
        cost_1024 = calculator.estimate_cost(
            provider='stability',
            resolution='1024x1024',
            steps=30,
            model='sd_1_5',
            count=1
        )
        
        cost_2048 = calculator.estimate_cost(
            provider='stability',
            resolution='2048x2048',
            steps=30,
            model='sd_1_5',
            count=1
        )
        
        # Higher resolution should cost more
        assert cost_1024['per_image'] > cost_512['per_image']
        assert cost_2048['per_image'] > cost_1024['per_image']
    
    def test_model_scaling(self, calculator):
        """Test that more advanced models cost more."""
        cost_sd15 = calculator.estimate_cost(
            provider='stability',
            resolution='1024x1024',
            steps=30,
            model='sd_1_5',
            count=1
        )
        
        cost_sdxl = calculator.estimate_cost(
            provider='stability',
            resolution='1024x1024',
            steps=30,
            model='sdxl',
            count=1
        )
        
        # SDXL should cost more than SD 1.5
        assert cost_sdxl['per_image'] > cost_sd15['per_image']
    
    def test_batch_scaling(self, calculator):
        """Test that batch count scales cost correctly."""
        cost_1 = calculator.estimate_cost(
            provider='stability',
            resolution='1024x1024',
            steps=30,
            model='sdxl',
            count=1
        )
        
        cost_100 = calculator.estimate_cost(
            provider='stability',
            resolution='1024x1024',
            steps=30,
            model='sdxl',
            count=100
        )
        
        # 100 images should cost 100x more
        assert abs(cost_100['total'] - (cost_1['total'] * 100)) < 0.01
        assert cost_100['per_image'] == cost_1['per_image']
    
    def test_cost_validation_safe(self, calculator):
        """Test cost validation for safe amounts."""
        is_safe, message = calculator.validate_cost(10.0)
        
        assert is_safe is True
        assert "safe" in message.lower()
    
    def test_cost_validation_warning(self, calculator):
        """Test cost validation for warning threshold."""
        # Default warning is $50
        is_safe, message = calculator.validate_cost(60.0)
        
        assert is_safe is True  # Still valid, just warning
        assert "warning" in message.lower()
    
    def test_cost_validation_exceeded(self, calculator):
        """Test cost validation for exceeded limits."""
        # Default max is $100
        is_safe, message = calculator.validate_cost(150.0)
        
        assert is_safe is False
        assert "exceed" in message.lower()
    
    def test_cost_validation_custom_limit(self, calculator):
        """Test cost validation with custom limit."""
        is_safe, message = calculator.validate_cost(30.0, max_cost=25.0)
        
        assert is_safe is False
        assert "25.00" in message
    
    def test_unknown_provider_raises_error(self, calculator):
        """Test that unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            calculator.estimate_cost(provider='invalid_provider')
    
    def test_list_providers(self, calculator):
        """Test listing available providers."""
        providers = calculator.list_providers()
        
        assert len(providers) >= 3  # local, stability, dreamstudio
        assert any(p['id'] == 'local' for p in providers)
        assert any(p['id'] == 'stability' for p in providers)
    
    def test_get_resolutions(self, calculator):
        """Test getting available resolutions."""
        resolutions = calculator.get_resolutions('stability')
        
        assert '512x512' in resolutions
        assert '1024x1024' in resolutions
        assert '2048x2048' in resolutions
    
    def test_get_models(self, calculator):
        """Test getting available models."""
        models = calculator.get_models('stability')
        
        assert len(models) > 0
        assert any(m['id'] == 'sdxl' for m in models)
    
    def test_get_provider_info(self, calculator):
        """Test getting provider information."""
        info = calculator.get_provider_info('stability')
        
        assert 'name' in info
        assert 'description' in info
        assert info['name'] == 'Stability AI'
    
    def test_realistic_batch_cost(self, calculator):
        """Test realistic batch rendering scenario."""
        # Scenario: 500 images, 1024x1024, SDXL, 50 steps
        cost = calculator.estimate_cost(
            provider='stability',
            resolution='1024x1024',
            steps=50,
            model='sdxl',
            count=500
        )
        
        # Should be reasonably priced
        assert cost['total'] > 5.0  # At least $5
        assert cost['total'] < 100.0  # But not crazy expensive
        
        # Validate against limits - should be valid
        is_safe, message = calculator.validate_cost(cost['total'])
        assert is_safe is True  # $8.25 is reasonable!


class TestCostCalculatorEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def calculator(self):
        return CostCalculator()
    
    def test_zero_count(self, calculator):
        """Test with zero images."""
        cost = calculator.estimate_cost(
            provider='local',
            count=0
        )
        
        assert cost['total'] == 0.0
        assert cost['count'] == 0
    
    def test_very_large_batch(self, calculator):
        """Test with very large batch (should trigger validation)."""
        cost = calculator.estimate_cost(
            provider='stability',
            resolution='2048x2048',
            steps=100,
            model='sdxl',
            count=10000  # 10,000 images!
        )
        
        # Should be very expensive
        assert cost['total'] > 100.0
        
        # Validation should fail
        is_safe, message = calculator.validate_cost(cost['total'])
        assert is_safe is False


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])

