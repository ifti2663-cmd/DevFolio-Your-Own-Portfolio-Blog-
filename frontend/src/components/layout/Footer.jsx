import { Link } from 'react-router-dom'
import { Github, Linkedin, Mail } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { profileApi } from '../../api/endpoints/portfolio'
import './layout.css'
export function Footer(){const {data:p}=useQuery({queryKey:['profile'],queryFn:profileApi.get,retry:false,staleTime:300000});return <footer className="footer"><div className="container footer-grid"><div><div className="brand">{p?.full_name || 'DevFolio'}<span>_</span></div><p className="muted">{p?.headline}</p></div><div><p className="footer-label">Navigate</p><Link to="/projects">Projects</Link><Link to="/blog">Writing</Link><Link to="/contact">Contact</Link></div><div><p className="footer-label">Elsewhere</p><div className="socials">{p?.github_url&&<a href={p.github_url} aria-label="GitHub"><Github/></a>}{p?.linkedin_url&&<a href={p.linkedin_url} aria-label="LinkedIn"><Linkedin/></a>}{p?.email&&<a href={`mailto:${p.email}`} aria-label="Email"><Mail/></a>}</div></div></div><div className="container footer-bottom">© {new Date().getFullYear()} {p?.full_name || 'DevFolio'}. Built with care.</div></footer>}
