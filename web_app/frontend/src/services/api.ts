const API_BASE_URL = 'http://localhost:8000'; // Assuming FastAPI runs on port 8000

interface TestRunRequest {
  module_name: string;
  skip_llm?: boolean;
  max_cases?: number;
}

export interface TestResult {
  // Define the structure of your test results here based on FastAPI's response
  // For example:
  return_code: number;
  stdout: string;
  stderr: string;
  json_report?: any;
  coverage_report?: any;
}

export async function runTests(request: TestRunRequest): Promise<TestResult> {
  const response = await fetch(`${API_BASE_URL}/run-tests`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorDetail = await response.json();
    throw new Error(errorDetail.detail || 'Failed to run tests');
  }

  return response.json();
}