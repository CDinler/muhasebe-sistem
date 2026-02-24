import { useState } from 'react';
import { Card, Upload, message, Select, Space, Alert } from 'antd';
import { InboxOutlined, InfoCircleOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import apiClient from '@/services/api';

const { Dragger } = Upload;
const API_URL = '/personnel';

export default function LucaBordroUploadPage() {
  const [uploadDonem, setUploadDonem] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [lastUploadInfo, setLastUploadInfo] = useState<{
    success: boolean;
    message: string;
    donem?: string;
  } | null>(null);

  const handleUpload = async (file: UploadFile) => {
    if (!uploadDonem) {
      message.error('Lütfen yüklemek istediğiniz dönemi seçin (örn: 2025-11)');
      return false;
    }

    const formData = new FormData();
    formData.append('file', file as any);

    setUploading(true);
    try {
      const res = await apiClient.post(`${API_URL}/luca-bordro/upload?donem=${uploadDonem}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      if (res.data.success) {
        message.success(res.data.message);
        setLastUploadInfo({
          success: true,
          message: res.data.message,
          donem: uploadDonem
        });
      }
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Yükleme hatası';
      message.error(errorMsg);
      setLastUploadInfo({
        success: false,
        message: errorMsg
      });
    } finally {
      setUploading(false);
    }
    
    return false;
  };

  // Dinamik dönem seçenekleri - sadece geçmiş ve mevcut ay
  const generateDonemOptions = () => {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1; // 0-indexed
    const options: { label: string; value: string }[] = [];
    
    // Son 2 yıl + mevcut yılın geçmiş ayları
    const startYear = currentYear - 2;
    
    for (let year = startYear; year <= currentYear; year++) {
      const maxMonth = year === currentYear ? currentMonth : 12;
      
      for (let month = 1; month <= maxMonth; month++) {
        const value = `${year}-${month.toString().padStart(2, '0')}`;
        options.push({ label: value, value });
      }
    }
    
    return options.reverse(); // En yeni dönem en üstte
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.xlsx,.xls',
    beforeUpload: handleUpload,
    showUploadList: false,
  };

  return (
    <div style={{ padding: 24 }}>
      <Card title="Luca Bordro Excel Yükleme" bordered={false}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Alert
            message="Luca Bordro Excel Dosyası Yükleme"
            description={
              <div>
                <p><strong>Kullanım Talimatları:</strong></p>
                <ol>
                  <li>Aşağıdaki dropdown'dan bordro dönemini seçin (örn: 2025-11)</li>
                  <li>Excel dosyasını sürükleyin veya tıklayarak Luca'dan indirdiğiniz bordro dosyasını seçin</li>
                  <li>Dosya otomatik olarak yüklenecek ve parse edilecektir</li>
                  <li>Yükleme tamamlandığında "Luca Bordro Listesi" sayfasından kayıtları görüntüleyebilirsiniz</li>
                </ol>
                <p><strong>Önemli Notlar:</strong></p>
                <ul>
                  <li>Excel dosyası Luca formatında olmalıdır (başlık satırı 9. satırda)</li>
                  <li>Aynı dönem için birden fazla yükleme yapılabilir</li>
                  <li>Aynı TC kimlik numarası ve giriş tarihi olan kayıtlar güncellenir</li>
                  <li>Sadece .xlsx ve .xls formatları desteklenmektedir</li>
                </ul>
              </div>
            }
            type="info"
            icon={<InfoCircleOutlined />}
          />

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              Dönem Seçiniz:
            </label>
            <Select
              style={{ width: 300 }}
              placeholder="Dönem seçin (YYYY-MM)"
              value={uploadDonem}
              onChange={setUploadDonem}
              allowClear
              showSearch
              options={generateDonemOptions()}
            />
          </div>

          <Dragger {...uploadProps} disabled={!uploadDonem || uploading}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">
              {uploadDonem 
                ? 'Excel dosyasını sürükleyin veya tıklayın'
                : 'Önce dönem seçiniz'}
            </p>
            <p className="ant-upload-hint">
              Luca Bordro Excel dosyası (.xlsx, .xls)
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

          {lastUploadInfo && (
            <Alert
              message={lastUploadInfo.success ? "Yükleme Başarılı" : "Yükleme Hatası"}
              description={
                <div>
                  <p>{lastUploadInfo.message}</p>
                  {lastUploadInfo.success && lastUploadInfo.donem && (
                    <p>
                      Dönem: <strong>{lastUploadInfo.donem}</strong>
                      <br />
                      <a href="/luca-bordro-list">Yüklenen kayıtları görüntülemek için tıklayın</a>
                    </p>
                  )}
                </div>
              }
              type={lastUploadInfo.success ? "success" : "error"}
              closable
              onClose={() => setLastUploadInfo(null)}
            />
          )}
        </Space>
      </Card>
    </div>
  );
}
