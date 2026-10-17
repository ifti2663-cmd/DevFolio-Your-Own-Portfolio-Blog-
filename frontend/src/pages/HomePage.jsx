import { Hero, AboutPreview, SkillGrid, ExperienceTimeline, FeaturedProjects, LatestPosts, ContactCta } from '../components/home/HomeSections'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
export function HomePage(){useDocumentTitle('Home');return <><Hero/><AboutPreview/><SkillGrid/><ExperienceTimeline/><FeaturedProjects/><LatestPosts/><ContactCta/></>}
