export const formatDate = (date) => date ? new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric',year:'numeric'}).format(new Date(date)) : ''
