import apiClient from './api';
import { message } from 'antd';
import type { Dayjs } from 'dayjs';

export const downloadCariExcel = async (
  contactId: number,
  contactCode: string,
  startDate: Dayjs,
  endDate: Dayjs,
  accountFilter?: string
) => {
  try {
    message.loading({ content: 'Excel hazırlanıyor...', key: 'excel' });

    const response = await apiClient.get('/reporting/reports/cari/excel', {
      params: {
        start_date: startDate.format('YYYY-MM-DD'),
        end_date: endDate.format('YYYY-MM-DD'),
        contact_id: contactId,
        account_filter: accountFilter ? [accountFilter] : undefined,
      },
      responseType: 'blob',
    });

    // Dosyayı indir
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute(
      'download',
      `cari_ekstre_${contactCode}_${startDate.format('YYYYMMDD')}_${endDate.format('YYYYMMDD')}.xlsx`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    message.success({ content: 'Excel indirildi', key: 'excel' });
  } catch (error) {
    console.error('Excel indirilemedi:', error);
    message.error({ content: 'Excel indirilemedi', key: 'excel' });
  }
};

export const downloadCariPDF = async (
  contactId: number,
  contactCode: string,
  startDate: Dayjs,
  endDate: Dayjs,
  accountFilter?: string
) => {
  try {
    message.loading({ content: 'PDF hazırlanıyor...', key: 'pdf' });

    const response = await apiClient.get('/reporting/reports/cari/pdf', {
      params: {
        start_date: startDate.format('YYYY-MM-DD'),
        end_date: endDate.format('YYYY-MM-DD'),
        contact_id: contactId,
        account_filter: accountFilter ? [accountFilter] : undefined,
      },
      responseType: 'blob',
    });

    // Dosyayı indir
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute(
      'download',
      `cari_ekstre_${contactCode}_${startDate.format('YYYYMMDD')}_${endDate.format('YYYYMMDD')}.pdf`
    );
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    message.success({ content: 'PDF indirildi', key: 'pdf' });
  } catch (error) {
    console.error('PDF indirilemedi:', error);
    message.error({ content: 'PDF indirilemedi', key: 'pdf' });
  }
};

export const printCariReport = () => {
  window.print();
};
