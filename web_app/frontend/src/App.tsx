import { useState } from 'react'
import './App.css'
import { runTests, TestResult } from './services/api'
import TestResultsDisplay from './components/TestResultsDisplay'

function App() {
  const [moduleName, setModuleName] = useState<string>('sample_module')
  const [skipLlm, setSkipLlm] = useState<boolean>(false)
  const [maxCases, setMaxCases] = useState<number>(3)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [testResults, setTestResults] = useState<TestResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setIsLoading(true)
    setTestResults(null)
    setError(null)
    try {
      const results = await runTests({
        module_name: moduleName,
        skip_llm: skipLlm,
        max_cases: maxCases,
      })
      setTestResults(results)
    } catch (err: any) {
      setError(err.message || 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="App">
      <h1>AI Test Generator</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="moduleName">Module Name:</label>
          <input
            type="text"
            id="moduleName"
            value={moduleName}
            onChange={(e) => setModuleName(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="skipLlm">
            <input
              type="checkbox"
              id="skipLlm"
              checked={skipLlm}
              onChange={(e) => setSkipLlm(e.target.checked)}
            />
            Skip LLM Generation
          </label>
        </div>
        <div>
          <label htmlFor="maxCases">Max LLM Test Cases:</label>
          <input
            type="number"
            id="maxCases"
            value={maxCases}
            onChange={(e) => setMaxCases(parseInt(e.target.value))}
            min="1"
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Running Tests...' : 'Run AI Tests'}
        </button>
      </form>

      {error && <div style={{ color: 'red' }}>Error: {error}</div>}

      {testResults && (
        <TestResultsDisplay results={testResults} />
      )}
    </div>
  )
}

export default App
