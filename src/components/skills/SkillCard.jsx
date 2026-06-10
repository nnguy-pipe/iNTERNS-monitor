function SkillCard({ name, description, category, isCritical }) {
  return (
    <article className={`h-full min-h-[14rem] rounded-lg p-6 border ${isCritical ? 'border-l-4 border-l-sky-600 border-slate-200 bg-white' : 'border-slate-200 bg-white'}`}>
      <div>
        <h3 className="text-lg font-semibold text-slate-900">{name}</h3>
        <p className="mt-1 text-sm text-slate-500">{category}</p>
      </div>
      <p className="mt-4 text-slate-600 leading-7">{description}</p>
    </article>
  );
}

export default SkillCard;
