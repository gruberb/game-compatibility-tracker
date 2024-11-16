from .config_handler import ConfigHandler

# Create a singleton instance
config = ConfigHandler()

# Export the instance
__all__ = ['config']
