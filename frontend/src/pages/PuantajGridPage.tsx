import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  DatePicker, 
  message, 
  Space, 
  Upload, 
  Table, 
  Select,
  Spin,
  Tooltip,
  Typography,
  Modal,
  Dropdown,
  Menu
} from 'antd';
import { 
  SaveOutlined,
  UploadOutlined,
  DownloadOutlined,
  ReloadOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import api from '../services/api';
import dayjs, { Dayjs } from 'dayjs';
import 'dayjs/locale/tr';
import type { ColumnsType } from 'antd/es/table';

dayjs.locale('tr');

const { Title } = Typography;
const { Option } = Select;

// Durum kodları - Luca ile uyumlu
const DURUM_KODLARI = [
  { kod: 'N', aciklama: 'Normal', color: '#52c41a' },
  { kod: 'H', aciklama: 'Hafta Tatili', color: '#722ed1' },
  { kod: 'T', aciklama: 'Resmi Tatil', color: '#ff4d4f' },
  { kod: 'İ', aciklama: 'İzinli', color: '#faad14' },
  { kod: 'S', aciklama: 'Yıllık İzin', color: '#fa8c16' },
  { kod: 'R', aciklama: 'Raporlu', color: '#f5222d' },
  { kod: 'E', aciklama: 'Eksik Gün', color: '#ff7875' },
  { kod: 'Y', aciklama: 'Yarım Gün', color: '#ffc53d' },
  { kod: 'G', aciklama: 'Gece Mesaisi', color: '#1890ff' },
  { kod: 'O', aciklama: 'Gündüz Mesaisi', color: '#40a9ff' },
  { kod: 'K', aciklama: 'Yarım Gün Resmi Tatil', color: '#ff9c6e' },
  { kod: 'C', aciklama: 'Yarım Gün Hafta Tatili', color: '#bfbfbf' },
];

interface PersonelRow {
  id: number;
  sicil_no: string;
  adi_soyadi: string;
  tckn: string;
  cost_center_id?: number;
  toplam_fm?: number;
  [key: string]: any; // gun_1, gun_2, ... gun_31 + fm_gun_1, fm_gun_2, ... fm_gun_31
}

const PuantajGridPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState<PersonelRow[]>([]);
  const [allData, setAllData] = useState<PersonelRow[]>([]);
  const [editedCells, setEditedCells] = useState<Set<string>>(new Set());
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [costCenters, setCostCenters] = useState<any[]>([]);
  const [selectedCostCenter, setSelectedCostCenter] = useState<number | null>(null);
  const [editingCell, setEditingCell] = useState<string | null>(null);
  const [holidayDays, setHolidayDays] = useState<number[]>([]);

  const donem = React.useMemo(() => selectedDate.format('YYYY-MM'), [selectedDate]);
  const gunSayisi = selectedDate.daysInMonth();

  const fetchData = React.useCallback(async () => {
    // Cost center seçilmediyse veri yükleme
    if (!selectedCostCenter) {
      setData([]);
      setAllData([]);
      setHolidayDays([]);
      return;
    }
    
    setLoading(true);
    try {
      const params: any = { donem, cost_center_id: selectedCostCenter };
      
      const response = await api.get('/puantaj-grid/grid', { params });
      const records = response.data.records || [];
      const holidays = response.data.holidays || [];
      setAllData(records);
      setData(records);
      setHolidayDays(holidays);
      setEditedCells(new Set());
    } catch (error: any) {
      console.error('Puantaj veri yükleme hatası:', error);
      message.error('Veri yüklenemedi: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  }, [donem, selectedCostCenter]);

  useEffect(() => {
    const loadCostCenters = async () => {
      try {
        const response = await api.get('/cost-centers/');
        const centers = Array.isArray(response.data) ? response.data : (response.data.value || response.data.cost_centers || []);
        setCostCenters(centers);
      } catch (error) {
        console.error('Maliyet merkezleri yüklenemedi:', error);
      }
    };
    loadCostCenters();
  }, []);

  useEffect(() => {
    fetchData();
  }, [donem, selectedCostCenter]);

  const handleCellChange = (personnelId: number, gunNo: number, value: string | number | null, type: 'durum' | 'fm' = 'durum') => {
    const cellKey = type === 'durum' ? `${personnelId}_${gunNo}` : `${personnelId}_fm_${gunNo}`;
    setEditedCells(prev => new Set(prev).add(cellKey));
    
    const fieldName = type === 'durum' ? `gun_${gunNo}` : `fm_gun_${gunNo}`;
    
    setData(prevData => 
      prevData.map(row => 
        row.id === personnelId 
          ? { ...row, [fieldName]: value }
          : row
      )
    );
  };

  const handleSave = async () => {
    setSaving(true);
    message.loading({ content: 'Kaydediliyor...', key: 'save' });
    
    try {
      await api.post('/puantaj-grid/grid/save', {
        donem,
        records: data
      });
      
      message.success({
        content: 'Puantaj başarıyla kaydedildi',
        key: 'save'
      });
      
      setEditedCells(new Set());
      await fetchData();
    } catch (error: any) {
      message.error({
        content: 'Kayıt hatası: ' + (error.response?.data?.detail || error.message),
        key: 'save'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleHaftaTatiliSec = (selectedDays: string[]) => {
    let degisiklikSayisi = 0;
    
    const updatedData = data.map(row => {
      const newRow = { ...row };
      for (let i = 1; i <= gunSayisi; i++) {
        const tarih = dayjs(`${donem}-${String(i).padStart(2, '0')}`);
        const gunAdi = tarih.format('dddd');
        const gunKey = `gun_${i}`;
        const oldValue = newRow[gunKey];
        
        // Önce mevcut H'yi temizle
        if (oldValue === 'H') {
          newRow[gunKey] = '';
          degisiklikSayisi++;
        }
        
        // Sonra seçilen günleri H yap
        if (selectedDays.includes(gunAdi)) {
          if (oldValue !== 'H') {
            degisiklikSayisi++;
          }
          newRow[gunKey] = 'H';
          const cellKey = `${row.id}-gun_${i}`;
          setEditedCells(prev => new Set([...prev, cellKey]));
        }
      }
      return newRow;
    });
    
    setData(updatedData);
    message.success(`Hafta tatili güncellendi - sadece seçilen günler işaretli`);
  };

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('donem', donem);

    message.loading({ content: 'Excel yükleniyor...', key: 'upload' });

    try {
      const response = await api.post('/puantaj-grid/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      message.success({
        content: `${response.data.total} kayıt işlendi`,
        key: 'upload'
      });

      setUploadModalVisible(false);
      await fetchData();
    } catch (error: any) {
      message.error({
        content: 'Upload hatası: ' + (error.response?.data?.detail || error.message),
        key: 'upload'
      });
    }

    return false;
  };

  // Excel benzeri kolonlar - ULTRA KOMPAKT (Luca gibi)
  const getColumns = (): ColumnsType<PersonelRow> => {
    const fixedColumns: ColumnsType<PersonelRow> = [
      {
        title: 'Personel',
        dataIndex: 'adi_soyadi',
        key: 'adi_soyadi',
        fixed: 'left',
        width: 150,
        ellipsis: true,
      },
    ];

    // Günlük kolonlar (1-31)
    const dayColumns: ColumnsType<PersonelRow> = [];
    const gunKisaltmalari: { [key: string]: string } = {
      'Pazartesi': 'Pt',
      'Salı': 'Sa',
      'Çarşamba': 'Ça',
      'Perşembe': 'Pe',
      'Cuma': 'Cu',
      'Cumartesi': 'Ct',
      'Pazar': 'Pz'
    };
    
    for (let i = 1; i <= gunSayisi; i++) {
      const tarih = dayjs(`${donem}-${String(i).padStart(2, '0')}`);
      const gunTam = tarih.format('dddd');
      const gunKisa = gunKisaltmalari[gunTam] || gunTam.substring(0, 2);
      const isHoliday = holidayDays.includes(i);
      
      dayColumns.push({
        title: (
          <Tooltip title={tarih.format('DD MMMM YYYY dddd') + (isHoliday ? ' - RESMİ TATİL' : '')}>
            <div style={{ 
              textAlign: 'center', 
              lineHeight: '1.1', 
              fontSize: '9px',
              backgroundColor: isHoliday ? '#ff4d4f20' : 'transparent',
              padding: '2px',
              borderRadius: '2px'
            }}>
              <div style={{ fontWeight: 'normal', color: isHoliday ? '#ff4d4f' : 'inherit' }}>{gunKisa}</div>
              <div style={{ fontWeight: 'bold', color: isHoliday ? '#ff4d4f' : 'inherit' }}>{i}</div>
              {isHoliday && <div style={{ fontSize: '7px', color: '#ff4d4f' }}>T</div>}
            </div>
          </Tooltip>
        ),
        dataIndex: `gun_${i}`,
        key: `gun_${i}`,
        width: 26,
        align: 'center',
        render: (value: string, record: PersonelRow) => {
          const cellKey = `${record.id}_${i}`;
          const fmKey = `${record.id}_fm_${i}`;
          const isEdited = editedCells.has(cellKey) || editedCells.has(fmKey);
          const durumInfo = DURUM_KODLARI.find(d => d.kod === value);
          const fmValue = record[`fm_gun_${i}`];
          const isEditing = editingCell === cellKey;
          
          return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1px', width: '100%' }}>
              {/* Durum kodu */}
              {isEditing ? (
                <Select
                  value={value || undefined}
                  placeholder="-"
                  style={{ width: '100%', fontSize: '11px', fontWeight: 'bold' }}
                  size="small"
                  variant="borderless"
                  popupMatchSelectWidth={110}
                  onChange={(newValue) => {
                    handleCellChange(record.id, i, newValue, 'durum');
                    setEditingCell(null);
                  }}
                  onBlur={() => setEditingCell(null)}
                  autoFocus
                  open={true}
                  suffixIcon={null}
                  removeIcon={null}
                  clearIcon={null}
                  menuItemSelectedIcon={false}
                  optionLabelProp="value"
                >
                  <Option value="">-</Option>
                  {DURUM_KODLARI.map(durum => (
                    <Option key={durum.kod} value={durum.kod} label={durum.kod}>
                      <span style={{ color: durum.color, fontWeight: 'bold', fontSize: '10px' }}>
                        {durum.kod}
                      </span>
                      <span style={{ fontSize: '9px', marginLeft: '6px', color: '#666' }}>
                        {durum.aciklama}
                      </span>
                    </Option>
                  ))}
                </Select>
              ) : (
                <div
                  onClick={() => setEditingCell(cellKey)}
                  style={{
                    width: '100%',
                    height: '18px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    fontSize: '11px',
                    fontWeight: 'bold',
                    color: durumInfo?.color || '#999',
                    userSelect: 'none'
                  }}
                >
                  {value || '-'}
                </div>
              )}
              
              {/* Fazla mesai - sadece çalışılan günlerde göster */}
              {value && ['N', 'G', 'O'].includes(value) && (
                <input
                  type="text"
                  inputMode="decimal"
                  value={fmValue || ''}
                  placeholder=""
                  onChange={(e) => {
                    const val = e.target.value.replace(',', '.');
                    const num = val ? parseFloat(val) : null;
                    if (val === '' || (!isNaN(num!) && num! >= 0 && num! <= 24)) {
                      handleCellChange(record.id, i, num, 'fm');
                    }
                  }}
                  style={{
                    width: '100%',
                    height: '16px',
                    fontSize: '8px',
                    padding: '1px 2px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '2px',
                    textAlign: 'center',
                    backgroundColor: 'white'
                  }}
                />
              )}
            </div>
          );
        },
        onCell: (record: PersonelRow) => {
          const value = record[`gun_${i}`];
          const durumInfo = DURUM_KODLARI.find(d => d.kod === value);
          return {
            style: {
              backgroundColor: durumInfo ? `${durumInfo.color}15` : 'transparent',
              padding: '1px',
            }
          };
        }
      });
    }

    // Özet kolonlar - Ultra Kompakt
    const summaryColumns: ColumnsType<PersonelRow> = [
      {
        title: 'Çalışılan',
        key: 'calisilan',
        width: 55,
        align: 'center',
        render: (_: any, record: PersonelRow) => {
          let count = 0;
          for (let i = 1; i <= gunSayisi; i++) {
            const val = record[`gun_${i}`];
            if (val === 'N' || val === 'G' || val === 'O') count++;
          }
          return <strong style={{ fontSize: '9px' }}>{count}</strong>;
        }
      },
      {
        title: 'İzin',
        key: 'izin',
        width: 40,
        align: 'center',
        render: (_: any, record: PersonelRow) => {
          let count = 0;
          for (let i = 1; i <= gunSayisi; i++) {
            const val = record[`gun_${i}`];
            if (val === 'İ' || val === 'S') count++;
          }
          return count > 0 ? <span style={{ color: '#faad14', fontSize: '9px' }}>{count}</span> : <span style={{ fontSize: '9px' }}>-</span>;
        }
      },
      {
        title: 'Eksik',
        key: 'eksik',
        width: 40,
        align: 'center',
        render: (_: any, record: PersonelRow) => {
          let count = 0;
          for (let i = 1; i <= gunSayisi; i++) {
            const val = record[`gun_${i}`];
            if (val === 'E') count++;
          }
          return count > 0 ? <span style={{ color: '#ff4d4f', fontSize: '9px' }}>{count}</span> : <span style={{ fontSize: '9px' }}>-</span>;
        }
      },
      {
        title: 'FM',
        key: 'fm',
        width: 40,
        align: 'center',
        render: (_: any, record: PersonelRow) => {
          let total = 0;
          for (let i = 1; i <= gunSayisi; i++) {
            const fm = record[`fm_gun_${i}`];
            if (fm) total += parseFloat(fm);
          }
          return total > 0 ? <span style={{ color: '#1890ff', fontSize: '9px', fontWeight: 'bold' }}>{total.toFixed(1)}</span> : <span style={{ fontSize: '9px' }}>-</span>;
        }
      }
    ];

    return [...fixedColumns, ...dayColumns, ...summaryColumns];
  };

  return (
    <div style={{ padding: '8px', height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
      <Card styles={{ body: { padding: '8px', height: '100%', display: 'flex', flexDirection: 'column' } }}>
        {/* Ultra Kompakt Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <Title level={4} style={{ margin: 0, fontSize: '14px' }}>
            <CalendarOutlined /> Puantaj Takip
          </Title>
          <Space size="small">
            <DatePicker
              picker="month"
              value={selectedDate}
              onChange={(date) => date && setSelectedDate(date)}
              format="MMM YYYY"
              allowClear={false}
              size="small"
            />
            <Select
              placeholder="⚠️ Önce Şantiye Seçin"
              style={{ width: 200 }}
              allowClear
              size="small"
              value={selectedCostCenter}
              onChange={setSelectedCostCenter}
              showSearch
              optionFilterProp="children"
            >
              {costCenters.map(cc => (
                <Option key={cc.id} value={cc.id}>
                  {cc.code} - {cc.name}
                </Option>
              ))}
            </Select>
            <Dropdown
              menu={{
                items: [
                  { key: 'cumartesi-pazar', label: 'Cumartesi-Pazar' },
                  { key: 'pazar', label: 'Pazar' },
                  { key: 'cumartesi', label: 'Cumartesi' },
                  { key: 'cuma', label: 'Cuma' },
                  { key: 'persembe', label: 'Perşembe' },
                  { key: 'carsamba', label: 'Çarşamba' },
                  { key: 'sali', label: 'Salı' },
                  { key: 'pazartesi', label: 'Pazartesi' },
                ],
                onClick: ({ key }) => {
                  switch(key) {
                    case 'cumartesi-pazar':
                      handleHaftaTatiliSec(['Cumartesi', 'Pazar']);
                      break;
                    case 'pazar':
                      handleHaftaTatiliSec(['Pazar']);
                      break;
                    case 'cumartesi':
                      handleHaftaTatiliSec(['Cumartesi']);
                      break;
                    case 'cuma':
                      handleHaftaTatiliSec(['Cuma']);
                      break;
                    case 'persembe':
                      handleHaftaTatiliSec(['Perşembe']);
                      break;
                    case 'carsamba':
                      handleHaftaTatiliSec(['Çarşamba']);
                      break;
                    case 'sali':
                      handleHaftaTatiliSec(['Salı']);
                      break;
                    case 'pazartesi':
                      handleHaftaTatiliSec(['Pazartesi']);
                      break;
                  }
                }
              }}
              disabled={!selectedCostCenter}
            >
              <Button size="small" disabled={!selectedCostCenter}>
                Hafta Tatili Seç
              </Button>
            </Dropdown>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchData}
              loading={loading}
              size="small"
            />
            <Upload
              accept=".xls,.xlsx"
              showUploadList={false}
              beforeUpload={handleUpload}
            >
              <Button icon={<UploadOutlined />} size="small">
                Excel
              </Button>
            </Upload>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={saving}
              disabled={editedCells.size === 0}
              size="small"
            >
              Kaydet {editedCells.size > 0 && `(${editedCells.size})`}
            </Button>
          </Space>
        </div>

        {/* Ultra Kompakt Durum Kodları */}
        <div style={{ 
          marginBottom: '6px', 
          padding: '4px 6px', 
          backgroundColor: '#fafafa', 
          borderRadius: '3px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '6px'
        }}>
          {DURUM_KODLARI.map(durum => (
            <div key={durum.kod} style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
              <span 
                style={{ 
                  width: '16px', 
                  height: '16px', 
                  backgroundColor: `${durum.color}30`,
                  border: `1px solid ${durum.color}`,
                  borderRadius: '2px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '8px',
                  color: durum.color
                }}
              >
                {durum.kod}
              </span>
              <span style={{ fontSize: '9px' }}>{durum.aciklama}</span>
            </div>
          ))}
          <span style={{ fontSize: '9px', color: '#999', marginLeft: 'auto' }}>
            {data.length} personel
          </span>
        </div>

        {/* Puantaj Tablosu - Tam Yükseklik */}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          {!selectedCostCenter ? (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '100%',
              color: '#999',
              fontSize: '14px'
            }}>
              ⬆️ Lütfen yukarıdan bir şantiye seçin
            </div>
          ) : (
            <Spin spinning={loading}>
              <Table
                columns={getColumns()}
                dataSource={data}
                rowKey="id"
                pagination={false}
                size="small"
                bordered
                scroll={{ x: 'max-content', y: 'calc(100vh - 280px)' }}
                virtual
              />
            </Spin>
          )}
        </div>
      </Card>

      <style>{`
        .edited-cell .ant-select-selector {
          background-color: #fffbe6 !important;
          border: 1px solid #faad14 !important;
        }
        
        .ant-table-cell {
          padding: 1px 2px !important;
          font-size: 9px !important;
          line-height: 1.2 !important;
        }
        
        .ant-table-thead > tr > th {
          padding: 2px 2px !important;
          font-size: 9px !important;
          font-weight: 600;
          line-height: 1.2 !important;
          background-color: #fafafa !important;
        }
        
        .ant-table-bordered .ant-table-cell {
          border-right: 1px solid #c0c0c0 !important;
        }
        
        .ant-table-bordered .ant-table-tbody > tr > td {
          border-bottom: 1px solid #c0c0c0 !important;
        }
        
        .ant-select-single.ant-select-sm .ant-select-selector {
          height: 20px !important;
          font-size: 11px !important;
          font-weight: bold !important;
          padding: 0 4px !important;
        }
        
        .ant-select-selection-item {
          line-height: 18px !important;
          font-size: 11px !important;
          font-weight: bold !important;
          overflow: hidden !important;
          text-overflow: clip !important;
          white-space: nowrap !important;
        }
        
        .ant-select-selector .ant-select-selection-item {
          padding-right: 0 !important;
        }
        
        .ant-table-small .ant-table-tbody > tr > td {
          padding: 1px 2px !important;
        }
        
        .ant-table-small .ant-table-tbody > tr {
          height: 42px !important;
        }
        
        /* Kaydırma çubuğu gerekmedikçe gizle */
        .ant-table-body {
          overflow-x: auto !important;
          overflow-y: auto !important;
        }
        
        .ant-table-body::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        
        .ant-table-body::-webkit-scrollbar-track {
          background: #f1f1f1;
        }
        
        .ant-table-body::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 4px;
        }
        
        .ant-table-body::-webkit-scrollbar-thumb:hover {
          background: #555;
        }
      `}</style>
    </div>
  );
};

export default PuantajGridPage;
