"""
Config Repository
Database operations for system configuration
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from .models import SystemConfig, TaxBracket


class ConfigRepository:
    """Sistem konfigürasyon repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # System Config
    def get_all_configs(self, category: Optional[str] = None) -> List[SystemConfig]:
        """Tüm konfigürasyonları getir"""
        query = self.db.query(SystemConfig)
        if category:
            query = query.filter(SystemConfig.category == category)
        return query.order_by(SystemConfig.category, SystemConfig.config_key).all()
    
    def get_config_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """Key'e göre config getir"""
        return self.db.query(SystemConfig).filter(
            SystemConfig.config_key == config_key
        ).first()
    
    def create_config(self, config_data: dict) -> SystemConfig:
        """Yeni config oluştur"""
        config = SystemConfig(**config_data)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_config(self, config_key: str, config_data: dict) -> Optional[SystemConfig]:
        """Config güncelle"""
        config = self.get_config_by_key(config_key)
        if not config:
            return None
        
        for key, value in config_data.items():
            setattr(config, key, value)
        
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def delete_config(self, config_id: int) -> bool:
        """Config sil"""
        config = self.db.query(SystemConfig).filter(SystemConfig.id == config_id).first()
        if not config:
            return False
        
        self.db.delete(config)
        self.db.commit()
        return True
    
    # Tax Brackets
    def get_tax_brackets(self, year: Optional[int] = None) -> List[TaxBracket]:
        """Vergi dilimlerini getir"""
        query = self.db.query(TaxBracket)
        if year:
            query = query.filter(TaxBracket.year == year)
        return query.order_by(TaxBracket.year.desc(), TaxBracket.min_amount).all()
    
    def create_tax_bracket(self, bracket_data: dict) -> TaxBracket:
        """Yeni vergi dilimi oluştur"""
        bracket = TaxBracket(**bracket_data)
        self.db.add(bracket)
        self.db.commit()
        self.db.refresh(bracket)
        return bracket
    
    def update_tax_bracket(self, bracket_id: int, bracket_data: dict) -> Optional[TaxBracket]:
        """Vergi dilimi güncelle"""
        bracket = self.db.query(TaxBracket).filter(TaxBracket.id == bracket_id).first()
        if not bracket:
            return None
        
        for key, value in bracket_data.items():
            setattr(bracket, key, value)
        
        self.db.commit()
        self.db.refresh(bracket)
        return bracket
    
    def delete_tax_bracket(self, bracket_id: int) -> bool:
        """Vergi dilimi sil"""
        bracket = self.db.query(TaxBracket).filter(TaxBracket.id == bracket_id).first()
        if not bracket:
            return False
        
        self.db.delete(bracket)
        self.db.commit()
        return True
