import re

# 1. Update QuotesPage.tsx
with open("src/features/quotes/pages/QuotesPage.tsx", "r", encoding="utf-8") as f:
    q_code = f.read()

if "import { useWedding }" not in q_code:
    q_code = q_code.replace(
        "import { formatINR } from '@/lib/formatters'",
        "import { formatINR } from '@/lib/formatters'\nimport { useWedding } from '@/context/WeddingContext'"
    )
q_code = re.sub(r"const\s+weddingId\s*=\s*['\"]w1['\"]", "const { activeWeddingId: weddingId } = useWedding()", q_code)
assert "—" not in q_code, "Em dash in QuotesPage.tsx"
with open("src/features/quotes/pages/QuotesPage.tsx", "w", encoding="utf-8") as f:
    f.write(q_code)
print("Updated QuotesPage.tsx with useWedding()")

# 2. Update FinancePage.tsx
with open("src/features/finance/pages/FinancePage.tsx", "r", encoding="utf-8") as f:
    fin_code = f.read()

if "import { useWedding }" not in fin_code:
    fin_code = fin_code.replace(
        "import { formatINR } from '@/lib/formatters'",
        "import { formatINR } from '@/lib/formatters'\nimport { useWedding } from '@/context/WeddingContext'"
    )
fin_code = re.sub(r"const\s+weddingId\s*=\s*['\"]w1['\"]", "const { activeWeddingId: weddingId } = useWedding()", fin_code)
assert "—" not in fin_code, "Em dash in FinancePage.tsx"
with open("src/features/finance/pages/FinancePage.tsx", "w", encoding="utf-8") as f:
    f.write(fin_code)
print("Updated FinancePage.tsx with useWedding()")

# 3. Update TasksPage.tsx
with open("src/features/tasks/pages/TasksPage.tsx", "r", encoding="utf-8") as f:
    t_code = f.read()

if "import { useWedding }" not in t_code:
    t_code = t_code.replace(
        "import { getWeddingTasks, updateTask } from '@/services/api'",
        "import { getWeddingTasks, updateTask } from '@/services/api'\nimport { useWedding } from '@/context/WeddingContext'"
    )
t_code = re.sub(r"const\s+weddingId\s*=\s*['\"]w1['\"]", "const { activeWeddingId: weddingId } = useWedding()", t_code)
assert "—" not in t_code, "Em dash in TasksPage.tsx"
with open("src/features/tasks/pages/TasksPage.tsx", "w", encoding="utf-8") as f:
    f.write(t_code)
print("Updated TasksPage.tsx with useWedding()")

# 4. Update RunOfShowPage.tsx
with open("src/features/run-of-show/pages/RunOfShowPage.tsx", "r", encoding="utf-8") as f:
    ros_code = f.read()

if "import { useWedding }" not in ros_code:
    ros_code = ros_code.replace(
        "import { Card, CardContent } from '@/components/ui/Card'",
        "import { Card, CardContent } from '@/components/ui/Card'\nimport { useWedding } from '@/context/WeddingContext'"
    )
ros_code = re.sub(r"const\s+\[weddingId\]\s*=\s*useState\(['\"]w1['\"]\)", "const { activeWeddingId: weddingId } = useWedding()", ros_code)
assert "—" not in ros_code, "Em dash in RunOfShowPage.tsx"
with open("src/features/run-of-show/pages/RunOfShowPage.tsx", "w", encoding="utf-8") as f:
    f.write(ros_code)
print("Updated RunOfShowPage.tsx with useWedding()")

# 5. Update DocumentsPage.tsx
with open("src/features/documents/pages/DocumentsPage.tsx", "r", encoding="utf-8") as f:
    doc_code = f.read()

if "import { useWedding }" not in doc_code:
    doc_code = doc_code.replace(
        "import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'",
        "import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'\nimport { useWedding } from '@/context/WeddingContext'"
    )
doc_code = re.sub(r"const\s+weddingId\s*=\s*['\"]w1['\"]", "const { activeWeddingId: weddingId } = useWedding()", doc_code)
assert "—" not in doc_code, "Em dash in DocumentsPage.tsx"
with open("src/features/documents/pages/DocumentsPage.tsx", "w", encoding="utf-8") as f:
    f.write(doc_code)
print("Updated DocumentsPage.tsx with useWedding()")

# 6. Update CustomerLoginPage.tsx with Demo Bypass UI
with open("src/features/customer/pages/CustomerLoginPage.tsx", "r", encoding="utf-8") as f:
    cust_code = f.read()

demo_bypass_snippet = '''          {/* Demo Bypass / Quick Access for Local Development */}
          <div className="mt-6 pt-5 border-t border-[#F0EBE1] space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-[#B8860B] uppercase tracking-wider flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Demo Access / Dev Bypass
              </span>
              <span className="text-[10px] text-[#A1A1AA] bg-[#FAF8F5] px-1.5 py-0.5 rounded border border-[#E8E2D9]">
                Auto-mapped
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setEmail('charanraghu38@gmail.com')
                  setPassword('demo1234')
                }}
                className="p-2 text-left bg-[#FAF8F5] hover:bg-[#F3EFEA] border border-[#E8E2D9] rounded-xl text-xs transition-colors cursor-pointer"
              >
                <span className="block font-medium text-[#1A1A1A]">Charan Raghu</span>
                <span className="block text-[10px] text-[#71717A] truncate">charanraghu38@gmail.com</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setEmail('priya.mehra@gmail.com')
                  setPassword('demo1234')
                }}
                className="p-2 text-left bg-[#FAF8F5] hover:bg-[#F3EFEA] border border-[#E8E2D9] rounded-xl text-xs transition-colors cursor-pointer"
              >
                <span className="block font-medium text-[#1A1A1A]">Priya Mehra</span>
                <span className="block text-[10px] text-[#71717A] truncate">priya.mehra@gmail.com</span>
              </button>
            </div>
          </div>
'''

if "Demo Access / Dev Bypass" not in cust_code:
    # Insert right before </form>
    cust_code = cust_code.replace("          </form>", demo_bypass_snippet + "          </form>")

assert "—" not in cust_code, "Em dash in CustomerLoginPage.tsx"
with open("src/features/customer/pages/CustomerLoginPage.tsx", "w", encoding="utf-8") as f:
    f.write(cust_code)
print("Updated CustomerLoginPage.tsx with Demo Bypass!")

# 7. Create src/components/ClientSanctuaryLogin.tsx
alias_code = '''// Alias export for canonical CustomerLoginPage component
export { CustomerLoginPage as default, CustomerLoginPage as ClientSanctuaryLogin } from '@/features/customer/pages/CustomerLoginPage'
'''
assert "—" not in alias_code, "Em dash in ClientSanctuaryLogin.tsx"
with open("src/components/ClientSanctuaryLogin.tsx", "w", encoding="utf-8") as f:
    f.write(alias_code)
print("Created src/components/ClientSanctuaryLogin.tsx successfully!")

