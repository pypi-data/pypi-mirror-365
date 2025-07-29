import time
import pytest
from vkb_lib.core import VKBGranule, ResourceContract, ExecutionStats

class TestGranule(VKBGranule):
    def execute(self, data):
        return data * 2

def test_granule_execution():
    granule = TestGranule(name="TestGranule", contract=ResourceContract())
    result = granule._execute_wrapper(5)
    assert result == 10
    assert granule.stats.success is True
    assert granule.stats.start_time > 0
    assert granule.stats.end_time > granule.stats.start_time

def test_granule_error_handling():
    class ErrorGranule(VKBGranule):
        def execute(self, data):
            raise ValueError("Test error")
    
    granule = ErrorGranule(name="ErrorGranule")
    with pytest.raises(ValueError):
        granule._execute_wrapper("data")
    
    # Проверим, что ошибка записана в статистику
    assert granule.stats.error is not None
    assert "Test error" in str(granule.stats.error)