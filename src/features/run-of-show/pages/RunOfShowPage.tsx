import { useState } from 'react'
import { Plus, MapPin } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface RunOfShowCue {
  time: string
  event: string
  venueLocus: string
  action: string
  cues: string
  responsibleLead: string
  status: 'Completed' | 'Current Cue' | 'Upcoming'
}

const MOCK_RUN_OF_SHOW: RunOfShowCue[] = [
  {
    time: '16:00',
    event: 'High Tea & Shehnai Welcoming',
    venueLocus: 'Zenana Mahal Courtyard',
    action: 'Royal welcome drink service commences; Shehnai troupe begins Raag Bhimpalasi',
    cues: 'Safa counters active with 12 tying artisans at East and West gates',
    responsibleLead: 'Pooja Chundawat',
    status: 'Completed',
  },
  {
    time: '18:15',
    event: 'Baraat Royal Procession Assembly',
    venueLocus: 'Main Palace Grand Gateway',
    action: 'Groom mounts ceremonial Marwari horse; Brass band leads procession toward Toran gate',
    cues: 'Folk dancers cue 200m before gate; Cold spark fountain cues on Groom arrival',
    responsibleLead: 'Vikramaditya Solanki',
    status: 'Current Cue',
  },
  {
    time: '19:45',
    event: 'Varmala & Royal Floral Shower',
    venueLocus: 'Manak Chowk Marble Stage',
    action: 'Bride entry on floral royal palanquin; exchange of garlands',
    cues: 'Audio cue: Track 04 Royal Varmala Theme; Rose petal shower triggered from palace ramparts',
    responsibleLead: 'Gayatri Rathore',
    status: 'Upcoming',
  },
  {
    time: '21:00',
    event: 'Vedic Pheras & Royal Mandap Ceremony',
    venueLocus: 'Central Octagonal Mandap',
    action: 'Traditional Vedic rituals conducted by royal head priest; sacred fire lighting',
    cues: 'Low volume instrumental sitar background; live relay to royal family lounges',
    responsibleLead: 'Gayatri Rathore',
    status: 'Upcoming',
  },
]

export function RunOfShowPage() {
  const [cues] = useState<RunOfShowCue[]>(MOCK_RUN_OF_SHOW)

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Minute by Minute Production
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Run of Show Run-Sheets
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Live technical cues, timing gates, musical cues, and lead producer assignments
            for active royal ceremonies.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Badge variant="bronze" className="py-1 px-3 text-xs">
            Live Ceremony: Ananya & Devendra Pheras
          </Badge>
          <Button
            variant="bronze"
            size="md"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => alert('New timeline cue entry form will open in Stage 2.')}
          >
            Add Cue
          </Button>
        </div>
      </div>

      <div className="relative border-l-2 border-warm-stone ml-4 md:ml-6 pl-6 space-y-6">
        {cues.map((cue) => (
          <div key={cue.time} className="relative group">
            {/* Timeline Node */}
            <div
              className={`absolute -left-[31px] top-2.5 w-4 h-4 rounded-full border-2 ${
                cue.status === 'Current Cue'
                  ? 'bg-bronze border-ink ring-4 ring-bronze/20'
                  : cue.status === 'Completed'
                  ? 'bg-garden border-white'
                  : 'bg-warm-stone-light border-warm-stone'
              }`}
            />

            <Card
              variant={cue.status === 'Current Cue' ? 'elevated' : 'default'}
              className={cue.status === 'Current Cue' ? 'border-bronze/60 bg-ivory-warm/40' : ''}
            >
              <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3">
                <div className="flex items-center gap-3">
                  <span className="font-serif font-bold text-lg text-ink bg-warm-stone-light/80 px-3 py-1 rounded-md border border-warm-stone/80">
                    {cue.time}
                  </span>
                  <div>
                    <CardTitle className="text-lg font-serif">{cue.event}</CardTitle>
                    <div className="flex items-center gap-1.5 text-xs text-ink-muted mt-0.5">
                      <MapPin className="w-3.5 h-3.5 text-bronze" aria-hidden="true" />
                      <span>{cue.venueLocus}</span>
                    </div>
                  </div>
                </div>

                <Badge
                  variant={
                    cue.status === 'Current Cue'
                      ? 'warning'
                      : cue.status === 'Completed'
                      ? 'success'
                      : 'neutral'
                  }
                >
                  {cue.status}
                </Badge>
              </CardHeader>

              <CardContent className="space-y-3 pt-3">
                <p className="text-sm text-ink leading-relaxed font-medium">
                  {cue.action}
                </p>

                <div className="bg-ivory-card p-3.5 rounded-md border border-warm-stone/80 text-xs">
                  <span className="font-semibold text-bronze uppercase tracking-wider text-[10px] block">
                    Technical & Production Cue
                  </span>
                  <p className="text-ink mt-0.5">{cue.cues}</p>
                </div>

                <div className="flex items-center justify-between text-xs text-ink-muted pt-2 border-t border-warm-stone/60">
                  <span>Producer On Ground: <strong className="text-ink">{cue.responsibleLead}</strong></span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => alert(`Broadcasting radio cue for ${cue.time} ${cue.event}`)}
                  >
                    Radio Broadcast
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        ))}
      </div>
    </div>
  )
}
