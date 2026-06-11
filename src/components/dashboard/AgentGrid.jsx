import AgentCard from './AgentCard.jsx';
import { useEffect, useState } from 'react';
function AgentGrid({ agents, environment }) {
  const [agentList, setAgentList] = useState(agents);

  useEffect(() => {
    fetch('http://localhost:8000/api/simulator/health')
      .then(response => response.json())
      .then(data => {
        setAgentList(prev =>
          prev.map(agent =>
            agent.name === 'Infrastructure Agent'
              ? { ...agent, status: data.status }
              : agent
          )
        );
      })
      .catch(err => console.error('Fetch error:', err));
  }, []);

  return (
    <section className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 items-stretch">
      {agents.map(agent => (
        <AgentCard key={agent.name} {...agent} />
      ))}
    </section>
  );
}

export default AgentGrid;
