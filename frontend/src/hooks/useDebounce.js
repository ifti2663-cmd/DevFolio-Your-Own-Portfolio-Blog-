import { useEffect, useState } from 'react'
export function useDebounce(value, delay = 400) { const [result,setResult]=useState(value); useEffect(()=>{const id=setTimeout(()=>setResult(value),delay);return()=>clearTimeout(id)},[value,delay]); return result }
