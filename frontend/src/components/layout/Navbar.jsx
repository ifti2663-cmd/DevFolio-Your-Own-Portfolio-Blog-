import { Link, NavLink } from 'react-router-dom'
import { Menu, Moon, Sun, X } from 'lucide-react'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { profileApi } from '../../api/endpoints/portfolio'
import { useTheme } from '../../context/ThemeContext'
import { useAuth } from '../../context/AuthContext'
import './layout.css'
const links=[['/','Home'],['/about','About'],['/projects','Projects'],['/blog','Blog'],['/contact','Contact']]
export function Navbar(){const [open,setOpen]=useState(false);const {data:profile}=useQuery({queryKey:['profile'],queryFn:profileApi.get,retry:false,staleTime:300000});const {theme,toggleTheme}=useTheme();const {isOwner}=useAuth();return <header className="nav"><div className="container nav-inner"><Link className="brand" to="/">{profile?.full_name || 'DevFolio'}<span>_</span></Link><nav className={open?'navlinks open':'navlinks'}>{links.map(([to,label])=><NavLink key={to} onClick={()=>setOpen(false)} to={to} end={to==='/'}>{label}</NavLink>)}{isOwner&&<NavLink to="/dashboard">Dashboard</NavLink>}</nav><div className="nav-actions"><button className="icon-btn" onClick={toggleTheme} aria-label="Toggle color theme">{theme==='dark'?<Sun size={18}/>:<Moon size={18}/>}</button><button className="icon-btn mobile-toggle" onClick={()=>setOpen(!open)} aria-label="Toggle navigation">{open?<X/>:<Menu/>}</button></div></div></header>}
