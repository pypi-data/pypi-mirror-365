from abc import ABC, abstractmethod
from typing import Dict, Optional


class WalletAddressCreateInterface(ABC):
    @staticmethod
    @abstractmethod
    def create(user_id: Optional[int] = None) -> Dict[str, str]:
        ...
