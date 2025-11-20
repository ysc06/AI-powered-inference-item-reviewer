import React, { useEffect, useState } from "react"
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from "react-router-dom"

/* ===============================
   Config: change to match backend
   =============================== 
*/
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
const ITEMS_BASE = `${BASE_URL}/api/items`
const GENERATE_URL = `${ITEMS_BASE}/generate`


/* ===============================
   API layer (fetch) backend
   =============================== */

async function apiListItems() {
  const r = await fetch(`${ITEMS_BASE}/`)
  if (!r.ok) throw new Error(`List items failed: ${r.status}`)
  return r.json() 
}
async function apiApprove(id) {
  const r = await fetch(`${ITEMS_BASE}/${id}/approve`, { method: "POST" })
  if (!r.ok) throw new Error(`Approve failed: ${r.status}`)
  // Some backends return empty body; ignore JSON parse errors.
  return r.json().catch(()=> ({}))
}
async function apiReject(id) {
  const r = await fetch(`${ITEMS_BASE}/${id}/reject`, { method: "POST" })
  if (!r.ok) throw new Error(`Reject failed: ${r.status}`)
  return r.json().catch(()=> ({}))
}
// async function apiSimilar(id) {
//   const r = await fetch(`${ITEMS_BASE}/${id}/similar`)
//   // const r = await fetch(`${ITEMS_BASE}/${id}/similar?top_k=${top_k}`)
//   if (!r.ok) throw new Error(`Similar failed: ${r.status}`)
//   return r.json()
async function apiSimilar(id,top_k) {
  // const r = await fetch(`${ITEMS_BASE}/${id}/similar?top_k=6`);
  const r = await fetch(`${ITEMS_BASE}/${id}/similar?top_k=${encodeURIComponent(top_k)}`);
  if (!r.ok) {
    
    const msg = await r.text().catch(() => "");
    throw new Error(`Similar failed: ${r.status} ${msg}`);
  }
  // 优先尝试按 JSON 解析；如果不是 JSON，就退回纯文本
  
    return r.json();
  
}


async function apiCartList() {
  const r = await fetch(`${ITEMS_BASE}/cart`, { method: "POST" })
  if (!r.ok) throw new Error(`Cart list failed: ${r.status}`)
  return r.json()
}
async function apiCartCommit() {
  const r = await fetch(`${ITEMS_BASE}/cart/commit`, { method: "POST" })
  if (!r.ok) throw new Error(`Commit failed: ${r.status}`)
  return r.json()
}
async function apiGenerate({ prompt_text, docx_path }) {
  const body = { prompt_text: prompt_text || null, docx_path: docx_path || null }
  const r = await fetch(GENERATE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!r.ok) {
    const msg = await r.text()
    throw new Error(`Generate failed: ${r.status} ${msg}`)
  }
  return r.json()
}

/* ===============================
   Reusable child component (Props)
   =============================== */
