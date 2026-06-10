import AgentCard from './AgentCard.jsx';

function AgentGrid({ agents }) {
  return (
    <section className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 items-stretch" aria-label="Agent status grid">
      {agents.map((agent) => (
        <AgentCard key={agent.name} {...agent} />
      ))}
    </section>
  );
}

export default AgentGrid;
