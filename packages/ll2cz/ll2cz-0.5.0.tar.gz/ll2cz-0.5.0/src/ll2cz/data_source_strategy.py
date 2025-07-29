# SPDX-FileCopyrightText: Copyright (c), CloudZero, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Strategy pattern implementation for handling different data sources."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import polars as pl
from rich.console import Console

from .database import LiteLLMDatabase
from .cached_database import CachedLiteLLMDatabase
from .date_utils import DateParser

console = Console()


class DataSourceStrategy(ABC):
    """Abstract base class for data source strategies."""
    
    @abstractmethod
    def get_data(self, database: LiteLLMDatabase, 
                 date_filter: Optional[Dict[str, str]] = None,
                 limit: Optional[int] = None) -> pl.DataFrame:
        """Fetch data from the specific source.
        
        Args:
            database: Database connection object
            date_filter: Optional dict with 'start_date' and 'end_date' keys
            limit: Optional limit on number of records
            
        Returns:
            Polars DataFrame with the fetched data
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Get human-readable source name."""
        pass
    
    @abstractmethod
    def get_table_name(self) -> str:
        """Get the database table name."""
        pass


class UserTableStrategy(DataSourceStrategy):
    """Strategy for fetching data from the LiteLLMSpendCalculator table."""
    
    def get_data(self, database: LiteLLMDatabase,
                 date_filter: Optional[Dict[str, str]] = None,
                 limit: Optional[int] = None) -> pl.DataFrame:
        """Fetch data from user table with optional filtering."""
        if date_filter:
            console.print(f"[blue]Fetching {date_filter['description']} from user table...[/blue]")
            return database.get_usage_data(
                start_date=date_filter['start_date'],
                end_date=date_filter['end_date'],
                limit=limit
            )
        else:
            console.print("[blue]Fetching all data from user table...[/blue]")
            return database.get_usage_data(limit=limit)
    
    def get_source_name(self) -> str:
        return "UserTable (LiteLLMSpendCalculator)"
    
    def get_table_name(self) -> str:
        return "LiteLLMSpendCalculator"


class SpendLogsStrategy(DataSourceStrategy):
    """Strategy for fetching data from the SpendLogs table."""
    
    def get_data(self, database: LiteLLMDatabase,
                 date_filter: Optional[Dict[str, str]] = None,
                 limit: Optional[int] = None) -> pl.DataFrame:
        """Fetch data from spend logs with optional filtering."""
        if isinstance(database, CachedLiteLLMDatabase):
            # Use the appropriate method for CachedLiteLLMDatabase
            if date_filter:
                console.print(f"[blue]Fetching {date_filter['description']} from SpendLogs...[/blue]")
                return database.get_spend_logs(
                    start_date=date_filter['start_date'],
                    end_date=date_filter['end_date'],
                    limit=limit
                )
            else:
                console.print("[blue]Fetching all data from SpendLogs...[/blue]")
                return database.get_spend_logs_for_analysis(limit=limit)
        else:
            # For non-cached database, use the analysis method
            console.print("[blue]Fetching data from SpendLogs for analysis...[/blue]")
            return database.get_spend_logs_for_analysis(limit=limit)
    
    def get_source_name(self) -> str:
        return "SpendLogs"
    
    def get_table_name(self) -> str:
        return "SpendLogs"


class DataSourceFactory:
    """Factory for creating data source strategies."""
    
    _strategies = {
        'usertable': UserTableStrategy,
        'logs': SpendLogsStrategy,
        'spendlogs': SpendLogsStrategy,  # Alias
    }
    
    @classmethod
    def create_strategy(cls, source_type: str) -> DataSourceStrategy:
        """Create a data source strategy based on source type.
        
        Args:
            source_type: Type of data source ('usertable' or 'logs')
            
        Returns:
            Appropriate DataSourceStrategy instance
            
        Raises:
            ValueError: If source_type is not recognized
        """
        source_type = source_type.lower()
        if source_type not in cls._strategies:
            raise ValueError(
                f"Unknown source type: {source_type}. "
                f"Valid options are: {', '.join(cls._strategies.keys())}"
            )
        
        return cls._strategies[source_type]()
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type[DataSourceStrategy]):
        """Register a new data source strategy.
        
        Args:
            name: Name to register the strategy under
            strategy_class: Strategy class to register
        """
        cls._strategies[name.lower()] = strategy_class