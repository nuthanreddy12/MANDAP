with open("src/features/weddings/pages/WeddingsPage.tsx", "r", encoding="utf-8") as f:
    w_code = f.read()

if "import { useWedding }" not in w_code:
    w_code = w_code.replace(
        "import { getWeddings } from '@/services/api'",
        "import { getWeddings } from '@/services/api'\nimport { useWedding } from '@/context/WeddingContext'"
    )

w_code = w_code.replace(
    "  const [selectedCity, setSelectedCity] = useState<'All' | 'Jaipur' | 'Udaipur' | 'Jaisalmer'>('All')",
    "  const [selectedCity, setSelectedCity] = useState<'All' | 'Jaipur' | 'Udaipur' | 'Jaisalmer'>('All')\n  const { activeWeddingId, setActiveWeddingId } = useWedding()"
)

target_footer = '''              <Button
                variant="ghost"
                size="sm"
                rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                onClick={() => navigate('/quotes')}
              >
                Open Operations Desk
              </Button>'''

replacement_footer = '''              <div className="flex items-center gap-2">
                {wedding.id === activeWeddingId && (
                  <span className="text-[10px] uppercase tracking-wider text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded-full">
                    Active Desk
                  </span>
                )}
                <Button
                  variant={wedding.id === activeWeddingId ? "bronze" : "outline"}
                  size="sm"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                  onClick={() => {
                    setActiveWeddingId(wedding.id)
                    navigate('/quotes')
                  }}
                >
                  {wedding.id === activeWeddingId ? 'Active Desk' : 'Switch Workspace'}
                </Button>
              </div>'''

target_lf = target_footer.replace("\r\n", "\n")
target_crlf = target_footer.replace("\r\n", "\n").replace("\n", "\r\n")

if target_crlf in w_code:
    w_code = w_code.replace(target_crlf, replacement_footer.replace("\n", "\r\n"), 1)
    print("Found CRLF in WeddingsPage.tsx")
elif target_lf in w_code:
    w_code = w_code.replace(target_lf, replacement_footer, 1)
    print("Found LF in WeddingsPage.tsx")
else:
    print("Warning: target_footer not matched, checking alternate")

assert "—" not in w_code, "Em dash in WeddingsPage.tsx"
with open("src/features/weddings/pages/WeddingsPage.tsx", "w", encoding="utf-8") as f:
    f.write(w_code)
print("Updated WeddingsPage.tsx successfully!")

