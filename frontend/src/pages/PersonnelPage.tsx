import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Space, Modal, Form, Input, message, Drawer, Card, Row, Col, Statistic, Descriptions, Select, DatePicker } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, TeamOutlined, IdcardOutlined, BankOutlined, FilterOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import axios from 'axios';
import dayjs from 'dayjs';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const { Option } = Select;

interface Personnel {
  id: number;
  tc_kimlik_no: string;
  ad: string;
  soyad: string;
  accounts_id: number | null;
  iban: string | null;
  created_at: string;
  updated_at: string;
  created_by: number | null;
  updated_by: number | null;
}

const PersonnelPage: React.FC = () => {
  const [personnel, setPersonnel] = useState<Personnel[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [editingPersonnel, setEditingPersonnel] = useState<Personnel | null>(null);
  const [selectedPersonnel, setSelectedPersonnel] = useState<Personnel | null>(null);
  const [form] = Form.useForm();
  
  // Filtre state'leri
  const [selectedPeriod, setSelectedPeriod] = useState<string | null>(null);

  useEffect(() => {
    fetchPersonnel();
  }, []);
  
  useEffect(() => {
    fetchPersonnel();
  }, [selectedPeriod]);

  const fetchPersonnel = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (selectedPeriod) params.period = selectedPeriod;
      
      const response = await axios.get(`${API_URL}/personnel/`, { params });
      // API artık { total, items } formatında dönüyor
      const data = response.data;
      if (data.items) {
        setPersonnel(data.items);
        setTotalCount(data.total);
        console.log(`Toplam personel: ${data.total}, Gösterilen: ${data.items.length}`);
      } else {
        // Eski format için backward compatibility
        setPersonnel(response.data);
        setTotalCount(response.data.length);
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Personel listesi yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingPersonnel(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record: Personnel) => {
    setEditingPersonnel(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    Modal.confirm({
      title: 'Personeli Sil',
      content: 'Bu personeli silmek istediğinizden emin misiniz?',
      okText: 'Evet',
      cancelText: 'Hayır',
      okType: 'danger',
      onOk: async () => {
        try {
          await axios.delete(`${API_URL}/personnel/${id}`);
          message.success('Personel başarıyla silindi');
          fetchPersonnel();
        } catch (error: any) {
          message.error(error.response?.data?.detail || 'Personel silinirken hata oluştu');
        }
      },
    });
  };

  const handleView = (record: Personnel) => {
    setSelectedPersonnel(record);
    setDrawerVisible(true);
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingPersonnel) {
        // Update
        await axios.put(`${API_URL}/personnel/${editingPersonnel.id}`, values);
        message.success('Personel başarıyla güncellendi');
      } else {
        // Create
        await axios.post(`${API_URL}/personnel/`, values);
        message.success('Personel başarıyla eklendi');
      }
      
      setModalVisible(false);
      form.resetFields();
      fetchPersonnel();
    } catch (error: any) {
      if (error.response) {
        message.error(error.response?.data?.detail || 'İşlem sırasında hata oluştu');
      }
    }
  };

  const columns: ColumnsType<Personnel> = [
    {
      title: 'TC Kimlik No',
      dataIndex: 'tc_kimlik_no',
      key: 'tc_kimlik_no',
      width: 130,
      fixed: 'left',
    },
    {
      title: 'Ad',
      dataIndex: 'ad',
      key: 'ad',
      width: 150,
    },
    {
      title: 'Soyad',
      dataIndex: 'soyad',
      key: 'soyad',
      width: 150,
    },
    {
      title: 'Hesap ID',
      dataIndex: 'accounts_id',
      key: 'accounts_id',
      width: 100,
      render: (id: number) => id || '-',
    },
    {
      title: 'IBAN',
      dataIndex: 'iban',
      key: 'iban',
      width: 200,
      render: (iban: string) => (
        iban ? (
          <span style={{ fontFamily: 'monospace' }}>{iban}</span>
        ) : (
          <Tag color="orange">Eksik</Tag>
        )
      ),
    },
    {
      title: 'Oluşturma',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 110,
      render: (date: string) => date ? dayjs(date).format('DD.MM.YYYY') : '-',
    },
    {
      title: 'İşlemler',
      key: 'actions',
      fixed: 'right',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
            size="small"
          >
            Görüntüle
          </Button>
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
      ),
    },
  ];

  // Aktif/pasif bilgisi artık Personnel tablosunda yok, PersonnelContract'ta

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="Toplam Personel"
                value={totalCount}
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="Kayıtlı Personel"
                value={personnel.length}
                prefix={<IdcardOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="Filtrelenmiş"
                value={selectedPeriod ? personnel.length : totalCount}
                prefix={<FilterOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Filtreler */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={8}>
            <DatePicker
              picker="month"
              placeholder="Dönem Seç (Örn: 2025 Aralık)"
              style={{ width: '100%' }}
              onChange={(date) => {
                if (date) {
                  setSelectedPeriod(date.format('YYYY-MM'));
                } else {
                  setSelectedPeriod(null);
                }
              }}
              format="YYYY MMMM"
            />
            <small style={{ color: '#999', marginTop: 4, display: 'block' }}>
              {selectedPeriod 
                ? `${selectedPeriod} döneminde çalışan personeller gösteriliyor` 
                : 'Tüm personeller gösteriliyor (dönem filtresi yok)'}
            </small>
          </Col>
          <Col span={8}>
            <Button
              type="default"
              icon={<FilterOutlined />}
              onClick={() => {
                setSelectedPeriod(null);
              }}
              style={{ marginRight: 8 }}
            >
              Filtreleri Temizle
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              Yeni Personel
            </Button>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={personnel}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1500 }}
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `Toplam ${total} personel`,
          }}
        />
      </Card>

      {/* Add/Edit Modal */}
      <Modal
        title={editingPersonnel ? 'Personel Düzenle' : 'Yeni Personel Ekle'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        width={800}
        okText={editingPersonnel ? 'Güncelle' : 'Ekle'}
        cancelText="İptal"
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="TC Kimlik No"
                name="tc_kimlik_no"
                rules={[
                  { required: true, message: 'TC Kimlik No zorunludur' },
                  { len: 11, message: 'TC Kimlik No 11 haneli olmalıdır' },
                  { pattern: /^\d+$/, message: 'Sadece rakam giriniz' },
                ]}
              >
                <Input placeholder="TC Kimlik No" maxLength={11} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Hesap ID"
                name="accounts_id"
              >
                <Input type="number" placeholder="Hesap ID (335.xxxx)" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Ad"
                name="ad"
                rules={[{ required: true, message: 'Ad zorunludur' }]}
              >
                <Input placeholder="Ad" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Soyad"
                name="soyad"
                rules={[{ required: true, message: 'Soyad zorunludur' }]}
              >
                <Input placeholder="Soyad" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="IBAN"
            name="iban"
            rules={[
              { len: 26, message: 'IBAN 26 karakter olmalıdır (TR dahil)' },
            ]}
          >
            <Input placeholder="TR00 0000 0000 0000 0000 0000 00" maxLength={26} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Detail Drawer */}
      <Drawer
        title="Personel Detayları"
        placement="right"
        width={600}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
      >
        {selectedPersonnel && (
          <div>
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="TC Kimlik No">
                {selectedPersonnel.tc_kimlik_no}
              </Descriptions.Item>
              <Descriptions.Item label="Ad Soyad">
                {selectedPersonnel.ad} {selectedPersonnel.soyad}
              </Descriptions.Item>
              <Descriptions.Item label="Hesap ID">
                {selectedPersonnel.accounts_id || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="IBAN">
                {selectedPersonnel.iban || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Oluşturan">
                {selectedPersonnel.created_by || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Kayıt Tarihi">
                {dayjs(selectedPersonnel.created_at).format('DD.MM.YYYY HH:mm')}
              </Descriptions.Item>
              <Descriptions.Item label="Güncelleyen">
                {selectedPersonnel.updated_by || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Güncelleme Tarihi">
                {dayjs(selectedPersonnel.updated_at).format('DD.MM.YYYY HH:mm')}
              </Descriptions.Item>
            </Descriptions>

            <div style={{ marginTop: 24 }}>
              <h3>335 Hesap Kodu</h3>
              <Card>
                <code style={{ fontSize: 16 }}>
                  335.{selectedPersonnel.tc_kimlik_no}
                </code>
                <div style={{ marginTop: 8, color: '#666' }}>
                  {selectedPersonnel.ad} {selectedPersonnel.soyad} - {selectedPersonnel.tc_kimlik_no}
                </div>
              </Card>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default PersonnelPage;
