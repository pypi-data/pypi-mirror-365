"""Binance exchange configuration."""

from typing import Dict, List
from .base import BaseExchangeConfig


class BinanceConfig(BaseExchangeConfig):
    """Binance exchange configuration with wallet types and network mappings."""
    
    @property
    def wallet_type_to_currencies(self) -> Dict[str, List[str]]:
        """Get wallet type to currencies mapping."""
        return dict(self._config.get("wallet_type_to_currencies", {}))
    
    @wallet_type_to_currencies.setter
    def wallet_type_to_currencies(self, value: Dict[str, List[str]]):
        """Set wallet type to currencies mapping."""
        self._config["wallet_type_to_currencies"] = dict(value)
    
    @property
    def networks(self) -> Dict[str, str]:
        """Get network mappings."""
        return dict(self._config.get("networks", {}))
    
    @networks.setter
    def networks(self, value: Dict[str, str]):
        """Set network mappings."""
        self._config["networks"] = dict(value)
    
    # Wallet Type Methods
    def get_wallet_types(self) -> List[str]:
        """Get available wallet types."""
        return list(self.wallet_type_to_currencies.keys())
    
    def get_wallet_currencies(self, wallet_type: str) -> List[str]:
        """Get currencies available for a specific wallet type."""
        return list(self.wallet_type_to_currencies.get(wallet_type, []))
    
    def add_wallet_type(self, wallet_type: str, currencies: List[str] = None):
        """Add a new wallet type."""
        wallet_mapping = self.wallet_type_to_currencies
        wallet_mapping[wallet_type] = currencies or []
        self.wallet_type_to_currencies = wallet_mapping
    
    def add_currency_to_wallet(self, wallet_type: str, currency: str):
        """Add a currency to a wallet type."""
        wallet_mapping = self.wallet_type_to_currencies
        if wallet_type not in wallet_mapping:
            wallet_mapping[wallet_type] = []
        
        if currency not in wallet_mapping[wallet_type]:
            wallet_mapping[wallet_type].append(currency)
            self.wallet_type_to_currencies = wallet_mapping
    
    def _remove_currency_from_mappings(self, currency: str):
        """Remove currency from all related mappings including wallet types."""
        super()._remove_currency_from_mappings(currency)
        
        # Remove from wallet_type_to_currencies
        wallet_mapping = self.wallet_type_to_currencies
        for wallet_type, currencies in wallet_mapping.items():
            if currency in currencies:
                currencies.remove(currency)
        self.wallet_type_to_currencies = wallet_mapping 