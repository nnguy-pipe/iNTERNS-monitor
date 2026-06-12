import { useState } from 'react';
import AgentCard from './AgentCard.jsx';

function AgentGrid({ agents }) {
  const agentList = Array.isArray(agents) ? agents : [];
  const [activeTab, setActiveTab] = useState('agents');

  const agentCards = agentList.filter((a) => a.type === 'agent');
  const subsystemCards = agentList.filter((a) => a.type === 'subsystem');

  const displayList = activeTab === 'agents' ? agentCards : subsystemCards;

  return (
    <div>
      <div className="flex gap-4 mb-6 border-b border-slate-200">
        <button
          onClick={() => setActiveTab('agents')}
          className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
            activeTab === 'agents'
              ? 'text-sky-600'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Agents
          {activeTab === 'agents' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-sky-600" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('subsystems')}
          className={`pb-3 px-1 text-sm font-medium transition-colors relative ${
            activeTab === 'subsystems'
              ? 'text-sky-600'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          Subsystems
          {activeTab === 'subsystems' && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-sky-600" />
          )}
        </button>
      </div>

      <section className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 items-stretch">
        {displayList.map((agent, index) => (
          <AgentCard key={agent.name || index} {...agent} />
        ))}
      </section>
    </div>
  );
}

export default AgentGrid;
