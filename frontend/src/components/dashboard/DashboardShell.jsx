import { BarChart3, BookOpenText, BriefcaseBusiness, FolderKanban, GraduationCap, Inbox, LogOut, MessageSquareMore, Tags, UserRound, Wrench } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './dashboard.css'
const links=[['/dashboard',BarChart3,'Overview'],['/dashboard/posts',BookOpenText,'Posts'],['/dashboard/projects',FolderKanban,'Projects'],['/dashboard/skills',Wrench,'Skills'],['/dashboard/experience',BriefcaseBusiness,'Experience'],['/dashboard/taxonomy',Tags,'Taxonomy'],['/dashboard/comments',MessageSquareMore,'Comments'],['/dashboard/messages',Inbox,'Messages'],['/dashboard/profile',UserRound,'Profile']]
export function DashboardShell(){const {logout}=useAuth();return <div className="dashboard"><aside className="dash-sidebar"><NavLink className="brand" to="/">DevFolio<span>_</span></NavLink><nav>{links.map(([to,Icon,label])=><NavLink end={to==='/dashboard'} key={to} to={to}><Icon size={17}/>{label}</NavLink>)}</nav><button className="side-logout" onClick={logout}><LogOut size={17}/>Sign out</button></aside><main className="dash-main"><Outlet/></main></div>}
