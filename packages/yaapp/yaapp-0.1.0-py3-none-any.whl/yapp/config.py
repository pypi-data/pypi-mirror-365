"""
Enterprise-grade configuration system for YAPP with environment variables and secrets support.
"""

import os
import json
HAS_YAML = False
yaml = None

# Try to import yaml from the system
try:
    import yaml
    HAS_YAML = True
except ImportError:
    # PyYAML not available - JSON-only mode
    pass
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class ConfigSource(Enum):
    """Configuration source priority order."""
    ENVIRONMENT = "environment"
    CONFIG_FILE = "config_file"
    SECRETS_FILE = "secrets_file"
    DEFAULT = "default"


@dataclass
class ServerConfig:
    """Server configuration settings."""
    host: str = "localhost"
    port: int = 8000
    reload: bool = False
    workers: int = 1
    timeout: int = 30
    
    @classmethod
    def from_env(cls, prefix: str = "YAPP_SERVER_") -> 'ServerConfig':
        """Load server config from environment variables."""
        return cls(
            host=os.getenv(f"{prefix}HOST", cls.host),
            port=int(os.getenv(f"{prefix}PORT", cls.port)),
            reload=os.getenv(f"{prefix}RELOAD", "false").lower() == "true",
            workers=int(os.getenv(f"{prefix}WORKERS", cls.workers)),
            timeout=int(os.getenv(f"{prefix}TIMEOUT", cls.timeout))
        )


@dataclass 
class SecurityConfig:
    """Security configuration settings."""
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    allowed_origins: list = field(default_factory=lambda: ["*"])
    rate_limit: int = 1000
    enable_cors: bool = True
    
    @classmethod
    def from_env(cls, prefix: str = "YAPP_SECURITY_") -> 'SecurityConfig':
        """Load security config from environment variables."""
        allowed_origins = os.getenv(f"{prefix}ALLOWED_ORIGINS", "*")
        if allowed_origins != "*":
            allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]
        else:
            allowed_origins = ["*"]
            
        return cls(
            api_key=os.getenv(f"{prefix}API_KEY"),
            secret_key=os.getenv(f"{prefix}SECRET_KEY"),
            allowed_origins=allowed_origins,
            rate_limit=int(os.getenv(f"{prefix}RATE_LIMIT", cls.rate_limit)),
            enable_cors=os.getenv(f"{prefix}ENABLE_CORS", "true").lower() == "true"
        )


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_size: int = 10_000_000  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls, prefix: str = "YAPP_LOG_") -> 'LoggingConfig':
        """Load logging config from environment variables."""
        return cls(
            level=os.getenv(f"{prefix}LEVEL", cls.level),
            format=os.getenv(f"{prefix}FORMAT", cls.format),
            file=os.getenv(f"{prefix}FILE"),
            max_size=int(os.getenv(f"{prefix}MAX_SIZE", cls.max_size)),
            backup_count=int(os.getenv(f"{prefix}BACKUP_COUNT", cls.backup_count))
        )