// ItemCard shows one item. Parent passes data and event handlers via props.
function ItemCard({ item, onApprove, onReject, onSimilar, showDetailLink=true }) {
  const stimulus = item.stimulus
  const stem = item.stem
  const choices = Array.isArray(item.choices) ? item.choices : item.choice || []
  const answer = item.answer
  //const metadata = item.metadata

  return (
    <div style={{border:"5px solid #dde2d9f8", borderRadius:12, padding:15, margin:"0 auto 12px", width: "100%",maxWidth:"1000px"}}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <strong>Item #{item.id}</strong>
        <span style={{fontSize:14, color:"#adaaaaff"}}>
          {(item.status || "pending")}{item.committed ? " committed" : ""}
        </span>
      </div>

      {stimulus && (
        <div style={{marginTop:8}}>
          <div style={{fontSize:12, color:"#666"}}>Stimulus</div>
          <pre
  style={{
    background:"#f7f7f7",
    fontSize:20,
    fontFamily:'"Forum", serif',
    padding:8,
    borderRadius:8,
    maxHeight:800,
    overflow:"auto",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    overflowWrap: "anywhere"
    
  }}
>
  {typeof stimulus === "string" ? stimulus : JSON.stringify(stimulus, null, 2)}
</pre>

        </div>
      )}

      {stem && (
        <div style={{marginTop:8}}>
          <div style={{fontSize:12, color:"#666"}}>Stem</div>
          <div>{typeof stem === "string" ? stem : JSON.stringify(stem, null, 2)}</div>
        </div>
      )}

      {choices && choices.length > 0 && (
        <div style={{marginTop:8}}>
          <div style={{fontSize:12, color:"#666"}}>Choices</div>
          <ul>
            {choices.map((c, i) => <li key={i}>{typeof c === "string" ? c : JSON.stringify(c)}</li>)}
          </ul>
        </div>
      )}

      {answer != null && (
        <div style={{marginTop:8}}>
          <div style={{fontSize:12, color:"#666"}}>Answer</div>
          <div>{typeof answer === "string" ? answer : JSON.stringify(answer)}</div>
        </div>
      )}

      <div style={{marginTop:10, display:"flex", gap:8, flexWrap:"wrap", color: "#b4bfabca"}}>
        {onApprove && <button onClick={onApprove}>Approve</button>}
        {onReject && <button onClick={onReject}>Reject</button>}
        {onSimilar && <button onClick={onSimilar}>Find Similar</button>}
        {showDetailLink && <Link to={`/items/${item.id}`}><button>Detail</button></Link>}
      </div>
    </div>
  )
}

/* ===============================
   Page: Home 
   =============================== 
*/

function HomePage() {
  return (
    <div style={{padding:380,backgroundImage:'url("/4733.jpg")',minHeight: "100vh",

    backgroundRepeat:"no-repeat",
    backgroundSize:"130% auto",
    backgroundPosition:"center" }}>
      <h2 style={{textAlign: "center", marginBottom:16}}>Welcome to ExamFlux</h2>
      <div style = {{whiteSpace: "pre-wrap", wordBreak: "break-word",overflowWrap: "anywhere", maxWidth: 1200}}>
        <p>
        This platform uses AI to help learners practice intertextual
        reasoning—a higher-order comprehension skill in <strong>Bloom’s
        Taxonomy</strong>, comparable to <strong>TOEIC</strong> double- and
        triple-passage reading tasks. It requires synthesizing evidence across
        multiple texts rather than answering from a single source.
      </p>

      <p>
        <em>
          Standard LLMs typically default to single-pass factual Q&A, struggle to
          generate multiple thematically related yet non-redundant stimuli, and
          produce weak or inconsistent cross-text evidence without structured
          validation.
        </em>
      </p>

      <p>
        In contrast, our structured generation and validation pipeline creates
        coherent multi-text scenarios and inference-dependent MCQs that require
        true cross-passage synthesis.
      </p>

      <h4>Our unique capabilities:</h4>

        <ul>
          <li>Prompt-engineered, controllable generation with editable templates</li>
          <li>Context switching across genres and scenarios with an intertextual reasoning focus</li>
          <li>Semantic-embedding computation for similarity and redundancy detection</li>
          <li>Reviewer workflow: queue → approve/reject → commit and persist to database</li>
          <li>Full traceability of model outputs, scores, and human decisions</li>
          <li>React Router–based navigation with a streamlined detail view</li>
          <li>Modern full-stack architecture: React + FastAPI + OpenAI/Hugging Face</li>
        </ul>


        <Link to="/items">
        <div>
           <button style={{marginTop:8, backgroundColor:"#F5C9B0"}}>Go to Items</button>
        </div>
       
        </Link>
      </div>
    </div>
  )
}

/* ===============================
   Page: Items list (state/effect/map)
   =============================== */
