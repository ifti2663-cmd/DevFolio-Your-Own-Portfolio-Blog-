import './ui.css'
export function Modal({open,children,onClose}){if(!open)return null;return <div className="modal-backdrop" onMouseDown={onClose}><div className="modal" onMouseDown={e=>e.stopPropagation()}>{children}</div></div>}
