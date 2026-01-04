/**
 * E-Invoice TypeScript Types
 */

export interface EInvoice {
  id: number;
  
  // XML Tracking
  xml_file_path?: string;
  xml_hash?: string;
  invoice_category: 'incoming' | 'outgoing' | 'incoming-archive' | 'outgoing-archive';
  
  // Core Invoice
  invoice_uuid: string;
  invoice_number: string;
  invoice_profile?: string;
  invoice_type?: string;
  
  // Dates
  issue_date: string;
  issue_time?: string;
  tax_point_date?: string;
  signing_time?: string;
  
  // Supplier
  supplier_tax_number?: string;
  supplier_id_scheme?: string;
  supplier_name?: string;
  supplier_address?: string;
  supplier_city?: string;
  supplier_country?: string;
  
  // Customer
  customer_tax_number?: string;
  customer_id_scheme?: string;
  customer_name?: string;
  customer_address?: string;
  customer_city?: string;
  customer_country?: string;
  
  // Amounts
  line_extension_amount?: number;
  tax_exclusive_amount?: number;
  tax_inclusive_amount?: number;
  allowance_total_amount?: number;
  payable_amount?: number;
  
  // Processing
  processing_status?: string;
  processing_error?: string;
  matched_pdf_path?: string;
  pdf_metadata?: any;
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}

export interface EInvoiceSummary {
  total_count: number;
  total_amount: number;
  parsed_count: number;
  imported_count: number;
  error_count: number;
  pending_count: number;
  incoming_count: number;
  incoming_amount: number;
  incoming_archive_count: number;
  incoming_archive_amount: number;
  outgoing_count: number;
  outgoing_amount: number;
  outgoing_archive_count: number;
  outgoing_archive_amount: number;
}

export interface EInvoiceFilters {
  skip?: number;
  limit?: number;
  invoice_category?: string;
  processing_status?: string;
  supplier_name?: string;
  invoice_number?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface EInvoiceCreate {
  invoice_uuid: string;
  invoice_number: string;
  invoice_category: string;
  issue_date: string;
  // ... diğer gerekli alanlar
}

export interface EInvoiceUpdate {
  processing_status?: string;
  processing_error?: string;
  matched_pdf_path?: string;
  // ... diğer güncellenebilir alanlar
}