// Uses state for data/loading/error and effect for initial load.
// Shows simple filter() on the array of items and maps to <ItemCard/>.
function ItemsPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [query, setQuery] = useState("")   // demo: filter by id or status

  async function load() {
    setLoading(true); setError("")
    try {
      const data = await apiListItems()
      setItems(Array.isArray(data) ? data : (data ? [data] : []))
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function handleApprove(id) {
  await apiApprove(id)
  setItems(prev => prev.filter(it => it.id !== id)) // Remove from the list
}

 async function handleReject(id) {
  await apiReject(id)
  setItems(prev => prev.filter(it => it.id !== id))
}

  async function handleSimilar(id) {
  try {
    const data = await apiSimilar(id, 6);          // { query_id, top_k, results }
    const results = Array.isArray(data?.results) ? data.results : [];
    if (results.length === 0) {
      alert(`No similar items for #${id}.`);
      return;
    }
    const lines = results.map(r => `#${r.id}  (score: ${r.score})`);
    alert(`Similar to #${id}:\n` + lines.join("\n"));
  } catch (e) {
    alert(String(e));
  }
}

  const shown = items
  .filter(it => {
    const s = (query || "").toLowerCase()
    return !s || String(it.id).includes(s) || String(it.status || "").toLowerCase().includes(s)
  })
  .filter(it => !["approved", "rejected"].includes((it.status || "").toLowerCase()))


  return (
    <div style={{padding:30, maxWidth: 1200, margin: "0 auto"}}>
      <h2>Items</h2>
      <div style={{margin:"50px", textAlign:"right"}}>
        <button onClick={load}>Refresh</button>
        <span style={{marginLeft:8}}>Search: </span>
        <input value={query} onChange={(e)=>setQuery(e.target.value)} placeholder=" enter id" />
      </div>

      {loading && <div>Loading…</div>}
      {error && <div style={{color:"red"}}>{error}</div>}
      {!loading && shown.length === 0 && <div>No items yet. Try Generate.</div>}

      {shown.map(it => (
        <ItemCard
          key={it.id}
          item={it}
          onApprove={() => handleApprove(it.id)} // event handler, pass as a prob to child components 
          onReject={() => handleReject(it.id)}
          onSimilar={() => handleSimilar(it.id)}
        />
      ))}
    </div>
  )
}

/* ===============================
   Page: Detail (useParams for /items/:id)
   =============================== */

function ItemDetailPage() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  async function load() {
    setLoading(true); setError("")
    try {
      const list = await apiListItems()
      const arr = Array.isArray(list) ? list : (list ? [list] : [])
      const found = arr.find(x => String(x.id) === String(id)) || null
      setItem(found)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }

  useEffect(()=>{ load() }, [id])

  async function onApprove(){ await apiApprove(id); load() }
  async function onReject() { await apiReject(id);  load() }
  async function onSimilar(){
    try { alert(JSON.stringify(await apiSimilar(id, 10), null, 2)) }
    catch(e){ alert(String(e)) }
  }

  return (
    <div style={{padding:16, maxWidth: 1200, margin: "0 auto"}}>

      <Link to="/items">← Back</Link>
      {loading && <div>Loading…</div>}
      {error && <div style={{color:"red"}}>{error}</div>}
      {item
        ? <ItemCard item={item} onApprove={onApprove} onReject={onReject} onSimilar={onSimilar} showDetailLink={false} />
        : (!loading && <div>Not found.</div>)
      }
    </div>
  )
}

/* ===============================
   Page: Generate (form handling)
   =============================== */
// Controlled inputs for prompt/docxPath. Submits to LLM endpoint.
function GeneratePage() {
  const [prompt, setPrompt] = useState("")
  const [docxPath, setDocxPath] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState("")
  const [result, setResult] = useState(null)
  const nav = useNavigate()

  async function onSubmit(e) {
    e.preventDefault()
    setBusy(true); setError(""); setResult(null)
    try {
      const out = await apiGenerate({ prompt_text: prompt, docx_path: docxPath || null })
      setResult(out)
    } catch (e) { setError(String(e)) }
    finally { setBusy(false) }
  }

  return (
  <div
    style={{
      minHeight: "100vh",
      display: "flex",
      justifyContent: "center",   // 整块卡片水平居中
      alignItems: "flex-start",   // 从上方开始排
      paddingTop: 60,
      paddingBottom: 40,
      paddingLeft: 16,
      paddingRight: 16,
      width:1200,
    }}
  >
    {/* 中间这张大卡片 */}
    <div
      style={{
        width: "100%",
        maxWidth: 900,             // 整块区域的最大宽度，比 600 大
        padding: 24,
        backgroundColor: "rgba(255,255,255,0.9)",
        borderRadius: 12,
        boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
        
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: 16 }}>Generate (LLM)</h2>

      <form
        onSubmit={onSubmit}
        style={{
          display: "grid",
          gap: 12,
          width: "100%",
        }}
      >
        <label style={{ display: "block" }}>
          Prompt Text
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            style={{
              width: "100%",
              height: 400,      // 固定一个大一点的高度
              resize: "none",   // 不允许用鼠标拖拉改变大小
              marginTop: 4,
              fontSize:20
            }}
          />
        </label>

        <label style={{ display: "block" }}>
          DOCX Path
          <input
            value={docxPath}
            onChange={(e) => setDocxPath(e.target.value)}
            style={{
              width: "100%",
              marginTop: 4,
            }}
          />
        </label>

        <div
          style={{
            display: "flex",
            gap: 8,
            marginTop: 8,
          }}
        >
          <button disabled={busy}>
            {busy ? "Generating..." : "Generate"}
          </button>
          <button type="button" onClick={() => nav("/items")}>
            Back to Items
          </button>
        </div>
      </form>

      {error && (
        <div style={{ color: "red", marginTop: 12 }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 20, color: "#666" }}>Backend Response</div>
          <pre
            style={{
              background: "#f7f7f7",
              padding: 12,
              borderRadius: 8,
              maxHeight: 400,
              overflow: "auto",
            }}
          >
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  </div>
)

}

/* ===============================
   Page: Cart (simple CRUD flow)
   =============================== */
// Shows approved-but-not-committed items and commits them.
function CartPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState("")
  const [committing, setCommitting] = useState(false)

  async function load() {
    setLoading(true); setErr("")
    try {
      const data = await apiCartList()
      const arr = Array.isArray(data) ? data : (data ? [data] : [])
      setItems(arr)
    } catch (e) { setErr(String(e)) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  async function commitAll() {
    setCommitting(true)
    try {
      const res = await apiCartCommit()
      alert(JSON.stringify(res, null, 2))
      await load()
    } catch (e) { alert(String(e)) }
    finally { setCommitting(false) }
  }

  return (
    <div style={{padding:16}}>
      <h2>Cart (approved but not committed)</h2>
      <div style={{margin:"8px 0", display:"flex", gap:8}}>
        <button onClick={load}>Refresh</button>
        <button onClick={commitAll} disabled={committing}>{committing ? "Committing..." : "Commit All"}</button>
      </div>

      {loading && <div>Loading…</div>}
      {err && <div style={{color:"red"}}>{err}</div>}
      {!loading && items.length === 0 && <div>No approved items to commit.</div>}

      {items.map(it => <ItemCard key={it.id} item={it} showDetailLink={false} />)}
    </div>
  )
}




/* ===============================
   Very simple NavBar (Links)
   =============================== */
function NavBar() {
  return (
    <nav style={{position:"sticky", top:0, background:"#fff", borderBottom:"1px solid #eee", padding:12}}>
      <div style={{display:"flex", alignItems:"center", gap:12}}>
        <Link to="/" style={{fontWeight:"bold"}}>Exam Item Reviewer</Link>
        <Link to="/items" style={{fontWeight:"bold"}}>Items</Link>
        <Link to="/generate" style={{fontWeight:"bold"}}>Generate</Link>
        <Link to="/cart" style={{fontWeight:"bold"}}>Cart</Link>
      </div>
    </nav>
  )
}

/* ===============================
   App root: Router + routes
   =============================== */
export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/items" element={<ItemsPage />} />
        <Route path="/items/:id" element={<ItemDetailPage />} />
        <Route path="/generate" element={<GeneratePage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="*" element={<div style={{padding:16}}>Not Found</div>} />
      </Routes>
    </BrowserRouter>
  )
}
