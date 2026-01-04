import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  InputNumber,
  DatePicker,
  Select,
  Space,
  Tag,
  Statistic,
  Row,
  Col,
  Modal,
  Descriptions,
  message,
  Popconfirm,
  Upload,
  Progress,
  Radio,
  Tabs,
  Divider,
  Spin,
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  DeleteOutlined,
  ImportOutlined,
  EyeOutlined,
  UploadOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import dayjs from 'dayjs';

// 🆕 Yeni domain imports
import {
  useEInvoiceSummary,
  useEInvoices,
  useDeleteEInvoice,
  useUploadXML,
  useUploadPDF,
  usePreviewXML,
  useCreateTransaction,
  useTransactionPreview,
} from '@/domains/invoicing/einvoices/hooks/useEInvoices';
import { einvoiceAPI } from '@/domains/invoicing/einvoices/api/einvoice.api';
import type {
  EInvoice,
  EInvoiceSummary,
  EInvoiceFilters,
} from '@/domains/invoicing/einvoices/types/einvoice.types';

// Legacy services (geçici - muhasebe servisleri için)
import { costCenterService, CostCenter, accountService, Account, documentTypeService, documentSubtypeService, DocumentType, DocumentSubtype } from '../services/muhasebe.service';
import './EInvoicesPage.compact.css';

const { RangePicker } = DatePicker;
const { Option } = Select;

