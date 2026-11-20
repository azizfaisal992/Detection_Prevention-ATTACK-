import { useState } from 'react'
import Sidebar from './components/Sidebar'
import BankingDemo from './pages/BankingDemo'
import Dashboard from './pages/Dashboard'
import Placeholder from './pages/Placeholder'

const titles = {
  banking: 'Banking Demo',
  attack: 'Attack Simulator',
  logs: 'Security Logs',
  about: 'About Project',
}

export default function App() {
  const [page, setPage] = useState('dashboard')

  return (
    <div className="min-h-screen bg-navy-950 text-slate-200 md:flex">
      <Sidebar activePage={page} onNavigate={setPage} />
      <main className="flex-1 p-6 sm:p-8 lg:p-12">
        {page === 'dashboard' && <Dashboard />}
        {page === 'banking' && <BankingDemo />}
        {!['dashboard', 'banking'].includes(page) && <Placeholder title={titles[page]} />}
      </main>
    </div>
  )
}

