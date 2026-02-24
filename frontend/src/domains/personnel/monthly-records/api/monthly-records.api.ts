import axios from 'axios';
import type {
  MonthlyPersonnelRecord,
  MonthlyRecordsListParams,
  MonthlyRecordsListResponse,
  UploadSicilParams,
  UploadSicilResponse
} from '../types/monthly-records.types';

const API_BASE_URL = 'http://localhost:8000/api/v2/personnel/monthly-records';

export const monthlyRecordsApi = {
  /**
   * List monthly personnel records with filters
   */
  list: async (params?: MonthlyRecordsListParams): Promise<MonthlyRecordsListResponse> => {
    const response = await axios.get<MonthlyRecordsListResponse>(API_BASE_URL, { params });
    return response.data;
  },

  /**
   * Get all available periods
   */
  getPeriods: async (): Promise<string[]> => {
    const response = await axios.get<string[]>(`${API_BASE_URL}/periods`);
    return response.data;
  },

  /**
   * Get a specific monthly personnel record
   */
  get: async (id: number): Promise<MonthlyPersonnelRecord> => {
    const response = await axios.get<MonthlyPersonnelRecord>(`${API_BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Upload personnel sicil Excel file
   */
  uploadSicil: async ({ donem, file }: UploadSicilParams): Promise<UploadSicilResponse> => {
    const formData = new FormData();
    formData.append('donem', donem);
    formData.append('file', file);

    const response = await axios.post<UploadSicilResponse>(
      `${API_BASE_URL}/upload-sicil`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};
