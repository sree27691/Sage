import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface ProductContext {
  product_id: string;
  url: string;
  metadata: {
    title: string;
    description: string;
  };
}

export interface TrustSummary {
  overall_verdict: string;
  aspects: {
    name: string;
    score_0_10: number;
    pros: string[];
    cons: string[];
  }[];
  claims: string[];
  conflicts: string[];
  uncertainties: string[];
}

export interface TCSComponents {
  groundedness: number;
  accuracy: number;
  coverage: number;
  conflict_detection: number;
  uncertainty: number;
  tcs_score: number;
  band: string;
}

export interface ProcessResult {
  product_id: string;
  tcs_score: number;
  tcs_band: string;
  tcs_components: TCSComponents;
  trust_summary: TrustSummary;
  product_context: ProductContext;
}

export const ingestWeb = async (url: string): Promise<ProductContext> => {
  const response = await axios.post(`${API_BASE_URL}/ingest/web`, { url });
  return response.data.product_context;
};

export const processContext = async (context: ProductContext): Promise<ProcessResult> => {
  const response = await axios.post(`${API_BASE_URL}/process`, { product_context: context });
  return response.data;
};
