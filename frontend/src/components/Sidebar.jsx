import {
  Activity,
  Building2,
  FileText,
  Info,
  LayoutDashboard,
  ShieldAlert,
} from 'lucide-react'

const items = [
  ['dashboard', 'Dashboard', LayoutDashboard],
  ['banking', 'Banking Demo', Building2],
  ['attack', 'Attack Simulator', ShieldAlert],
  ['logs', 'Security Logs', FileText],
  ['about', 'About Project', Info],
]

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="border-b border-slate-800 bg-navy-900 p-4 md:min-h-screen md:w-64 md:border-b-0 md:border-r">
      <div className="mb-6 flex items-center gap-3 px-2">
        {/* <span className="rounded-lg bg-cyan-500/15 p-2 text-cyan-400">
          <Activity size={22} />
        </span> */}
        <div>
          <p className="m-0 font-bold text-white">MasqueradeGuard</p>
          <p className="m-0 text-xs text-slate-500">TCP Security Lab</p>
        </div>
      </div>
      <nav className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-1">
        {items.map(([id, label, Icon]) => (
          <button
            key={id}
            type="button"
            onClick={() => onNavigate(id)}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition ${
              activePage === id
                ? 'bg-cyan-500/15 text-cyan-300'
                : 'text-slate-400 hover:bg-slate-800 hover:text-white'
            }`}
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </nav>
    </aside>
  )
}

