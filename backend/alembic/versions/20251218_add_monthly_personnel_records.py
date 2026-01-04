"""add monthly_personnel_records table

Revision ID: 20251218_monthly_personnel
Revises: 
Create Date: 2025-12-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '20251218_monthly_personnel'
down_revision = None  # Önceki migration ID'sini buraya yazacağız
branch_labels = None
depends_on = None


def upgrade():
    """
    Aylık personel sicil kayıtları tablosu
    Bir personel aynı ayda birden fazla şantiyede çalışabilir
    """
    op.create_table(
        'monthly_personnel_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('personnel_id', sa.Integer(), nullable=False),
        sa.Column('donem', sa.String(7), nullable=False, comment='YYYY-MM format'),
        
        # Şantiye/Bölüm Bilgileri
        sa.Column('bolum_adi', sa.String(200), nullable=True, comment='Luca bölüm adı'),
        sa.Column('cost_center_id', sa.Integer(), nullable=True, comment='Maliyet merkezi ID'),
        sa.Column('cost_center_code', sa.String(50), nullable=True, comment='Maliyet merkezi kodu'),
        
        # Çalışma Tarihleri
        sa.Column('ise_giris_tarihi', sa.Date(), nullable=True, comment='Dönem içi giriş'),
        sa.Column('isten_cikis_tarihi', sa.Date(), nullable=True, comment='Dönem içi çıkış'),
        sa.Column('calisilan_gun', sa.Integer(), nullable=True, default=0, comment='Çalışılan gün sayısı'),
        
        # Ücret Bilgileri (Luca sicil verisi)
        sa.Column('ucret', sa.Numeric(18, 2), nullable=True),
        sa.Column('ucret_tipi', sa.String(10), nullable=True, comment='N=Net, B=Brüt'),
        
        # Luca Sicil Raw Data (JSON)
        sa.Column('luca_sicil_data', sa.JSON(), nullable=True, comment='Luca sicil Excel satırı'),
        
        # İşyeri Bilgisi
        sa.Column('isyeri', sa.String(200), nullable=True, comment='Luca işyeri adı'),
        sa.Column('unvan', sa.String(200), nullable=True, comment='Ünvan/Pozisyon'),
        sa.Column('meslek_adi', sa.String(200), nullable=True, comment='Meslek adı'),
        
        # Sistem
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        
        # Primary Key
        sa.PrimaryKeyConstraint('id'),
        
        # Unique Constraint: Bir personel, bir dönemde, bir bölümde sadece 1 kayıt
        sa.UniqueConstraint('personnel_id', 'donem', 'bolum_adi', name='uq_personnel_donem_bolum'),
        
        # Indexes
        sa.Index('idx_monthly_personnel_donem', 'donem'),
        sa.Index('idx_monthly_personnel_personnel_id', 'personnel_id'),
        sa.Index('idx_monthly_personnel_cost_center', 'cost_center_id'),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['personnel_id'], ['personnel.id'], name='fk_monthly_personnel_personnel', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cost_center_id'], ['cost_centers.id'], name='fk_monthly_personnel_cost_center', ondelete='SET NULL'),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )


def downgrade():
    """Tabloyu sil"""
    op.drop_table('monthly_personnel_records')
