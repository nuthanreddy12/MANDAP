import React, { useState, useEffect, useCallback } from "react"
import { useParams } from "react-router-dom"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { WeddingWorkspaceHeader } from "@/components/layout/WeddingWorkspaceHeader"
import { StatusBadge } from "@/components/ui/StatusBadge"
import { OwnerChip } from "@/components/ui/OwnerChip"
import { Modal } from "@/components/ui/Modal"
import { ToastContainer } from "@/components/ui/Toast"
import { useToast } from "@/hooks/useToast"
import { Plus, Clock, AlertTriangle, Edit2, Filter, CheckCircle2 } from "lucide-react"
import { fetchWithAuth } from "@/lib/api"

const taskSchema = z.object({
  title: z.string().min(3, "Task title must be at least 3 characters"),
  stage: z.string().default("venue"),
  status: z.string().default("to_plan"),
  priority: z.string().default("medium"),
  owner_name: z.string().default("Aarav Mehta"),
  due_date: z.string().optional(),
})

type TaskFormData = z.infer<typeof taskSchema>

interface TaskItem {
  id: string
  wedding_id: string
  title: string
  stage: string
  status: string
  priority: string
  owner_name: string
  due_date?: string
}

interface WeddingHeaderData {
  couple_names: string
  dates: string
  destination: string
  package_type: string
  guest_count: number
  health_status: string
}

