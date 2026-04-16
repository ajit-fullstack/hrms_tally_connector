"""
Enhanced data models for Accounting Connector with accounting data tabs
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum

class ConnectorStatus(Enum):
    """Connection status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    PENDING = "pending"
    ERROR = "error"

class LogLevel(Enum):
    """Log level enumeration"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"

@dataclass
class LogEntry:
    """Log entry data model"""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] [{self.level.value}] [{self.source}] {self.message}"

@dataclass
class TallyConfig:
    """Tally connector configuration"""
    host: str = "localhost"
    port: int = 9000
    company: str = ""
    selected_data_types: List[str] = field(default_factory=lambda: ["Ledgers", "Groups"])
    date_from: datetime = field(default_factory=lambda: datetime.now() - timedelta(days=30))
    date_to: datetime = field(default_factory=datetime.now)

@dataclass
class BusyConfig:
    """BUSY connector configuration"""
    dsn: str = ""
    username: str = ""
    company: str = ""
    selected_data_types: List[str] = field(default_factory=lambda: ["Ledgers"])
    date_from: datetime = field(default_factory=lambda: datetime.now() - timedelta(days=30))
    date_to: datetime = field(default_factory=datetime.now)

@dataclass
class AccountingTab:
    """Accounting data tab model"""
    name: str
    icon: str = ""
    description: str = ""
    columns: List[str] = field(default_factory=list)
    data: List[List[Any]] = field(default_factory=list)
    selected: bool = False

class DataCategory(Enum):
    """Data category enumeration"""
    LEDGERS = "Ledgers"
    JOURNAL = "Journal"
