import SkillCard from './SkillCard.jsx';

function SkillsRegistry({ skills }) {
  return (
    <section id="skills" className="rounded-xl bg-white p-8 border border-slate-200 h-full">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-600">Skills registry</p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-900">Operational skills</h2>
        </div>
        <p className="text-sm text-slate-500">Skills are matched to active alerts in each environment.</p>
      </div>

      <div className="mt-8 grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-1 items-stretch">
        {skills.map((skill) => (
          <SkillCard
            key={skill.name}
            name={skill.name}
            description={skill.description}
            category={skill.category}
            isCritical={skill.name === 'Memory Leak Detection'}
          />
        ))}
      </div>
    </section>
  );
}

export default SkillsRegistry;
