"""
Unit tests för Loggamera Integration
Visar hur man testar async Home Assistant components
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import timedelta

# Mock Home Assistant modules for testing
import sys
sys.modules['homeassistant'] = Mock()
sys.modules['homeassistant.components'] = Mock()
sys.modules['homeassistant.components.sensor'] = Mock()
sys.modules['homeassistant.const'] = Mock()
sys.modules['homeassistant.helpers'] = Mock()
sys.modules['homeassistant.helpers.aiohttp_client'] = Mock()
sys.modules['homeassistant.helpers.entity'] = Mock()
sys.modules['homeassistant.helpers.config_validation'] = Mock()
sys.modules['homeassistant.helpers.update_coordinator'] = Mock()
sys.modules['homeassistant.config_entries'] = Mock()
sys.modules['homeassistant.core'] = Mock()
sys.modules['voluptuous'] = Mock()
sys.modules['aiohttp'] = Mock()

# Import after mocking
from loggamera_integration_v2 import (
    LoggameraApiClient,
    LoggameraDataParser,
    LoggameraDataUpdateCoordinator,
    SENSOR_TYPES
)

class TestLoggameraApiClient:
    """Test API client functionality."""
    
    @pytest.fixture
    def api_client(self):
        session = AsyncMock()
        return LoggameraApiClient(session)
    
    @pytest.mark.asyncio
    async def test_fetch_data_success(self, api_client):
        """Test successful data fetching."""
        # Setup mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '<div data-value="15.5">Temperature</div>'
        
        api_client.session.post.return_value.__aenter__.return_value = mock_response
        
        # Test
        result = await api_client.fetch_data(22)
        
        # Verify
        assert result == '<div data-value="15.5">Temperature</div>'
        api_client.session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_fetch_data_retry_on_failure(self, api_client):
        """Test retry logic on failures."""
        # Setup mock to fail twice, succeed third time
        mock_response = AsyncMock()
        mock_response.status = 500
        
        mock_success_response = AsyncMock()
        mock_success_response.status = 200
        mock_success_response.text.return_value = '<div data-value="16.2">Temperature</div>'
        
        api_client.session.post.return_value.__aenter__.side_effect = [
            mock_response,  # First attempt fails
            mock_response,  # Second attempt fails
            mock_success_response  # Third attempt succeeds
        ]
        
        # Mock sleep to speed up test
        with patch('asyncio.sleep', return_value=None):
            result = await api_client.fetch_data(22)
        
        # Verify retry happened and succeeded
        assert result == '<div data-value="16.2">Temperature</div>'
        assert api_client.session.post.call_count == 3

class TestLoggameraDataParser:
    """Test data parsing functionality."""
    
    def test_parse_temperature_success(self):
        """Test successful temperature parsing."""
        html = '<div class="temp" data-value="18.7">Current Temperature</div>'
        
        result = LoggameraDataParser.parse_sensor_data(html, "temperature")
        
        assert result == 18.7
    
    def test_parse_temperature_multiple_values(self):
        """Test parsing when multiple values exist - should return first valid."""
        html = '''
        <div data-value="999">Invalid high value</div>
        <div data-value="19.3">Valid temperature</div>
        <div data-value="20.1">Another valid value</div>
        '''
        
        result = LoggameraDataParser.parse_sensor_data(html, "temperature")
        
        assert result == 19.3
    
    def test_parse_temperature_out_of_range(self):
        """Test handling of out-of-range values."""
        html = '<div data-value="999">Invalid temperature</div>'
        
        result = LoggameraDataParser.parse_sensor_data(html, "temperature")
        
        assert result is None
    
    def test_parse_temperature_no_match(self):
        """Test handling when no temperature data found."""
        html = '<div>No temperature data here</div>'
        
        result = LoggameraDataParser.parse_sensor_data(html, "temperature")
        
        assert result is None
    
    def test_parse_unknown_sensor_type(self):
        """Test handling of unknown sensor types."""
        html = '<div data-value="25">Some value</div>'
        
        result = LoggameraDataParser.parse_sensor_data(html, "pressure")
        
        assert result is None

class TestLoggameraDataUpdateCoordinator:
    """Test coordinator functionality."""
    
    @pytest.fixture
    def mock_hass(self):
        return Mock()
    
    @pytest.fixture
    def mock_api_client(self):
        return AsyncMock(spec=LoggameraApiClient)
    
    @pytest.fixture
    def coordinator(self, mock_hass, mock_api_client):
        with patch('loggamera_integration_v2.DataUpdateCoordinator.__init__'):
            return LoggameraDataUpdateCoordinator(
                mock_hass, mock_api_client, 22, "temperature"
            )
    
    @pytest.mark.asyncio
    async def test_update_data_success(self, coordinator, mock_api_client):
        """Test successful data update."""
        # Setup
        mock_api_client.fetch_data.return_value = '<div data-value="17.8">Temp</div>'
        coordinator.parser = LoggameraDataParser()
        
        # Test
        result = await coordinator._async_update_data()
        
        # Verify
        assert result == 17.8
        assert coordinator._cached_data == 17.8
        assert coordinator._last_successful_update is not None
    
    @pytest.mark.asyncio
    async def test_update_data_uses_cache_on_parse_failure(self, coordinator, mock_api_client):
        """Test fallback to cached data when parsing fails."""
        # Setup - set cached data
        coordinator._cached_data = 16.5
        coordinator._last_successful_update = Mock()
        coordinator._last_successful_update.total_seconds = Mock(return_value=300)  # 5 min ago
        
        # Mock current time calculation
        with patch('loggamera_integration_v2.datetime') as mock_datetime:
            mock_now = Mock()
            mock_datetime.now.return_value = mock_now
            mock_now.__sub__.return_value.total_seconds.return_value = 300
            
            # Setup API to return unparseable data
            mock_api_client.fetch_data.return_value = '<div>No valid data</div>'
            coordinator.parser = LoggameraDataParser()
            
            # Test
            result = await coordinator._async_update_data()
            
            # Verify cached data is returned
            assert result == 16.5

class TestSensorConfiguration:
    """Test sensor type configurations."""
    
    def test_sensor_types_defined(self):
        """Test that required sensor types are defined."""
        assert "temperature" in SENSOR_TYPES
        assert "humidity" in SENSOR_TYPES
    
    def test_temperature_config_valid(self):
        """Test temperature sensor configuration."""
        config = SENSOR_TYPES["temperature"]
        
        assert config.name == "Temperature"
        assert config.unit == "°C"  # Assuming TEMP_CELSIUS maps to this
        assert config.device_class == "temperature"
        assert config.validation_range == (-5, 40)
    
    def test_humidity_config_valid(self):
        """Test humidity sensor configuration."""
        config = SENSOR_TYPES["humidity"]
        
        assert config.name == "Humidity"
        assert config.unit == "%"
        assert config.device_class == "humidity"
        assert config.validation_range == (0, 100)

# Integration test
class TestEndToEndFlow:
    """Test complete integration flow."""
    
    @pytest.mark.asyncio
    async def test_complete_temperature_flow(self):
        """Test complete flow from API call to parsed result."""
        # Setup
        session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '''
        <html>
            <div class="sensor-data">
                <span data-value="19.4">Vättern Temperature</span>
            </div>
        </html>
        '''
        session.post.return_value.__aenter__.return_value = mock_response
        
        # Create client and test
        client = LoggameraApiClient(session)
        html = await client.fetch_data(22)
        temperature = LoggameraDataParser.parse_sensor_data(html, "temperature")
        
        # Verify
        assert temperature == 19.4

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 