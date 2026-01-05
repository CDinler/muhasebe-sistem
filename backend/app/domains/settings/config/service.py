"""
Config Service
Business logic for system configuration
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from .repository import ConfigRepository
from .models import SystemConfig, TaxBracket


class ConfigService:
    """Sistem konfigürasyon business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = ConfigRepository(db)
    
    def get_all_configs_grouped(self, category: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Tüm konfigürasyonları kategorilere göre grupla"""
        configs = self.repo.get_all_configs(category)
        
        result = {}
        for config in configs:
            cat = config.category or 'GENEL'
            if cat not in result:
                result[cat] = []
            result[cat].append({
                "id": config.id,
                "key": config.config_key,
                "value": config.config_value,
                "type": config.config_type,
                "description": config.description
            })
        
        return result
    
    def get_config(self, config_key: str) -> Optional[SystemConfig]:
        """Config getir"""
        return self.repo.get_config_by_key(config_key)
    
    def create_config(self, config_data: dict) -> SystemConfig:
        """Yeni config oluştur"""
        # Key kontrolü
        existing = self.repo.get_config_by_key(config_data['config_key'])
        if existing:
            raise ValueError("Bu config key zaten var")
        
        return self.repo.create_config(config_data)
    
    def update_config(self, config_key: str, config_data: dict) -> Optional[SystemConfig]:
        """Config güncelle"""
        return self.repo.update_config(config_key, config_data)
    
    def delete_config(self, config_id: int) -> bool:
        """Config sil"""
        return self.repo.delete_config(config_id)
    
    # Tax Brackets
    def get_tax_brackets(self, year: Optional[int] = None) -> List[TaxBracket]:
        """Vergi dilimlerini getir"""
        return self.repo.get_tax_brackets(year)
    
    def create_tax_bracket(self, bracket_data: dict) -> TaxBracket:
        """Yeni vergi dilimi oluştur"""
        return self.repo.create_tax_bracket(bracket_data)
    
    def update_tax_bracket(self, bracket_id: int, bracket_data: dict) -> Optional[TaxBracket]:
        """Vergi dilimi güncelle"""
        return self.repo.update_tax_bracket(bracket_id, bracket_data)
    
    def delete_tax_bracket(self, bracket_id: int) -> bool:
        """Vergi dilimi sil"""
        return self.repo.delete_tax_bracket(bracket_id)
