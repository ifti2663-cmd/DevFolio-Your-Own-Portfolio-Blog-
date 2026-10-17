import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { LockKeyhole } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { errorMessage } from '../utils/httpError'
import './pages.css'
export function LoginPage(){const [form,setForm]=useState({username:'',password:''});const {login,loginError}=useAuth();const navigate=useNavigate();const location=useLocation();const submit=async e=>{e.preventDefault();try{await login(form);navigate(location.state?.from?.pathname||'/dashboard',{replace:true})}catch{}};return <main className="login-page"><form className="card login-card" onSubmit={submit}><LockKeyhole size={28}/><div><div className="eyebrow">Owner access</div><h1>Welcome back.</h1></div><label className="field">Username<input autoComplete="username" required value={form.username} onChange={e=>setForm({...form,username:e.target.value})}/></label><label className="field">Password<input autoComplete="current-password" required type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label>{loginError&&<p className="error">{errorMessage(loginError)}</p>}<button className="btn primary">Sign in</button></form></main>}
