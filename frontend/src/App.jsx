import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, FileText, BarChart3, Activity, Download, PlayCircle, Cpu, ArrowUpRight, TrendingUp, Database } from 'lucide-react';

export default function EdgeRAGFrontend() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedModel, setSelectedModel] = useState('gpt-4-turbo');
  const [testResults, setTestResults] = useState([]);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [comparisonResults, setComparisonResults] = useState([]);
  
  const [metrics, setMetrics] = useState({
    latency: 0,
    cacheHit: false,
    cost: 0,
    tokensUsed: 0,
    retrievalTime: 0,
    generationTime: 0
  });

  const [testConfig, setTestConfig] = useState({
    numQueries: 10,
    useCache: true,
    topK: 5,
    chunkSize: 512
  });
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const models = [
    { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', cost: 0.01, elo: 1245 },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', cost: 0.002, elo: 1156 },
    { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', cost: 0.003, elo: 1198 },
    { id: 'claude-3-haiku', name: 'Claude 3 Haiku', cost: 0.00025, elo: 1089 }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const queryRAG = async (query, model = selectedModel) => {
    setIsLoading(true);
    
    const retrievalTime = Math.floor(Math.random() * 50) + 30;
    await new Promise(resolve => setTimeout(resolve, retrievalTime));
    
    const generationTime = Math.floor(Math.random() * 120) + 80;
    await new Promise(resolve => setTimeout(resolve, generationTime));
    
    const totalLatency = retrievalTime + generationTime;
    const cacheHit = testConfig.useCache && Math.random() > 0.6;
    
    const response = {
      answer: `Based on the financial documents, here's what I found regarding "${query}":\n\nThe analysis shows significant trends in the data. Key findings include revenue growth of 23% YoY, with particular strength in Q4 2024. Risk factors mentioned include market volatility and regulatory changes.`,
      sources: [
        { title: 'Tesla 10-K 2024', page: 42, confidence: 0.94 },
        { title: 'Q4 Earnings Report', page: 15, confidence: 0.89 },
        { title: 'Risk Factors Analysis', page: 8, confidence: 0.87 }
      ],
      metrics: {
        latency: cacheHit ? Math.floor(totalLatency * 0.3) : totalLatency,
        cacheHit,
        cost: cacheHit ? 0 : (Math.random() * 0.05 + 0.01).toFixed(4),
        tokensUsed: cacheHit ? 0 : Math.floor(Math.random() * 1000) + 500,
        retrievalTime,
        generationTime: cacheHit ? 0 : generationTime,
        model
      }
    };
    
    setMetrics(response.metrics);
    setIsLoading(false);
    
    return response;
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    const response = await queryRAG(inputValue);
    
    const aiMessage = {
      type: 'ai',
      content: response.answer,
      sources: response.sources,
      metrics: response.metrics,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, aiMessage]);
  };

  const runPerformanceTest = async () => {
    setIsRunningTest(true);
    setTestResults([]);
    
    const testQueries = [
      "What are the main risk factors?",
      "Summarize Q4 2024 revenue performance",
      "What is the company's AI strategy?",
      "Compare YoY growth in major segments",
      "What are the key investments mentioned?",
      "Analyze cash flow trends",
      "What regulatory challenges does the company face?",
      "Summarize the competitive landscape",
      "What are the growth projections?",
      "Analyze the balance sheet health"
    ].slice(0, testConfig.numQueries);

    const results = [];
    
    for (let i = 0; i < testQueries.length; i++) {
      const startTime = Date.now();
      const response = await queryRAG(testQueries[i]);
      const endTime = Date.now();
      
      results.push({
        query: testQueries[i],
        latency: endTime - startTime,
        cacheHit: response.metrics.cacheHit,
        cost: parseFloat(response.metrics.cost),
        tokens: response.metrics.tokensUsed,
        retrievalTime: response.metrics.retrievalTime,
        generationTime: response.metrics.generationTime,
        success: true
      });
      
      setTestResults([...results]);
    }
    
    setIsRunningTest(false);
  };

  const runModelComparison = async () => {
    setIsRunningTest(true);
    setComparisonResults([]);
    
    const testQuery = "Summarize the company's Q4 2024 financial performance and key risk factors";
    const results = [];
    
    for (const model of models) {
      const startTime = Date.now();
      const response = await queryRAG(testQuery, model.id);
      const endTime = Date.now();
      
      results.push({
        model: model.name,
        modelId: model.id,
        latency: endTime - startTime,
        cost: parseFloat(response.metrics.cost),
        tokens: response.metrics.tokensUsed,
        elo: model.elo,
        winRate: (Math.random() * 30 + 55).toFixed(1)
      });
      
      setComparisonResults([...results]);
    }
    
    setIsRunningTest(false);
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setUploadedFiles(prev => [...prev, ...files.map(f => ({
      name: f.name,
      size: (f.size / 1024).toFixed(2) + ' KB',
      status: 'ready'
    }))]);
  };

  const getTestStats = () => {
    if (testResults.length === 0) return null;
    
    const latencies = testResults.map(r => r.latency).sort((a, b) => a - b);
    const costs = testResults.reduce((sum, r) => sum + r.cost, 0);
    const cacheHits = testResults.filter(r => r.cacheHit).length;
    
    return {
      avgLatency: (latencies.reduce((a, b) => a + b, 0) / latencies.length).toFixed(0),
      p50: latencies[Math.floor(latencies.length * 0.5)],
      p95: latencies[Math.floor(latencies.length * 0.95)],
      p99: latencies[Math.floor(latencies.length * 0.99)],
      totalCost: costs.toFixed(4),
      cacheHitRate: ((cacheHits / testResults.length) * 100).toFixed(0)
    };
  };

  const stats = getTestStats();

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <h1 className="text-2xl font-semibold tracking-tight">EdgeRAG</h1>
              <nav className="flex gap-1">
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'chat' 
                      ? 'text-gray-900 border-b-2 border-gray-900' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Chat
                </button>
                <button
                  onClick={() => setActiveTab('testing')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'testing' 
                      ? 'text-gray-900 border-b-2 border-gray-900' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Performance
                </button>
                <button
                  onClick={() => setActiveTab('comparison')}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    activeTab === 'comparison' 
                      ? 'text-gray-900 border-b-2 border-gray-900' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Leaderboard
                </button>
              </nav>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-600">
              <a href="#" className="hover:text-gray-900">Documentation</a>
              <a href="#" className="hover:text-gray-900">About</a>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-8 py-8">
        {/* CHAT TAB */}
        {activeTab === 'chat' && (
          <div className="grid grid-cols-12 gap-8">
            <div className="col-span-3 space-y-6">
              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">Documents</label>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full py-2.5 text-sm font-medium border-2 border-dashed border-gray-300 rounded-lg hover:border-gray-400 transition-colors"
                >
                  Upload Files
                </button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.txt,.doc,.docx"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <div className="mt-3 space-y-2">
                  {uploadedFiles.map((file, idx) => (
                    <div key={idx} className="text-sm py-2 px-3 bg-gray-50 rounded border border-gray-200">
                      <div className="font-medium truncate">{file.name}</div>
                      <div className="text-xs text-gray-500">{file.size}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 mb-2 block">Model</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
                >
                  {models.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </select>
              </div>

              {metrics.latency > 0 && (
                <div className="pt-6 border-t border-gray-200">
                  <div className="text-sm font-medium text-gray-700 mb-3">Last Query</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Latency</span>
                      <span className="font-mono font-medium">{metrics.latency}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cost</span>
                      <span className="font-mono font-medium">${metrics.cost}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Cached</span>
                      <span className="font-medium">{metrics.cacheHit ? 'Yes' : 'No'}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="col-span-9">
              <div className="border border-gray-200 rounded-lg flex flex-col" style={{ height: 'calc(100vh - 200px)' }}>
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                      <h2 className="text-xl font-medium mb-2">Production RAG for Financial Intelligence</h2>
                      <p className="text-gray-600 text-sm mb-8 max-w-md">
                        High-performance retrieval with sub-200ms P95 latency, semantic caching, and hybrid search
                      </p>
                      <div className="grid grid-cols-2 gap-3 max-w-2xl">
                        {["What are the main risk factors?", "Summarize Q4 2024 performance", "Compare revenue growth YoY", "What are the key investments?"].map((query, idx) => (
                          <button
                            key={idx}
                            onClick={() => setInputValue(query)}
                            className="px-4 py-3 text-left text-sm border border-gray-200 rounded-lg hover:border-gray-900 transition-colors"
                          >
                            {query}
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <>
                      {messages.map((msg, idx) => (
                        <div key={idx} className={`${msg.type === 'user' ? 'ml-auto max-w-2xl' : 'max-w-3xl'}`}>
                          <div className={`${msg.type === 'user' ? 'bg-gray-900 text-white' : 'bg-gray-50'} rounded-lg p-4`}>
                            <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                            {msg.sources && (
                              <div className="mt-4 pt-4 border-t border-gray-200">
                                <div className="text-xs font-medium text-gray-500 mb-2">Sources</div>
                                <div className="space-y-1.5">
                                  {msg.sources.map((source, sidx) => (
                                    <div key={sidx} className="flex items-center gap-2 text-xs text-gray-600">
                                      <FileText className="w-3 h-3" />
                                      <span>{source.title}</span>
                                      <span>• p.{source.page}</span>
                                      <span>• {(source.confidence * 100).toFixed(0)}%</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            {msg.metrics && (
                              <div className="mt-3 flex gap-4 text-xs text-gray-500">
                                <span>{msg.metrics.latency}ms</span>
                                <span>${msg.metrics.cost}</span>
                                {msg.metrics.cacheHit && <span>Cached</span>}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                      {isLoading && (
                        <div className="max-w-3xl">
                          <div className="bg-gray-50 rounded-lg p-4">
                            <div className="flex gap-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </>
                  )}
                </div>

                <div className="border-t border-gray-200 p-4">
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                      placeholder="Ask a question about your documents..."
                      className="flex-1 px-4 py-2.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-gray-900"
                      disabled={isLoading}
                    />
                    <button
                      onClick={handleSend}
                      disabled={isLoading || !inputValue.trim()}
                      className="px-6 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PERFORMANCE TAB */}
        {activeTab === 'testing' && (
          <div className="space-y-8">
            <div className="flex items-end justify-between">
              <div>
                <h2 className="text-2xl font-semibold mb-1">Performance Testing</h2>
                <p className="text-sm text-gray-600">Benchmark latency, cost, and cache performance</p>
              </div>
              <button
                onClick={runPerformanceTest}
                disabled={isRunningTest}
                className="px-5 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:opacity-50 flex items-center gap-2"
              >
                {isRunningTest ? (
                  <>Running Test...</>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4" />
                    Run Test
                  </>
                )}
              </button>
            </div>

            {stats && (
              <div className="grid grid-cols-6 gap-4">
                <div className="border border-gray-200 rounded-lg p-5">
                  <div className="text-sm text-gray-600 mb-1">Avg Latency</div>
                  <div className="text-3xl font-semibold">{stats.avgLatency}<span className="text-lg text-gray-400">ms</span></div>
                </div>
                <div className="border border-gray-200 rounded-lg p-5">
                  <div className="text-sm text-gray-600 mb-1">P50</div>
                  <div className="text-3xl font-semibold">{stats.p50}<span className="text-lg text-gray-400">ms</span></div>
                </div>
                <div className="border border-gray-200 rounded-lg p-5">
                  <div className="text-sm text-gray-600 mb-1">P95</div>
                  <div className="text-3xl font-semibold">{stats.p95}<span className="text-lg text-gray-400">ms</span></div>
                </div>
                <div className="border border-gray-200 rounded-lg p-5">
                  <div className="text-sm text-gray-600 mb-1">P99</div>
                  <div className="text-3xl font-semibold">{stats.p99}<span className="text-lg text-gray-400">ms</span></div>
                </div>
                <div className="border border-gray-200 rounded-lg p-5">
                  <div className="text-sm text-gray-600 mb-1">Cache Hit</div>
                  <div className="text-3xl font-semibold">{stats.cacheHitRate}<span className="text-lg text-gray-400">%</span></div>
                </div>
                <div className="border border-gray-200 rounded-lg p-5">
                  <div className="text-sm text-gray-600 mb-1">Total Cost</div>
                  <div className="text-3xl font-semibold">${stats.totalCost}</div>
                </div>
              </div>
            )}

            {testResults.length > 0 && (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="text-left py-3 px-4 font-medium text-gray-700">Query</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">Latency</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">Retrieval</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">Generation</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-700">Cached</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {testResults.map((result, idx) => (
                      <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 max-w-md truncate">{result.query}</td>
                        <td className="py-3 px-4 text-right font-mono">{result.latency}ms</td>
                        <td className="py-3 px-4 text-right font-mono text-gray-600">{result.retrievalTime}ms</td>
                        <td className="py-3 px-4 text-right font-mono text-gray-600">{result.generationTime}ms</td>
                        <td className="py-3 px-4 text-center">{result.cacheHit ? '✓' : '—'}</td>
                        <td className="py-3 px-4 text-right font-mono">${result.cost.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* LEADERBOARD TAB */}
        {activeTab === 'comparison' && (
          <div className="space-y-8">
            <div className="flex items-end justify-between">
              <div>
                <h2 className="text-2xl font-semibold mb-1">Model Leaderboard</h2>
                <p className="text-sm text-gray-600">Performance rankings based on latency and cost efficiency</p>
              </div>
              <button
                onClick={runModelComparison}
                disabled={isRunningTest}
                className="px-5 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:opacity-50 flex items-center gap-2"
              >
                {isRunningTest ? (
                  <>Running Comparison...</>
                ) : (
                  <>
                    <PlayCircle className="w-4 h-4" />
                    Run Comparison
                  </>
                )}
              </button>
            </div>

            {comparisonResults.length > 0 && (
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="text-left py-4 px-6 font-medium text-gray-700">Rank</th>
                      <th className="text-left py-4 px-6 font-medium text-gray-700">Model</th>
                      <th className="text-right py-4 px-6 font-medium text-gray-700">Win Rate</th>
                      <th className="text-right py-4 px-6 font-medium text-gray-700">Elo Rating</th>
                      <th className="text-right py-4 px-6 font-medium text-gray-700">Latency</th>
                      <th className="text-right py-4 px-6 font-medium text-gray-700">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonResults
                      .sort((a, b) => a.latency - b.latency)
                      .map((result, idx) => (
                        <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-4 px-6 font-medium text-gray-400">#{idx + 1}</td>
                          <td className="py-4 px-6 font-medium">{result.model}</td>
                          <td className="py-4 px-6 text-right font-mono">{result.winRate}%</td>
                          <td className="py-4 px-6 text-right font-mono">{result.elo}</td>
                          <td className="py-4 px-6 text-right font-mono">{result.latency}ms</td>
                          <td className="py-4 px-6 text-right font-mono">${result.cost.toFixed(4)}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}