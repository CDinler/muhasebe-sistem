import { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag, message, Modal, Form, Input, InputNumber, Select } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { draftContractsApi } from '@/domains/personnel/draft_contracts/api/draft-contracts.api';
import type { PersonnelDraftContract, PersonnelDraftContractCreate, PersonnelDraftContractUpdate } from '@/domains/personnel/draft_contracts/types/draft-contracts.types';
import { costCenterService, CostCenter } from '@/services/muhasebe.service';
import { usePersonnel } from '@/domains/personnel/hooks/usePersonnel';

export default function DraftContractsTab() {
  const [loading, setLoading] = useState(false);
  const [draftContracts, setDraftContracts] = useState<PersonnelDraftContract[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingDraft, setEditingDraft] = useState<PersonnelDraftContract | null>(null);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [form] = Form.useForm();

  // Personnel listesi
  const { data: personnelData } = usePersonnel({ limit: 10000 });
  const personnelList = personnelData?.items || [];

  useEffect(() => {
    loadDraftContracts();
    loadCostCenters();
  }, []);

  const loadDraftContracts = async () => {
    setLoading(true);
    try {
      // Tüm kayıtları getir (aktif + pasif), backend is_active DESC sıralaması yaptığı için aktifler önce gelir
      const response = await draftContractsApi.getAll({});
      setDraftContracts(response.data);
    } catch (error: any) {
      message.error('Taslak sözleşmeler yüklenemedi');
      console.error('Draft contracts load error:', error);
      console.error('Error response:', error?.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const loadCostCenters = async () => {
    try {
      const response: any = await costCenterService.getAll({ is_active: true });
      const data = response.data;
      setCostCenters(Array.isArray(data) ? data : data?.items || []);
    } catch (error) {
      console.error('Cost center yükleme hatası:', error);
    }
  };

  const handleCreate = () => {
    setEditingDraft(null);
    form.resetFields();
    form.setFieldsValue({ 
      fm_orani: 1.00, 
      tatil_orani: 1.00,
      is_active: 1,
      ucret_nevi: 'aylik'
    });
    setModalVisible(true);
  };

  const handleEdit = (record: PersonnelDraftContract) => {
    setEditingDraft(record);
    form.setFieldsValue({
      ...record,
      ucret_nevi: record.ucret_nevi || 'aylik',
      fm_orani: record.fm_orani || 1.00,
      tatil_orani: record.tatil_orani || 1.00
    });
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Silme Onayı',
      content: 'Bu taslak sözleşmeyi silmek istediğinizden emin misiniz?',
      okText: 'Evet',
      cancelText: 'Hayır',
      onOk: async () => {
        try {
          await draftContractsApi.delete(id);
          message.success('Taslak sözleşme silindi');
          loadDraftContracts();
        } catch (error: any) {
          if (error.response?.status === 400) {
            message.error(error.response.data.detail || 'Bu taslak sözleşme kullanımda, silinemez');
          } else {
            message.error('Silme işlemi başarısız');
          }
          console.error(error);
        }
      }
    });
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingDraft) {
        // Update
        await draftContractsApi.update(editingDraft.id, values as PersonnelDraftContractUpdate);
        message.success('Taslak sözleşme güncellendi');
      } else {
        // Create
        await draftContractsApi.create(values as PersonnelDraftContractCreate);
        message.success('Taslak sözleşme oluşturuldu');
      }
      
      setModalVisible(false);
      loadDraftContracts();
    } catch (error) {
      message.error('İşlem başarısız');
      console.error(error);
    }
  };

  const columns: ColumnsType<PersonnelDraftContract> = [
    {
      title: 'Personel Adı',
      key: 'personnel_name',
      width: 180,
      ellipsis: true,
      sorter: (a, b) => {
        const nameA = a.personnel ? `${a.personnel.ad} ${a.personnel.soyad}` : '';
        const nameB = b.personnel ? `${b.personnel.ad} ${b.personnel.soyad}` : '';
        return nameA.localeCompare(nameB, 'tr');
      },
      render: (_, record) => {
        if (record.personnel?.ad && record.personnel?.soyad) {
          return `${record.personnel.ad} ${record.personnel.soyad}`;
        }
        return '-';
      }
    },
    {
      title: 'TC No',
      dataIndex: 'tc_kimlik_no',
      key: 'tc_kimlik_no',
      width: 110,
      ellipsis: true,
      sorter: (a, b) => (a.tc_kimlik_no || '').localeCompare(b.tc_kimlik_no || '', 'tr')
    },
    {
      title: 'Ücret Nevi',
      dataIndex: 'ucret_nevi',
      key: 'ucret_nevi',
      width: 100,
      sorter: (a, b) => (a.ucret_nevi || '').localeCompare(b.ucret_nevi || '', 'tr'),
      render: (ucretNevi: string) => {
        const colorMap: Record<string, string> = {
          'aylik': 'blue',
          'sabit aylik': 'green',
          'gunluk': 'orange'
        };
        const labelMap: Record<string, string> = {
          'aylik': 'Aylık',
          'sabit aylik': 'Sabit',
          'gunluk': 'Günlük'
        };
        return <Tag color={colorMap[ucretNevi] || 'default'}>{labelMap[ucretNevi] || ucretNevi}</Tag>;
      }
    },
    {
      title: 'Net Ücret',
      dataIndex: 'net_ucret',
      key: 'net_ucret',
      width: 110,
      align: 'right',
      sorter: (a, b) => (a.net_ucret || 0) - (b.net_ucret || 0),
      render: (value: number | null) => value ? `₺${value.toLocaleString('tr-TR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}` : '-'
    },
    {
      title: 'FM',
      dataIndex: 'fm_orani',
      key: 'fm_orani',
      width: 60,
      align: 'center',
      sorter: (a, b) => (a.fm_orani || 0) - (b.fm_orani || 0),
      render: (value: number) => value || 1.00
    },
    {
      title: 'Tatil',
      dataIndex: 'tatil_orani',
      key: 'tatil_orani',
      width: 60,
      align: 'center',
      sorter: (a, b) => (a.tatil_orani || 0) - (b.tatil_orani || 0),
      render: (value: number) => value || 1.00
    },
    {
      title: 'Takvim',
      dataIndex: 'calisma_takvimi',
      key: 'calisma_takvimi',
      width: 80,
      sorter: (a, b) => (a.calisma_takvimi || '').localeCompare(b.calisma_takvimi || '', 'tr'),
      render: (takvim: string | null) => {
        if (!takvim) return '-';
        const labelMap: Record<string, string> = {
          'atipi': 'A Tipi',
          'btipi': 'B Tipi',
          'ctipi': 'C Tipi'
        };
        return <span style={{ fontSize: '12px' }}>{labelMap[takvim] || takvim}</span>;
      }
    },
    {
      title: 'Durum',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 70,
      align: 'center',
      sorter: (a, b) => (a.is_active || 0) - (b.is_active || 0),
      render: (isActive: number) => (
        <Tag color={isActive === 1 ? 'success' : 'error'}>
          {isActive === 1 ? 'Aktif' : 'Pasif'}
        </Tag>
      )
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 100,
      fixed: 'right' as const,
      render: (_: any, record: PersonnelDraftContract) => (
        <Space size="small">
          <Button 
            type="link" 
            icon={<EditOutlined />} 
            onClick={() => handleEdit(record)}
            size="small"
          />
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record.id)}
            size="small"
          />
        </Space>
      )
    }
  ];

  return (
    <>
      <style>
        {`
          .inactive-row {
            background-color: #f5f5f5 !important;
            opacity: 0.7;
          }
          .inactive-row:hover {
            background-color: #e8e8e8 !important;
          }
        `}
      </style>
      <Card 
      title="Taslak Sözleşmeler" 
      extra={
        <Space>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={loadDraftContracts}
          >
            Yenile
          </Button>
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={handleCreate}
          >
            Yeni Taslak
          </Button>
        </Space>
      }
    >
      <Table
        columns={columns}
        dataSource={draftContracts}
        rowKey="id"
        loading={loading}
        size="small"
        rowClassName={(record) => record.is_active === 0 ? 'inactive-row' : ''}
        scroll={{ x: 'max-content' }}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showTotal: (total) => `Toplam ${total} kayıt`
        }}
      />

      <Modal
        title={editingDraft ? 'Taslak Sözleşme Düzenle' : 'Yeni Taslak Sözleşme'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={handleSubmit}
        width={700}
        okText={editingDraft ? 'Güncelle' : 'Oluştur'}
        cancelText="İptal"
      >
        <Form form={form} layout="vertical">
          {!editingDraft && (
            <Form.Item 
              label="Personel" 
              name="personnel_id" 
              rules={[{ required: true, message: 'Personel seçiniz' }]}
            >
              <Select
                showSearch
                placeholder="Personel seçin"
                filterOption={(input, option) => {
                  const personnel = personnelList.find(p => p.id === option?.value);
                  if (personnel) {
                    const fullName = `${personnel.ad} ${personnel.soyad}`.toLowerCase();
                    return fullName.includes(input.toLowerCase());
                  }
                  return false;
                }}
              >
                {personnelList.map(person => (
                  <Select.Option key={person.id} value={person.id}>
                    {person.ad} {person.soyad}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          )}

          <Form.Item label="TC Kimlik No" name="tc_kimlik_no">
            <Input placeholder="TC Kimlik No (opsiyonel)" maxLength={11} />
          </Form.Item>

          <Form.Item 
            label="Ücret Nevi" 
            name="ucret_nevi"
            rules={[{ required: true, message: 'Ücret nevi seçiniz' }]}
          >
            <Select>
              <Select.Option value="aylik">Aylık</Select.Option>
              <Select.Option value="sabit aylik">Sabit Aylık</Select.Option>
              <Select.Option value="gunluk">Günlük</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="Net Ücret" name="net_ucret">
            <InputNumber
              style={{ width: '100%' }}
              placeholder="Net Ücret"
              min={0}
              precision={2}
              formatter={(value) => `₺ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={(value) => (parseFloat(value!.replace(/₺\s?|(,*)/g, '')) || 0) as any}
            />
          </Form.Item>

          <Form.Item label="FM Oranı" name="fm_orani">
            <InputNumber
              style={{ width: '100%' }}
              placeholder="FM Oranı"
              min={0}
              max={99.99}
              step={0.01}
              precision={2}
            />
          </Form.Item>

          <Form.Item label="Tatil Oranı" name="tatil_orani">
            <InputNumber
              style={{ width: '100%' }}
              placeholder="Tatil Oranı"
              min={0}
              max={99.99}
              step={0.01}
              precision={2}
            />
          </Form.Item>

          <Form.Item label="Masraf Merkezi" name="cost_center_id">
            <Select
              showSearch
              optionFilterProp="children"
              placeholder="Masraf Merkezi Seçin"
              allowClear
            >
              {costCenters.map(cc => (
                <Select.Option key={cc.id} value={cc.id}>
                  {cc.code} - {cc.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="Çalışma Takvimi" name="calisma_takvimi">
            <Select allowClear>
              <Select.Option value="atipi">A Tipi</Select.Option>
              <Select.Option value="btipi">B Tipi</Select.Option>
              <Select.Option value="ctipi">C Tipi</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item label="Durum" name="is_active">
            <Select>
              <Select.Option value={1}>Aktif</Select.Option>
              <Select.Option value={0}>Pasif</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
    </>
  );
}
