import React, { useState } from 'react';
import { Card, Button, DatePicker, message, Space, Upload, Modal, Table } from 'antd';
import { DownloadOutlined, FileExcelOutlined, ExperimentOutlined, UploadOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import axios from 'axios';
import dayjs, { Dayjs } from 'dayjs';

const PuantajPage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<Dayjs>(dayjs());
  const [downloading, setDownloading] = useState(false);
  const [testResults, setTestResults] = useState<any>(null);
  const [testModalVisible, setTestModalVisible] = useState(false);

  const handleDownloadTemplate = () => {
    setDownloading(true);
    try {
      const donem = selectedDate.format('YYYY-MM');
      const url = `http://localhost:8000/api/v1/puantaj/template/${donem}`;
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `Puantaj_Sablonu_${donem}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setTimeout(() => {
        message.success('Şablon indiriliyor...');
        setDownloading(false);
      }, 500);
    } catch (error) {
      console.error('Hata:', error);
      message.error('İndirme hatası');
      setDownloading(false);
    }
  };

  const handleTestUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      message.loading({ content: 'Test ediliyor...', key: 'test' });
      const response = await axios.post('http://localhost:8000/api/v1/puantaj/test-upload', formData);
      
      setTestResults(response.data);
      setTestModalVisible(true);
      message.success({ content: 'Test tamamlandı', key: 'test' });
    } catch (error: any) {
      message.error({ content: 'Test hatası: ' + (error.response?.data?.detail || error.message), key: 'test' });
    }
    return false;
  };

  const testColumns = [
    { title: 'TC', dataIndex: 'tckn', width: 120 },
    { title: 'Ad Soyad', dataIndex: 'ad_soyad', width: 200 },
    { title: 'Normal Gün', dataIndex: 'normal_gun', width: 100 },
    { title: 'FM Saat', dataIndex: 'fm_saat', width: 100 },
    { title: 'Sözleşme', dataIndex: 'sozlesme_var', width: 100, render: (val: boolean) => val ? '✅' : '❌' },
    { title: 'Sözleşme Ücret', dataIndex: 'sozlesme_ucret', width: 120, render: (val: number) => val.toFixed(2) },
    { title: 'Günlük Ücret', dataIndex: 'gunluk_ucret', width: 120, render: (val: number) => val.toFixed(2) },
    { title: 'Normal Gün Toplam', dataIndex: 'normal_gun_toplam', width: 150, render: (val: number) => val.toFixed(2) },
    { title: 'FM Ücreti', dataIndex: 'fm_ucret_saat', width: 120, render: (val: number) => val.toFixed(2) },
    { title: 'Luca Bordro', dataIndex: 'luca_bordro_var', width: 100, render: (val: boolean) => val ? '✅' : '❌' },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Card
        title={
          <Space>
            <FileExcelOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
            <span>Puantaj Yönetimi (TEST MODE)</span>
          </Space>
        }
      >
        <Space size="large" direction="vertical" style={{ width: '100%' }}>
          <Space size="large">
            <DatePicker
              picker="month"
              value={selectedDate}
              onChange={(date) => date && setSelectedDate(date)}
              format="YYYY-MM"
              size="large"
            />
            <Button
              type="primary"
              size="large"
              icon={<DownloadOutlined />}
              onClick={handleDownloadTemplate}
              loading={downloading}
            >
              Şablon İndir ({selectedDate.format('YYYY-MM')})
            </Button>
            <Upload
              beforeUpload={handleTestUpload}
              maxCount={1}
              accept=".xlsx,.xls"
              showUploadList={false}
            >
              <Button
                size="large"
                icon={<ExperimentOutlined />}
                style={{ background: '#faad14', borderColor: '#faad14', color: 'white' }}
              >
                TEST: Excel Yükle
              </Button>
            </Upload>
          </Space>
          
          <div style={{ marginTop: '16px', padding: '16px', background: '#fff7e6', borderRadius: '8px', border: '1px solid #faad14' }}>
            <h4>⚠️ TEST MODE - Veritabanına Kayıt Yapılmaz</h4>
            <ol>
              <li>Dönem seçin ve şablon indirin</li>
              <li>Excel'i doldurun (Normal Gün, FM Saat, vb.)</li>
              <li><strong>TEST: Excel Yükle</strong> ile hesaplamaları kontrol edin</li>
              <li>Sözleşme ücretleri, Luca bordro eşleşmelerini görün</li>
              <li>Sorun yoksa gerçek upload yapılacak (henüz hazır değil)</li>
            </ol>
          </div>
        </Space>
      </Card>

      <Modal
        title="🧪 Test Sonuçları - Veritabanına Kayıt Yapılmadı"
        open={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        width={1400}
        footer={[
          <Button key="close" onClick={() => setTestModalVisible(false)}>Kapat</Button>
        ]}
      >
        {testResults && (
          <div>
            <Space size="large" style={{ marginBottom: 16 }}>
              <div>Toplam Personel: <strong>{testResults.summary?.toplam_personel}</strong></div>
              <div>Sözleşmesi Var: <strong>{testResults.summary?.sozlesme_var}</strong></div>
              <div>Luca Bordro Var: <strong>{testResults.summary?.luca_bordro_var}</strong></div>
              {testResults.summary?.hatalar?.length > 0 && (
                <div style={{ color: 'red' }}>Hatalar: <strong>{testResults.summary.hatalar.length}</strong></div>
              )}
            </Space>

            {testResults.summary?.hatalar?.length > 0 && (
              <div style={{ marginBottom: 16, padding: 12, background: '#fff1f0', borderRadius: 4 }}>
                <h4>Hatalar:</h4>
                {testResults.summary.hatalar.slice(0, 10).map((err: string, i: number) => (
                  <div key={i} style={{ color: 'red' }}>• {err}</div>
                ))}
              </div>
            )}

            <Table
              columns={testColumns}
              dataSource={testResults.results || []}
              rowKey="tckn"
              scroll={{ x: 1200 }}
              pagination={{ pageSize: 20 }}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default PuantajPage;
