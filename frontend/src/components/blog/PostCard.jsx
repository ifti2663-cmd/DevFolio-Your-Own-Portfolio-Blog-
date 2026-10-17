import { Link } from 'react-router-dom'
import { ArrowUpRight, Clock3, Eye } from 'lucide-react'
import { formatDate } from '../../utils/formatDate'
import './blog.css'
export function PostCard({post}){return <article className="card post-card">{post.cover_image_url&&<img src={post.cover_image_url} alt={`Cover image for ${post.title}`} loading="lazy"/>}<div className="post-body"><div className="post-meta">{post.category?.name}<span>·</span>{formatDate(post.published_at)}</div><h3>{post.title}</h3><p>{post.excerpt}</p><div className="post-footer"><span><Clock3 size={14}/>{post.reading_time} min</span><span><Eye size={14}/>{post.views_count}</span><Link aria-label={`Read ${post.title}`} to={`/blog/${post.slug}`}><ArrowUpRight size={18}/></Link></div></div></article>}
