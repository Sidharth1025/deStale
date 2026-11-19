"""
deStale - Configuration Management Module
Loads settings from environment variables and provides sensible defaults
for Bifrost AI Gateway, Tavily Search API, and application behavior.
"""

import os
import streamlit as st
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

def get_setting(name, default=""):
    value = os.getenv(name)

    if value:
        return value

    try:
        return st.secrets.get(name, default)
    except Exception:
        return default
# Load .env if present
load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """Application configuration container."""

    # Project Information
    APP_NAME: str = "deStale"
    APP_TAGLINE: str = "Instant AI Freshness & Stale-Answer Detection Engine"
    APP_VERSION: str = "1.1.0"

    # Bifrost AI Gateway Configuration
    # Bifrost documentation: https://github.com/maximhq/bifrost
    # Default local Bifrost gateway runs on port 8080 or can point to custom proxy/hosted endpoint
   # Bifrost Configuration
    BIFROST_BASE_URL: str = get_setting(
        "BIFROST_BASE_URL", "http://localhost:8080/v1"
    )
    BIFROST_API_KEY: str = get_setting("BIFROST_API_KEY") or get_setting("OPENAI_API_KEY")
    BIFROST_MODEL: str = get_setting("BIFROST_MODEL", "openai/gpt-oss-20b")
    BIFROST_TIMEOUT: int = int(get_setting("BIFROST_TIMEOUT", "45"))
    BIFROST_MAX_RETRIES: int = int(get_setting("BIFROST_MAX_RETRIES", "3"))

    # Tavily Configuration
    TAVILY_API_KEY: str = get_setting("TAVILY_API_KEY")
    TAVILY_SEARCH_DEPTH: str = get_setting("TAVILY_SEARCH_DEPTH", "advanced")
    TAVILY_MAX_RESULTS: int = int(get_setting("TAVILY_MAX_RESULTS", "5"))
    TAVILY_TIMEOUT: int = int(get_setting("TAVILY_TIMEOUT", "20"))
    TAVILY_MAX_RETRIES: int = int(get_setting("TAVILY_MAX_RETRIES", "3"))

    # Processing Boundaries & Security
    MAX_INPUT_LENGTH: int = 12000  # Character limit for submitted AI text
    MIN_INPUT_LENGTH: int = 15     # Minimum chars for sensible extraction
    MAX_CLAIMS_TO_PROCESS: int = 10  # Maximum claims per run to conserve API quota and time

    # Freshness Heuristic Thresholds (0 - 100)
    SCORE_VERIFIED_BASE: float = 100.0
    SCORE_OUTDATED_BASE: float = 15.0
    SCORE_CONTRADICTED_BASE: float = 0.0
    SCORE_UNCERTAIN_BASE: float = 45.0
    SCORE_INSUFFICIENT_BASE: float = 50.0

    # Demo / Fallback Mode
    # If True or if API credentials are missing, enables interactive demo mode with curated real-world examples
    DEMO_MODE_DEFAULT: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

    @property
    def has_bifrost_credentials(self) -> bool:
        """Checks whether Bifrost base URL is defined."""
        return bool(self.BIFROST_BASE_URL)

    @property
    def has_tavily_credentials(self) -> bool:
        """Checks whether Tavily API Key is present."""
        return bool(self.TAVILY_API_KEY and self.TAVILY_API_KEY.strip())


# Singleton config instance
config = AppConfig()
