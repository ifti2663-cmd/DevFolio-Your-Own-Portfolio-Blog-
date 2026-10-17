import { AlertCircle, RotateCw } from 'lucide-react'
import { errorMessage } from '../../utils/httpError'
export function LoadingGrid({count=3}){return <div className="grid">{Array.from({length:count},(_,i)=><div className="skeleton" key={i}/>)}</div>}
export function EmptyState({children}){return <div className="state">{children}</div>}
export function ErrorState({error,retry}){return <div className="state"><AlertCircle size={28}/><p>{errorMessage(error)}</p><button className="btn" onClick={retry}><RotateCw size={16}/>Retry</button></div>}
