import {
  CheckCircle2,
  Eye,
  EyeOff,
  LoaderCircle,
  LockKeyhole,
  LogOut,
  RefreshCw,
  ShieldCheck,
  UserRound,
  WalletCards,
} from 'lucide-react'
import { useState } from 'react'
import { getOwnBalance, login, logout } from '../services/api'

const initialCredentials = {
  username: 'demo.rahim',
  password: 'Taka@2025',
}

function formatBalance(value, currency) {
  return new Intl.NumberFormat('en-BD', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(Number(value))
}

export default function BankingDemo() {
  const [credentials, setCredentials] = useState(initialCredentials)
  const [showPassword, setShowPassword] = useState(false)
  const [session, setSession] = useState(null)
  const [account, setAccount] = useState(null)
  const [loading, setLoading] = useState('')
  const [error, setError] = useState('')

  const handleChange = (event) => {
    setCredentials((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }))
  }

  const handleLogin = async (event) => {
    event.preventDefault()
    setLoading('login')
    setError('')
    try {
      const response = await login(credentials.username, credentials.password)
      setSession(response)
      setAccount(null)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading('')
    }
  }

  const handleBalance = async () => {
    setLoading('balance')
    setError('')
    try {
      setAccount(await getOwnBalance(session.session_token))
    } catch (requestError) {
      setError(requestError.message)
      if (requestError.code === 'INVALID_SESSION') {
        setSession(null)
        setAccount(null)
      }
    } finally {
      setLoading('')
    }
  }

  const handleLogout = async () => {
    setLoading('logout')
    setError('')
    try {
      await logout(session.session_token)
      setSession(null)
      setAccount(null)
      setCredentials(initialCredentials)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading('')
    }
  }

  return (
    <section className="mx-auto max-w-6xl">
      <div className="mb-8">
        <p className="mb-2 text-sm font-semibold uppercase tracking-[0.2em] text-cyan-400">
          Protected banking portal
        </p>
        <h1 className="m-0 text-3xl font-bold text-white">Customer account access</h1>
        <p className="max-w-3xl text-slate-400">
          Every action travels through the HTTP bridge and is enforced by the Python TCP banking server.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="overflow-hidden rounded-2xl border border-slate-800 bg-navy-900 shadow-2xl shadow-cyan-950/20">
          <div className="flex items-center gap-3 border-b border-slate-800 bg-emerald-500/5 px-6 py-4">
            <span className="rounded-lg bg-emerald-500/10 p-2 text-emerald-400">
              <LockKeyhole size={20} />
            </span>
            <div>
              <h2 className="m-0 text-base font-semibold text-white">Secure sign in</h2>
              <p className="m-0 text-sm text-slate-500">Synthetic demonstration account</p>
            </div>
          </div>

          <div className="p-6">
            {!session ? (
              <form onSubmit={handleLogin} className="space-y-5">
                <div>
                  <label htmlFor="username" className="mb-2 block text-sm font-medium text-slate-300">
                    Username
                  </label>
                  <div className="relative">
                    <UserRound className="absolute left-3 top-3 text-slate-500" size={19} />
                    <input
                      id="username"
                      name="username"
                      value={credentials.username}
                      onChange={handleChange}
                      autoComplete="username"
                      className="w-full rounded-lg border border-slate-700 bg-slate-950 py-2.5 pl-11 pr-3 text-white outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                    />
                  </div>
                </div>
                <div>
                  <label htmlFor="password" className="mb-2 block text-sm font-medium text-slate-300">
                    Password
                  </label>
                  <div className="relative">
                    <LockKeyhole className="absolute left-3 top-3 text-slate-500" size={19} />
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={credentials.password}
                      onChange={handleChange}
                      autoComplete="current-password"
                      className="w-full rounded-lg border border-slate-700 bg-slate-950 py-2.5 pl-11 pr-11 text-white outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((visible) => !visible)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      className="absolute right-3 top-2.5 p-1 text-slate-500 hover:text-slate-200"
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading === 'login'}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-500 px-4 py-3 font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading === 'login' ? <LoaderCircle className="animate-spin" size={19} /> : <ShieldCheck size={19} />}
                  Sign in securely
                </button>
                <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3 text-sm text-slate-400">
                  Demo credentials are prefilled. Passwords are stored only as PBKDF2 hashes by the protected service.
                </div>
              </form>
            ) : (
              <div className="space-y-5">
                <div className="flex items-start gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
                  <CheckCircle2 className="mt-0.5 text-emerald-400" size={21} />
                  <div>
                    <p className="m-0 font-semibold text-emerald-300">Authenticated session active</p>
                    <p className="mt-1 text-sm text-slate-400">Signed in as {session.display_name}</p>
                  </div>
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 text-sm">
                  <div className="flex justify-between gap-4 py-1 text-slate-400">
                    <span>Username</span><span className="font-mono text-slate-200">{session.username}</span>
                  </div>
                  <div className="flex justify-between gap-4 py-1 text-slate-400">
                    <span>Session</span><span className="text-emerald-400">Verified server-side</span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  disabled={loading === 'logout'}
                  className="flex w-full items-center justify-center gap-2 rounded-lg border border-slate-700 px-4 py-3 font-semibold text-slate-300 transition hover:border-red-500/60 hover:text-red-300 disabled:opacity-60"
                >
                  {loading === 'logout' ? <LoaderCircle className="animate-spin" size={19} /> : <LogOut size={19} />}
                  Log out
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-800 bg-navy-900 shadow-2xl shadow-blue-950/20">
          <div className="flex items-center gap-3 border-b border-slate-800 bg-blue-500/5 px-6 py-4">
            <span className="rounded-lg bg-blue-500/10 p-2 text-blue-400">
              <WalletCards size={20} />
            </span>
            <div>
              <h2 className="m-0 text-base font-semibold text-white">Account balance</h2>
              <p className="m-0 text-sm text-slate-500">Authorized owner-only operation</p>
            </div>
          </div>
          <div className="flex min-h-[390px] flex-col justify-center p-6 sm:p-8">
            {!session ? (
              <div className="text-center">
                <LockKeyhole className="mx-auto mb-4 text-slate-600" size={42} />
                <h3 className="text-lg font-semibold text-slate-200">Authentication required</h3>
                <p className="mx-auto max-w-md text-slate-500">
                  Sign in before requesting protected account information. The server does not trust a browser-supplied account identity.
                </p>
              </div>
            ) : account ? (
              <div>
                <p className="mb-2 text-sm uppercase tracking-[0.18em] text-slate-500">Available balance</p>
                <p className="my-0 font-mono text-4xl font-bold text-white sm:text-5xl">
                  {formatBalance(account.balance, account.currency)}
                </p>
                <div className="mt-6 flex items-center gap-2 text-sm text-emerald-400">
                  <ShieldCheck size={18} /> Authorized for {account.display_name}
                </div>
                <button
                  type="button"
                  onClick={handleBalance}
                  disabled={loading === 'balance'}
                  className="mt-8 flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2.5 text-sm text-slate-300 hover:border-cyan-500"
                >
                  <RefreshCw size={17} className={loading === 'balance' ? 'animate-spin' : ''} />
                  Refresh balance
                </button>
              </div>
            ) : (
              <div className="text-center">
                <WalletCards className="mx-auto mb-4 text-blue-400" size={46} />
                <h3 className="text-xl font-semibold text-white">Session verified</h3>
                <p className="mx-auto max-w-md text-slate-400">
                  Request your own balance through the protected TCP banking service.
                </p>
                <button
                  type="button"
                  onClick={handleBalance}
                  disabled={loading === 'balance'}
                  className="mx-auto mt-4 flex items-center justify-center gap-2 rounded-lg bg-blue-500 px-5 py-3 font-semibold text-white hover:bg-blue-400 disabled:opacity-60"
                >
                  {loading === 'balance' ? <LoaderCircle className="animate-spin" size={19} /> : <WalletCards size={19} />}
                  Check my balance
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div role="alert" className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-red-300">
          {error}
        </div>
      )}
    </section>
  )
}
