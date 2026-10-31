import { LandingNavbar } from '../components/LandingNavbar'
import { HeroSection } from '../components/HeroSection'
import { AboutSection } from '../components/AboutSection'
import { HowItWorksSection } from '../components/HowItWorksSection'
import { CtaSection } from '../components/CtaSection'
import { LandingFooter } from '../components/LandingFooter'

export function LandingPage() {
  return (
    <div className="min-h-screen bg-ivory text-ink selection:bg-antique-brass/20 selection:text-ink">
      <LandingNavbar />
      <main>
        <HeroSection />
        <AboutSection />
        <HowItWorksSection />
        <CtaSection />
      </main>
      <LandingFooter />
    </div>
  )
}

export default LandingPage
