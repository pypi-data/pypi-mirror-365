"""
Common data models for LogSentinelAI
Shared Pydantic models for structured data across all analyzers
"""
from pydantic import BaseModel, Field
from typing import Optional

class GeoIPInfo(BaseModel):
    """GeoIP information for an IP address"""
    ip: str = Field(description="IP address")
    country_code: str = Field(description="ISO country code (e.g., 'US', 'KR', 'UNKNOWN', 'PRIVATE')")
    country_name: str = Field(description="Full country name (e.g., 'United States', 'South Korea', 'Private IP')")
    city: Optional[str] = Field(default=None, description="City name (only available with GeoLite2-City database)")
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate (only available with GeoLite2-City database)")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate (only available with GeoLite2-City database)")

class IPStatistic(BaseModel):
    """IP address with count and GeoIP information"""
    ip: str = Field(description="IP address")
    country_code: str = Field(description="ISO country code")
    country_name: str = Field(description="Full country name")
    city: Optional[str] = Field(default=None, description="City name")
    latitude: Optional[float] = Field(default=None, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, description="Longitude coordinate")
    count: int = Field(description="Request/event count for this IP")
