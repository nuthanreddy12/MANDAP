import { useState } from 'react'
import { Plus, Clock } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

interface ProductionTask {
  id: string
  title: string
  wedding: string
  deadline: string
  lead: string
  priority: 'Critical' | 'Urgent' | 'Standard'
  completed: boolean
}

const MOCK_TASKS: ProductionTask[] = [
  {
    id: 't-1',
    title: 'Submit District Collector sound clearance for Jagmandir evening Sangeet',
    wedding: 'Meera & Kabir (Jagmandir)',
    deadline: 'Tomorrow, 5:00 PM',
    lead: 'Gayatri Rathore',
    priority: 'Critical',
    completed: false,
  },
  {
    id: 't-2',
    title: 'Finalize royal elephant procession route with Rambagh heritage authorities',
    wedding: 'Rhea & Arjun (Rambagh)',
    deadline: '03 Nov 2026',
    lead: 'Vikramaditya Solanki',
    priority: 'Urgent',
    completed: false,
  },
  {
    id: 't-3',
    title: 'Confirm cold pyro safety certificates with Udaipur fire department',
    wedding: 'Ananya & Devendra (Udaivilas)',
    deadline: '05 Nov 2026',
    lead: 'Gayatri Rathore',
    priority: 'Critical',
    completed: false,
  },
  {
    id: 't-4',
    title: 'Sample gold-printed welcome parchment menus with calligraphy master',
    wedding: 'Ananya & Devendra (Udaivilas)',
    deadline: '08 Nov 2026',
    lead: 'Pooja Chundawat',
    priority: 'Standard',
    completed: true,
  },
]

export function TasksPage() {
  const [tasks, setTasks] = useState<ProductionTask[]>(MOCK_TASKS)

  const toggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    )
  }

  const priorityVariant = (p: ProductionTask['priority']) => {
    switch (p) {
      case 'Critical':
        return 'danger'
      case 'Urgent':
        return 'warning'
      default:
        return 'neutral'
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Execution Checklists
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Production Tasks & Milestones
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Time sensitive permits, heritage venue compliances, and critical path deliverables
            monitored by lead event producers.
          </p>
        </div>

        <Button
          variant="bronze"
          size="md"
          leftIcon={<Plus className="w-4 h-4" />}
          onClick={() => alert('New production milestone form will open in Stage 2.')}
        >
          Add Critical Milestone
        </Button>
      </div>

      <Card variant="default" className="p-0 overflow-hidden shadow-xs">
        <div className="divide-y divide-warm-stone/60">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="p-5 flex items-start gap-4 hover:bg-ivory-warm/40 transition-colors"
            >
              <input
                type="checkbox"
                id={`task-${task.id}`}
                checked={task.completed}
                onChange={() => toggleTask(task.id)}
                className="mt-1 h-4 w-4 rounded-md border-warm-stone text-bronze focus:ring-bronze cursor-pointer accent-bronze"
              />

              <div className="flex-1">
                <label
                  htmlFor={`task-${task.id}`}
                  className={`text-sm font-semibold block cursor-pointer transition-colors ${
                    task.completed ? 'line-through text-ink-faint' : 'text-ink'
                  }`}
                >
                  {task.title}
                </label>

                <div className="flex flex-wrap items-center gap-3 text-xs text-ink-muted mt-1.5">
                  <span className="font-medium text-bronze">{task.wedding}</span>
                  <span>•</span>
                  <span>Lead: {task.lead}</span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-ink-muted" aria-hidden="true" />
                    Due: {task.deadline}
                  </span>
                </div>
              </div>

              <Badge variant={priorityVariant(task.priority)}>{task.priority}</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
