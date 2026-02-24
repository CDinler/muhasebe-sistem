// Fatura güncelle (PATCH)
export const updateEInvoice = async (id: number, data: Partial<EInvoice>): Promise<EInvoice> => {
  const response = await axios.patch(`${API_URL}/${id}`, data);
  return response.data;
};
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/v2/invoicing/einvoices';

export interface EInvoice {
  id: number;
  invoice_number: string;
  issue_date: string;
  issue_time?: string;
  signing_time?: string;
  invoice_uuid?: string;
  invoice_profile?: string;
  invoice_type?: string;
  invoice_category?: string;
  
  buyer_name?: string;
  buyer_tax_number?: string;
  buyer_tax_office?: string;
  
  supplier_name: string;
  supplier_tax_number?: string;
  supplier_tax_office?: string;
  supplier_address?: string;
  supplier_city?: string;
  supplier_district?: string;
  supplier_iban?: string;
  
  customer_name?: string;
  customer_tax_number?: string;
  
  currency_code: string;
  exchange_rate?: number;
  
  line_extension_amount: number;
  allowance_total?: number;
  charge_total?: number;
  tax_exclusive_amount?: number;
  tax_inclusive_amount?: number;
  payable_amount: number;
  
  total_tax_amount?: number;
  withholding_tax_amount?: number;
  withholding_percent?: number;
  withholding_code?: string;
  
  // PDF Support
  pdf_path?: string;
  has_xml?: boolean;
  source?: 'xml' | 'pdf_only' | 'manual' | 'api';
  
  payment_due_date?: string;
  order_number?: string;
  order_date?: string;
  waybill_number?: string;
  waybill_date?: string;
  
  processing_status: string;
  error_message?: string;
  
  contact_id?: number;
  contact_iban?: string;  // Contact'tan gelen IBAN (öncelikli)
  transaction_id?: number;
  cost_center_id?: number;
  xml_file_path?: string;
  raw_data?: any;
  invoice_lines?: InvoiceLine[];  // XML'den parse edilen satırlar
  tax_details?: TaxDetail[];  // Vergi detayları (UBL-TR TaxSubtotal)
  tax_totals?: TaxTotal[];  // Fatura seviyesinde vergiler (ESKİ)
  allowance_charges?: AllowanceCharge[];  // Masraf/indirimler
  created_at?: string;
  updated_at?: string;
}

export interface InvoiceLine {
  id?: string;
  item_name?: string;
  quantity?: number;
  unit?: string;
  unit_price?: number;
  line_total?: number;
  tax_amount?: number;
  tax_percent?: number;
  currency?: string;
}

export interface TaxDetail {
  id?: number;
  tax_type_code?: string;
  tax_name?: string;
  tax_percent?: number;
  taxable_amount?: number;
  tax_amount?: number;
  currency_code?: string;
  exemption_reason_code?: string;
  exemption_reason?: string;
}

export interface TaxTotal {
  tax_name?: string;
  tax_percent?: number;
  taxable_amount?: number;
  tax_amount?: number;
  currency?: string;
}

export interface AllowanceCharge {
  is_charge?: boolean;  // true: masraf, false: indirim
  reason?: string;
  amount?: number;
  tax_amount?: number;
  currency?: string;
}

export interface EInvoiceSummary {
  total_count: number;
  total_amount: number;
  parsed_count: number;
  imported_count: number;
  error_count: number;
  pending_count: number;
  
  // Kategorilere göre ayrım
  incoming_count: number;
  incoming_amount: number;
  incoming_archive_count: number;
  incoming_archive_amount: number;
  outgoing_count: number;
  outgoing_amount: number;
  outgoing_archive_count: number;
  outgoing_archive_amount: number;
}

export interface EInvoiceSupplier {
  supplier_name: string;
  supplier_tax_number: string;
  invoice_count: number;
  total_amount: number;
}

export interface EInvoiceFilters {
  skip?: number;
  limit?: number;
  status?: string;
  import_status?: string;
  supplier_tax_number?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  invoice_category?: string;
}

export const einvoiceService = {
    updateEInvoice,
  // Özet istatistikler
  getSummary: async (filters?: { date_from?: string; date_to?: string }): Promise<EInvoiceSummary> => {
    const response = await axios.get(`${API_URL}/summary`, { params: filters });
    return response.data;
  },

  // Fatura listesi
  getEInvoices: async (filters: EInvoiceFilters = {}): Promise<EInvoice[]> => {
    const response = await axios.get(API_URL, { params: filters });
    return response.data;
  },

  // Fatura detayı
  getEInvoice: async (id: number): Promise<EInvoice> => {
    const response = await axios.get(`${API_URL}/${id}`);
    return response.data;
  },

  // Tedarikçi listesi
  getSuppliers: async (): Promise<EInvoiceSupplier[]> => {
    const response = await axios.get(`${API_URL}/suppliers/list`);
    return response.data;
  },

  // Fatura sil
  deleteEInvoice: async (id: number): Promise<void> => {
    await axios.delete(`${API_URL}/${id}`);
  },

  // Muhasebe kaydına aktar
  importToAccounting: async (id: number, transactionData?: any): Promise<any> => {
    const response = await axios.post(`${API_URL}/${id}/import`, transactionData || null);
    return response.data;
  },

  // 🆕 Import önizleme (kayıt oluşturmadan göster)
  previewImport: async (id: number, categoryData?: any): Promise<any> => {
    const response = await axios.post(`${API_URL}/${id}/import-preview`, categoryData || null);
    return response.data;
  },

  // Excel/CSV dosyası yükle
  uploadFile: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // XML dosyası önizle (yüklemeden analiz et)
  previewXML: async (files: File[]): Promise<any> => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    const response = await axios.post(`${API_URL}/upload-xml-preview`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // XML dosyası yükle (tek XML veya ZIP)
  uploadXML: async (files: File[], direction: 'incoming' | 'outgoing' = 'incoming'): Promise<any> => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('direction', direction);
    const response = await axios.post(`${API_URL}/upload-xml`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // PDF dosyası yükle (E-Arşiv faturalar için)
  uploadPDF: async (file: File, direction: 'incoming' | 'outgoing' = 'incoming'): Promise<any> => {
    const formData = new FormData();
    formData.append('pdf_file', file);
    formData.append('direction', direction);
    const response = await axios.post(`${API_URL}/pdf/upload-pdf`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Mevcut faturaya PDF ekle
  attachPDF: async (invoiceId: number, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('pdf_file', file);
    const response = await axios.post(`${API_URL}/pdf/attach-pdf/${invoiceId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // PDF görüntüle/indir
  getPDF: async (invoiceId: number): Promise<Blob> => {
    const response = await axios.get(`${API_URL}/pdf/${invoiceId}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