export const WeddingPlanPage: React.FC = () => {
  const { id = "w1" } = useParams<{ id: string }>()
  const { toasts, addToast, removeToast } = useToast()

  const [wedding, setWedding] = useState<WeddingHeaderData>({
    couple_names: "Mehra x Kapoor",
    dates: "14 to 16 November 2026",
    destination: "Jaipur",
    package_type: "Full service",
    guest_count: 420,
    health_status: "on_track",
  })

  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [loading, setLoading] = useState(true)
  const [stageFilter, setStageFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [ownerFilter, setOwnerFilter] = useState("all")
  const [overdueOnly, setOverdueOnly] = useState(false)

  const [isAddOpen, setIsAddOpen] = useState(false)
  const [editingTask, setEditingTask] = useState<TaskItem | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema) as any,

    defaultValues: {
      title: "",
      stage: "venue",
      status: "to_plan",
      priority: "medium",
      owner_name: "Aarav Mehta",
      due_date: "",
    },
  })

  // Load wedding info
  useEffect(() => {
    fetchWithAuth(`/api/v1/weddings/${id}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && !data.error) {
          setWedding({
            couple_names: data.couple_names,
            dates: data.dates,
            destination: data.destination,
            package_type: data.package_type,
            guest_count: data.guest_count,
            health_status: data.health_status,
          })
        }
      })
      .catch(() => {})
  }, [id])

  // Load tasks
  const fetchTasks = useCallback(() => {
    setLoading(true)
    fetchWithAuth(`/api/v1/weddings/${id}/tasks`)
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        setTasks(data || [])
      })
      .catch(() => {
        addToast("Failed to load tasks from server", "error")
      })
      .finally(() => setLoading(false))
  }, [id, addToast])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  // Toggle status
  const handleToggleStatus = async (task: TaskItem) => {
    const nextStatus = task.status === "done" ? "in_progress" : "done"
    // Optimistic UI update
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, status: nextStatus } : t))
    )

    try {
      const res = await fetchWithAuth(`/api/v1/tasks/${task.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      })
      if (!res.ok) throw new Error("Failed to update status")
      addToast(`Task marked as ${nextStatus.replace("_", " ")}`, "success")
    } catch {
      // Revert on error
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: task.status } : t))
      )
      addToast("Failed to update task status on server", "error")
    }
  }

  // Open Edit Task Modal
  const handleEditClick = (task: TaskItem) => {
    setEditingTask(task)
    setValue("title", task.title)
    setValue("stage", task.stage)
    setValue("status", task.status)
    setValue("priority", task.priority)
    setValue("owner_name", task.owner_name)
    setValue("due_date", task.due_date || "")
  }

  // Submit Add or Edit Form
  const onSubmit = async (data: TaskFormData) => {
    setIsSubmitting(true)
    try {
      if (editingTask) {
        const res = await fetchWithAuth(`/api/v1/tasks/${editingTask.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        })
        if (!res.ok) throw new Error("Failed to update task")
        addToast("Task updated successfully", "success")
        setEditingTask(null)
      } else {
        const res = await fetchWithAuth(`/api/v1/weddings/${id}/tasks`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        })
        if (!res.ok) throw new Error("Failed to create task")
        addToast("New task added to wedding timeline", "success")
        setIsAddOpen(false)
      }
      reset()
      fetchTasks()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error saving task"
      addToast(msg, "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  const stages = ["all", "venue", "design", "catering", "vendors", "big_day", "wrap_up"]
  const owners = ["all", "Aarav Mehta", "Nisha Sharma", "Kabir Verma", "Rhea Kapoor"]

  // Filter tasks
  const todayStr = new Date().toISOString().split("T")[0]
  const filtered = tasks.filter((t) => {
    const matchStage = stageFilter === "all" || t.stage === stageFilter
    const matchStatus = statusFilter === "all" || t.status === statusFilter
    const matchOwner =
      ownerFilter === "all" || t.owner_name.toLowerCase().includes(ownerFilter.toLowerCase())
    const isOverdue = t.due_date && t.due_date < todayStr && t.status !== "done"
    const matchOverdue = !overdueOnly || isOverdue

    return matchStage && matchStatus && matchOwner && matchOverdue
  })

  const completedCount = tasks.filter((t) => t.status === "done").length

  return (
    <div className="flex flex-col min-h-full">
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      <WeddingWorkspaceHeader
        coupleName={wedding.couple_names}
        dates={wedding.dates}
        destination={wedding.destination}
        packageType={wedding.package_type}
        guestCount={wedding.guest_count}
        healthStatus={wedding.health_status}
      />

      <div className="p-4 md:p-8 max-w-[1440px] w-full mx-auto space-y-6">
        {/* Title bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2DBD0] pb-4">
          <div>
            <h3 className="font-editorial text-2xl text-[#292E27] font-normal">
              Instant Wedding Plan & Tasks
            </h3>
            <p className="text-xs text-[#878074] mt-0.5">
              {tasks.length} standard operational tasks · {completedCount} completed (
              {tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0}%)
            </p>
          </div>
          <button
            type="button"
            onClick={() => {
              reset()
              setIsAddOpen(true)
            }}
            className="px-3.5 py-2 bg-[#292E27] hover:bg-[#3D443A] text-[#FBFAF7] text-xs font-medium rounded-md transition-colors inline-flex items-center gap-1.5 self-start sm:self-auto shadow-xs cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5 text-[#C4A46D]" aria-hidden="true" />
            <span>Add task</span>
          </button>
        </div>

        {/* Filters and Controls */}
        <div className="bg-white p-3 border border-[#E2DBD0] rounded-lg flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          <div className="flex items-center gap-2 overflow-x-auto scrollbar-none pb-1">
            <span className="text-xs text-[#878074] shrink-0 font-medium">Stage:</span>
            {stages.map((stage) => (
              <button
                key={stage}
                type="button"
                onClick={() => setStageFilter(stage)}
                className={`px-2.5 py-1 text-xs rounded capitalize transition-colors shrink-0 cursor-pointer ${
                  stageFilter === stage
                    ? "bg-[#292E27] text-[#FBFAF7] font-medium"
                    : "bg-[#F4EFEA] text-[#69655D] hover:text-[#292E27]"
                }`}
              >
                {stage === "all" ? "All Stages" : stage.replace("_", " ")}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <Filter className="w-3.5 h-3.5 text-[#878074]" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md px-2 py-1 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
            >
              <option value="all">All Statuses</option>
              <option value="to_plan">To Plan</option>
              <option value="in_progress">In Progress</option>
              <option value="blocked">Blocked</option>
              <option value="done">Done</option>
            </select>

            <select
              value={ownerFilter}
              onChange={(e) => setOwnerFilter(e.target.value)}
              className="text-xs bg-[#F4EFEA] border border-[#E2DBD0] rounded-md px-2 py-1 text-[#292E27] focus:outline-none focus:border-[#C4A46D]"
            >
              <option value="all">All Planners</option>
              {owners.filter((o) => o !== "all").map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>

            <button
              type="button"
              onClick={() => setOverdueOnly(!overdueOnly)}
              className={`px-2.5 py-1 text-xs rounded border transition-colors flex items-center gap-1 cursor-pointer ${
                overdueOnly
                  ? "bg-rose-50 border-rose-300 text-rose-700 font-medium"
                  : "bg-white border-[#E2DBD0] text-[#69655D] hover:text-[#292E27]"
              }`}
            >
              <AlertTriangle className="w-3 h-3" />
              <span>Overdue Only</span>
            </button>
          </div>
        </div>

        {/* Task List */}
        {loading ? (
          <div className="bg-white border border-[#E2DBD0] rounded-lg p-6 space-y-4 animate-pulse">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-slate-100 rounded" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white border border-[#E2DBD0] rounded-lg p-12 text-center space-y-2">
            <p className="text-sm font-medium text-[#292E27]">No tasks match filter criteria</p>
            <p className="text-xs text-[#878074]">
              Adjust your stage or status selection to display tasks.
            </p>
          </div>
        ) : (
          <div className="bg-white border border-[#E2DBD0] rounded-lg divide-y divide-[#F4EFEA] shadow-xs">
            {filtered.map((task) => {
              const isDone = task.status === "done"
              const isOverdue =
                task.due_date && task.due_date < todayStr && !isDone

              return (
                <div
                  key={task.id}
                  className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-[#F9F7F4] transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <button
                      type="button"
                      onClick={() => handleToggleStatus(task)}
                      className="mt-0.5 text-slate-400 hover:text-emerald-600 transition-colors cursor-pointer"
                      title={isDone ? "Mark as in progress" : "Mark as done"}
                    >
                      <CheckCircle2
                        className={`w-5 h-5 ${
                          isDone ? "text-emerald-600 fill-emerald-100" : "text-slate-300"
                        }`}
                      />
                    </button>
                    <div>
                      <p
                        className={`text-xs font-medium ${
                          isDone ? "line-through text-[#878074]" : "text-[#292E27]"
                        }`}
                      >
                        {task.title}
                      </p>
                      <div className="flex items-center gap-2 text-[11px] text-[#878074] mt-0.5 flex-wrap">
                        <span className="capitalize">{task.stage.replace("_", " ")}</span>
                        <span>·</span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3 text-[#C4A46D]" />
                          <span>Due {task.due_date || "TBD"}</span>
                        </span>
                        {isOverdue && (
                          <span className="inline-flex items-center gap-0.5 px-1.5 py-0.2 bg-rose-100 text-rose-800 text-[10px] font-semibold rounded">
                            <AlertTriangle className="w-2.5 h-2.5" /> Overdue
                          </span>
                        )}
                        <span className="capitalize text-slate-500">
                          Priority: {task.priority}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2.5 shrink-0 self-end sm:self-center">
                    <OwnerChip name={task.owner_name} size="sm" />
                    <StatusBadge status={task.status} />
                    <button
                      type="button"
                      onClick={() => handleEditClick(task)}
                      className="p-1 rounded text-[#878074] hover:text-[#292E27] hover:bg-[#E9E3D8] transition-colors cursor-pointer"
                      title="Edit task"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Add / Edit Task Modal */}
        <Modal
          isOpen={isAddOpen || editingTask !== null}
          onClose={() => {
            setIsAddOpen(false)
            setEditingTask(null)
            reset()
          }}
          title={editingTask ? "Edit Wedding Task" : "Add Task to Wedding Plan"}
          subtitle="Assign responsible planner, priority, and completion deadline"
        >
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1 text-xs">
              <label className="text-slate-300 font-medium">Task Title *</label>
              <input
                {...register("title")}
                placeholder="e.g. Confirm guest transfer manifest"
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
              {errors.title && (
                <p className="text-rose-400 text-[11px]">{errors.title.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="space-y-1">
                <label className="text-slate-300 font-medium">Stage *</label>
                <select
                  {...register("stage")}
                  className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
                >
                  <option value="venue">Venue</option>
                  <option value="design">Design & Floral</option>
                  <option value="catering">Catering</option>
                  <option value="vendors">Vendors</option>
                  <option value="big_day">Big Day Operations</option>
                  <option value="wrap_up">Wrap Up & Settlement</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 font-medium">Status *</label>
                <select
                  {...register("status")}
                  className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
                >
                  <option value="to_plan">To Plan</option>
                  <option value="in_progress">In Progress</option>
                  <option value="blocked">Blocked</option>
                  <option value="done">Done</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 font-medium">Priority *</label>
                <select
                  {...register("priority")}
                  className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-300 font-medium">Responsible Planner *</label>
                <select
                  {...register("owner_name")}
                  className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
                >
                  <option value="Aarav Mehta">Aarav Mehta</option>
                  <option value="Nisha Sharma">Nisha Sharma</option>
                  <option value="Kabir Verma">Kabir Verma</option>
                  <option value="Rhea Kapoor">Rhea Kapoor</option>
                </select>
              </div>
            </div>

            <div className="space-y-1 text-xs">
              <label className="text-slate-300 font-medium">Completion Deadline</label>
              <input
                type="date"
                {...register("due_date")}
                className="w-full bg-[#1A2234] border border-[#2A364F] rounded px-3 py-2 text-white focus:outline-none focus:border-[#C4A46D]"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#1F293D]">
              <button
                type="button"
                onClick={() => {
                  setIsAddOpen(false)
                  setEditingTask(null)
                  reset()
                }}
                className="px-4 py-2 rounded text-xs text-slate-300 hover:text-white hover:bg-[#1E293B] transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 rounded text-xs font-semibold bg-[#C4A46D] hover:bg-[#B3935C] text-[#131926] transition-colors disabled:opacity-50 cursor-pointer"
              >
                {isSubmitting ? "Saving..." : editingTask ? "Update Task" : "Add Task"}
              </button>
            </div>
          </form>
        </Modal>
      </div>
    </div>
  )
}
