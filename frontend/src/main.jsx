import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import App from './App'
import './styles/tokens.css'
import './styles/app.css'

const client = new QueryClient({ defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } } })
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><QueryClientProvider client={client}><ThemeProvider><AuthProvider><BrowserRouter><App /></BrowserRouter></AuthProvider></ThemeProvider></QueryClientProvider></React.StrictMode>)
