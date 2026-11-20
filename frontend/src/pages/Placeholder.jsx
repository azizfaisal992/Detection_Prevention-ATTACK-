export default function Placeholder({ title }) {
  return (
    <section>
      <h1 className="text-3xl font-bold text-white">{title}</h1>
      <div className="mt-8 rounded-2xl border border-dashed border-slate-700 bg-navy-900/60 p-10 text-center text-slate-400">
        This module is reserved for the next approved development stage.
      </div>
    </section>
  )
}

