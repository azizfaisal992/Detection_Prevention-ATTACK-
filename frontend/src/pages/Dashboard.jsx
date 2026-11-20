import { CheckCircle2, RefreshCw, Server, XCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getServerStatus } from '../services/api'

export default function Dashboard() {
  const [state, setState] = useState({
    loading: true,
    data: null,
    error: '',
  })

  const refresh = async () => {
    setState((old) => ({ ...old, loading: true, error: '' }))
    try {
      const data = await getServerStatus()
      setState({ loading: false, data, error: '' })
    } catch (error) {
      setState({ loading: false, data: null, error: error.message })
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  const online = state.data?.tcp_connected === true

  return (
    <section>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-cyan-400">
            Live system status
          </p>
          <h1 className="m-0 text-3xl font-bold text-white">Security overview</h1>
          <p className="text-slate-400">
            Live connectivity from React through HTTP to the protected TCP server.
          </p>
        </div>
        <button
          type="button"
          onClick={refresh}
          disabled={state.loading}
          className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-200 hover:border-cyan-500 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={state.loading ? 'animate-spin' : ''}
          />
          Refresh
        </button>
      </div>

      <div className="max-w-2xl rounded-2xl border border-slate-800 bg-navy-900 p-6 shadow-2xl shadow-cyan-950/20">
        <div className="flex items-start justify-between gap-4">
          <span className="rounded-xl bg-blue-500/10 p-3 text-blue-400">
            <Server />
          </span>
          {state.loading ? (
            <span className="text-sm text-slate-400">Checking...</span>
          ) : online ? (
            <span className="flex items-center gap-2 text-sm font-semibold text-emerald-400">
              <CheckCircle2 size={17} /> Connected
            </span>
          ) : (
            <span className="flex items-center gap-2 text-sm font-semibold text-red-400">
              <XCircle size={17} /> Offline
            </span>
          )}
        </div>
        <h2 className="mt-6 text-xl font-semibold text-white">
          Protected TCP banking server
        </h2>
        <p className="mb-0 text-slate-400">
          {state.error ||
            state.data?.message ||
            'Waiting for a real server response.'}
        </p>
      </div>
    </section>
  )
}

