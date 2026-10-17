import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ExternalLink, Github, ArrowLeft } from 'lucide-react'
import { projectsApi } from '../api/endpoints/portfolio'
import { ErrorState, LoadingGrid } from '../components/ui/AppState'
import { formatDate } from '../utils/formatDate'
import './pages.css'
export function ProjectDetailPage(){const {slug}=useParams();const q=useQuery({queryKey:['project',slug],queryFn:()=>projectsApi.get(slug)});if(q.isLoading)return <section className="section"><div className="container"><LoadingGrid count={1}/></div></section>;if(q.isError)return <section className="section"><div className="container"><ErrorState error={q.error} retry={q.refetch}/></div></section>;const p=q.data;return <article className="section"><div className="container article"><Link className="text-link" to="/projects"><ArrowLeft size={16}/>All projects</Link>{p.cover_image_url&&<img className="detail-cover" src={p.cover_image_url} alt={`Screenshot of ${p.title}`}/>}<div className="eyebrow">{p.category} · {formatDate(p.completed_date)}</div><h1 className="title">{p.title}</h1><p className="lead">{p.summary}</p><div className="tag-list">{p.tech_stack_details?.map(t=><span key={t.id}>{t.name}</span>)}</div><div className="article-copy">{p.description}</div><div className="row">{p.live_url&&<a className="btn primary" href={p.live_url}>Live site <ExternalLink size={16}/></a>}{p.github_url&&<a className="btn" href={p.github_url}>Source <Github size={16}/></a>}</div></div></article>}
