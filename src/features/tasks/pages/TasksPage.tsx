import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Clock, RefreshCw, CheckCircle2, User, Filter } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { getWeddingTasks, updateTask } from '@/services/api'
import { useWedding } from '@/context/WeddingContext'
import { fetchWithAuth } from '@/lib/api'

export function TasksPage() {
  const queryClient = useQueryClient()
  const { activeWeddingId: weddingId } = useWedding()
  const [assigneeFilter, setAssigneeFilter] = useState('All Staff')
  const [stageFilter, setStageFilter] = useState('all')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [actionMessage, setActionMessage] = useState<string | null>(null)

  // Form state
  const [newTitle, setNewTitle] = useState('')
  const [newStage, setNewStage] = useState('venue')
  const [newOwner, setNewOwner] = useState('Nisha Sharma')
  const [newPriority, setNewPriority] = useState('medium')
  const [newDueDate, setNewDueDate] = useState('10 Nov 2026')

  const { data: apiTasks = [], isLoading, refetch } = useQuery({
    queryKey: ['tasks', weddingId],
    queryFn: () => getWeddingTasks(weddingId),
  })

  // Mutation for updating task completion status
  const toggleMutation = useMutation({
    mutationFn: async ({ taskId, newStatus }: { taskId: string; newStatus: string }) => {
      return updateTask(taskId, { status: newStatus })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks', weddingId] })
    },
  })

  // Mutation for adding a new task
  const createMutation = useMutation({
    mutationFn: async () => {
      const res = await fetchWithAuth(`/api/v1/weddings/${weddingId}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle.trim(),
          stage: newStage,
          owner_name: newOwner,
          priority: newPriority,
          due_date: newDueDate,
          status: 'to_plan',
        }),
      })
      if (!res.ok) throw new Error('Failed to create task')
      return res.json()
    },
    onSuccess: (data) => {
      setActionMessage(`Task "${data.title}" added to production master file.`)
      setIsAddModalOpen(false)
      setNewTitle('')
      queryClient.invalidateQueries({ queryKey: ['tasks', weddingId] })
    },
  })

  const handleToggle = (task: any) => {
    const isCurrentlyDone = task.status === 'done' || task.status === 'completed'
    const newStatus = isCurrentlyDone ? 'to_plan' : 'done'
    toggleMutation.mutate({ taskId: task.id, newStatus })
  }

  // Filter tasks
  const filteredTasks = apiTasks.filter((t: any) => {
    const matchesAssignee =
      assigneeFilter === 'All Staff' ||
      (t.owner_name && t.owner_name.toLowerCase().includes(assigneeFilter.toLowerCase()))
    const matchesStage = stageFilter === 'all' || t.stage === stageFilter
    return matchesAssignee && matchesStage
  })

  const priorityVariant = (p?: string) => {
    switch (p?.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'danger'
      case 'urgent':
      case 'medium':
        return 'warning'
      default:
        return 'neutral'
    }
  }

  const staffOptions = ['All Staff', 'Aarav Mehta', 'Nisha Sharma', 'Kabir Verma', 'Rhea Kapoor']

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-warm-stone/80">
        <div>
          <span className="text-xs uppercase tracking-widest font-semibold text-bronze">
            Compliance & Milestones
          </span>
          <h1 className="font-serif text-3xl md:text-4xl font-bold text-ink mt-1 tracking-tight">
            Production Task Master
          </h1>
          <p className="text-sm text-ink-muted mt-2 max-w-2xl leading-relaxed">
            Statutory clearances, heritage site protocols, fire permits, and technical rigging deadlines for Mehra x Kapoor wedding.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="md"
            leftIcon={<RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={() => refetch()}
          >
            Refresh
          </Button>

          <Button
            variant="bronze"
            size="md"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={() => setIsAddModalOpen(true)}
          >
            Add Task
          </Button>
        </div>
      </div>

      {actionMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-3">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-3.5 rounded-xl border border-warm-stone">
        {/* Assignee Filter Dropdown */}
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-bronze" />
          <span className="text-xs font-semibold text-ink uppercase tracking-wider">Assignee:</span>
          <select
            value={assigneeFilter}
            onChange={(e) => setAssigneeFilter(e.target.value)}
            className="text-xs font-medium text-ink bg-ivory-warm border border-warm-stone rounded-md px-3 py-1.5 focus:outline-none focus:border-bronze"
          >
            {staffOptions.map((staff) => (
              <option key={staff} value={staff}>
                {staff}
              </option>
            ))}
          </select>
        </div>

        {/* Stage Filter Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-ink-muted font-medium mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5 text-bronze" />
            Stage:
          </span>
          {[
            { id: 'all', label: 'All' },
            { id: 'venue', label: 'Venue' },
            { id: 'catering', label: 'Catering' },
            { id: 'vendors', label: 'Vendors' },
            { id: 'transport', label: 'Transport' },
            { id: 'big_day', label: 'Ceremony' },
            { id: 'wrap_up', label: 'Wrap-up' },
          ].map((stg) => (
            <button
              key={stg.id}
              onClick={() => setStageFilter(stg.id)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium transition-all cursor-pointer ${
                stageFilter === stg.id
                  ? 'bg-[#541424] text-white'
                  : 'bg-warm-stone-light text-ink hover:bg-warm-stone'
              }`}
            >
              {stg.label}
            </button>
          ))}
        </div>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {filteredTasks.length === 0 && !isLoading && (
          <div className="p-8 text-center bg-white border border-warm-stone rounded-xl">
            <p className="text-sm font-medium text-ink">No tasks found matching your filter.</p>
            <p className="text-xs text-ink-muted mt-1">Try selecting a different staff member or stage.</p>
          </div>
        )}

        {filteredTasks.map((task: any) => {
          const isDone = task.status === 'done' || task.status === 'completed'
          const leadName = task.owner_name || 'Aarav Mehta'

          return (
            <Card
              key={task.id}
              variant="elevated"
              className={`p-4 flex items-center justify-between gap-4 transition-all ${
                isDone ? 'opacity-65 bg-ivory-warm/40' : 'hover:border-bronze/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={isDone}
                  onChange={() => handleToggle(task)}
                  className="w-4 h-4 accent-[#541424] rounded-sm cursor-pointer"
                  title={isDone ? 'Mark as in-progress' : 'Mark as completed'}
                />
                <div>
                  <p className={`text-sm font-medium ${isDone ? 'line-through text-ink-muted' : 'text-ink'}`}>
                    {task.title}
                  </p>
                  <div className="flex items-center gap-3 text-xs text-ink-muted mt-1">
                    <span className="font-serif">Mehra x Kapoor</span>
                    <span className="text-bronze font-medium">Lead: {leadName}</span>
                    <span className="capitalize px-1.5 py-0.2 bg-warm-stone-light rounded-sm text-[10px]">
                      {task.stage}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <Badge variant={priorityVariant(task.priority)}>
                  {task.priority || 'standard'}
                </Badge>
                <div className="flex items-center gap-1 text-xs text-ink-muted">
                  <Clock className="w-3.5 h-3.5 text-bronze" />
                  <span>{task.due_date || 'Upcoming'}</span>
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Add Task Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Production Task & Milestone"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
              Task Title
            </label>
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Confirm acoustic sound check with Superintendent of Police"
              className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
                Production Stage
              </label>
              <select
                value={newStage}
                onChange={(e) => setNewStage(e.target.value)}
                className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink"
              >
                <option value="venue">Venue & Heritage</option>
                <option value="catering">Catering & Banquet</option>
                <option value="design">Design & Florals</option>
                <option value="vendors">Vendors & Audio</option>
                <option value="transport">Transport & Valet</option>
                <option value="big_day">Ceremonial Cues</option>
                <option value="wrap_up">Wrap-up & Settlements</option>
              </select>
            </div>

            <div>
              <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
                Assigned Lead
              </label>
              <select
                value={newOwner}
                onChange={(e) => setNewOwner(e.target.value)}
                className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink"
              >
                <option value="Aarav Mehta">Aarav Mehta (Principal Producer)</option>
                <option value="Nisha Sharma">Nisha Sharma (Lead Planner)</option>
                <option value="Kabir Verma">Kabir Verma (Ceremony Coordinator)</option>
                <option value="Rhea Kapoor">Rhea Kapoor (Finance & Production)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
                Priority Level
              </label>
              <select
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
                className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink"
              >
                <option value="low">Standard</option>
                <option value="medium">Medium</option>
                <option value="high">Critical</option>
              </select>
            </div>

            <div>
              <label className="block font-medium text-ink mb-1 uppercase tracking-wider">
                Due Date / Milestone
              </label>
              <input
                type="text"
                value={newDueDate}
                onChange={(e) => setNewDueDate(e.target.value)}
                placeholder="14 Nov 2026"
                className="w-full p-2.5 bg-ivory-warm border border-warm-stone rounded-lg text-ink"
              />
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <Button variant="outline" size="sm" onClick={() => setIsAddModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="bronze"
              size="sm"
              onClick={() => createMutation.mutate()}
              disabled={createMutation.isPending || !newTitle.trim()}
            >
              {createMutation.isPending ? 'Saving...' : 'Save Milestone'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
