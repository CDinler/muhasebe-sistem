import dayjs from 'dayjs';

/**
 * E-Fatura fiş numarası üretir (Backend mantığıyla uyumlu)
 * Format: EFT-YYYY-MM-XXXX
 * Örnek: EFT-2026-01-0001
 * 
 * NOT: Bu fonksiyon son fiş numarasını alarak sıralı numara üretir.
 * Backend'deki generate_transaction_number() fonksiyonuyla aynı mantık.
 * 
 * @param lastTransactionNumber - Son fiş numarası (örn: "EFT-2026-01-0025")
 * @param period - Muhasebe dönemi (YYYY-MM formatında, örn: "2026-01")
 * @returns Yeni fiş numarası
 */
export const generateEInvoiceTransactionNumber = (
  lastTransactionNumber: string | null | undefined,
  period?: string
): string => {
  // Dönem belirtilmemişse mevcut ayı kullan
  const accountingPeriod = period || dayjs().format('YYYY-MM');
  
  if (lastTransactionNumber) {
    try {
      // Son numarayı parse et (örn: "EFT-2026-01-0025" -> 25)
      const parts = lastTransactionNumber.split('-');
      const lastNum = parseInt(parts[parts.length - 1], 10);
      
      if (!isNaN(lastNum)) {
        // Bir sonraki numarayı üret
        return `EFT-${accountingPeriod}-${(lastNum + 1).toString().padStart(4, '0')}`;
      }
    } catch (error) {
      console.error('Son fiş numarası parse edilemedi:', error);
    }
  }
  
  // İlk fiş veya hata durumunda
  return `EFT-${accountingPeriod}-0001`;
};

/**
 * Genel fiş numarası üretir
 * Format: FIS-YYYY-MM-XXXX
 * Örnek: FIS-2026-01-0001
 * 
 * @param lastTransactionNumber - Son fiş numarası (örn: "FIS-2026-01-0025")
 * @param period - Muhasebe dönemi (YYYY-MM formatında, örn: "2026-01")
 * @returns Yeni fiş numarası
 */
export const generateTransactionNumber = (
  lastTransactionNumber: string | null | undefined,
  period?: string
): string => {
  const accountingPeriod = period || dayjs().format('YYYY-MM');
  
  if (lastTransactionNumber) {
    try {
      const parts = lastTransactionNumber.split('-');
      const lastNum = parseInt(parts[parts.length - 1], 10);
      
      if (!isNaN(lastNum)) {
        return `FIS-${accountingPeriod}-${(lastNum + 1).toString().padStart(4, '0')}`;
      }
    } catch (error) {
      console.error('Son fiş numarası parse edilemedi:', error);
    }
  }
  
  return `FIS-${accountingPeriod}-0001`;
};

/**
 * Dekont numarası üretir
 * Format: DKT-YYYY-MM-XXXX
 * Örnek: DKT-2026-01-0001
 * 
 * @param lastReceiptNumber - Son dekont numarası
 * @param period - Muhasebe dönemi (YYYY-MM formatında)
 * @returns Yeni dekont numarası
 */
export const generateReceiptNumber = (
  lastReceiptNumber: string | null | undefined,
  period?: string
): string => {
  const accountingPeriod = period || dayjs().format('YYYY-MM');
  
  if (lastReceiptNumber) {
    try {
      const parts = lastReceiptNumber.split('-');
      const lastNum = parseInt(parts[parts.length - 1], 10);
      
      if (!isNaN(lastNum)) {
        return `DKT-${accountingPeriod}-${(lastNum + 1).toString().padStart(4, '0')}`;
      }
    } catch (error) {
      console.error('Son dekont numarası parse edilemedi:', error);
    }
  }
  
  return `DKT-${accountingPeriod}-0001`;
};

/**
 * Fatura numarası üretir
 * Format: FAT-YYYY-MM-XXXX
 * Örnek: FAT-2026-01-0001
 * 
 * @param lastInvoiceNumber - Son fatura numarası
 * @param period - Muhasebe dönemi (YYYY-MM formatında)
 * @returns Yeni fatura numarası
 */
export const generateInvoiceNumber = (
  lastInvoiceNumber: string | null | undefined,
  period?: string
): string => {
  const accountingPeriod = period || dayjs().format('YYYY-MM');
  
  if (lastInvoiceNumber) {
    try {
      const parts = lastInvoiceNumber.split('-');
      const lastNum = parseInt(parts[parts.length - 1], 10);
      
      if (!isNaN(lastNum)) {
        return `FAT-${accountingPeriod}-${(lastNum + 1).toString().padStart(4, '0')}`;
      }
    } catch (error) {
      console.error('Son fatura numarası parse edilemedi:', error);
    }
  }
  
  return `FAT-${accountingPeriod}-0001`;
};