@dataclass
class YAppConfig:
    """Main YAPP configuration container."""
    server: ServerConfig = field(default_factory=ServerConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    custom: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def load(cls, 
             config_file: Optional[Union[str, Path]] = None,
             secrets_file: Optional[Union[str, Path]] = None,
             env_prefix: str = "YAPP_") -> 'YAppConfig':
        """
        Load configuration from multiple sources with priority order:
        1. Environment variables (highest priority)
        2. Config file
        3. Secrets file
        4. Defaults (lowest priority)
        """
        
        config = cls()
        
        # Load from files first (lower priority)
        if config_file:
            config._load_from_file(config_file)
        
        if secrets_file:
            config._load_secrets_from_file(secrets_file)
        
        # Load from environment (higher priority)
        config._load_from_environment(env_prefix)
        
        return config
    
    def _load_from_file(self, config_file: Union[str, Path]) -> None:
        """Load configuration from YAML or JSON file."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            return
        
        try:
            with open(config_path, 'r') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    if not HAS_YAML:
                        print("Warning: YAML config file found but PyYAML not installed")
                        return
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Update configuration sections (merge, don't replace)
            if 'server' in data:
                for key, value in data['server'].items():
                    if hasattr(self.server, key):
                        setattr(self.server, key, value)
            if 'security' in data:
                # Don't load secrets from regular config file
                security_data = {k: v for k, v in data['security'].items() 
                               if k not in ['api_key', 'secret_key']}
                for key, value in security_data.items():
                    if hasattr(self.security, key):
                        setattr(self.security, key, value)
            if 'logging' in data:
                for key, value in data['logging'].items():
                    if hasattr(self.logging, key):
                        setattr(self.logging, key, value)  
            if 'custom' in data:
                self.custom.update(data['custom'])
                
        except (json.JSONDecodeError, yaml.YAMLError, TypeError) as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")
    
    def _load_secrets_from_file(self, secrets_file: Union[str, Path]) -> None:
        """Load secrets from encrypted/secure file."""
        secrets_path = Path(secrets_file)
        
        if not secrets_path.exists():
            return
        
        try:
            with open(secrets_path, 'r') as f:
                if secrets_path.suffix.lower() in ['.yaml', '.yml']:
                    if not HAS_YAML:
                        print("Warning: YAML secrets file found but PyYAML not installed")
                        return
                    secrets = yaml.safe_load(f)
                else:
                    secrets = json.load(f)
            
            # Load only secret values
            if 'security' in secrets:
                if 'api_key' in secrets['security']:
                    self.security.api_key = secrets['security']['api_key']
                if 'secret_key' in secrets['security']:
                    self.security.secret_key = secrets['security']['secret_key']
                    
        except (json.JSONDecodeError, yaml.YAMLError, TypeError) as e:
            print(f"Warning: Failed to load secrets file {secrets_file}: {e}")
    
    def _load_from_environment(self, prefix: str = "YAPP_") -> None:
        """Load configuration from environment variables."""
        # Load subsection configs from environment
        self.server = ServerConfig.from_env(f"{prefix}SERVER_")
        self.security = SecurityConfig.from_env(f"{prefix}SECURITY_")
        self.logging = LoggingConfig.from_env(f"{prefix}LOG_")
        
        # Load custom environment variables
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}CUSTOM_"):
                custom_key = key[len(f"{prefix}CUSTOM_"):].lower()
                self.custom[custom_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        parts = key.split('.')
        obj = self
        
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return default
        
        return obj
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)."""
        return {
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'reload': self.server.reload,
                'workers': self.server.workers,
                'timeout': self.server.timeout
            },
            'security': {
                'allowed_origins': self.security.allowed_origins,
                'rate_limit': self.security.rate_limit,
                'enable_cors': self.security.enable_cors,
                # Secrets intentionally excluded
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file': self.logging.file,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count
            },
            'custom': self.custom
        }


class ConfigManager:
    """Singleton configuration manager for global access."""
    
    _instance: Optional[YAppConfig] = None
    
    @classmethod
    def get_config(cls) -> YAppConfig:
        """Get the global configuration instance."""
        if cls._instance is None:
            cls._instance = YAppConfig.load()
        return cls._instance
    
    @classmethod
    def set_config(cls, config: YAppConfig) -> None:
        """Set the global configuration instance."""
        cls._instance = config
    
    @classmethod
    def load_config(cls, 
                   config_file: Optional[Union[str, Path]] = None,
                   secrets_file: Optional[Union[str, Path]] = None) -> YAppConfig:
        """Load and set global configuration."""
        cls._instance = YAppConfig.load(config_file, secrets_file)
        return cls._instance


# Convenience function for common usage
def get_config() -> YAppConfig:
    """Get the global YAPP configuration."""
    return ConfigManager.get_config()


# Example usage and defaults
if __name__ == "__main__":
    # Example configuration file structure
    example_config = {
        "server": {
            "host": "0.0.0.0",
            "port": 8080,
            "workers": 4
        },
        "security": {
            "allowed_origins": ["https://myapp.com", "https://api.myapp.com"],
            "rate_limit": 500
        },
        "logging": {
            "level": "DEBUG",
            "file": "/var/log/yapp.log"
        },
        "custom": {
            "app_name": "My YAPP Application",
            "version": "1.0.0"
        }
    }
    
    print("Example config structure:")
    print(json.dumps(example_config, indent=2))