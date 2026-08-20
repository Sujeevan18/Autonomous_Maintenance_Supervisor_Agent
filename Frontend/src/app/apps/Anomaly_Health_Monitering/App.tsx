import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  Award,
  Brain,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  FileText,
  Flame,
  Gauge,
  Info,
  Layers,
  Play,
  RefreshCw,
  RotateCcw,
  ShieldAlert,
  Sliders,
  Volume2,
  VolumeX,
  Wrench,
  Zap,
} from 'lucide-react';

export default function App() {
  // Active state variables
  const [simulatedCycles, setSimulatedCycles] = useState<number>(0);
  const [selectedComponent, setSelectedComponent] = useState<'HPC' | 'FAN' | 'LPC' | 'CC' | 'HPT'>('HPC');
  const [selectedEngine, setSelectedEngine] = useState<string>('ENG-FD001-042');
  const [selectedPolicy, setSelectedPolicy] = useState<string>('RL PPO Agent (Autonomous)');
  const [engineerValidation, setEngineerValidation] = useState<string>('Accept: Perform Preventive Maintenance');
  const [engineerNotes, setEngineerNotes] = useState<string>('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<boolean>(false);
  const [isRetraining, setIsRetraining] = useState<boolean>(false);
  const [isFusionRunning, setIsFusionRunning] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);

  // Engine Base Cycles mapping
  const engineBaseCycles: Record<string, number> = {
    'ENG-FD001-042': 168,
    'ENG-FD001-104': 142,
    'ENG-FD001-182': 185,
  };

  const baseCycle = engineBaseCycles[selectedEngine] || 168;
  const currentCycle = baseCycle + simulatedCycles;

  // Interrelated Dynamic Calculations based on simulated cycles slider
  const failureRisk = Math.min(99, Math.round(89 + simulatedCycles * 0.45));
  const risk24h = Math.min(98, Math.round(78 + simulatedCycles * 0.5));
  const risk72h = Math.min(100, Math.round(96 + simulatedCycles * 0.2));

  // RUL & Conformal Bounds
  const rulCycles = Math.max(2, 24 - simulatedCycles);
  const conformalLower = Math.max(1, Math.round(rulCycles - 5.2));
  const conformalUpper = Math.round(rulCycles + 5.2);

  // Anomaly Score
  const anomalyScore = (Math.min(0.99, 0.84 + simulatedCycles * 0.006)).toFixed(2);

  // Component Health Values
  const componentMetrics = {
    FAN: {
      name: 'Fan Inlet',
      health: Math.max(90, 98 - Math.floor(simulatedCycles * 0.3)),
      temp: (15.2 + simulatedCycles * 0.1).toFixed(1),
      press: '14.7',
      vib: (0.12 + simulatedCycles * 0.01).toFixed(2),
      sensor: 'Sensor_2 (Fan Inlet Temp)',
      xai: `Fan Inlet operating within nominal thermal bounds (${15.2 + simulatedCycles * 0.1}°C, 14.7 psi). No aerodynamic stall risks detected.`,
      counterfactual: 'Fan operational margins optimal; no operational throttling needed.',
    },
    LPC: {
      name: 'Low Press. Compressor',
      health: Math.max(80, 88 - Math.floor(simulatedCycles * 0.35)),
      temp: (240.5 + simulatedCycles * 0.4).toFixed(1),
      press: '45.2',
      vib: (0.35 + simulatedCycles * 0.02).toFixed(2),
      sensor: 'Sensor_3 (LPC Outlet Temp)',
      xai: `Low Pressure Compressor pressure ratio stable at 45.2 psi with low vibration variance (${0.35 + simulatedCycles * 0.02} mm/s).`,
      counterfactual: 'LPC pressure bleed valves operating within normal tolerance.',
    },
    HPC: {
      name: 'High Press. Compressor',
      health: Math.max(12, 42 - Math.floor(simulatedCycles * 1.2)),
      temp: (642.8 + simulatedCycles * 1.5).toFixed(1),
      press: '582.4',
      vib: (1.84 + simulatedCycles * 0.05).toFixed(2),
      sensor: 'Sensor_11 (HPC Pressure)',
      xai: `At Cycle ${currentCycle}, predicted 48h failure probability reached ${failureRisk}% with RUL at ${rulCycles} cycles. High Pressure Compressor (HPC) pressure anomaly attribution triggers action policy.`,
      counterfactual: 'If flight operations reduce HPC cruise pressure by 4.2% (thrust adjustment -3.0%), predicted RUL increases from ' + rulCycles + ' to ' + (rulCycles + 14) + ' cycles.',
    },
    CC: {
      name: 'Combustor Chamber',
      health: Math.max(38, 60 - Math.floor(simulatedCycles * 0.7)),
      temp: (1420 + simulatedCycles * 2.1).toFixed(0),
      press: '380.0',
      vib: (0.95 + simulatedCycles * 0.03).toFixed(2),
      sensor: 'Sensor_12 (CC Pressure)',
      xai: `Combustor Chamber thermal efficiency drops to ${Math.max(38, 60 - Math.floor(simulatedCycles * 0.7))}% due to HPC outlet pressure imbalance.`,
      counterfactual: 'Throttling combustor fuel flow ratio by 2.8% extends RUL by +8.5 cycles.',
    },
    HPT: {
      name: 'High Press. Turbine',
      health: Math.max(30, 54 - Math.floor(simulatedCycles * 0.8)),
      temp: (920.6 + simulatedCycles * 1.8).toFixed(1),
      press: '180.2',
      vib: (1.25 + simulatedCycles * 0.04).toFixed(2),
      sensor: 'Sensor_14 (HPT Temp)',
      xai: `High Pressure Turbine thermal variance (${(920.6 + simulatedCycles * 1.8).toFixed(1)}°C) triggers secondary thermal degradation alert.`,
      counterfactual: 'Cooling bleed valve adjustment (+1.5%) stabilizes turbine inlet temperature.',
    },
  };

  const activeComp = componentMetrics[selectedComponent];

  // Interrelated Policy Confidence Score
  const policyConfidences: Record<string, number> = {
    'RL PPO Agent (Autonomous)': 92.4,
    'Rule-Based Decision Fusion': 99.96,
    'Deep Q-Network Supervisor': 88.5,
  };
  const activeConfidence = policyConfidences[selectedPolicy] || 92.4;

  // Interrelated Action Policy & Urgency transition based on simulated cycles
  let actionTitle = 'Perform Preventive Maintenance';
  let actionCode = '#3';
  let actionUrgency = 'HIGH';
  let cardStyle = 'from-[#19150B] to-[#120F08] border-amber-500/40 text-amber-400';
  let badgeStyle = 'bg-amber-500/20 text-amber-300 border-amber-500/40';

  if (simulatedCycles >= 18 || rulCycles <= 6) {
    actionTitle = 'IMMEDIATE ENGINE GROUNDING';
    actionCode = '#5';
    actionUrgency = 'CRITICAL';
    cardStyle = 'from-[#260A0A] to-[#150505] border-red-500/60 text-red-400 animate-pulse';
    badgeStyle = 'bg-red-500/30 text-red-200 border-red-500/50';
  } else if (simulatedCycles >= 8 || rulCycles <= 16) {
    actionTitle = 'SCHEDULE IMMEDIATE OVERHAUL';
    actionCode = '#4';
    actionUrgency = 'HIGH';
    cardStyle = 'from-[#201005] to-[#120803] border-orange-500/50 text-orange-400';
    badgeStyle = 'bg-orange-500/25 text-orange-300 border-orange-500/40';
  }

  // Voice AI Speech Synthesis Helper
  const speakText = (text: string) => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleToggleAudio = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      } else {
        const scenarioSpeech = `Attention Chief Maintenance Engineer. Fleet monitoring unit ${selectedEngine}. Currently at Cycle ${currentCycle}. 48-hour failure risk is at ${failureRisk} percent, with predicted Remaining Useful Life of ${rulCycles} cycles. Component focus is ${activeComp.name}, attributed to ${activeComp.sensor}. Recommended action policy: ${actionTitle}, with policy confidence of ${activeConfidence} percent. ${activeComp.counterfactual}`;
        speakText(scenarioSpeech);
      }
    }
  };

  const handleRunFusion = () => {
    setIsFusionRunning(true);
    speakText(`Executing real-time decision fusion across RUL, failure risk, and anomaly agents for ${selectedEngine}.`);
    setTimeout(() => {
      setIsFusionRunning(false);
    }, 1200);
  };

  const handleRetrain = () => {
    setIsRetraining(true);
    speakText("Initiating multi-model retraining on LightGBM champion supervisor network. Calibrating hyper-parameters across 40,463 engine cycles.");
    setTimeout(() => {
      setIsRetraining(false);
    }, 1500);
  };

  const handleSubmitFeedback = (e: React.FormEvent) => {
    e.preventDefault();
    setFeedbackSubmitted(true);
    speakText(`Engineer feedback submitted. Policy network updated with validation: ${engineerValidation}.`);
    setTimeout(() => {
      setFeedbackSubmitted(false);
    }, 3000);
  };

  const handleGenerateCertificate = () => {
    speakText("Generating Maintenance Supervisor Compliance Certificate and audit report.");
    setTimeout(() => window.print(), 500);
  };

  return (
    <div className="min-h-screen bg-[#070A12] text-slate-100 font-sans p-4 lg:p-6 space-y-4 select-none">
      {/* ---------------------------------------------------------------- Top Header ---------------------------------------------------------------- */}
      <header className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4 bg-[#0D121F] border border-slate-800/80 rounded-2xl p-4 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-indigo-600/20 border border-indigo-500/40 rounded-xl text-indigo-400 shadow-inner">
            <Brain className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl lg:text-2xl font-extrabold tracking-tight text-white">
                Autonomous Maintenance Supervisor Agent
              </h1>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                Continuous Learning Active
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 font-medium">
              Reinforcement Learning Decision Fusion, Digital Twin &amp; Self-Adaptive Retraining Engine
            </p>
          </div>
        </div>

        {/* Header Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Engine Selection Dropdown */}
          <div className="relative">
            <select
              value={selectedEngine}
              onChange={(e) => setSelectedEngine(e.target.value)}
              className="appearance-none bg-slate-900 border border-slate-800 text-slate-200 text-xs font-bold rounded-xl px-3 py-2 pr-8 cursor-pointer focus:outline-none focus:border-indigo-500"
            >
              <option value="ENG-FD001-042">Unit: Engine-FD001-042</option>
              <option value="ENG-FD001-104">Unit: Engine-FD001-104</option>
              <option value="ENG-FD001-182">Unit: Engine-FD001-182</option>
            </select>
          </div>

          {/* AI Voice Assistant Audio Button */}
          <button
            onClick={handleToggleAudio}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl border transition ${
              isSpeaking
                ? 'bg-indigo-600/30 border-indigo-400 text-indigo-200 animate-pulse shadow-lg shadow-indigo-600/30'
                : 'bg-slate-900 border-slate-800 hover:border-slate-700 text-slate-300'
            }`}
            title="Click to Listen to Voice AI Scenario Briefing"
          >
            {isSpeaking ? (
              <>
                <Volume2 className="w-4 h-4 text-indigo-400 animate-bounce" />
                <span className="text-xs font-bold text-indigo-300">Speaking...</span>
              </>
            ) : (
              <>
                <Volume2 className="w-4 h-4 text-slate-400" />
                <span className="text-xs font-semibold text-slate-300">Audio Briefing</span>
              </>
            )}
          </button>

          <button
            onClick={handleGenerateCertificate}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-850 text-slate-200 text-xs font-semibold transition"
          >
            <Award className="w-4 h-4 text-blue-400" />
            Generate Certificate
          </button>

          {/* Policy Selector Dropdown */}
          <div className="relative">
            <select
              value={selectedPolicy}
              onChange={(e) => setSelectedPolicy(e.target.value)}
              className="appearance-none bg-slate-900 border border-indigo-500/40 text-indigo-300 text-xs font-bold rounded-xl px-4 py-2 pr-8 cursor-pointer focus:outline-none focus:border-indigo-400"
            >
              <option value="RL PPO Agent (Autonomous)">Policy: RL PPO Agent (Autonomous)</option>
              <option value="Rule-Based Decision Fusion">Policy: Rule-Based Decision Fusion</option>
              <option value="Deep Q-Network Supervisor">Policy: Deep Q-Network Supervisor</option>
            </select>
          </div>

          <button
            onClick={handleRetrain}
            disabled={isRetraining}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-200 text-xs font-semibold transition"
          >
            <RotateCcw className={`w-3.5 h-3.5 text-purple-400 ${isRetraining ? 'animate-spin' : ''}`} />
            {isRetraining ? 'Retraining...' : 'Retrain Models'}
          </button>

          <button
            onClick={handleRunFusion}
            disabled={isFusionRunning}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition active:scale-95"
          >
            <Play className={`w-3.5 h-3.5 fill-current ${isFusionRunning ? 'animate-bounce' : ''}`} />
            {isFusionRunning ? 'Fusing Telemetry...' : 'Run Decision Fusion'}
          </button>
        </div>
      </header>

      {/* ---------------------------------------------------------------- Live Status Bar ---------------------------------------------------------------- */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-2 bg-[#0D121F]/80 border border-slate-800/60 rounded-xl px-4 py-2 text-xs text-slate-400">
        <div className="flex items-center gap-2 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-bold text-slate-300">Live Federated Telemetry Stream:</span>
          <span className="text-slate-400">{selectedEngine} [Continuous Sampling Rate: 100 Hz]</span>
        </div>

        <div className="flex items-center gap-4 font-semibold text-[11px]">
          <span>
            Failure Risk Agent: <span className="text-emerald-400">ACTIVE</span>
          </span>
          <span>|</span>
          <span>
            RUL Prognostics Agent: <span className="text-emerald-400">ACTIVE</span>
          </span>
          <span>|</span>
          <span>
            Explainable Anomaly Agent: <span className="text-emerald-400">ACTIVE</span>
          </span>
        </div>
      </div>

      {/* ---------------------------------------------------------------- Prescriptive What-If Scenario Simulator ---------------------------------------------------------------- */}
      <section className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-3">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-indigo-400" />
              Prescriptive &quot;What-If&quot; Operational Scenario Simulator
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Simulate operational cycles into the future to observe real-time RL policy adaptation &amp; risk trajectory acceleration.
            </p>
          </div>

          <div className="bg-indigo-950/60 border border-indigo-500/40 rounded-lg px-3 py-1 text-xs font-mono font-bold text-indigo-300">
            Target Cycle: <span className="text-white">Cycle {currentCycle}</span>{' '}
            <span className="text-indigo-400">(+{simulatedCycles} cycles simulated)</span>
          </div>
        </div>

        {/* Range Slider Track */}
        <div className="pt-2 pb-1 space-y-2">
          <input
            type="range"
            min="0"
            max="22"
            step="1"
            value={simulatedCycles}
            onChange={(e) => setSimulatedCycles(Number(e.target.value))}
            className="w-full h-2 bg-slate-900 border border-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />

          <div className="flex justify-between text-[11px] font-mono text-slate-400 font-semibold px-1">
            <span className={simulatedCycles === 0 ? 'text-indigo-400 font-bold' : ''}>Current (Cycle {baseCycle})</span>
            <span className={simulatedCycles >= 5 && simulatedCycles < 10 ? 'text-indigo-400 font-bold' : ''}>+5 Cycles</span>
            <span className={simulatedCycles >= 10 && simulatedCycles < 15 ? 'text-indigo-400 font-bold' : ''}>+10 Cycles</span>
            <span className={simulatedCycles >= 15 && simulatedCycles < 22 ? 'text-indigo-400 font-bold' : ''}>+15 Cycles</span>
            <span className={simulatedCycles === 22 ? 'text-red-400 font-bold' : ''}>+22 Cycles (Critical Threshold)</span>
          </div>
        </div>
      </section>

      {/* ---------------------------------------------------------------- Top Metrics & Action Row ---------------------------------------------------------------- */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Card 1: Failure Risk */}
        <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl relative overflow-hidden flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center text-xs font-extrabold tracking-wider text-slate-400 uppercase">
              <span>FAILURE RISK (48H)</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>

            <div className="flex items-baseline gap-3 my-3">
              <span className={`text-4xl font-black font-mono tracking-tight ${failureRisk >= 95 ? 'text-red-400 animate-pulse' : 'text-amber-400'}`}>
                {failureRisk}%
              </span>
              <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold border uppercase ${failureRisk >= 95 ? 'bg-red-500/20 text-red-300 border-red-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'}`}>
                {failureRisk >= 95 ? 'Critical' : 'High Risk'}
              </span>
            </div>

            <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden mb-3 border border-slate-800">
              <div
                className={`h-full transition-all duration-300 ${failureRisk >= 95 ? 'bg-gradient-to-r from-red-600 to-amber-500' : 'bg-gradient-to-r from-amber-500 to-yellow-400'}`}
                style={{ width: `${failureRisk}%` }}
              />
            </div>
          </div>

          <div className="text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800/60 flex justify-between">
            <span>24h: {risk24h}%</span>
            <span>|</span>
            <span>72h: {risk72h}%</span>
          </div>
        </div>

        {/* Card 2: Remaining Useful Life & Conformal Interval */}
        <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center text-xs font-extrabold tracking-wider text-slate-400 uppercase">
              <span>REMAINING USEFUL LIFE (RUL)</span>
              <Clock className="w-4 h-4 text-indigo-400" />
            </div>

            <div className="flex items-baseline gap-2 my-3">
              <span className="text-4xl font-black text-indigo-400 font-mono tracking-tight">{rulCycles}</span>
              <span className="text-sm font-semibold text-slate-300">Cycles</span>
            </div>
          </div>

          <div className="space-y-1.5 pt-2 border-t border-slate-800/60 text-[11px]">
            <p className="text-slate-300 font-mono">
              95% Conformal CI: <span className="text-indigo-300 font-bold">[{conformalLower} - {conformalUpper}] cycles</span>
            </p>
            <p className="text-emerald-400 font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> Inductive Conformal Predictor (q_alpha: ±5.2)
            </p>
          </div>
        </div>

        {/* Card 3: Explainable Anomaly */}
        <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center text-xs font-extrabold tracking-wider text-slate-400 uppercase">
              <span>EXPLAINABLE ANOMALY</span>
              <Activity className="w-4 h-4 text-pink-400" />
            </div>

            <div className="flex items-baseline gap-3 my-3">
              <span className="text-4xl font-black text-pink-500 font-mono tracking-tight">{anomalyScore}</span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-pink-500/20 text-pink-300 border border-pink-500/40 uppercase">
                HIGH SEVERITY
              </span>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-800/60 text-[11px] text-slate-300">
            <span className="text-slate-400">Focus Component:</span>{' '}
            <span className="font-semibold text-pink-300">{activeComp.sensor}</span>
          </div>
        </div>

        {/* Card 4: Recommended Action (Dynamic Policy & Urgency) */}
        <div className={`bg-gradient-to-br ${cardStyle} rounded-2xl p-5 shadow-xl flex flex-col justify-between relative overflow-hidden`}>
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-1.5 text-xs font-bold">
              <Zap className="w-4 h-4 fill-current" />
              <span>RECOMMENDED ACTION ({selectedPolicy.split(' ')[0]})</span>
            </div>
            <span className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase border ${badgeStyle}`}>
              {actionUrgency} URGENCY
            </span>
          </div>

          <div className="my-2">
            <h3 className="text-xl font-black tracking-tight leading-snug">
              {actionTitle}
            </h3>
            <p className="text-xs opacity-80 font-mono mt-1">Action Code: {actionCode}</p>
          </div>

          <div className="flex justify-between items-center text-xs pt-2 border-t border-current/20">
            <span className="opacity-70 font-mono">Policy Confidence:</span>
            <span className="text-emerald-400 font-bold font-mono">{activeConfidence}%</span>
          </div>
        </div>
      </div>

      {/* ---------------------------------------------------------------- Middle Row: Component Heatmap & Interrelated Panels ---------------------------------------------------------------- */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Digital Twin Component Heatmap (Left 2/3) */}
        <div className="xl:col-span-2 bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Flame className="w-4 h-4 text-amber-400" />
                Digital Twin Aircraft Engine Component Thermal &amp; Degradation Heatmap ({selectedEngine})
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Click any component to inspect XAI attribution &amp; actionable counterfactual recommendations:
              </p>
            </div>

            <span className="text-xs font-mono text-indigo-400 font-semibold bg-indigo-950/60 border border-indigo-500/40 px-2.5 py-1 rounded-lg">
              Selected: {selectedComponent} ({activeComp.name})
            </span>
          </div>

          {/* 5 Component Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
            {(Object.keys(componentMetrics) as Array<keyof typeof componentMetrics>).map((key) => {
              const comp = componentMetrics[key];
              const isSelected = selectedComponent === key;
              const isDegraded = key === 'HPC' || comp.health < 60;

              return (
                <div
                  key={key}
                  onClick={() => setSelectedComponent(key)}
                  className={`p-3.5 rounded-xl space-y-2 cursor-pointer transition ${
                    isSelected
                      ? 'bg-indigo-950/50 border-2 border-indigo-500 shadow-lg shadow-indigo-950/60 ring-2 ring-indigo-500/30'
                      : isDegraded
                      ? 'bg-pink-950/20 border border-pink-500/40 hover:border-pink-400'
                      : 'bg-[#090D16] border border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className={`font-extrabold text-sm ${isSelected ? 'text-indigo-300' : 'text-white'}`}>
                      {key}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        comp.health >= 80
                          ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                          : comp.health >= 50
                          ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                          : 'bg-pink-500/30 text-pink-200 border-pink-500/50 animate-pulse'
                      }`}
                    >
                      {comp.health}%
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400">{comp.name}</p>

                  <div className="space-y-1 text-[11px] font-mono text-slate-300 pt-1 border-t border-slate-800/60">
                    <p>
                      Temp: <span className="text-white font-bold">{comp.temp}°C</span>
                    </p>
                    <p>
                      Press: <span className="text-white font-bold">{comp.press} psi</span>
                    </p>
                    <p>
                      Vib: <span className="text-white font-bold">{comp.vib} mm/s</span>
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Actionable Counterfactual Scenario Optimizer Box */}
          <div className="bg-indigo-950/30 border border-indigo-500/40 rounded-xl p-4 space-y-2">
            <h3 className="text-xs font-bold text-indigo-300 flex items-center gap-2 uppercase tracking-wider">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              Actionable Counterfactual Operational Optimization ({selectedComponent})
            </h3>
            <p className="text-xs text-slate-200 leading-relaxed font-mono">
              {activeComp.counterfactual}
            </p>
          </div>
        </div>

        {/* Right Stack: XAI Justification & Engineer Feedback (Right 1/3) */}
        <div className="space-y-4">
          {/* Explainable Decision Justification (XAI) */}
          <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-4 shadow-xl space-y-2">
            <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              Explainable Decision Justification (XAI)
            </h3>

            <div className="bg-[#070A12] border border-slate-800 rounded-xl p-3 text-xs text-slate-300 italic leading-relaxed">
              &quot;{activeComp.xai}&quot;
            </div>
          </div>

          {/* Human Engineer Feedback & Policy Adaptation */}
          <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-4 shadow-xl space-y-3">
            <div>
              <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wider">
                <FileText className="w-3.5 h-3.5 text-indigo-400" />
                Human Engineer Feedback &amp; Policy Adaptation
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Log engineer override or validation to continuously retrain the supervisor policy network.
              </p>
            </div>

            <form onSubmit={handleSubmitFeedback} className="space-y-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1 font-semibold">Engineer Decision Validation:</label>
                <select
                  value={engineerValidation}
                  onChange={(e) => setEngineerValidation(e.target.value)}
                  className="w-full bg-[#070A12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Accept: Perform Preventive Maintenance">Accept: {actionTitle}</option>
                  <option value="Override: Continue Operation">Override: Continue Operation</option>
                  <option value="Override: Immediate Grounding">Override: Immediate Grounding</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] text-slate-400 mb-1 font-semibold">Chief Engineer Notes:</label>
                <input
                  type="text"
                  value={engineerNotes}
                  onChange={(e) => setEngineerNotes(e.target.value)}
                  placeholder={`Notes for ${selectedComponent} (${activeComp.name})...`}
                  className="w-full bg-[#070A12] border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition active:scale-98"
              >
                {feedbackSubmitted ? '✓ Policy Network Updated!' : 'Submit Engineer Feedback & Adapt Policy'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* ---------------------------------------------------------------- Bottom Row: Multi-Horizon Risk Trajectory Evolution ---------------------------------------------------------------- */}
      <div className="bg-[#0D121F] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-3">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-400" />
            Multi-Horizon Failure Risk Trajectory Evolution ({selectedEngine} - {selectedComponent})
          </h2>
          <span className="text-xs text-slate-400 font-mono">Conformal Confidence Band: ±5.2 Cycles</span>
        </div>

        {/* SVG Risk Trajectory Chart */}
        <div className="w-full h-44 bg-[#070A12] border border-slate-800/80 rounded-xl p-4 relative overflow-hidden flex items-end">
          <svg className="w-full h-full overflow-visible" viewBox="0 0 1000 140" preserveAspectRatio="none">
            <defs>
              <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={failureRisk >= 95 ? '#ef4444' : '#f59e0b'} stopOpacity="0.5" />
                <stop offset="100%" stopColor={failureRisk >= 95 ? '#ef4444' : '#f59e0b'} stopOpacity="0.05" />
              </linearGradient>
            </defs>

            {/* Grid lines */}
            <line x1="0" y1="35" x2="1000" y2="35" stroke="#1e293b" strokeDasharray="4 4" />
            <line x1="0" y1="70" x2="1000" y2="70" stroke="#1e293b" strokeDasharray="4 4" />
            <line x1="0" y1="105" x2="1000" y2="105" stroke="#1e293b" strokeDasharray="4 4" />

            {/* Filled Area */}
            <path
              d="M 0 120 Q 250 110, 500 80 T 1000 20 L 1000 140 L 0 140 Z"
              fill="url(#riskGrad)"
            />

            {/* Main Risk Trajectory Line */}
            <path
              d="M 0 120 Q 250 110, 500 80 T 1000 20"
              fill="none"
              stroke={failureRisk >= 95 ? '#ef4444' : '#f59e0b'}
              strokeWidth="3"
            />

            {/* Interactive simulated cycle node */}
            <circle
              cx={Math.min(990, 50 + simulatedCycles * 42)}
              cy={120 - simulatedCycles * 4.5}
              r="6"
              fill={failureRisk >= 95 ? '#ef4444' : '#fbbf24'}
              stroke="#ffffff"
              strokeWidth="2"
              className="animate-pulse"
            />
          </svg>

          {/* Chart Y-Axis Labels */}
          <div className="absolute top-2 left-3 text-[10px] font-mono text-slate-500 space-y-5">
            <p>1.0</p>
            <p>0.75</p>
            <p>0.50</p>
            <p>0.25</p>
          </div>
        </div>
      </div>
    </div>
  );
}
