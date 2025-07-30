"""
GoAsyncIO Server Management
"""

import warnings


class ServerManager:
    """Manage GoAsyncIO server lifecycle"""
    
    @staticmethod
    async def start_server(port: int = 8765, **kwargs):
        """Start GoAsyncIO server (if binary is available)"""
        warnings.warn(
            "Server management not implemented in this version. "
            "Please start the server manually with: goasyncio-server start",
            UserWarning
        )
    
    @staticmethod
    async def stop_server():
        """Stop GoAsyncIO server"""
        warnings.warn(
            "Server management not implemented in this version. "
            "Please stop the server manually.",
            UserWarning
        )