const EInvoicesPage: React.FC = () => {
    const [costCenters, setCostCenters] = useState<CostCenter[]>([]);
    const [costCenterLoading, setCostCenterLoading] = useState(false);
    const [accounts, setAccounts] = useState<Account[]>([]);
    const [accountsLoading, setAccountsLoading] = useState(false);
    const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
    const [documentSubtypes, setDocumentSubtypes] = useState<DocumentSubtype[]>([]);
    const [selectedDocumentTypeId, setSelectedDocumentTypeId] = useState<number | null>(null);
    const [selectedDocumentSubtypeId, setSelectedDocumentSubtypeId] = useState<number | null>(null);
    
    // Maliyet merkezlerini ve document types yükle
    useEffect(() => {
      const fetchCostCenters = async () => {
        setCostCenterLoading(true);
        try {
          const res = await costCenterService.getAll({ is_active: true });
          setCostCenters(res.data || []);
        } catch (e) {
          message.error('Maliyet merkezleri yüklenemedi');
        } finally {
          setCostCenterLoading(false);
        }
      };
      
      const fetchDocumentTypes = async () => {
        try {
          const res = await documentTypeService.getAll({ is_active: true });
          setDocumentTypes(res.data || []);
        } catch (e) {
          message.error('Belge tipleri yüklenemedi');
        }
      };
      
      const fetchDocumentSubtypes = async () => {
        try {
          const res = await documentSubtypeService.getAll({ is_active: true });
          setDocumentSubtypes(res.data || []);
        } catch (e) {
          message.error('Belge alt tipleri yüklenemedi');
        }
      };
      
      fetchCostCenters();
      fetchDocumentTypes();
      fetchDocumentSubtypes();
    }, []);
  
  // Hesap planını yükle
  useEffect(() => {
    const fetchAccounts = async () => {
      setAccountsLoading(true);
      try {
        const res = await accountService.getAll({ is_active: true });
        setAccounts(res.data || []);
      } catch (e) {
        message.error('Hesap planı yüklenemedi');
      } finally {
        setAccountsLoading(false);
      }
    };
    fetchAccounts();
  }, []);
  
  // ========== LOCAL STATE (UI ONLY) ==========
  const [selectedInvoice, setSelectedInvoice] = useState<EInvoice | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [isImportMode, setIsImportMode] = useState(false);
  const [importPreviewData, setImportPreviewData] = useState<any>(null);
  const [importPreviewLoading, setImportPreviewLoading] = useState(false);
  const [editableLines, setEditableLines] = useState<any[]>([]);
  const [editableTransactionNumber, setEditableTransactionNumber] = useState<string>('');
  
  // Fatura türü ve kategori seçimi için state'ler
  const [invoiceType, setInvoiceType] = useState<string>('Satış');
  const [invoiceLineCategories, setInvoiceLineCategories] = useState<{[key: string]: string}>({});
  const [invoiceLineAccounts, setInvoiceLineAccounts] = useState<{[key: string]: string}>({});
  const [fixedAssetCategories, setFixedAssetCategories] = useState<{[key: string]: string}>({});
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [xmlDirectionModalVisible, setXmlDirectionModalVisible] = useState(false);
  const [xmlPreviewModalVisible, setXmlPreviewModalVisible] = useState(false);
  const [pendingXmlFiles, setPendingXmlFiles] = useState<File[]>([]);
  const [selectedDirection, setSelectedDirection] = useState<'incoming' | 'outgoing'>('incoming');
  const [previewData, setPreviewData] = useState<any>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  
  // PDF Upload States
  const [pdfDirectionModalVisible, setPdfDirectionModalVisible] = useState(false);
  const [pendingPdfFiles, setPendingPdfFiles] = useState<File[]>([]);
  const [pdfDirection, setPdfDirection] = useState<'incoming' | 'outgoing' | 'incoming-archive' | 'outgoing-archive'>('incoming-archive');

  // Bulunduğumuz ayın tarih aralığını hesapla
  const currentMonthStart = dayjs().startOf('month').format('YYYY-MM-DD');
  const currentMonthEnd = dayjs().endOf('month').format('YYYY-MM-DD');

  // Filtreler - varsayılan olarak bulunduğumuz ay
  const [filters, setFilters] = useState<EInvoiceFilters>({
    skip: 0,
    limit: 50,
    invoice_category: 'incoming',
    date_from: currentMonthStart,
    date_to: currentMonthEnd,
  });

  // ========== REACT QUERY HOOKS ==========
  // 🆕 Summary (özet istatistikler)
  const { data: summary, isLoading: summaryLoading } = useEInvoiceSummary({
    date_from: filters.date_from,
    date_to: filters.date_to,
  });

  // 🆕 E-Invoice List (fatura listesi)
  const { data: einvoices = [], isLoading: loading, refetch: refetchInvoices } = useEInvoices(filters);

  // 🆕 Mutations
  const deleteInvoiceMutation = useDeleteEInvoice();
  const uploadXMLMutation = useUploadXML();
  const uploadPDFMutation = useUploadPDF();
  const previewXMLMutation = usePreviewXML();
  const createTransactionMutation = useCreateTransaction();
  const transactionPreviewMutation = useTransactionPreview();

  // Upload modal reset
  useEffect(() => {
    setUploadModalVisible(false);
    setUploadProgress(0);
    setUploadStatus('');
  }, [einvoices]); // Liste değiştiğinde upload modal'ı kapat

  // 🆕 Hesap seçimi değiştiğinde otomatik preview yenile
  useEffect(() => {
    if (isImportMode && selectedInvoice?.id) {
      const hasAnyAccount = Object.keys(invoiceLineAccounts).length > 0;
      if (hasAnyAccount) {
        const timeoutId = setTimeout(() => {
          refreshPreviewWithCategories();
        }, 300);
        
        return () => clearTimeout(timeoutId);
      }
    }
  }, [invoiceLineAccounts]);

  // ========== LEGACY FUNCTIONS (converted to use hooks) ==========
  const loadSummary = async () => {
    // 🔄 Artık hook kullanıyor, bu fonksiyon gereksiz ama uyumluluk için bırakıldı
    // Direkt summary state'i kullanılabilir
  };

  const loadEInvoices = async () => {
    // 🔄 Artık hook kullanıyor, refetchInvoices() ile tetiklenebilir
    await refetchInvoices();
  };

  const handleDelete = async (id: number) => {
    deleteInvoiceMutation.mutate(id, {
      onSuccess: () => {
        refetchInvoices();
      }
    });
  };

  const handleUploadXML = async (formData: FormData) => {
    setUploadModalVisible(true);
    setUploadStatus('Yükleniyor...');
    
    uploadXMLMutation.mutate(formData, {
      onSuccess: (data) => {
        setUploadStatus(`✅ Başarılı: ${data.imported_count} fatura`);
        setUploadProgress(100);
        refetchInvoices();
      },
      onError: () => {
        setUploadStatus('❌ Hata oluştu');
      }
    });
  };

  const handleUploadPDF = async (formData: FormData) => {
    setUploadModalVisible(true);
    setUploadStatus('Yükleniyor...');
    
    uploadPDFMutation.mutate(formData, {
      onSuccess: (data) => {
        setUploadStatus(`✅ Başarılı: ${data.processed_count} PDF`);
        setUploadProgress(100);
        refetchInvoices();
      },
      onError: () => {
        setUploadStatus('❌ Hata oluştu');
      }
    });
  };

  const handlePreviewXML = async (formData: FormData) => {
    setPreviewLoading(true);
    
    previewXMLMutation.mutate(formData, {
      onSuccess: (data) => {
        setPreviewData(data);
        setXmlPreviewModalVisible(true);
        setPreviewLoading(false);
      },
      onError: () => {
        setPreviewLoading(false);
      }
    });
  };

  const handleCreateTransaction = async (invoiceId: number, data: any) => {
    createTransactionMutation.mutate(
      { invoiceId, data },
      {
        onSuccess: () => {
          setDetailModalVisible(false);
          setIsImportMode(false);
          refetchInvoices();
        }
      }
    );
  };

  // 🆕 Kategorizasyon değiştiğinde preview'ı yenile
  const refreshPreviewWithCategories = async () => {
    if (!selectedInvoice?.id) return;
    
    try {
      setImportPreviewLoading(true);
      
      // Fatura satırları mapping'i oluştur (TÜM BİLGİLERİ GÖNDER)
      const invoiceLinesMapping = selectedInvoice?.invoice_lines?.map((line: any, idx: number) => ({
        line_id: String(idx + 1),
        category: invoiceLineCategories[line.id],
        account_code: invoiceLineAccounts[line.id],
        item_name: line.item_name,
        quantity: line.quantity,
        unit_price: line.unit_price,
        line_total: line.line_total,
      })) || [];
      
      // Kategori mapping ile preview al
      const previewData = await einvoiceAPI.previewImport(selectedInvoice.id, {
        invoice_lines_mapping: invoiceLinesMapping,
        cost_center_id: selectedInvoice.cost_center_id
      });
      
      setImportPreviewData(previewData);
      setEditableLines(previewData.transaction?.lines || []);
      setImportPreviewLoading(false);
    } catch (error: any) {
      setImportPreviewLoading(false);
      message.error(error.response?.data?.detail || 'Import önizlemesi yüklenemedi');
    }
  };

  const handleViewDetail = async (invoice: EInvoice) => {
    try {
      // API'den tam detayı çek (invoice_lines dahil)
      const response = await einvoiceAPI.getEInvoice(invoice.id);
      console.log('Fatura detayı:', response);
      console.log('invoice_lines:', response.invoice_lines);
      setSelectedInvoice(response);
      setDetailModalVisible(true);
    } catch (error) {
      console.error('Detay yükleme hatası:', error);
      setSelectedInvoice(invoice);
      setDetailModalVisible(true);
    }
  };

  const handleImport = async (id: number) => {
    try {
      // Faturayı bul ve detay modalını import modunda aç
      const invoice = einvoices.find(inv => inv.id === id);
      if (!invoice) {
        message.error('Fatura bulunamadı');
        return;
      }
      
      // Detaylı fatura bilgisini al
      const response = await einvoiceAPI.getEInvoice(id);
      console.log('📋 Import için fatura detayı:', response);
      console.log('📋 Invoice lines:', response.invoice_lines);
      console.log('📋 Tax details:', response.tax_details);
      setSelectedInvoice(response);
      
      // Import preview verilerini al
      setImportPreviewLoading(true);
      const previewData = await einvoiceAPI.previewImport(id);
      setImportPreviewData(previewData);
      
      // Düzenlenebilir satırları set et
      setEditableLines(previewData.transaction?.lines || []);
      setEditableTransactionNumber(previewData.transaction?.number || '');
      
      // Fatura türünü XML'den al - varsayılan invoice_type veya invoice_profile
      const defaultInvoiceType = response.invoice_type || 'Satış';
      setInvoiceType(defaultInvoiceType);
      
      // Kategori state'lerini resetle
      setInvoiceLineCategories({});
      setInvoiceLineAccounts({});
      setFixedAssetCategories({});
      
      // Cari hesabı varsayılan seç (320'li hesap - preview'dan gelen)
      if (previewData.contact?.code) {
        // Preview'daki supplier account'u bul (320'li)
        const supplierLine = previewData.transaction?.lines?.find((line: any) => 
          line.account_code?.startsWith('320')
        );
        if (supplierLine) {
          console.log('🏦 Varsayılan cari hesap:', supplierLine.account_code);
        }
      }
      
      // Import modunda detay modalını aç
      setIsImportMode(true);
      setDetailModalVisible(true);
      setImportPreviewLoading(false);
    } catch (error: any) {
      setImportPreviewLoading(false);
      message.error(error.response?.data?.detail || 'Import önizlemesi yüklenemedi');
    }
  };

  // 🆕 Kategorizasyon değiştiğinde preview'ı yenile
  const refreshPreviewWithCategories = async () => {
    if (!selectedInvoice?.id) return;
    
    try {
      setImportPreviewLoading(true);
      
      // Fatura satırları mapping'i oluştur (TÜM BİLGİLERİ GÖNDER)
      const invoiceLinesMapping = selectedInvoice?.invoice_lines?.map((line: any, idx: number) => ({
        line_id: String(idx + 1),  // XML'deki satır sırası
        category: invoiceLineCategories[line.id],
        account_code: invoiceLineAccounts[line.id],
        item_name: line.item_name,  // TEKNOBOND 401 P - 410 ML gibi
        quantity: line.quantity,
        unit_price: line.unit_price,
        line_total: line.line_total,
      })) || [];
      
      // Kategori mapping ile preview al
      const previewData = await einvoiceAPI.previewImport(selectedInvoice.id, {
        invoice_lines_mapping: invoiceLinesMapping,
        cost_center_id: selectedInvoice.cost_center_id
      });
      
      setImportPreviewData(previewData);
      setEditableLines(previewData.transaction?.lines || []);
      setImportPreviewLoading(false);
    } catch (error: any) {
      setImportPreviewLoading(false);
      message.error(error.response?.data?.detail || 'Import önizlemesi yüklenemedi');
    }
  };

  const handleConfirmImport = async () => {
    if (!importPreviewData?.invoice?.id) return;
    
    try {
      setImportPreviewLoading(true);
      
      // Fatura satırları mapping'i oluştur
      const invoiceLinesMapping = selectedInvoice?.invoice_lines?.map((line: any) => ({
        line_id: line.id,
        category: invoiceLineCategories[line.id],
        account_code: invoiceLineAccounts[line.id],
        fixed_asset_category: fixedAssetCategories[line.id],
        item_name: line.item_name,
        line_total: line.line_total,
      })) || [];
      
      // Düzenlenmiş veriyi gönder - TÜM ALANLARI EKLE
      const customData = {
        invoice_type: invoiceType,
        transaction_number: editableTransactionNumber,
        lines: editableLines,
        invoice_lines_mapping: invoiceLinesMapping,
        cost_center_id: selectedInvoice.cost_center_id,
        document_type_id: selectedDocumentTypeId || importPreviewData.transaction?.document_type_id,
        document_subtype_id: selectedDocumentSubtypeId || importPreviewData.transaction?.document_subtype_id,
      };
      
      const result = await einvoiceAPI.importToAccounting(
        importPreviewData.invoice.id,
        customData
      );
      
      message.success(result.message || 'Import başarılı');
      setDetailModalVisible(false);
      setIsImportMode(false);
      setImportPreviewData(null);
      setSelectedInvoice(null);
      loadEInvoices();
      loadSummary();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Import başarısız');
    } finally {
      setImportPreviewLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      setLoading(true);
      setUploadModalVisible(true);
      setUploadProgress(0);
      setUploadStatus('Dosya yükleniyor...');

      // Simüle edilmiş progress (backend gerçek progress dönmüyor)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + 10;
        });
      }, 500);

      const result = await einvoiceAPI.uploadFile(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus(`✅ Tamamlandı! ${result.imported_count} fatura yüklendi`);

      setTimeout(() => {
        setUploadModalVisible(false);
        message.success(result.message || 'Dosya başarıyla yüklendi');
        
        if (result.errors && result.errors.length > 0) {
          Modal.warning({
            title: 'Bazı satırlarda hata oluştu',
            content: (
              <div>
                <p>{result.imported_count} kayıt eklendi, {result.error_count} hata</p>
                <ul>
                  {result.errors.slice(0, 10).map((err: string, idx: number) => (
                    <li key={idx}>{err}</li>
                  ))}
                  {result.errors.length > 10 && <li>... ve {result.errors.length - 10} hata daha</li>}
                </ul>
              </div>
            ),
          });
        }
        
        loadEInvoices();
        loadSummary();
      }, 1500);
    } catch (error: any) {
      setUploadStatus('❌ Hata: ' + (error.response?.data?.detail || 'Dosya yüklenemedi'));
      setTimeout(() => setUploadModalVisible(false), 3000);
      message.error(error.response?.data?.detail || 'Dosya yüklenemedi');
    } finally {
      setLoading(false);
    }
    return false; // Otomatik upload'u engelle
  };

  // PDF Upload Handler
  const handlePDFUpload = async (files: File[], direction: 'incoming' | 'outgoing' | 'incoming-archive' | 'outgoing-archive') => {
    try {
      setLoading(true);
      setUploadModalVisible(true);
      setUploadProgress(0);
      setUploadStatus(`${files.length} PDF dosyası işleniyor...`);

      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + 5;
        });
      }, 300);

      let successCount = 0;
      let errorCount = 0;
      let warningCount = 0;  // Uyarılı ama kaydedilmiş
      const errors: string[] = [];
      const warnings: string[] = [];

      // PDF'leri paralel yükle (her seferinde 10 dosya)
      const BATCH_SIZE = 10;
      let processedCount = 0;

      for (let i = 0; i < files.length; i += BATCH_SIZE) {
        const batch = files.slice(i, i + BATCH_SIZE);
        setUploadStatus(`PDF ${processedCount + 1}-${Math.min(processedCount + batch.length, files.length)}/${files.length} işleniyor...`);

        // Batch içindeki dosyaları paralel yükle
        const results = await Promise.allSettled(
          batch.map(file => 
            einvoiceAPI.uploadPDF(file, direction)
              .then(result => ({ file, result, success: true }))
              .catch((err: any) => ({ 
                file, 
                error: err.response?.data?.detail || 'Yükleme hatası',
                success: false 
              }))
          )
        );

        // Sonuçları işle
        results.forEach((promiseResult) => {
          if (promiseResult.status === 'fulfilled') {
            const { file, result, success, error } = promiseResult.value;
            
            if (success && result.success) {
              if (result.warnings && result.warnings.length > 0) {
                warningCount++;
                warnings.push(`${file.name}: ${result.warnings.join(', ')}`);
              } else {
                successCount++;
              }
            } else if (success && !result.success) {
              errorCount++;
              const errorMsg = `${file.name}: ${result.errors?.join(', ') || 'Bilinmeyen hata'}`;
              errors.push(errorMsg);
              console.error('PDF Upload Failed:', errorMsg);
            } else if (!success) {
              errorCount++;
              const errorMsg = `${file.name}: ${error}`;
              errors.push(errorMsg);
              console.error('PDF Upload Error:', errorMsg);
            }
          } else {
            errorCount++;
            const errorMsg = `Beklenmeyen hata`;
            errors.push(errorMsg);
            console.error('Promise Error:', promiseResult.reason);
          }
        });

        processedCount += batch.length;
        setUploadProgress(Math.min(90, (processedCount / files.length) * 90));
      }
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      const totalSuccess = successCount + warningCount;
      
      if (totalSuccess > 0 && errorCount === 0) {
        if (warningCount > 0) {
          setUploadStatus(`✅ ${totalSuccess} PDF yüklendi (${warningCount} uyarılı)`);
          setTimeout(() => {
            setUploadModalVisible(false);
            Modal.info({
              title: 'PDF Yükleme Başarılı',
              content: (
                <div>
                  <p><strong>{totalSuccess}</strong> PDF fatura kaydedildi.</p>
                  {warningCount > 0 && (
                    <>
                      <p><strong>{warningCount}</strong> faturada doğrulama uyarısı var (tutar uyumsuzluğu vb.):</p>
                      <ul style={{ maxHeight: 300, overflow: 'auto', fontSize: 11 }}>
                        {warnings.map((warn, idx) => (
                          <li key={idx}>{warn}</li>
                        ))}
                      </ul>
                      <p style={{ color: '#1890ff' }}>💡 Faturalar kaydedildi, ancak manuel kontrol önerilir.</p>
                    </>
                  )}
                </div>
              ),
            });
            loadEInvoices();
            loadSummary();
          }, 1500);
        } else {
          setUploadStatus(`✅ Başarılı! ${successCount} PDF faturası eklendi`);
          setTimeout(() => {
            setUploadModalVisible(false);
            message.success(`${successCount} PDF fatura kaydedildi`);
            loadEInvoices();
            loadSummary();
          }, 1500);
        }
      } else if (totalSuccess > 0 && errorCount > 0) {
        setUploadStatus(`⚠️ ${totalSuccess} başarılı, ${errorCount} hatalı`);
        setTimeout(() => {
          setUploadModalVisible(false);
          Modal.warning({
            title: 'Kısmi Başarı',
            content: (
              <div>
                <p><strong>{totalSuccess}</strong> PDF başarıyla yüklendi{warningCount > 0 ? ` (${warningCount} uyarılı)` : ''}.</p>
                <p><strong>{errorCount}</strong> PDF'de hata oluştu:</p>
                <ul style={{ maxHeight: 300, overflow: 'auto' }}>
                  {errors.map((err, idx) => (
                    <li key={idx}>{err}</li>
                  ))}
                </ul>
              </div>
            ),
          });
          loadEInvoices();
          loadSummary();
        }, 1500);
      } else {
        setUploadStatus('❌ Tüm PDF\'ler hatalı');
        setTimeout(() => {
          setUploadModalVisible(false);
          Modal.error({
            title: 'PDF Yükleme Hatası',
            content: (
              <div>
                <p>Hiçbir PDF yüklenemedi:</p>
                <ul style={{ maxHeight: 300, overflow: 'auto' }}>
                  {errors.map((err, idx) => (
                    <li key={idx}>{err}</li>
                  ))}
                </ul>
              </div>
            ),
          });
        }, 1500);
      }
    } catch (error: any) {
      setUploadStatus('❌ Hata: ' + (error.message || 'PDF yüklenemedi'));
      setTimeout(() => setUploadModalVisible(false), 3000);
      message.error('PDF dosyaları yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleXMLUpload = async (fileList: File[], direction: 'incoming' | 'outgoing') => {
    try {
      setLoading(true);
      setUploadModalVisible(true);
      setUploadProgress(0);
      setUploadStatus(`${fileList.length} XML dosyası yükleniyor...`);

      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + 10;
        });
      }, 500);

      const result = await einvoiceAPI.uploadXML(fileList, direction);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus(`✅ Tamamlandı! ${result.imported_count} fatura eklendi`);

      setTimeout(() => {
        setUploadModalVisible(false);
        message.success(result.message || 'XML dosyaları yüklendi');
        
        if (result.errors && result.errors.length > 0) {
          Modal.warning({
            title: 'Bazı XML dosyalarında hata',
            content: (
              <div>
                <p>
                  {result.imported_count} fatura eklendi
                  {result.skipped_count > 0 && `, ${result.skipped_count} duplicate atlandı`}
                  {result.error_count > 0 && `, ${result.error_count} hata`}
                </p>
                {result.errors.length > 0 && (
                  <ul style={{ maxHeight: 300, overflow: 'auto' }}>
                    {result.errors.slice(0, 20).map((err: string, idx: number) => (
                      <li key={idx}><small>{err}</small></li>
                    ))}
                    {result.errors.length > 20 && <li>... ve {result.errors.length - 20} hata daha</li>}
                  </ul>
                )}
              </div>
            ),
          });
        }
        
        loadEInvoices();
        loadSummary();
      }, 1500);
    } catch (error: any) {
      setUploadStatus('❌ Hata: ' + (error.response?.data?.detail || 'XML yüklenemedi'));
      setTimeout(() => setUploadModalVisible(false), 3000);
      message.error(error.response?.data?.detail || 'XML dosyaları yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const columns: ColumnsType<EInvoice> = [
    {
      title: 'Fatura No',
      dataIndex: 'invoice_number',
      key: 'invoice_number',
      width: 90,
      render: (text: string, record: EInvoice) => (
        <div style={{ fontSize: 12, lineHeight: '1.3' }}>
          <div style={{ fontWeight: 600 }}>{text}</div>
          <div style={{ fontSize: 11, color: '#666' }}>ETTN: {record.invoice_uuid?.substring(0, 8)}...</div>
        </div>
      ),
    },
    {
      title: 'Fatura Tarihi',
      dataIndex: 'issue_date',
      key: 'issue_date',
      width: 75,
      sorter: (a, b) => {
        // Önce signing_time'a göre sırala (varsa), sonra issue_date
        const aTime = a.signing_time || a.issue_date;
        const bTime = b.signing_time || b.issue_date;
        return dayjs(aTime).unix() - dayjs(bTime).unix();
      },
      defaultSortOrder: 'descend',
      render: (date: string, record: EInvoice) => (
        <div style={{ fontSize: 12, lineHeight: '1.3' }}>
          <div style={{ fontSize: 10, color: '#999' }}>Fatura Tarihi:</div>
          <div>{date ? dayjs(date).format('DD.MM.YYYY') : '-'}</div>
          {record.signing_time && (
            <>
              <div style={{ fontSize: 10, color: '#999', marginTop: 2 }}>Alınma Tarihi:</div>
              <div>{dayjs(record.signing_time).format('DD.MM.YYYY HH:mm')}</div>
            </>
          )}
        </div>
      ),
    },
    {
      title: 'Gönderen Unvan',
      key: 'partner_name',
      width: 160,
      render: (_, record) => {
        const name = filters.invoice_category?.startsWith('incoming') 
          ? record.supplier_name 
          : record.customer_name;
        const taxNumber = filters.invoice_category?.startsWith('incoming')
          ? record.supplier_tax_number
          : record.customer_tax_number;
        // IBAN: Önce contact'tan, yoksa XML'den
        const iban = record.contact_iban || record.supplier_iban;
        
        return (
          <div style={{ fontSize: 12, lineHeight: '1.3' }}>
            <div style={{ fontWeight: 500, whiteSpace: 'normal', wordBreak: 'break-word', maxHeight: '2.6em', overflow: 'hidden' }}>{name || '-'}</div>
            <div style={{ fontSize: 11, color: '#666' }}>VKN/TCKN: {taxNumber || '-'}</div>
            {iban && (
              <div style={{ fontSize: 11, color: '#1890ff', marginTop: 2 }}>
                IBAN: {iban}
              </div>
            )}
          </div>
        );
      },
    },
    {
      title: 'Mal/Hiz & Vhtt',
      key: 'amounts',
      width: 85,
      align: 'right',
      render: (_, record) => (
        <div style={{ fontSize: 12, lineHeight: '1.3', textAlign: 'right' }}>
          <div style={{ fontSize: 11, color: '#999' }}>Mal/Hiz Toplam:</div>
          <div style={{ fontSize: 11 }}>{new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(record.line_extension_amount || 0)} TRY</div>
          <div style={{ fontSize: 11, color: '#999', marginTop: 2 }}>Vergi Hariç:</div>
          <div style={{ fontSize: 11 }}>{new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(record.tax_exclusive_amount || record.line_extension_amount || 0)} TRY</div>
        </div>
      ),
    },
    {
      title: 'Toplam KDV',
      dataIndex: 'total_tax_amount',
      key: 'vat_total',
      width: 75,
      align: 'right',
      render: (amount: number) => (
        <div style={{ fontSize: 12, lineHeight: '1.3', textAlign: 'right' }}>
          <div style={{ fontWeight: 600 }}>{new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(amount || 0)}</div>
          <div style={{ fontSize: 10, color: '#999' }}>TRY</div>
        </div>
      ),
    },
    {
      title: 'Ödenecek Tutar',
      dataIndex: 'payable_amount',
      key: 'payable_amount',
      width: 85,
      align: 'right',
      render: (amount: number) => (
        <div style={{ fontSize: 12, lineHeight: '1.3', textAlign: 'right' }}>
          <div style={{ fontWeight: 600 }}>{new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2 }).format(amount)}</div>
          <div style={{ fontSize: 10, color: '#999' }}>TRY</div>
        </div>
      ),
    },
    {
      title: 'Senaryo Türü',
      key: 'scenario',
      width: 70,
      render: (_, record) => {
        const profileMap: Record<string, { text: string; color: string }> = {
          'TICARIFATURA': { text: 'TİCARİFATURA', color: 'blue' },
          'TEMELFATURA': { text: 'TEMELFATURA', color: 'green' },
          'EARSIVFATURA': { text: 'E-ARŞİV', color: 'purple' },
        };
        const profileInfo = profileMap[record.invoice_profile || ''] || { text: record.invoice_profile || '-', color: 'default' };
        const cc = costCenters.find(c => c.id === record.cost_center_id);
        
        return (
          <div style={{ fontSize: 12, lineHeight: '1.3' }}>
            <Tag color={profileInfo.color} style={{ fontSize: 10, padding: '0 3px', margin: 0 }}>{profileInfo.text}</Tag>
            <div style={{ fontSize: 11, color: '#666', marginTop: 2 }}>{record.invoice_type || 'SATIS'}</div>
            {cc && <div style={{ fontSize: 11, color: '#999', marginTop: 2 }}>{cc.name}</div>}
          </div>
        );
      },
    },
    {
      title: 'Durum',
      dataIndex: 'transaction_id',
      key: 'transaction_id',
      width: 80,
      render: (transaction_id: number | null) => {
        if (transaction_id) {
          return (
            <div style={{ fontSize: 12, lineHeight: '1.3' }}>
              <Tag color="green" style={{ fontSize: 10, margin: 0 }}>İŞLENDİ</Tag>
            </div>
          );
        }
        return (
          <div style={{ fontSize: 12, lineHeight: '1.3' }}>
            <Tag color="orange" style={{ fontSize: 10, margin: 0 }}>BEKLEMEDE</Tag>
          </div>
        );
      },
    },
    {
      title: 'İşlemler',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space size="small" style={{ width: '100%' }}>
          <Select
            style={{ width: 120 }}
            size="small"
            placeholder="İşlemler"
            dropdownStyle={{ minWidth: 160 }}
            onSelect={(value) => {
              if (value === 'detail') {
                // Eğer import edilmemişse import modunda aç, edilmişse sadece detay göster
                if (!record.transaction_id) {
                  handleImport(record.id);
                } else {
                  handleViewDetail(record);
                }
              } else if (value === 'pdf-view') {
                // PDF Görüntüle
                einvoiceAPI.getPDF(record.id)
                  .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    window.open(url, '_blank');
                  })
                  .catch(() => message.error('PDF açılamadı'));
              } else if (value === 'pdf-download') {
                // PDF İndir
                einvoiceAPI.getPDF(record.id)
                  .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${record.invoice_number}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    message.success('PDF indirildi');
                  })
                  .catch(() => message.error('PDF indirilemedi'));
              } else if (value === 'delete') {
                Modal.confirm({
                  title: 'Silmek istediğinize emin misiniz?',
                  onOk: () => handleDelete(record.id),
                  okText: 'Evet',
                  cancelText: 'Hayır',
              });
            }
          }}
        >
          <Select.Option value="detail">
            {!record.transaction_id ? (
              <>
                <ImportOutlined style={{ marginRight: 6, color: '#1890ff' }} /> <span>İmport Et</span>
              </>
            ) : (
              <>
                <EyeOutlined style={{ marginRight: 6 }} /> <span>Detay Göster</span>
              </>
            )}
          </Select.Option>
          {record.pdf_path && (
            <>
              <Select.Option value="pdf-view">
                <FileTextOutlined style={{ marginRight: 6, color: '#52c41a' }} /> <span>PDF Göster</span>
              </Select.Option>
              <Select.Option value="pdf-download">
                <FileTextOutlined style={{ marginRight: 6, color: '#1890ff' }} /> <span>PDF İndir</span>
              </Select.Option>
            </>
          )}
          <Select.Option value="delete">
            <DeleteOutlined style={{ marginRight: 6 }} /> <span>Sil</span>
          </Select.Option>
        </Select>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1>
        <FileTextOutlined /> Fatura Takip
      </h1>

      {/* İstatistikler */}
      {summary && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="📥 Gelen E-Fatura"
                value={summary.incoming_count}
                suffix="adet"
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(summary.incoming_amount || 0).toLocaleString('tr-TR', { 
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })} ₺
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="📥 Gelen E-Arşiv"
                value={summary.incoming_archive_count}
                suffix="adet"
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(summary.incoming_archive_amount || 0).toLocaleString('tr-TR', { 
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })} ₺
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="📤 Giden E-Fatura"
                value={summary.outgoing_count}
                suffix="adet"
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(summary.outgoing_amount || 0).toLocaleString('tr-TR', { 
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })} ₺
              </div>
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="📤 Giden E-Arşiv"
                value={summary.outgoing_archive_count}
                suffix="adet"
              />
              <div style={{ marginTop: 8, fontSize: 14, color: '#666' }}>
                {(summary.outgoing_archive_amount || 0).toLocaleString('tr-TR', { 
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })} ₺
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* Genel İstatistikler */}
      {summary && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="İmport Edilmiş"
                value={summary.imported_count}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="Bekleyen"
                value={summary.pending_count}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="Hatalı"
                value={summary.error_count}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Filtreler */}
      <Card style={{ marginBottom: 16 }}>
        <Tabs
          activeKey={filters.invoice_category}
          onChange={(key) => {
            setFilters({ 
              ...filters, 
              invoice_category: key,
              skip: 0, // Sekme değişince sayfayı sıfırla
            });
          }}
          items={[
            { key: 'incoming', label: '📥 Gelen E-Fatura' },
            { key: 'incoming-archive', label: '📥 Gelen E-Arşiv' },
            { key: 'outgoing', label: '📤 Giden E-Fatura' },
            { key: 'outgoing-archive', label: '📤 Giden E-Arşiv' },
          ]}
          style={{ marginBottom: 16 }}
        />
        
        <Space wrap>
          <Input
            placeholder="Fatura No, Tedarikçi Ara..."
            prefix={<SearchOutlined />}
            style={{ width: 250 }}
            onChange={(e) =>
              setFilters({ ...filters, search: e.target.value })
            }
            allowClear
          />
          <RangePicker
            format="DD.MM.YYYY"
            placeholder={['Başlangıç', 'Bitiş']}
            value={filters.date_from && filters.date_to ? [dayjs(filters.date_from), dayjs(filters.date_to)] : null}
            onChange={(dates) => {
              if (dates) {
                setFilters({
                  ...filters,
                  date_from: dates[0]?.format('YYYY-MM-DD'),
                  date_to: dates[1]?.format('YYYY-MM-DD'),
                });
              } else {
                setFilters({
                  ...filters,
                  date_from: undefined,
                  date_to: undefined,
                });
              }
            }}
          />
          <Select
            placeholder="İmport Durumu"
            style={{ width: 150 }}
            allowClear
            onChange={(value) =>
              setFilters({ ...filters, import_status: value })
            }
          >
            <Option value="COMPLETED">Tamamlandı</Option>
            <Option value="PENDING">Bekliyor</Option>
            <Option value="ERROR">Hatalı</Option>
          </Select>
          <Button onClick={loadEInvoices}>Listele</Button>
          
          <Upload
            accept=".xlsx,.xls,.csv"
            showUploadList={false}
            beforeUpload={handleFileUpload}
          >
            <Button type="default" icon={<UploadOutlined />} loading={loading}>
              Excel Yükle
            </Button>
          </Upload>

          <Upload
            accept=".xml,.zip"
            multiple
            showUploadList={false}
            beforeUpload={(_file, fileList) => {
              setPendingXmlFiles(fileList);
              setXmlDirectionModalVisible(true);
              return false;
            }}
          >
            <Button type="default" icon={<FileTextOutlined />} loading={loading}>
              XML Yükle
            </Button>
          </Upload>

          <Upload
            accept=".pdf"
            multiple
            showUploadList={false}
            beforeUpload={(file, fileList) => {
              setPendingPdfFiles(fileList);
              setPdfDirectionModalVisible(true);
              return false;
            }}
          >
            <Button type="default" icon={<FileTextOutlined />} loading={loading} style={{ borderColor: '#52c41a', color: '#52c41a' }}>
              PDF Yükle
            </Button>
          </Upload>
        </Space>

        {/* Tarih Filtreleri - Yıl ve Ay Sekmeleri */}
        <div style={{ marginTop: 16, borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
          <Tabs
            size="small"
            type="card"
            defaultActiveKey={dayjs().format('YYYY')} 
            onChange={(key) => {
              if (key === 'all') {
                // Tümü seçildiğinde tarihleri temizle
                setFilters({
                  ...filters,
                  date_from: undefined,
                  date_to: undefined,
                });
              } else {
                // Ay seçildiğinde (format: 2024-01, 2024-02, vb.)
                const [year, month] = key.split('-');
                const startDate = dayjs(`${year}-${month}-01`);
                const endDate = startDate.endOf('month');
                setFilters({
                  ...filters,
                  date_from: startDate.format('YYYY-MM-DD'),
                  date_to: endDate.format('YYYY-MM-DD'),
                });
              }
            }}
            items={[
              {
                key: '2025',
                label: '2025',
                children: (
                  <Tabs
                    size="small"
                    type="line"
                    defaultActiveKey={dayjs().year() === 2025 ? dayjs().format('YYYY-MM') : undefined}
                    onChange={(monthKey) => {
                      if (monthKey === 'all-2025') {
                        const startDate = dayjs('2025-01-01');
                        const endDate = dayjs('2025-12-31');
                        setFilters({
                          ...filters,
                          date_from: startDate.format('YYYY-MM-DD'),
                          date_to: endDate.format('YYYY-MM-DD'),
                        });
                      } else {
                        const month = monthKey.split('-')[1];
                        const startDate = dayjs(`2025-${month}-01`);
                        const endDate = startDate.endOf('month');
                        setFilters({
                          ...filters,
                          date_from: startDate.format('YYYY-MM-DD'),
                          date_to: endDate.format('YYYY-MM-DD'),
                        });
                      }
                    }}
                    items={[
                      { key: '2025-01', label: 'OCAK' },
                      { key: '2025-02', label: 'ŞUBAT' },
                      { key: '2025-03', label: 'MART' },
                      { key: '2025-04', label: 'NİSAN' },
                      { key: '2025-05', label: 'MAYIS' },
                      { key: '2025-06', label: 'HAZİRAN' },
                      { key: '2025-07', label: 'TEMMUZ' },
                      { key: '2025-08', label: 'AĞUSTOS' },
                      { key: '2025-09', label: 'EYLÜL' },
                      { key: '2025-10', label: 'EKİM' },
                      { key: '2025-11', label: 'KASIM' },
                      { key: '2025-12', label: 'ARALIK' },
                      { key: 'all-2025', label: 'TÜMÜ' },
                    ]}
                  />
                ),
              },
              {
                key: '2024',
                label: '2024',
                children: (
                  <Tabs
                    size="small"
                    type="line"
                    defaultActiveKey={dayjs().year() === 2024 ? dayjs().format('YYYY-MM') : undefined}
                    onChange={(monthKey) => {
                      if (monthKey === 'all-2024') {
                        const startDate = dayjs('2024-01-01');
                        const endDate = dayjs('2024-12-31');
                        setFilters({
                          ...filters,
                          date_from: startDate.format('YYYY-MM-DD'),
                          date_to: endDate.format('YYYY-MM-DD'),
                        });
                      } else {
                        const month = monthKey.split('-')[1];
                        const startDate = dayjs(`2024-${month}-01`);
                        const endDate = startDate.endOf('month');
                        setFilters({
                          ...filters,
                          date_from: startDate.format('YYYY-MM-DD'),
                          date_to: endDate.format('YYYY-MM-DD'),
                        });
                      }
                    }}
                    items={[
                      { key: '2024-01', label: 'OCAK' },
                      { key: '2024-02', label: 'ŞUBAT' },
                      { key: '2024-03', label: 'MART' },
                      { key: '2024-04', label: 'NİSAN' },
                      { key: '2024-05', label: 'MAYIS' },
                      { key: '2024-06', label: 'HAZİRAN' },
                      { key: '2024-07', label: 'TEMMUZ' },
                      { key: '2024-08', label: 'AĞUSTOS' },
                      { key: '2024-09', label: 'EYLÜL' },
                      { key: '2024-10', label: 'EKİM' },
                      { key: '2024-11', label: 'KASIM' },
                      { key: '2024-12', label: 'ARALIK' },
                      { key: 'all-2024', label: 'TÜMÜ' },
                    ]}
                  />
                ),
              },
              {
                key: 'all',
                label: 'TÜMÜ',
                children: <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>Tüm tarihler gösteriliyor</div>,
              },
            ]}
          />
        </div>
      </Card>

      {/* Tablo */}
      <Card>
        <Table
          columns={columns}
          dataSource={einvoices}
          rowKey="id"
          loading={loading}
          size="small"
          pagination={{
            total: summary?.total_count || 0,
            current: Math.floor(filters.skip / filters.limit) + 1,
            pageSize: filters.limit,
            showSizeChanger: true,
            showTotal: (total) => `Toplam ${total} fatura`,
            onChange: (page, pageSize) => {
              setFilters({
                ...filters,
                skip: (page - 1) * pageSize,
                limit: pageSize,
              });
            },
          }}
        />
      </Card>

      {/* Upload Progress Modal */}
      <Modal
        title="Dosya Yükleniyor"
        open={uploadModalVisible}
        footer={uploadProgress === 100 ? [
          <Button key="close" type="primary" onClick={() => setUploadModalVisible(false)}>
            Kapat
          </Button>
        ] : null}
        closable={uploadProgress === 100}
        onCancel={() => setUploadModalVisible(false)}
        width={500}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Progress 
            type="circle" 
            percent={uploadProgress} 
            status={uploadProgress === 100 ? 'success' : 'active'}
          />
          <p style={{ marginTop: 20, fontSize: 16 }}>{uploadStatus}</p>
        </div>
      </Modal>

      {/* PDF Direction Selection Modal */}
      <Modal
        title="Fatura Türü Seçin"
        open={pdfDirectionModalVisible}
        onOk={() => {
          setPdfDirectionModalVisible(false);
          if (pendingPdfFiles.length > 0) {
            handlePDFUpload(pendingPdfFiles, pdfDirection);
          }
        }}
        onCancel={() => {
          setPdfDirectionModalVisible(false);
          setPendingPdfFiles([]);
        }}
        okText="Yükle"
        cancelText="İptal"
        width={500}
      >
        <div style={{ padding: '20px 0' }}>
          <p style={{ marginBottom: 16 }}>
            <strong>{pendingPdfFiles.length}</strong> PDF dosyası seçildi. Bu faturalar hangi türde?
          </p>
          {pendingPdfFiles.length <= 5 && (
            <div style={{ marginBottom: 16, fontSize: 12, color: '#666' }}>
              {pendingPdfFiles.map((f, idx) => (
                <div key={idx}>• {f.name}</div>
              ))}
            </div>
          )}
          {pendingPdfFiles.length > 5 && (
            <div style={{ marginBottom: 16, fontSize: 12, color: '#666' }}>
              İlk 5 dosya: {pendingPdfFiles.slice(0, 5).map(f => f.name).join(', ')}...
            </div>
          )}
          <Radio.Group 
            onChange={(e) => setPdfDirection(e.target.value)} 
            value={pdfDirection}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="incoming">
                <strong>📥 Gelen E-Fatura</strong>
                <div style={{ fontSize: 12, color: '#666', marginLeft: 24 }}>
                  Tedarikçilerden aldığımız e-faturalar (PDF'i eklenecek veya sadece PDF varsa)
                </div>
              </Radio>
              <Radio value="outgoing">
                <strong>📤 Giden E-Fatura</strong>
                <div style={{ fontSize: 12, color: '#666', marginLeft: 24 }}>
                  Müşterilere gönderdiğimiz e-faturalar (PDF'i eklenecek veya sadece PDF varsa)
                </div>
              </Radio>
              <Radio value="incoming-archive">
                <strong>📥 Gelen E-Arşiv Fatura</strong>
                <div style={{ fontSize: 12, color: '#666', marginLeft: 24 }}>
                  Tedarikçilerden aldığımız e-arşiv faturalar (genelde sadece PDF)
                </div>
              </Radio>
              <Radio value="outgoing-archive">
                <strong>📤 Giden E-Arşiv Fatura</strong>
                <div style={{ fontSize: 12, color: '#666', marginLeft: 24 }}>
                  Müşterilere gönderdiğimiz e-arşiv faturalar (genelde sadece PDF)
                </div>
              </Radio>
            </Space>
          </Radio.Group>
          <div style={{ marginTop: 16, padding: 12, backgroundColor: '#e6f7ff', border: '1px solid #91d5ff', borderRadius: 4 }}>
            <p style={{ margin: 0, fontSize: 12, color: '#0050b3' }}>
              ℹ️ <strong>Not:</strong> PDF'den otomatik olarak fatura bilgileri (fatura no, ETTN, tutar, VKN, vb.) çıkartılacaktır.
              GİB standart formatındaki PDF'lerde %100 başarı garantisi.
            </p>
          </div>
        </div>
      </Modal>

      {/* XML Direction Selection Modal */}
      <Modal
        title="XML Fatura Yönü Seçin"
        open={xmlDirectionModalVisible}
        onOk={async () => {
          setXmlDirectionModalVisible(false);
          
          // Önce önizleme yap
          setPreviewLoading(true);
          setXmlPreviewModalVisible(true);
          
          try {
            const preview = await einvoiceAPI.previewXML(pendingXmlFiles);
            setPreviewData(preview);
          } catch (error: any) {
            message.error('Önizleme oluşturulamadı: ' + error.message);
            setXmlPreviewModalVisible(false);
          } finally {
            setPreviewLoading(false);
          }
        }}
        onCancel={() => {
          setXmlDirectionModalVisible(false);
          setPendingXmlFiles([]);
        }}
        okText="Yükle"
        cancelText="İptal"
        width={450}
      >
        <div style={{ padding: '20px 0' }}>
          <p style={{ marginBottom: 16 }}>
            {pendingXmlFiles.length} XML dosyası seçildi. Bu faturalar gelen mi giden mi?
          </p>
          <Radio.Group 
            onChange={(e) => setSelectedDirection(e.target.value)} 
            value={selectedDirection}
            style={{ width: '100%' }}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <Radio value="incoming">
                <strong>Gelen Faturalar</strong>
                <div style={{ fontSize: 12, color: '#666', marginLeft: 24 }}>
                  Tedarikçilerden aldığımız e-fatura ve e-arşiv faturalar
                </div>
              </Radio>
              <Radio value="outgoing">
                <strong>Giden Faturalar</strong>
                <div style={{ fontSize: 12, color: '#666', marginLeft: 24 }}>
                  Müşterilere gönderdiğimiz e-fatura ve e-arşiv faturalar
                </div>
              </Radio>
            </Space>
          </Radio.Group>
        </div>
      </Modal>

      {/* XML Preview Modal */}
      <Modal
        title="Yükleme Önizleme"
        open={xmlPreviewModalVisible}
        onOk={async () => {
          setXmlPreviewModalVisible(false);
          handleXMLUpload(pendingXmlFiles, selectedDirection);
        }}
        onCancel={() => {
          setXmlPreviewModalVisible(false);
          setPendingXmlFiles([]);
          setPreviewData(null);
        }}
        okText="Yüklemeyi Onayla"
        cancelText="İptal"
        width={900}
        confirmLoading={previewLoading}
      >
        {previewLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Progress type="circle" percent={50} status="active" />
            <p style={{ marginTop: 20 }}>Faturalar analiz ediliyor...</p>
          </div>
        ) : previewData ? (
          <>
            <Row gutter={16} style={{ marginBottom: 20 }}>
              <Col span={6}>
                <Card>
                  <Statistic 
                    title="Toplam Dosya" 
                    value={previewData.total_files} 
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic 
                    title="Eşleşen Cariler" 
                    value={previewData.summary.matched_contacts} 
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic 
                    title="Yeni Cari" 
                    value={previewData.summary.new_contacts} 
                    valueStyle={{ color: '#faad14' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic 
                    title="Başarı Tahmini" 
                    value={previewData.success_estimate} 
                    valueStyle={{ color: '#52c41a' }}
                  />
                </Card>
              </Col>
            </Row>

            {previewData.summary.possible_matches > 0 && (
              <div style={{ 
                background: '#fffbe6', 
                border: '1px solid #ffe58f', 
                padding: 12, 
                borderRadius: 4,
                marginBottom: 16
              }}>
                <strong>⚠️ {previewData.summary.possible_matches} faturada benzer cari bulundu</strong>
                <div style={{ fontSize: 12, marginTop: 4 }}>
                  Aşağıdaki tabloda benzer carileri görebilir ve eşleştirme yapabilirsiniz.
                </div>
              </div>
            )}

            <Table
              dataSource={previewData.details}
              columns={[
                {
                  title: 'Dosya',
                  dataIndex: 'filename',
                  key: 'filename',
                  width: 200,
                  ellipsis: true,
                },
                {
                  title: 'Fatura No',
                  dataIndex: 'invoice_number',
                  key: 'invoice_number',
                  width: 150,
                },
                {
                  title: selectedDirection === 'incoming' ? 'Tedarikçi' : 'Müşteri',
                  dataIndex: selectedDirection === 'incoming' ? 'supplier_name' : 'customer_name',
                  key: 'partner_name',
                  width: 200,
                  ellipsis: true,
                },
                {
                  title: 'VKN',
                  dataIndex: selectedDirection === 'incoming' ? 'supplier_vkn' : 'customer_vkn',
                  key: 'partner_vkn',
                  width: 120,
                },
                {
                  title: 'Durum',
                  dataIndex: 'status',
                  key: 'status',
                  width: 150,
                  render: (status: string, record: any) => {
                    if (status === 'matched') {
                      return <Tag color="green">✓ Cari Eşleşti</Tag>;
                    } else if (status === 'new_contact') {
                      return <Tag color="orange">+ Yeni Cari</Tag>;
                    } else if (status === 'missing_vkn') {
                      return <Tag color="red">⚠ VKN Yok</Tag>;
                    }
                    return <Tag>{status}</Tag>;
                  },
                },
                {
                  title: 'Benzer Cariler',
                  key: 'possible_matches',
                  width: 200,
                  render: (_, record: any) => {
                    if (record.possible_matches && record.possible_matches.length > 0) {
                      return (
                        <div style={{ whiteSpace: 'normal' }}>
                          {record.possible_matches.map((match: any, idx: number) => (
                            <div key={idx} style={{ fontSize: 11, marginBottom: 4 }}>
                              <Tag color="blue" style={{ cursor: 'pointer' }}>
                                {match.name} ({(match.similarity * 100).toFixed(0)}%)
                              </Tag>
                            </div>
                          ))}
                        </div>
                      );
                    }
                    return '-';
                  },
                },
              ]}
              pagination={false}
              scroll={{ y: 400 }}
              size="small"
            />
          </>
        ) : null}
      </Modal>

      {/* Detay Modal */}
      <Modal
        title={isImportMode ? "🔍 Fatura İmport Önizleme ve Düzenleme" : "Fatura Detayı"}
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false);
          setIsImportMode(false);
          setImportPreviewData(null);
        }}
        width={isImportMode ? 1200 : 900}
        style={isImportMode ? { top: 20 } : undefined}
        footer={
          isImportMode ? [
            <Button 
              key="cancel"
              onClick={() => {
                setDetailModalVisible(false);
                setIsImportMode(false);
                setImportPreviewData(null);
              }}
            >
              İptal
            </Button>,
            <Button
              key="confirm"
              type="primary"
              loading={importPreviewLoading}
              disabled={!importPreviewData?.can_import}
              onClick={handleConfirmImport}
            >
              ✅ Onayla ve İmport Et
            </Button>,
          ] : [
            <Button key="close" onClick={() => setDetailModalVisible(false)}>
              Kapat
            </Button>,
          ]
        }
      >
        {/* Import Mode Loading */}
        {isImportMode && !importPreviewData ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="Muhasebe fişi hazırlanıyor..." />
          </div>
        ) : selectedInvoice && (
          <>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="Fatura No" span={1}>
                {selectedInvoice.invoice_number}
              </Descriptions.Item>
              <Descriptions.Item label="Tarih" span={1}>
                {dayjs(selectedInvoice.issue_date).format('DD.MM.YYYY')}
              </Descriptions.Item>
              <Descriptions.Item label="Maliyet Merkezi" span={2}>
                <Space>
                  <Select
                    value={selectedInvoice.cost_center_id ?? undefined}
                    style={{ width: 300 }}
                    loading={costCenterLoading}
                    placeholder="Maliyet Merkezi Seçiniz"
                    allowClear
                    onChange={(value) => {
                      setSelectedInvoice({ ...selectedInvoice, cost_center_id: value });
                    }}
                  >
                    {costCenters.map((cc) => (
                      <Select.Option key={cc.id} value={cc.id}>
                        {cc.name}
                      </Select.Option>
                    ))}
                  </Select>
                  <Button
                    type="primary"
                    size="small"
                    onClick={async () => {
                      try {
                        await einvoiceAPI.updateEInvoice(selectedInvoice.id, { cost_center_id: selectedInvoice.cost_center_id });
                        message.success('Maliyet merkezi kaydedildi');
                        loadEInvoices();
                      } catch (e) {
                        message.error('Kaydetme başarısız');
                      }
                    }}
                  >
                    Kaydet
                  </Button>
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="ETTN (UUID)" span={2}>
                <code style={{ fontSize: '11px' }}>{selectedInvoice.invoice_uuid || '-'}</code>
              </Descriptions.Item>
              <Descriptions.Item label="Senaryo" span={1}>
                <Tag color="blue">{selectedInvoice.invoice_profile || '-'}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Tip" span={1}>
                {selectedInvoice.invoice_type}
              </Descriptions.Item>
            </Descriptions>

            <h3 style={{ marginTop: 16 }}>
              {selectedInvoice.invoice_category?.startsWith('incoming') ? 'Tedarikçi Bilgileri' : 'Müşteri Bilgileri'}
            </h3>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label={selectedInvoice.invoice_category?.startsWith('incoming') ? 'Tedarikçi' : 'Müşteri'} span={2}>
                {selectedInvoice.invoice_category?.startsWith('incoming') 
                  ? selectedInvoice.supplier_name 
                  : selectedInvoice.customer_name || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="VKN" span={1}>
                {selectedInvoice.invoice_category?.startsWith('incoming')
                  ? selectedInvoice.supplier_tax_number
                  : selectedInvoice.customer_tax_number || '-'}
              </Descriptions.Item>
              <Descriptions.Item label="Vergi Dairesi" span={1}>
                {selectedInvoice.invoice_category?.startsWith('incoming')
                  ? selectedInvoice.supplier_tax_office
                  : '-'}
              </Descriptions.Item>
              {selectedInvoice.invoice_category?.startsWith('incoming') && (
                <>
                  <Descriptions.Item label="Adres" span={2}>
                    {selectedInvoice.supplier_address}
                  </Descriptions.Item>
                  <Descriptions.Item label="Şehir" span={1}>
                    {selectedInvoice.supplier_city}
                  </Descriptions.Item>
                  <Descriptions.Item label="İlçe" span={1}>
                    {selectedInvoice.supplier_district}
                  </Descriptions.Item>
                </>
              )}
            </Descriptions>

            <h3 style={{ marginTop: 16 }}>Tutar Bilgileri</h3>
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="Mal/Hizmet Toplam" span={1}>
                {new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(selectedInvoice.line_extension_amount || 0)}
              </Descriptions.Item>
              {selectedInvoice.allowance_total && selectedInvoice.allowance_total > 0 && (
                <Descriptions.Item label="Toplam İndirim" span={1}>
                  {new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(selectedInvoice.allowance_total || 0)}
                </Descriptions.Item>
              )}
              <Descriptions.Item label="Vergi Hariç Tutar" span={1}>
                <span style={{ fontWeight: 600 }}>
                  {new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(selectedInvoice.tax_exclusive_amount || selectedInvoice.line_extension_amount || 0)}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="Toplam Vergi" span={1}>
                <span style={{ fontWeight: 600, color: '#1890ff' }}>
                  {new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(
                    selectedInvoice.tax_details?.reduce((sum: number, tax: any) => sum + (tax.tax_amount || 0), 0) || 
                    (selectedInvoice.tax_inclusive_amount || 0) - (selectedInvoice.tax_exclusive_amount || 0)
                  )}
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="Ödenecek Tutar" span={2}>
                <span style={{ fontWeight: 700, fontSize: 16, color: '#52c41a' }}>
                  {new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(selectedInvoice.payable_amount || 0)}
                </span>
              </Descriptions.Item>
            </Descriptions>

            {selectedInvoice.payment_due_date && (
              <>
                <h3 style={{ marginTop: 16 }}>Ödeme Bilgileri</h3>
                <Descriptions bordered column={2} size="small">
                  <Descriptions.Item label="Vade Tarihi" span={2}>
                    {dayjs(selectedInvoice.payment_due_date).format(
                      'DD.MM.YYYY'
                    )}
                  </Descriptions.Item>
                </Descriptions>
              </>
            )}

            {/* Fatura Kalemleri */}
            {selectedInvoice.invoice_lines && selectedInvoice.invoice_lines.length > 0 && (
              <>
                <h3 style={{ marginTop: 16 }}>Fatura Kalemleri</h3>
                <Table
                  size="small"
                  pagination={false}
                  scroll={{ x: 800 }}
                  dataSource={selectedInvoice.invoice_lines}
                  rowKey="id"
                  columns={[
                    {
                      title: 'Sıra',
                      dataIndex: 'id',
                      key: 'id',
                      width: 50,
                    },
                    {
                      title: 'Ürün/Hizmet',
                      dataIndex: 'item_name',
                      key: 'item_name',
                      width: 250,
                      render: (val: any) => val || '-',
                    },
                    {
                      title: 'Miktar',
                      dataIndex: 'quantity',
                      key: 'quantity',
                      width: 80,
                      align: 'right',
                      render: (val: any) => val ? new Intl.NumberFormat('tr-TR', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 2,
                      }).format(val) : '-',
                    },
                    {
                      title: 'Birim',
                      dataIndex: 'unit',
                      key: 'unit',
                      width: 70,
                    },
                    {
                      title: 'Birim Fiyat',
                      dataIndex: 'unit_price',
                      key: 'unit_price',
                      width: 110,
                      align: 'right',
                      render: (val: any) => val !== null && val !== undefined ? new Intl.NumberFormat('tr-TR', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 4,
                      }).format(val) + ' TL' : '-',
                    },
                    {
                      title: 'Tutar',
                      dataIndex: 'line_total',
                      key: 'line_total',
                      width: 120,
                      align: 'right',
                      render: (val: any) => val !== null && val !== undefined ? new Intl.NumberFormat('tr-TR', {
                        style: 'currency',
                        currency: 'TRY',
                      }).format(val) : '-',
                    },
                    {
                      title: 'KDV %',
                      dataIndex: 'tax_percent',
                      key: 'tax_percent',
                      width: 70,
                      align: 'center',
                      render: (val: any) => val !== null && val !== undefined ? `%${val}` : '-',
                    },
                    {
                      title: 'KDV Tutarı',
                      dataIndex: 'tax_amount',
                      key: 'tax_amount',
                      width: 120,
                      align: 'right',
                      render: (val: any) => val !== null && val !== undefined ? new Intl.NumberFormat('tr-TR', {
                        style: 'currency',
                        currency: 'TRY',
                      }).format(val) : '-',
                    },
                  ]}
                />
              </>
            )}

            {/* Vergi Detayları */}
            {selectedInvoice.tax_details && selectedInvoice.tax_details.length > 0 && (
              <>
                <h3 style={{ marginTop: 24 }}>Vergi Detayları</h3>
                <Table
                  size="small"
                  pagination={false}
                  style={{ marginBottom: 16 }}
                  dataSource={selectedInvoice.tax_details}
                  rowKey={(record, index) => `tax-${index}`}
                  columns={[
                    {
                      title: 'Kod',
                      dataIndex: 'tax_type_code',
                      key: 'tax_type_code',
                      width: 80,
                      align: 'center',
                      render: (val: string) => <Tag color="blue">{val}</Tag>,
                    },
                    {
                      title: 'Vergi Adı',
                      dataIndex: 'tax_name',
                      key: 'tax_name',
                      width: 300,
                    },
                    {
                      title: 'Oran',
                      dataIndex: 'tax_percent',
                      key: 'tax_percent',
                      width: 80,
                      align: 'center',
                      render: (val: any) => val !== null && val !== undefined ? `%${val}` : '-',
                    },
                    {
                      title: 'Matrah',
                      dataIndex: 'taxable_amount',
                      key: 'taxable_amount',
                      width: 150,
                      align: 'right',
                      render: (val: any, record: any) => val ? new Intl.NumberFormat('tr-TR', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }).format(val) + ' ' + (record.currency_code || 'TRY') : '-',
                    },
                    {
                      title: 'Vergi Tutarı',
                      dataIndex: 'tax_amount',
                      key: 'tax_amount',
                      width: 150,
                      align: 'right',
                      render: (val: any) => val ? new Intl.NumberFormat('tr-TR', {
                        style: 'currency',
                        currency: 'TRY',
                      }).format(val) : '-',
                    },
                  ]}
                />
              </>
            )}

            {/* VERGİLER VE MASRAFLAR (ESKİ - EĞER tax_totals VARSA) */}
            {(selectedInvoice.tax_totals?.length || selectedInvoice.allowance_charges?.length) && (
              <>
                <h3 style={{ marginTop: 24 }}>Diğer Ücretler</h3>
                
                {/* Vergiler */}
                {selectedInvoice.tax_totals && selectedInvoice.tax_totals.length > 0 && (
                  <Table
                    size="small"
                    pagination={false}
                    style={{ marginBottom: 16 }}
                    dataSource={selectedInvoice.tax_totals}
                    rowKey={(record, index) => `tax-${index}`}
                    columns={[
                      {
                        title: 'Vergi Türü',
                        dataIndex: 'tax_name',
                        key: 'tax_name',
                        width: 250,
                      },
                      {
                        title: 'Oran',
                        dataIndex: 'tax_percent',
                        key: 'tax_percent',
                        width: 80,
                        align: 'center',
                        render: (val: any) => val !== null && val !== undefined ? `%${val}` : '-',
                      },
                      {
                        title: 'Matrah',
                        dataIndex: 'taxable_amount',
                        key: 'taxable_amount',
                        width: 150,
                        align: 'right',
                        render: (val: any, record: any) => val ? new Intl.NumberFormat('tr-TR', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }).format(val) + ' ' + (record.currency || 'TRY') : '-',
                      },
                      {
                        title: 'Tutar',
                        dataIndex: 'tax_amount',
                        key: 'tax_amount',
                        width: 150,
                        align: 'right',
                        render: (val: any) => val ? new Intl.NumberFormat('tr-TR', {
                          style: 'currency',
                          currency: 'TRY',
                        }).format(val) : '-',
                      },
                    ]}
                  />
                )}

                {/* Masraflar/İndirimler */}
                {selectedInvoice.allowance_charges && selectedInvoice.allowance_charges.length > 0 && (
                  <Table
                    size="small"
                    pagination={false}
                    dataSource={selectedInvoice.allowance_charges}
                    rowKey={(record, index) => `charge-${index}`}
                    columns={[
                      {
                        title: 'Tür',
                        dataIndex: 'is_charge',
                        key: 'is_charge',
                        width: 100,
                        render: (val: boolean) => val ? '🔴 Masraf' : '🟢 İndirim',
                      },
                      {
                        title: 'Açıklama',
                        dataIndex: 'reason',
                        key: 'reason',
                        width: 300,
                      },
                      {
                        title: 'Tutar',
                        dataIndex: 'amount',
                        key: 'amount',
                        width: 150,
                        align: 'right',
                        render: (val: any, record: any) => val ? new Intl.NumberFormat('tr-TR', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }).format(val) + ' ' + (record.currency || 'TRY') : '-',
                      },
                      {
                        title: 'Vergi',
                        dataIndex: 'tax_amount',
                        key: 'tax_amount',
                        width: 120,
                        align: 'right',
                        render: (val: any) => val ? new Intl.NumberFormat('tr-TR', {
                          style: 'currency',
                          currency: 'TRY',
                        }).format(val) : '-',
                      },
                    ]}
                  />
                )}
              </>
            )}

            {/* 📊 Import Modu: Muhasebe Fişi Düzenleme */}
            {isImportMode && importPreviewData && (
              <>
                <Divider style={{ margin: '32px 0 24px 0' }}>
                  <Tag color="blue" style={{ fontSize: 14 }}>📊 Fatura Kategorizasyonu ve Muhasebe Kaydı</Tag>
                </Divider>

                {/* Fatura Türü Seçimi */}
                <Card title="🏷️ Fatura Türü" size="small" style={{ marginBottom: 16 }}>
                  <div style={{ marginBottom: 8, fontSize: 12, color: '#666' }}>
                    XML'den: <Tag color="blue">{selectedInvoice?.invoice_type || 'Belirtilmemiş'}</Tag>
                    {selectedInvoice?.invoice_profile && (
                      <Tag color="cyan" style={{ marginLeft: 4 }}>{selectedInvoice.invoice_profile}</Tag>
                    )}
                  </div>
                  <Select
                    value={invoiceType}
                    onChange={setInvoiceType}
                    style={{ width: '100%' }}
                    size="large"
                  >
                    <Select.Option value="Satış">Satış</Select.Option>
                    <Select.Option value="İade">İade</Select.Option>
                    <Select.Option value="Tevkifat">Tevkifat</Select.Option>
                    <Select.Option value="İstisna">İstisna</Select.Option>
                    <Select.Option value="Özel Matrah">Özel Matrah</Select.Option>
                    <Select.Option value="İhraç Kayıtlı">İhraç Kayıtlı</Select.Option>
                    <Select.Option value="SGK">SGK</Select.Option>
                    <Select.Option value="Tevkifat İade">Tevkifat İade</Select.Option>
                    <Select.Option value="Konaklama Vergisi">Konaklama Vergisi</Select.Option>
                  </Select>
                </Card>

                {/* Fatura Satırları Kategorizasyonu (sadece gelen fatura için) */}
                {selectedInvoice?.invoice_category?.includes('incoming') && selectedInvoice.invoice_lines && selectedInvoice.invoice_lines.length > 0 && (
                  <Card title="📝 Fatura Satırları Kategorizasyonu" size="small" style={{ marginBottom: 16 }}>
                    <Table
                      size="small"
                      dataSource={selectedInvoice.invoice_lines}
                      rowKey="id"
                      pagination={false}
                      columns={[
                        {
                          title: 'Ürün/Hizmet',
                          dataIndex: 'item_name',
                          key: 'item_name',
                          width: 200,
                        },
                        {
                          title: 'Tutar',
                          dataIndex: 'line_total',
                          key: 'line_total',
                          width: 120,
                          align: 'right',
                          render: (val: any) => val ? new Intl.NumberFormat('tr-TR', {
                            style: 'currency',
                            currency: 'TRY',
                          }).format(val) : '-',
                        },
                        {
                          title: 'Kategori',
                          key: 'category',
                          width: 220,
                          render: (_, record: any) => (
                            <Select
                              value={invoiceLineCategories[record.id] || undefined}
                              onChange={(value) => {
                                setInvoiceLineCategories({ ...invoiceLineCategories, [record.id]: value });
                                // Kategori değişince hesap kodunu temizle
                                const newAccounts = { ...invoiceLineAccounts };
                                delete newAccounts[record.id];
                                setInvoiceLineAccounts(newAccounts);
                              }}
                              placeholder="Kategori seçin"
                              style={{ width: '100%' }}
                              size="small"
                            >
                              <Select.Option value="hizmet_maliyet">Hizmet Üretim Maliyeti</Select.Option>
                              <Select.Option value="genel_yonetim">Genel Yönetim Giderleri</Select.Option>
                              <Select.Option value="ticari_mal">Ticari Mallar (153)</Select.Option>
                              <Select.Option value="diger_stok">Diğer Stoklar (157)</Select.Option>
                              <Select.Option value="demirbaş">Demirbaş Alımı</Select.Option>
                              <Select.Option value="taşıt">Taşıt Alımı</Select.Option>
                            </Select>
                          ),
                        },
                        {
                          title: 'Hesap/Detay',
                          key: 'account',
                          width: 250,
                          render: (_, record: any) => {
                            const category = invoiceLineCategories[record.id];
                            
                            if (!category) return <span style={{ color: '#999' }}>Önce kategori seçin</span>;
                            
                            // Hizmet Üretim Maliyeti - 740'lı hesaplar
                            if (category === 'hizmet_maliyet') {
                              const accounts740 = accounts.filter(a => a.code.startsWith('740'));
                              return (
                                <Select
                                  value={invoiceLineAccounts[record.id]}
                                  onChange={(value) => {
                                    setInvoiceLineAccounts({ ...invoiceLineAccounts, [record.id]: value });
                                    // useEffect otomatik preview'ı yenileyecek
                                  }}
                                  placeholder="740'lı hesap seçin"
                                  style={{ width: '100%' }}
                                  size="small"
                                  showSearch
                                  optionFilterProp="children"
                                >
                                  {accounts740.map(acc => (
                                    <Select.Option key={acc.code} value={acc.code}>{acc.code} - {acc.name}</Select.Option>
                                  ))}
                                </Select>
                              );
                            }
                            
                            // Genel Yönetim Giderleri - 770'li hesaplar
                            if (category === 'genel_yonetim') {
                              const accounts770 = accounts.filter(a => a.code.startsWith('770'));
                              return (
                                <Select
                                  value={invoiceLineAccounts[record.id]}
                                  onChange={(value) => {
                                    setInvoiceLineAccounts({ ...invoiceLineAccounts, [record.id]: value });
                                    // useEffect otomatik preview'ı yenileyecek
                                  }}
                                  placeholder="770'li hesap seçin"
                                  style={{ width: '100%' }}
                                  size="small"
                                  showSearch
                                  optionFilterProp="children"
                                >
                                  {accounts770.map(acc => (
                                    <Select.Option key={acc.code} value={acc.code}>{acc.code} - {acc.name}</Select.Option>
                                  ))}
                                </Select>
                              );
                            }
                            
                            // Ticari Mallar - 153
                            if (category === 'ticari_mal') {
                              return <Tag color="green">153 - Ticari Mallar</Tag>;
                            }
                            
                            // Diğer Stoklar - 157
                            if (category === 'diger_stok') {
                              return <Tag color="cyan">157 - Diğer Stoklar</Tag>;
                            }
                            
                            // Demirbaş Alımı - Kategori seçimi
                            if (category === 'demirbaş') {
                              return (
                                <Select
                                  value={fixedAssetCategories[record.id]}
                                  onChange={(value) => setFixedAssetCategories({ ...fixedAssetCategories, [record.id]: value })}
                                  placeholder="Demirbaş türü seçin"
                                  style={{ width: '100%' }}
                                  size="small"
                                >
                                  <Select.Option value="Konteynerler">Konteynerler (255.01.xxx)</Select.Option>
                                  <Select.Option value="Makine Ve Ekipmanlar">Makine ve Ekipmanlar (255.02.xxx)</Select.Option>
                                  <Select.Option value="İnşaat Kalıpları">İnşaat Kalıpları (255.03.xxx)</Select.Option>
                                  <Select.Option value="Şantiyeye Ait Alet Ve Gereçleri">Şantiye Alet ve Gereçler (255.04.xxx)</Select.Option>
                                  <Select.Option value="İş Makinası Ekipmanları">İş Makinası Ekipmanları (255.05.xxx)</Select.Option>
                                </Select>
                              );
                            }
                            
                            // Taşıt Alımı
                            if (category === 'taşıt') {
                              return <Tag color="purple">255.06.xxx - Yeni taşıt hesabı oluşturulacak</Tag>;
                            }
                            
                            return null;
                          },
                        },
                      ]}
                    />
                  </Card>
                )}

                <Divider style={{ margin: '24px 0' }} />
                
                <Card 
                  title={
                    <span>
                      👤 Cari Hesap 
                      {importPreviewData.contact?.will_create && <Tag color="green" style={{ marginLeft: 8 }}>YENİ OLUŞTURULACAK</Tag>}
                      {!importPreviewData.contact?.will_create && <Tag color="blue" style={{ marginLeft: 8 }}>MEVCUT</Tag>}
                    </span>
                  }
                  size="small" 
                  style={{ marginBottom: 16 }}
                >
                  <Descriptions column={2} size="small">
                    <Descriptions.Item label="Kod">{importPreviewData.contact?.code}</Descriptions.Item>
                    <Descriptions.Item label="Ünvan">{importPreviewData.contact?.name}</Descriptions.Item>
                    <Descriptions.Item label="VKN/TCKN">{importPreviewData.contact?.tax_number || '-'}</Descriptions.Item>
                    <Descriptions.Item label="IBAN">{importPreviewData.contact?.iban || '-'}</Descriptions.Item>
                  </Descriptions>
                </Card>

                <Card 
                  title="📊 Muhasebe Fişi" 
                  size="small" 
                  style={{ marginBottom: 16 }}
                  extra={
                    <Button
                      type="primary"
                      size="small"
                      icon={<PlusOutlined />}
                      onClick={() => {
                        const newLineNo = Math.max(...editableLines.map(l => l.line_no), 0) + 1;
                        const newLine = {
                          line_no: newLineNo,
                          account_code: '',
                          description: '',
                          debit: 0,
                          credit: 0,
                        };
                        setEditableLines([...editableLines, newLine]);
                      }}
                    >
                      Satır Ekle
                    </Button>
                  }
                >
                  <Descriptions column={3} size="small" style={{ marginBottom: 12 }} bordered>
                    <Descriptions.Item label="Fiş No">
                      <Input 
                        value={editableTransactionNumber}
                        onChange={(e) => setEditableTransactionNumber(e.target.value)}
                        style={{ width: 200 }}
                        placeholder="F00000001"
                      />
                    </Descriptions.Item>
                    <Descriptions.Item label="Tarih">{importPreviewData.transaction?.date}</Descriptions.Item>
                    <Descriptions.Item label="Maliyet Merkezi">{importPreviewData.transaction?.cost_center_name || '-'}</Descriptions.Item>
                    <Descriptions.Item label="Belge Tipi">
                      <Select
                        value={selectedDocumentTypeId || importPreviewData.transaction?.document_type_id}
                        onChange={(value) => setSelectedDocumentTypeId(value)}
                        style={{ width: 200 }}
                        placeholder="Belge Tipi Seçin"
                      >
                        {documentTypes.map(dt => (
                          <Option key={dt.id} value={dt.id}>{dt.name}</Option>
                        ))}
                      </Select>
                    </Descriptions.Item>
                    <Descriptions.Item label="Belge Alt Tipi">
                      <Select
                        value={selectedDocumentSubtypeId || importPreviewData.transaction?.document_subtype_id}
                        onChange={(value) => setSelectedDocumentSubtypeId(value)}
                        style={{ width: 200 }}
                        placeholder="Belge Alt Tipi Seçin"
                      >
                        {documentSubtypes
                          .filter(dst => {
                            // Seçilen document type'a göre filtrele
                            const selectedTypeId = selectedDocumentTypeId || importPreviewData.transaction?.document_type_id;
                            if (!selectedTypeId) return true;
                            const selectedType = documentTypes.find(dt => dt.id === selectedTypeId);
                            return !selectedType || dst.parent_code === selectedType.code;
                          })
                          .map(dst => (
                            <Option key={dst.id} value={dst.id}>{dst.name}</Option>
                          ))
                        }
                      </Select>
                    </Descriptions.Item>
                    <Descriptions.Item label="Belge No">{importPreviewData.transaction?.document_number}</Descriptions.Item>
                    <Descriptions.Item label="Açıklama" span={3}>{importPreviewData.transaction?.description || '-'}</Descriptions.Item>
                  </Descriptions>

                  <Table
                    size="small"
                    dataSource={editableLines}
                    rowKey="line_no"
                    pagination={false}
                    bordered
                    columns={[
                      {
                        title: 'Sıra',
                        dataIndex: 'line_no',
                        key: 'line_no',
                        width: 50,
                        align: 'center',
                      },
                      {
                        title: 'Hesap Kodu',
                        dataIndex: 'account_code',
                        key: 'account_code',
                        width: 130,
                        render: (val: string, record: any, index: number) => (
                          <Select 
                            value={val}
                            onChange={(newValue) => {
                              const newLines = [...editableLines];
                              newLines[index].account_code = newValue;
                              setEditableLines(newLines);
                            }}
                            size="small"
                            showSearch
                            style={{ width: '100%' }}
                            placeholder="Hesap seç"
                            optionFilterProp="children"
                            filterOption={(input, option) =>
                              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                            }
                            options={accounts.map(acc => ({
                              value: acc.code,
                              label: `${acc.code} - ${acc.name}`
                            }))}
                          />
                        ),
                      },
                      {
                        title: 'Cari',
                        dataIndex: 'contact_name',
                        key: 'contact_name',
                        width: 150,
                        render: (val: string) => val || '-',
                      },
                      {
                        title: 'Açıklama',
                        dataIndex: 'description',
                        key: 'description',
                        width: 200,
                        render: (val: string, record: any, index: number) => (
                          <Input 
                            value={val}
                            onChange={(e) => {
                              const newLines = [...editableLines];
                              newLines[index].description = e.target.value;
                              setEditableLines(newLines);
                            }}
                            size="small"
                          />
                        ),
                      },
                      {
                        title: 'Borç',
                        dataIndex: 'debit',
                        key: 'debit',
                        width: 120,
                        align: 'right',
                        render: (val: number, record: any, index: number) => (
                          <InputNumber 
                            value={val}
                            onChange={(newValue) => {
                              const newLines = [...editableLines];
                              newLines[index].debit = newValue || 0;
                              setEditableLines(newLines);
                            }}
                            size="small"
                            style={{ width: '100%' }}
                            precision={2}
                            formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                            parser={value => value!.replace(/,/g, '')}
                          />
                        ),
                      },
                      {
                        title: 'Alacak',
                        dataIndex: 'credit',
                        key: 'credit',
                        width: 120,
                        align: 'right',
                        render: (val: number, record: any, index: number) => (
                          <InputNumber 
                            value={val}
                            onChange={(newValue) => {
                              const newLines = [...editableLines];
                              newLines[index].credit = newValue || 0;
                              setEditableLines(newLines);
                            }}
                            size="small"
                            style={{ width: '100%' }}
                            precision={2}
                            formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                            parser={value => value!.replace(/,/g, '')}
                          />
                        ),
                      },
                      {
                        title: 'Miktar',
                        dataIndex: 'quantity',
                        key: 'quantity',
                        width: 100,
                        align: 'right',
                        render: (val: number) => val ? val.toFixed(4) : '-',
                      },
                      {
                        title: 'Birim',
                        dataIndex: 'unit',
                        key: 'unit',
                        width: 80,
                        render: (val: string) => val || '-',
                      },
                      {
                        title: 'KDV %',
                        dataIndex: 'vat_rate',
                        key: 'vat_rate',
                        width: 80,
                        align: 'right',
                        render: (val: number) => val ? `%${(val * 100).toFixed(0)}` : '-',
                      },
                      {
                        title: 'Tevkifat %',
                        dataIndex: 'withholding_rate',
                        key: 'withholding_rate',
                        width: 90,
                        align: 'right',
                        render: (val: number) => val ? `%${(val * 100).toFixed(0)}` : '-',
                      },
                      {
                        title: 'Matrah',
                        dataIndex: 'vat_base',
                        key: 'vat_base',
                        width: 120,
                        align: 'right',
                        render: (val: number) => val ? val.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '-',
                      },
                      {
                        title: 'İşlem',
                        key: 'action',
                        width: 60,
                        align: 'center',
                        render: (_: any, record: any, index: number) => (
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => {
                              const newLines = editableLines.filter((_, i) => i !== index);
                              // Satır numaralarını yeniden düzenle
                              const reorderedLines = newLines.map((line, idx) => ({
                                ...line,
                                line_no: idx + 1
                              }));
                              setEditableLines(reorderedLines);
                            }}
                            disabled={editableLines.length <= 1}
                          />
                        ),
                      },
                    ]}
                    summary={() => {
                      const totalDebit = editableLines.reduce((sum, line) => sum + (parseFloat(line.debit as any) || 0), 0);
                      const totalCredit = editableLines.reduce((sum, line) => sum + (parseFloat(line.credit as any) || 0), 0);
                      const isBalanced = Math.abs(totalDebit - totalCredit) < 0.01;
                      
                      return (
                        <Table.Summary.Row>
                          <Table.Summary.Cell index={0} colSpan={4} align="right">
                            <strong>TOPLAM:</strong>
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={1} align="right">
                            <strong style={{ color: isBalanced ? 'green' : 'red' }}>
                              {totalDebit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </strong>
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={2} align="right">
                            <strong style={{ color: isBalanced ? 'green' : 'red' }}>
                              {totalCredit.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </strong>
                          </Table.Summary.Cell>
                          <Table.Summary.Cell index={3} colSpan={7}>
                            {!isBalanced && (
                              <span style={{ color: 'red', marginLeft: 8 }}>
                                ⚠️ Dengesiz (Fark: {Math.abs(totalDebit - totalCredit).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
                              </span>
                            )}
                          </Table.Summary.Cell>
                        </Table.Summary.Row>
                      );
                    }}
                  />
                </Card>

                {/* Uyarılar */}
                {importPreviewData.warnings && importPreviewData.warnings.length > 0 && (
                  <Card title="⚠️  Uyarılar" size="small">
                    <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                      {importPreviewData.warnings.map((warning: string, idx: number) => (
                        <li key={idx}>{warning}</li>
                      ))}
                    </ul>
                  </Card>
                )}
              </>
            )}
          </>
        )}
      </Modal>
    </div>
  );
};

export default EInvoicesPage;
