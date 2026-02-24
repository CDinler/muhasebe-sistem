import React, { useState } from 'react';
import { Upload, Card, message, Select, Space, Alert, Form } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import apiClient from '@/services/api';

const { Dragger } = Upload;

const MonthlyRecordsUploadPage: React.FC = () => {
  const [form] = Form.useForm();
  const [uploading, setUploading] = useState(false);
  const [selectedDonem, setSelectedDonem] = useState<string>('');

  const handleUpload = async (file: File) => {
    if (!selectedDonem) {
      message.error('Lütfen dönem seçiniz');
      return false;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('donem', selectedDonem);

    setUploading(true);
    try {
      const response = await apiClient.post('/personnel/monthly-records/upload-sicil', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        const data = response.data;
        
        // Başarı mesajı
        message.success(
          `✅ ${data.total_records} kayıt başarıyla işlendi!`,
          5
        );
        
        // Detaylı bilgi
        const details = [];
        if (data.created_personnel > 0) details.push(`Yeni personel: ${data.created_personnel}`);
        if (data.updated_personnel > 0) details.push(`Güncellenen personel: ${data.updated_personnel}`);
        if (data.created_records > 0) details.push(`Yeni sicil kaydı: ${data.created_records}`);
        if (data.updated_records > 0) details.push(`Güncellenen sicil: ${data.updated_records}`);
        if (data.created_contracts > 0) details.push(`Yeni sözleşme: ${data.created_contracts}`);
        if (data.updated_contracts > 0) details.push(`Güncellenen sözleşme: ${data.updated_contracts}`);
        
        if (details.length > 0) {
          message.info(details.join(' | '), 8);
        }
        
        // Hatalar varsa göster
        if (data.errors && data.errors.length > 0) {
          message.warning(
            `⚠️ ${data.errors.length} kayıtta hata oluştu. Konsolu kontrol edin.`,
            6
          );
          console.error('Upload errors:', data.errors);
        }
        
        form.resetFields();
        setSelectedDonem('');
      } else {
        message.error('Yükleme başarısız oldu');
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      message.error(error.response?.data?.detail || 'Yükleme sırasında hata oluştu');
    } finally {
      setUploading(false);
    }

    return false;
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    beforeUpload: handleUpload,
    showUploadList: false,
  };

  // Generate donem options for current and previous months
  const generateDonemOptions = () => {
    const options = [];
    const now = new Date();
    
    for (let i = 0; i < 12; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const yil = d.getFullYear();
      const ay = String(d.getMonth() + 1).padStart(2, '0');
      const donem = `${yil}-${ay}`;
      const label = `${d.toLocaleString('tr-TR', { month: 'long' })} ${yil}`;
      options.push({ value: donem, label });
    }
    
    return options;
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="Aylık Personel Sicil Yükleme" bordered={false}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Alert
            message="Personel Sicil Hakkında"
            description={
              <div>
                <p>Bu sayfadan Luca Personel Sicil Excel dosyasını yükleyebilirsiniz.</p>
                <p><strong>Yapılan işlemler:</strong></p>
                <ul>
                  <li>Yeni personeller otomatik olarak sisteme eklenir</li>
                  <li>Her personel için 335.* hesap kodu otomatik oluşturulur</li>
                  <li>Personel sözleşmeleri otomatik oluşturulur veya güncellenir</li>
                  <li>Aylık sicil kayıtları oluşturulur</li>
                  <li>Personel sözleşmelerindeki maaş bilgileri sicil dosyasından güncellenir</li>
                </ul>
                <p><strong>Excel formatı:</strong> Luca Personel Sicil standardı (Adı, Soyadı, TC Kimlik No, vb.)</p>
              </div>
            }
            type="info"
            showIcon
          />

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              Dönem Seçiniz:
            </label>
            <Select
              style={{ width: 300 }}
              placeholder="Dönem seçiniz"
              value={selectedDonem}
              onChange={setSelectedDonem}
              options={generateDonemOptions()}
            />
          </div>

          <Dragger {...uploadProps} disabled={!selectedDonem || uploading}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">
              {selectedDonem 
                ? 'Excel dosyasını sürükleyin veya tıklayın'
                : 'Önce dönem seçiniz'}
            </p>
            <p className="ant-upload-hint">
              Luca Personel Sicil Excel dosyası (.xlsx, .xls)
            </p>
          </Dragger>

          {uploading && (
            <Alert
              message="Yükleniyor..."
              description="Dosya işleniyor, lütfen bekleyin."
              type="warning"
              showIcon
            />
          )}
        </Space>
      </Card>
    </div>
  );
};

export default MonthlyRecordsUploadPage;
