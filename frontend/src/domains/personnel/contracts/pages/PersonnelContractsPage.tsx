import { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag, Modal, Select, Form, Input, DatePicker, InputNumber, Tabs } from 'antd';
import { ReloadOutlined, EditOutlined, FileTextOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

// 🆕 V2 Domain imports
import { useContractsList, useUpdateContract } from '@/domains/personnel/contracts/hooks/useContracts';
import type { PersonnelContract } from '@/domains/personnel/contracts/types/contracts.types';
import { useContactsList } from '@/domains/partners/contacts/hooks/useContacts';
import { costCenterService, CostCenter } from '@/services/muhasebe.service';
import { PersonnelReportModal } from '@/domains/reporting/reports/components/PersonnelReportModal';
import apiClient from '@/services/api';
import dayjs from 'dayjs';
import DraftContractsTab from '../../draft_contracts/pages/DraftContractsTab';

const API_URL = 'http://localhost:8000/api/v2/personnel';

interface Period {
  donem: string;
  yil: number;
  ay: number;
  label: string;
  is_latest: boolean;
}

export default function PersonnelContractsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<string | undefined>(undefined);
  const [periods, setPeriods] = useState<Period[]>([]);
  const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
  const [selectedCostCenter, setSelectedCostCenter] = useState<number | undefined>(undefined);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingContract, setEditingContract] = useState<PersonnelContract | null>(null);
  const [form] = Form.useForm();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(100);
  const [sortField, setSortField] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<'ascend' | 'descend' | undefined>(undefined);
  const [reportModalVisible, setReportModalVisible] = useState(false);
  const [selectedPersonnel, setSelectedPersonnel] = useState<PersonnelContract | null>(null);
  
  // 🆕 V2 React Query hooks - selectedPeriod ve cost_center_id ile
  const { data: contractData, isLoading: loading, refetch } = useContractsList({
    donem: selectedPeriod,
    cost_center_id: selectedCostCenter,
    page: page,
    page_size: pageSize,
    order_by: sortField,
    order_direction: sortOrder === 'ascend' ? 'asc' : 'desc'
  });
  
  const updateContractMutation = useUpdateContract();
  
  // Taşeron contacts listesi (contact_type='Taşeron' olanlar)
  const { data: taseronData } = useContactsList({ 
    contact_type: 'Taşeron',
    is_active: true 
  });
  const taseronContacts = taseronData?.items || [];
  
  const contracts = contractData?.items || [];
  const total = contractData?.total || 0;
  
  // Dönemleri ve cost center'ları yükle
  useEffect(() => {
    loadPeriods();
    loadCostCenters();
  }, []);
  
  const loadPeriods = async () => {
    try {
      const response = await apiClient.get(`${API_URL}/contracts/periods`);
      setPeriods(response.data.periods || []);
      
      // En son dönemi otomatik seç
      if (response.data.latest_period) {
        setSelectedPeriod(response.data.latest_period.donem);
      }
    } catch (error) {
      console.error('Dönem yükleme hatası:', error);
    }
  };
  
  const loadCostCenters = async () => {
    try {
      const response = await costCenterService.getAll({ is_active: true });
      const data: any = response.data;
      setCostCenters(Array.isArray(data) ? data : data?.items || []);
    } catch (error) {
      console.error('Cost center yükleme hatası:', error);
    }
  };
  
  // Note: Ücret Nevi, Çalışma Takvimi, Maaş2 Tutar, Maaş Hesabı, FM Oranı, Tatil Oranı
  // artık personnel_draft_contracts tablosunda - Taslak Sözleşmeler tab'ından düzenlenebilir
  
  const handleEditContract = (contract: PersonnelContract) => {
    setEditingContract(contract);
    form.setFieldsValue({
      ...contract,
      ise_giris_tarihi: contract.ise_giris_tarihi ? dayjs(contract.ise_giris_tarihi) : null,
      isten_cikis_tarihi: contract.isten_cikis_tarihi ? dayjs(contract.isten_cikis_tarihi) : null,
    });
    setEditModalVisible(true);
  };
  
  const handleUpdateContract = async () => {
    try {
      const values = await form.validateFields();
      if (!editingContract) return;
      
      const updateData = {
        ...values,
        ise_giris_tarihi: values.ise_giris_tarihi ? values.ise_giris_tarihi.format('YYYY-MM-DD') : null,
        isten_cikis_tarihi: values.isten_cikis_tarihi ? values.isten_cikis_tarihi.format('YYYY-MM-DD') : null,
      };
      
      console.log('Gönderilen veri:', updateData);
      
      await updateContractMutation.mutateAsync({ id: editingContract.id, data: updateData });
      setEditModalVisible(false);
      setEditingContract(null);
      form.resetFields();
    } catch (error: any) {
      console.error('Güncelleme hatası:', error);
      console.error('Error message:', error.message);
      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error status:', error.response.status);
      }
    }
  };
  
  const loadContracts = () => {
    refetch();
  };


  const columns: ColumnsType<PersonnelContract> = [
    {
      title: 'Personel Adı Soyadı',
      key: 'personnel_name',
      dataIndex: 'personnel_ad', // dataIndex ekle ki sıralama çalışsın
      width: 200,
      fixed: 'left',
      sorter: true,
      sortOrder: sortField === 'personnel_ad' ? sortOrder : null,
      render: (_: any, record: PersonnelContract) => (
        <span>{record.personnel_ad} {record.personnel_soyad}</span>
      )
    },
    {
      title: 'TC Kimlik No',
      dataIndex: 'tc_kimlik_no',
      key: 'tc_kimlik_no',
      width: 120,
      sorter: true,
      sortOrder: sortField === 'tc_kimlik_no' ? sortOrder : null
    },
    {
      title: 'İşe Giriş',
      dataIndex: 'ise_giris_tarihi',
      key: 'ise_giris_tarihi',
      width: 120,
      sorter: true,
      sortOrder: sortField === 'ise_giris_tarihi' ? sortOrder : null,
      render: (val: string | null) => val ? new Date(val).toLocaleDateString('tr-TR') : '-'
    },
    {
      title: 'İşten Çıkış',
      dataIndex: 'isten_cikis_tarihi',
      key: 'isten_cikis_tarihi',
      width: 120,
      sorter: true,
      sortOrder: sortField === 'isten_cikis_tarihi' ? sortOrder : null,
      render: (val: string | null) => val ? new Date(val).toLocaleDateString('tr-TR') : '-'
    },
    {
      title: 'Bölüm',
      dataIndex: 'bolum',
      key: 'bolum',
      width: 200,
      ellipsis: true,
      sorter: true,
      sortOrder: sortField === 'bolum' ? sortOrder : null
    },
    {
      title: 'Masraf Merkezi',
      dataIndex: 'cost_center_name',
      key: 'cost_center_name',
      width: 200,
      render: (val: string | null) => val ? <Tag color="cyan">{val}</Tag> : '-'
    },
    {
      title: 'Departman',
      dataIndex: 'departman',
      key: 'departman',
      width: 150,
      sorter: true,
      sortOrder: sortField === 'departman' ? sortOrder : null,
      render: (val: string | null) => val ? <Tag color="blue">{val}</Tag> : '-'
    },
    {
      title: 'Taşeron',
      dataIndex: 'taseron_name',
      key: 'taseron_name',
      width: 150,
      sorter: true,
      sortOrder: sortField === 'taseron_name' ? sortOrder : null,
      render: (val: string | null) => val ? <Tag color="orange">{val}</Tag> : '-'
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_: any, record: PersonnelContract) => (
        <Select
          style={{ width: 130 }}
          placeholder="İşlemler"
          onSelect={(value) => {
            if (value === 'report') {
              setSelectedPersonnel(record);
              setReportModalVisible(true);
            } else if (value === 'edit') {
              handleEditContract(record);
            }
          }}
        >
          <Select.Option value="report">
            <FileTextOutlined style={{ marginRight: 6, color: '#1890ff' }} /> <span>Rapor</span>
          </Select.Option>
          <Select.Option value="edit">
            <EditOutlined style={{ marginRight: 6, color: '#fa8c16' }} /> <span>Düzenle</span>
          </Select.Option>
        </Select>
      )
    }
  ];

  // Resmi Sözleşmeler tab content
  const contractsTabContent = (
    <Card 
      title="Personel Sözleşmeleri"
        extra={
          <Space>
            <Select
              style={{ width: 220 }}
              placeholder="Dönem Seç"
              value={selectedPeriod}
              onChange={(value) => {
                setSelectedPeriod(value);
                setPage(1);
              }}
              allowClear
              onClear={() => {
                setSelectedPeriod(undefined);
                setPage(1);
              }}
            >
              {periods.map(p => (
                <Select.Option key={p.donem} value={p.donem}>
                  {p.label} {p.is_latest && <Tag color="green">Son</Tag>}
                </Select.Option>
              ))}
            </Select>
            <Select
              style={{ width: 220 }}
              placeholder="Masraf Merkezi Seç"
              value={selectedCostCenter}
              onChange={(value) => {
                setSelectedCostCenter(value);
                setPage(1);
              }}
              allowClear
              onClear={() => {
                setSelectedCostCenter(undefined);
                setPage(1);
              }}
              showSearch
              optionFilterProp="children"
            >
              {costCenters.map(cc => (
                <Select.Option key={cc.id} value={cc.id}>
                  {cc.name}
                </Select.Option>
              ))}
            </Select>
            <Button icon={<ReloadOutlined />} onClick={loadContracts} loading={loading}>
              Yenile
            </Button>
          </Space>
        }
      >
        <Table
          dataSource={contracts}
          columns={columns}
          rowKey="id"
          loading={loading}
          onChange={(pagination, _filters, sorter: any) => {
            // Sayfalama
            if (pagination.current !== page) {
              setPage(pagination.current || 1);
            }
            if (pagination.pageSize !== pageSize) {
              setPageSize(pagination.pageSize || 100);
              setPage(1);
            }
            // Sıralama
            if (sorter && sorter.field) {
              setSortField(sorter.field);
              setSortOrder(sorter.order);
            } else {
              setSortField(undefined);
              setSortOrder(undefined);
            }
          }}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Toplam ${total} sözleşme`,
            pageSizeOptions: ['50', '100', '200', '500']
          }}
          scroll={{ x: 1200 }}
          size="small"
        />

        {/* Düzenleme Modalı */}
        <Modal
        title={
          <div>
            <div>{editingContract ? `Sözleşme Düzenle - ${editingContract.personnel_ad} ${editingContract.personnel_soyad}` : "Sözleşme Düzenle"}</div>
          </div>
        }
        open={editModalVisible}
        onOk={handleUpdateContract}
        onCancel={() => {
          setEditModalVisible(false);
          setEditingContract(null);
          form.resetFields();
        }}
        width={800}
        okText="Güncelle"
        cancelText="İptal"
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item label="Bölüm" name="bolum">
            <Input />
          </Form.Item>
          
          <Form.Item label="İşe Giriş Tarihi" name="ise_giris_tarihi">
            <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
          </Form.Item>
          
          <Form.Item label="İşten Çıkış Tarihi" name="isten_cikis_tarihi">
            <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
          </Form.Item>
          
          {/* Note: Ücret Nevi, Çalışma Takvimi, Maaş2 Tutar, Maaş Hesabı, FM/Tatil Oranları */}
          {/* artık "Taslak Sözleşmeler" tabından düzenlenebilir */}
          
          <Form.Item label="Kanun Tipi" name="kanun_tipi">
            <Select>
              <Select.Option value="4857">4857</Select.Option>
              <Select.Option value="5510">5510</Select.Option>
            </Select>
          </Form.Item>
          
          <Space style={{ width: '100%' }} size="large">
            <Form.Item label="Net/Brüt" name="net_brut" style={{ flex: 1 }}>
              <Select>
                <Select.Option value="B">Brüt</Select.Option>
                <Select.Option value="N">Net</Select.Option>
              </Select>
            </Form.Item>
            
            <Form.Item label="Ücret" name="ucret" style={{ flex: 1 }}>
              <InputNumber style={{ width: '100%' }} min={0} />
            </Form.Item>
          </Space>
          
          <Form.Item label="IBAN" name="iban">
            <Input />
          </Form.Item>
          
          <Form.Item label="Departman" name="departman">
            <Select
              showSearch
              optionFilterProp="children"
              placeholder="Departman Seçin"
              allowClear
            >
              <Select.Option value="Ankraj Ekibi">Ankraj Ekibi</Select.Option>
              <Select.Option value="Asfaltlama Ekibi">Asfaltlama Ekibi</Select.Option>
              <Select.Option value="Bekçi Ekibi">Bekçi Ekibi</Select.Option>
              <Select.Option value="Beton Kesim Ekibi">Beton Kesim Ekibi</Select.Option>
              <Select.Option value="Demirci Ekibi">Demirci Ekibi</Select.Option>
              <Select.Option value="Döşeme Ekibi">Döşeme Ekibi</Select.Option>
              <Select.Option value="Elektrikçi Ekibi">Elektrikçi Ekibi</Select.Option>
              <Select.Option value="Fore Kazık Ekibi">Fore Kazık Ekibi</Select.Option>
              <Select.Option value="İdare Ekibi">İdare Ekibi</Select.Option>
              <Select.Option value="Kalıpçı Ekibi">Kalıpçı Ekibi</Select.Option>
              <Select.Option value="Kalıpçı Kolon Ekibi">Kalıpçı Kolon Ekibi</Select.Option>
              <Select.Option value="Kaynakçı Ekibi">Kaynakçı Ekibi</Select.Option>
              <Select.Option value="Merkez Ekibi">Merkez Ekibi</Select.Option>
              <Select.Option value="Operatör Ekibi">Operatör Ekibi</Select.Option>
              <Select.Option value="Saha Beton Ekibi">Saha Beton Ekibi</Select.Option>
              <Select.Option value="Stajyer Ekibi">Stajyer Ekibi</Select.Option>
              <Select.Option value="Şöför Ekibi">Şöför Ekibi</Select.Option>
              <Select.Option value="Yıkım Ekibi">Yıkım Ekibi</Select.Option>
            </Select>
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
                  {cc.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item label="Taşeron" name="taseron_id">
            <Select
              showSearch
              optionFilterProp="children"
              placeholder="Taşeron Seçin"
              allowClear
            >
              {taseronContacts.map(contact => (
                <Select.Option key={contact.id} value={contact.id}>
                  {contact.name}
                </Select.Option>
              ))}
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

      {/* Personel Cari Rapor Modalı */}
      <PersonnelReportModal
        visible={reportModalVisible}
        personnel={selectedPersonnel}
        selectedPeriod={selectedPeriod}
        onClose={() => setReportModalVisible(false)}
      />
    </Card>
  );

  // Main return with Tabs
  return (
    <div style={{ padding: 24 }}>
      <Tabs
        defaultActiveKey="contracts"
        items={[
          {
            key: 'contracts',
            label: 'Resmi Sözleşmeler',
            children: contractsTabContent
          },
          {
            key: 'drafts',
            label: 'Taslak Sözleşmeler',
            children: <DraftContractsTab />
          }
        ]}
      />
    </div>
  );
}
