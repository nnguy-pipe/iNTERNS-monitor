function SkillCard({ name, description, category, isCritical }) {
  return (
    <article className={`h-full rounded-3xl p-6 shadow-sm ring-1 ring-slate-200 ${isCritical ? 'border-2 border-sky-600 bg-sky-50' : 'bg-white'}`}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-xl font-semibold text-slate-900">{name}</h3>
          <p className="mt-2 text-sm text-slate-500">{category}</p>
        </div>
        {isCritical && (
          <span className="rounded-full bg-sky-600 px-3 py-1 text-sm font-semibold text-white">Critical</span>
        )}
      </div>
      <p className="mt-4 text-slate-600 leading-7">{description}</p>
    </article>
  );
}

export default SkillCard;
