import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'
import { Footer } from './Footer'
import { useVisitorId } from '../../hooks/useVisitorId'
export function Layout(){useVisitorId();return <><Navbar/><Outlet/><Footer/></>}
