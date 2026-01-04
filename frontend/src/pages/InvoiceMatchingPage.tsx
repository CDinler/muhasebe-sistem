import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Tag, 
  Space, 
  message, 
  Modal, 
  Descriptions,
  Statistic,
  Row,
  Col,
  Input,
  Popconfirm,
  Tooltip,
  Alert
} from 'antd';
import { 
  CheckOutlined, 
  CloseOutlined, 
  ThunderboltOutlined,
  EditOutlined,
  EyeOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';
import type { ColumnsType } from 'antd/es/table';

const API_BASE = 'http://localhost:8000/api/v1';

interface MatchSuggestion {
  payment: {
    transaction_id: number;
    transaction_number: string;
    date: string;
    description: string;
    amount: number;
    account_code: string;
  };
  invoice: {
    id: number;
    invoice_number: string;
    invoice_date: string;
    payable_amount: number;
    supplier_title: string;
  };
  score: number;
  reasons: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  invoice_numbers_in_desc: string[];
  dates_in_desc: string[];
}

const InvoiceMatchingPage: React.FC = () => {
  const [suggestions, setSuggestions] = useState<MatchSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoMatching, setAutoMatching] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState<MatchSuggestion | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editTransactionId, setEditTransactionId] = useState<number | null>(null);
  const [editInvoiceNumbers, setEditInvoiceNumbers] = useState('');

  const [stats, setStats] = useState({
    total: 0,
    high: 0,
    medium: 0
  });

  // Önerileri yükle
  const loadSuggestions = async (minScore: number = 70) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/invoice-matching/suggestions`, {
        params: { min_score: minScore, limit: 200 }
      });
      
      const data = response.data;
      setSuggestions(data);

      // İstatistikleri hesapla
      const high = data.filter((s: MatchSuggestion) => s.confidence === 'HIGH').length;
      const medium = data.filter((s: MatchSuggestion) => s.confidence === 'MEDIUM').length;
      
      setStats({
        total: data.length,
        high,
        medium
      });

      message.success(`${data.length} eşleştirme önerisi yüklendi`);
    } catch (error) {
      console.error('Öneri yükleme hatası:', error);
      message.error('Eşleştirme önerileri yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  // Otomatik eşleştirme
  const runAutoMatching = async () => {
    setAutoMatching(true);
    try {
      const response = await axios.post(`${API_BASE}/invoice-matching/auto-match`, null, {
        params: { min_score: 80 }
      });
      
      const { matched_count, matches } = response.data;
      
      Modal.success({
        title: 'Otomatik Eşleştirme Tamamlandı',
        content: (
          <div>
            <p><strong>{matched_count}</strong> ödeme otomatik olarak faturalarıyla eşleştirildi.</p>
            {matches.slice(0, 5).map((m: any, idx: number) => (
              <div key={idx} style={{ fontSize: '12px', marginTop: '8px' }}>
                • {m.transaction_number} → {m.invoice_number} (Skor: {m.score})
              </div>
            ))}
            {matches.length > 5 && <div style={{ marginTop: '8px' }}>... ve {matches.length - 5} diğer eşleşme</div>}
          </div>
        ),
        onOk: () => loadSuggestions()
      });
    } catch (error) {
      console.error('Otomatik eşleştirme hatası:', error);
      message.error('Otomatik eşleştirme başarısız');
    } finally {
      setAutoMatching(false);
    }
  };

  // Manuel onay
  const handleApprove = async (suggestion: MatchSuggestion) => {
    try {
      await axios.post(`${API_BASE}/invoice-matching/approve`, {
        transaction_id: suggestion.payment.transaction_id,
        invoice_number: suggestion.invoice.invoice_number
      });
      
      message.success('Eşleştirme onaylandı');
      loadSuggestions();
    } catch (error) {
      console.error('Onay hatası:', error);
      message.error('Eşleştirme onaylanamadı');
    }
  };

  // Manuel reddet
  const handleReject = async (suggestion: MatchSuggestion) => {
    try {
      await axios.post(`${API_BASE}/invoice-matching/reject`, {
        transaction_id: suggestion.payment.transaction_id,
        invoice_number: suggestion.invoice.invoice_number
      });
      
      message.info('Öneri reddedildi');
      // Listeden kaldır (sadece UI'dan)
      setSuggestions(prev => prev.filter(s => 
        s.payment.transaction_id !== suggestion.payment.transaction_id ||
        s.invoice.invoice_number !== suggestion.invoice.invoice_number
      ));
    } catch (error) {
      console.error('Red hatası:', error);
      message.error('Reddetme işlemi başarısız');
    }
  };

  // Detay modalı
  const showDetail = (suggestion: MatchSuggestion) => {
    setSelectedMatch(suggestion);
    setDetailModalVisible(true);
  };

  // Manuel düzenleme modalı
  const showEditModal = (transactionId: number, currentValue: string = '') => {
    setEditTransactionId(transactionId);
    setEditInvoiceNumbers(currentValue);
    setEditModalVisible(true);
  };

  // Manuel düzenleme kaydet
  const handleEditSave = async () => {
    if (editTransactionId === null) return;

    try {
      await axios.put(`${API_BASE}/invoice-matching/update-related-invoices`, {
        transaction_id: editTransactionId,
        invoice_numbers: editInvoiceNumbers
      });
      
      message.success('Fatura ilişkisi güncellendi');
      setEditModalVisible(false);
      loadSuggestions();
    } catch (error) {
      console.error('Düzenleme hatası:', error);
      message.error('Güncelleme başarısız');
    }
  };

  useEffect(() => {
    loadSuggestions();
  }, []);

  // Tablo kolonları
  const columns: ColumnsType<MatchSuggestion> = [
    {
      title: 'Güven',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 80,
      render: (conf: string, record: MatchSuggestion) => {
        const colors = { HIGH: 'green', MEDIUM: 'orange', LOW: 'default' };
        return (
          <Tag color={colors[conf as keyof typeof colors]}>
            {record.score}
          </Tag>
        );
      },
      sorter: (a, b) => b.score - a.score
    },
    {
      title: 'Ödeme Fiş',
      key: 'payment',
      width: 200,
      render: (_: any, record: MatchSuggestion) => (
        <div>
          <div><strong>{record.payment.transaction_number}</strong></div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            Tarih: {record.payment.date}
          </div>
          <div style={{ fontSize: '12px', color: '#1890ff', fontWeight: 'bold' }}>
            Tutar: {record.payment.amount.toLocaleString('tr-TR', {minimumFractionDigits: 2})} TL
          </div>
        </div>
      )
    },
    {
      title: 'Açıklama',
      key: 'description',
      width: 250,
      render: (_: any, record: MatchSuggestion) => (
        <div style={{ fontSize: '11px', color: '#666' }}>
          {record.payment.description?.substring(0, 100)}...
        </div>
      )
    },
    {
      title: 'Fatura',
      key: 'invoice',
      width: 200,
      render: (_: any, record: MatchSuggestion) => (
        <div>
          <div><strong>{record.invoice.invoice_number}</strong></div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            Tarih: {record.invoice.invoice_date}
          </div>
          <div style={{ fontSize: '12px', color: '#52c41a', fontWeight: 'bold' }}>
            Tutar: {record.invoice.payable_amount.toLocaleString('tr-TR', {minimumFractionDigits: 2})} TL
          </div>
        </div>
      )
    },
    {
      title: 'Tedarikçi',
      key: 'supplier',
      width: 180,
      render: (_: any, record: MatchSuggestion) => (
        <div style={{ fontSize: '11px', color: '#666' }}>
          {record.invoice.supplier_title?.substring(0, 50)}
        </div>
      )
    },
    {
      title: 'Tutar Farkı',
      key: 'amount_diff',
      width: 120,
      render: (_: any, record: MatchSuggestion) => {
        const diff = Math.abs(record.payment.amount - record.invoice.payable_amount);
        const diffPercent = (diff / record.invoice.payable_amount * 100).toFixed(2);
        const isMatch = diff < 1;
        return (
          <div style={{ fontSize: '11px' }}>
            <div style={{ color: isMatch ? '#52c41a' : '#ff4d4f' }}>
              {diff.toLocaleString('tr-TR', {minimumFractionDigits: 2})} TL
            </div>
            <div style={{ color: '#888' }}>
              ({diffPercent}%)
            </div>
          </div>
        );
      }
    },
    {
      title: 'Eşleşme Nedenleri',
      dataIndex: 'reasons',
      key: 'reasons',
      render: (reasons: string[]) => (
        <div>
          {reasons.map((reason, idx) => (
            <Tag key={idx} style={{ marginBottom: '4px' }}>{reason}</Tag>
          ))}
        </div>
      )
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 200,
      render: (_: any, record: MatchSuggestion) => (
        <Space>
          <Tooltip title="Detay">
            <Button 
              icon={<EyeOutlined />} 
              size="small"
              onClick={() => showDetail(record)}
            />
          </Tooltip>
          
          {record.confidence === 'MEDIUM' && (
            <>
              <Tooltip title="Onayla">
                <Popconfirm
                  title="Bu eşleştirmeyi onaylıyor musunuz?"
                  onConfirm={() => handleApprove(record)}
                  okText="Evet"
                  cancelText="Hayır"
                >
                  <Button 
                    type="primary" 
                    icon={<CheckOutlined />} 
                    size="small"
                  />
                </Popconfirm>
              </Tooltip>
              
              <Tooltip title="Reddet">
                <Popconfirm
                  title="Bu öneriyi reddetmek istediğinizden emin misiniz?"
                  onConfirm={() => handleReject(record)}
                  okText="Evet"
                  cancelText="Hayır"
                >
                  <Button 
                    danger 
                    icon={<CloseOutlined />} 
                    size="small"
                  />
                </Popconfirm>
              </Tooltip>
            </>
          )}
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1>Fatura-Ödeme Eşleştirme</h1>

      {/* İstatistikler */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Toplam Öneri" 
              value={stats.total}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Yüksek Güvenilirlik" 
              value={stats.high}
              valueStyle={{ color: '#52c41a' }}
              suffix={`/ ${stats.total}`}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Orta Güvenilirlik" 
              value={stats.medium}
              valueStyle={{ color: '#faad14' }}
              suffix={`/ ${stats.total}`}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Button 
              type="primary" 
              icon={<ThunderboltOutlined />}
              loading={autoMatching}
              onClick={runAutoMatching}
              block
              size="large"
              style={{ height: '100%' }}
            >
              Otomatik Eşleştir
              <div style={{ fontSize: '12px', fontWeight: 'normal' }}>
                (≥80 puan)
              </div>
            </Button>
          </Card>
        </Col>
      </Row>

      {/* Uyarı */}
      <Alert
        message="Eşleştirme Bilgisi"
        description={
          <div>
            <p>• <strong>Yüksek Güvenilirlik (≥80)</strong>: Otomatik eşleştirme önerilir (Fatura no + Tarih + Tutar eşleşmesi)</p>
            <p>• <strong>Orta Güvenilirlik (60-79)</strong>: Manuel onay gerekir (Kısmi eşleşme)</p>
            <p>• Birden fazla fatura için virgülle ayırarak ekleyebilirsiniz (örn: ABC123,DEF456)</p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: '24px' }}
      />

      {/* Tablo */}
      <Card 
        title="Eşleştirme Önerileri"
        extra={
          <Button 
            icon={<ReloadOutlined />} 
            onClick={() => loadSuggestions()}
            loading={loading}
          >
            Yenile
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={suggestions}
          loading={loading}
          rowKey={(record) => `${record.payment.transaction_id}-${record.invoice.invoice_number}`}
          pagination={{ 
            pageSize: 20,
            showTotal: (total) => `Toplam ${total} öneri`
          }}
        />
      </Card>

      {/* Detay Modal */}
      <Modal
        title="Eşleştirme Detayı"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            Kapat
          </Button>
        ]}
      >
        {selectedMatch && (
          <div>
            <Descriptions title="Ödeme Bilgileri" bordered column={2}>
              <Descriptions.Item label="Fiş No">{selectedMatch.payment.transaction_number}</Descriptions.Item>
              <Descriptions.Item label="Tarih">{selectedMatch.payment.date}</Descriptions.Item>
              <Descriptions.Item label="Tutar">{selectedMatch.payment.amount.toLocaleString('tr-TR')} TL</Descriptions.Item>
              <Descriptions.Item label="Hesap">{selectedMatch.payment.account_code}</Descriptions.Item>
              <Descriptions.Item label="Açıklama" span={2}>{selectedMatch.payment.description}</Descriptions.Item>
            </Descriptions>

            <Descriptions title="Fatura Bilgileri" bordered column={2} style={{ marginTop: '16px' }}>
              <Descriptions.Item label="Fatura No">{selectedMatch.invoice.invoice_number}</Descriptions.Item>
              <Descriptions.Item label="Tarih">{selectedMatch.invoice.invoice_date}</Descriptions.Item>
              <Descriptions.Item label="Tutar">{selectedMatch.invoice.payable_amount.toLocaleString('tr-TR')} TL</Descriptions.Item>
              <Descriptions.Item label="Tedarikçi" span={2}>{selectedMatch.invoice.supplier_title}</Descriptions.Item>
            </Descriptions>

            <Descriptions title="Eşleşme Analizi" bordered column={1} style={{ marginTop: '16px' }}>
              <Descriptions.Item label="Skor">
                <Tag color={selectedMatch.confidence === 'HIGH' ? 'green' : 'orange'}>
                  {selectedMatch.score}/100 - {selectedMatch.confidence}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Nedenler">
                {selectedMatch.reasons.map((r, idx) => <Tag key={idx}>{r}</Tag>)}
              </Descriptions.Item>
              <Descriptions.Item label="Açıklamada Bulunan Fatura No">
                {selectedMatch.invoice_numbers_in_desc.length > 0 
                  ? selectedMatch.invoice_numbers_in_desc.join(', ')
                  : 'Bulunamadı'}
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </Modal>

      {/* Manuel Düzenleme Modal */}
      <Modal
        title="Fatura İlişkisini Düzenle"
        open={editModalVisible}
        onOk={handleEditSave}
        onCancel={() => setEditModalVisible(false)}
        okText="Kaydet"
        cancelText="İptal"
      >
        <p>Fatura numaralarını virgülle ayırarak girin (örn: ABC123,DEF456)</p>
        <Input.TextArea
          value={editInvoiceNumbers}
          onChange={(e) => setEditInvoiceNumbers(e.target.value)}
          placeholder="OSE2025000016671,GNL2025000062152"
          rows={4}
        />
        <p style={{ marginTop: '8px', fontSize: '12px', color: '#888' }}>
          Boş bırakırsanız ilişki kaldırılır.
        </p>
      </Modal>
    </div>
  );
};

export default InvoiceMatchingPage;
