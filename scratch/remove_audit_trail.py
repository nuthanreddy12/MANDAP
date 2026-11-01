with open("src/features/quotes/pages/QuotesPage.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Clean imports
old_imports = """  Award,
  AlertTriangle,
  Info,
  Check,
  Eye,
  FileSearch,
} from 'lucide-react'"""

new_imports = """  Award,
  AlertTriangle,
  Info,
  Check,
} from 'lucide-react'"""

assert old_imports in content, "old_imports not found"
content = content.replace(old_imports, new_imports, 1)

# 2. Remove state showAuditTrail
old_state = "  const [showAuditTrail, setShowAuditTrail] = useState<boolean>(false)\n"
assert old_state in content, "old_state not found"
content = content.replace(old_state, "", 1)

# 3. Remove button
old_button = """              <Button
                variant="ghost"
                size="sm"
                leftIcon={<Eye className="w-3.5 h-3.5 text-ink-muted" />}
                onClick={() => setShowAuditTrail(!showAuditTrail)}
              >
                {showAuditTrail ? 'Hide AI Audit Trail' : 'Inspect AI Audit Trail'}
              </Button>
"""
assert old_button in content, "old_button not found"
content = content.replace(old_button, "", 1)

# 4. Remove inspector block
old_inspector = """          {/* Judge AI Audit Trail Inspector */}
          {showAuditTrail && (
            <div className="bg-neutral-900 text-neutral-100 rounded-xl p-4 font-mono text-[11px] space-y-2 border border-neutral-700">
              <div className="flex items-center justify-between pb-2 border-b border-neutral-800">
                <span className="text-amber-400 font-semibold uppercase tracking-wider">
                  Gemini Evaluation Telemetry (Judge Audit Mode)
                </span>
                <span className="text-neutral-400">
                  Timestamp: {geminiWrapper?.ai_timestamp || new Date().toISOString()}
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-neutral-300">
                <div>Provider: <span className="text-emerald-400">{geminiWrapper?.ai_provider || 'Google Gemini'}</span></div>
                <div>Model: <span className="text-emerald-400">{geminiWrapper?.ai_model || 'gemini-3.5-flash-lite'}</span></div>
                <div>Status: <span className="text-emerald-400">{geminiWrapper?.ai_status || 'completed'}</span></div>
                <div>Math Deterministic: <span className="text-emerald-400">Verified (100% Match)</span></div>
              </div>
              <div className="pt-2">
                <span className="text-neutral-400 block mb-1">Evaluated Bidder Count: {quotes.length} Vendors</span>
                <pre className="bg-black/60 p-2.5 rounded-lg overflow-x-auto text-[10px] text-neutral-300">
                  {JSON.stringify(geminiIntel || insights, null, 2)}
                </pre>
              </div>
            </div>
          )}
"""
assert old_inspector in content, "old_inspector not found"
content = content.replace(old_inspector, "", 1)

assert "—" not in content, "Em dash detected"

with open("src/features/quotes/pages/QuotesPage.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("QuotesPage.tsx updated successfully without AI audit trail.")

