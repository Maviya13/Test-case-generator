import React from 'react';
import { TestResult } from '../services/api';

interface TestResultsDisplayProps {
  results: TestResult;
}

const TestResultsDisplay: React.FC<TestResultsDisplayProps> = ({ results }) => {
  const { json_report, coverage_report, stdout, stderr } = results;

  const renderSummary = () => {
    if (!json_report || !json_report.summary) return null;
    const summary = json_report.summary;
    return (
      <div className="results-summary">
        <h3>Summary</h3>
        <p>Total tests: {summary.total || 0}</p>
        <p style={{ color: summary.failed > 0 ? 'red' : 'green' }}>Passed: {summary.passed || 0}</p>
        {summary.failed > 0 && <p style={{ color: 'red' }}>Failed: {summary.failed}</p>}
        {summary.skipped > 0 && <p>Skipped: {summary.skipped}</p>}
        {summary.error > 0 && <p style={{ color: 'red' }}>Errors: {summary.error}</p>}
      </div>
    );
  };

  const renderFailedTests = () => {
    if (!json_report || !json_report.tests) return null;
    const failedTests = json_report.tests.filter((test: any) => test.outcome === 'failed');
    if (failedTests.length === 0) return null;

    return (
      <div className="failed-tests">
        <h3>Failed Tests</h3>
        {failedTests.map((test: any, index: number) => (
          <div key={index} className="test-item failed">
            <h4>{test.nodeid}</h4>
            <pre>{test.call?.longrepr || 'Unknown error'}</pre>
          </div>
        ))}
      </div>
    );
  };

  const renderCoverage = () => {
    if (!coverage_report || !coverage_report.files) return null;

    const files = coverage_report.files;
    const moduleName = Object.keys(files)[0]; // Assuming one module for now
    const moduleCoverage = files[moduleName];

    if (!moduleCoverage || !moduleCoverage.summary) return null;

    const summary = moduleCoverage.summary;
    return (
      <div className="coverage-report">
        <h3>Code Coverage: {moduleName}</h3>
        <p>Statements: {summary.num_statements}</p>
        <p>Covered: {summary.covered_lines.length}</p>
        <p>Missing: {summary.missing_lines.length} ({summary.missing_lines.join(', ')})</p>
        <p>Percentage: {summary.percent_covered_display}%</p>
      </div>
    );
  };

  return (
    <div className="test-results-display">
      <h2>Test Run Details</h2>
      {renderSummary()}
      {renderFailedTests()}
      {renderCoverage()}
      {stdout && (
        <div className="raw-output">
          <h3>Standard Output</h3>
          <pre>{stdout}</pre>
        </div>
      )}
      {stderr && ( <div className="raw-output"><h3 style={{ color: 'red' }}>Standard Error</h3><pre>{stderr}</pre></div>)}
    </div>
  );
};

export default TestResultsDisplay;