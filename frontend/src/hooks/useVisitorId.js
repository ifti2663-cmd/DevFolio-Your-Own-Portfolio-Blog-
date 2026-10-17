import { useEffect } from 'react'
export function useVisitorId(){ useEffect(()=>{if(!localStorage.getItem('visitorId')) localStorage.setItem('visitorId',crypto.randomUUID())},[]) }
