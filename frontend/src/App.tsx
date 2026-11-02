import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from './api'
import type { Candidate, CostSummary, Project, Shot } from './types'

const STATUS_LABEL: Record<Shot['status'], string> = {
  pending: '排队中',
  running: '生成中',
  succeeded: '已完成',
  failed: '失败',
}

const SAMPLE_PROMPTS = [
  '雨夜街头，女主撑伞走过霓虹，浅景深',
  '特写：女主眼神坚定，睫毛挂着雨珠',
  '男主推门而入，逆光剪影，尘埃在光束里浮动',
  '女主回头，雨水滑落脸颊，浅景深',
  '空荡的地铁站台，灯光闪烁',
  '两人隔桌对坐，桌上摊开一张旧照片',
]

export default function App() {
  const [projects, setProjects] = useState<Project[]>([])
  const [currentId, setCurrentId] = useState<number | null>(null)
  const [shots, setShots] = useState<Shot[]>([])
  const [cost, setCost] = useState<CostSummary | null>(null)
  const [prompts, setPrompts] = useState<string[]>(SAMPLE_PROMPTS)
  const [charRef, setCharRef] = useState('char_xiaoyu')
  const [detail, setDetail] = useState<(Shot & { candidates: Candidate[] }) | null>(null)
  const [connected, setConnected] = useState(false)
  const esRef = useRef<EventSource | null>(null)

  // ---------- 初始化 ----------
  useEffect(() => {
    api.listProjects().then((ps) => {
      setProjects(ps)
      if (ps.length) setCurrentId(ps[0].id)
      else {
        api.createProject('我的第一部 AI 短剧').then((p) => {
          setProjects([p])
          setCurrentId(p.id)
        })
      }
    })
  }, [])

  // ---------- SSE 实时进度 ----------
  useEffect(() => {
    const es = new EventSource('/api/events')
    esRef.current = es
    es.onopen = () => setConnected(true)
    es.onerror = () => setConnected(false)
    es.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setShots(data.shots)
      setCost(data.cost)
    }
    return () => es.close()
  }, [])

  // ---------- 拉取候选详情 ----------
  const openDetail = useCallback(async (id: number) => {
    const d = await api.getShot(id)
    setDetail(d)
  }, [])

  const shotsOfCurrent = useMemo(
    () => shots.filter((s) => s.project_id === currentId).sort((a, b) => a.idx - b.idx),
    [shots, currentId],
  )

  const submit = async () => {
    if (!currentId || prompts.length === 0) return
    await api.submitShots(currentId, prompts, charRef || undefined)
  }

  const retry = async (id: number) => {
    await api.retryShot(id)
  }

  const pick = async (shotId: number, candidateId: number) => {
    await api.selectCandidate(shotId, candidateId)
    await openDetail(shotId)
  }

  return (
    <div className="wrap">
      <header>
        <div>
          <h1>AI 短剧素材流水线 · 工作台</h1>
          <p className="sub">
            剧本分镜 → 批量生成 → 人工挑选候选 → 成本核算
            <span className={connected ? 'dot on' : 'dot off'} />
            {connected ? '实时通道已连接' : '实时通道断开'}
          </p>
        </div>
        <div className="projects">
          {projects.map((p) => (
            <button
              key={p.id}
              className={p.id === currentId ? 'pill active' : 'pill'}
              onClick={() => setCurrentId(p.id)}
            >
              {p.name}
            </button>
          ))}
          <button
            className="pill ghost"
            onClick={() =>
              api.createProject(`短剧 ${projects.length + 1}`).then((p) => {
                setProjects((prev) => [p, ...prev])
                setCurrentId(p.id)
              })
            }
          >
            + 新项目
          </button>
        </div>
      </header>

      <section className="panel">
        <div className="panel-head">
          <h2>① 提交分镜</h2>
          <button className="primary" onClick={submit}>
            批量生成 {prompts.length} 个镜头
          </button>
        </div>
        <div className="field">
          <label>角色资产引用（对应同一角色的 LoRA / 参考图集）</label>
          <input value={charRef} onChange={(e) => setCharRef(e.target.value)} />
        </div>
        <ul className="prompts">
          {prompts.map((p, i) => (
            <li key={i}>
              <span className="num">{i + 1}</span>
              <input
                value={p}
                onChange={(e) =>
                  setPrompts((prev) => prev.map((x, idx) => (idx === i ? e.target.value : x)))
                }
              />
              <button className="mini" onClick={() => setPrompts((prev) => prev.filter((_, idx) => idx !== i))}>
                ×
              </button>
            </li>
          ))}
        </ul>
        <button
          className="mini"
          onClick={() => setPrompts((prev) => [...prev, '新镜头描述…'])}
        >
          + 添加镜头
        </button>
      </section>

      <section className="panel">
        <div className="panel-head">
          <h2>② 生产队列</h2>
        </div>
        <div className="table">
          <div className="tr th">
            <span>#</span>
            <span>分镜描述</span>
            <span>状态</span>
            <span>尝试</span>
            <span>耗时</span>
            <span>成本</span>
            <span>操作</span>
          </div>
          {shotsOfCurrent.map((s) => (
            <div key={s.id} className={`tr ${s.status}`}>
              <span>{s.idx + 1}</span>
              <span className="prompt" title={s.prompt}>{s.prompt}</span>
              <span>
                <em className={`tag ${s.status}`}>{STATUS_LABEL[s.status]}</em>
                {s.error && <em className="err">{s.error}</em>}
              </span>
              <span>{s.attempts}</span>
              <span>{s.duration_seconds ? `${s.duration_seconds}s` : '-'}</span>
              <span>{s.cost ? `¥${s.cost}` : '-'}</span>
              <span className="ops">
                <button className="mini" onClick={() => openDetail(s.id)}>
                  候选
                </button>
                {s.status === 'failed' && (
                  <button className="mini warn" onClick={() => retry(s.id)}>
                    重试
                  </button>
                )}
              </span>
            </div>
          ))}
          {shotsOfCurrent.length === 0 && <div className="empty">还没有提交任何镜头</div>}
        </div>
      </section>

      <section className="panel">
        <div className="panel-head"><h2>③ 成本面板</h2></div>
        {cost && (
          <div className="stats">
            <div><b>¥{cost.total_cost.toFixed(2)}</b><span>总成本</span></div>
            <div><b>{cost.total_shots}</b><span>镜头总数</span></div>
            <div><b>{cost.succeeded}</b><span>成功</span></div>
            <div><b>{cost.failed}</b><span>失败</span></div>
            <div><b>¥{cost.avg_cost_per_succeeded_shot.toFixed(2)}</b><span>单镜头均价</span></div>
            <div><b>{cost.attempts_total}</b><span>总生成次数</span></div>
          </div>
        )}
        <p className="note">
          抽卡率视角：总生成次数 ÷ 成功镜头数 = {cost ? (cost.attempts_total / Math.max(cost.succeeded, 1)).toFixed(2) : '-'}
          ，这个倍数就是重试带来的成本放大系数。
        </p>
      </section>

      {detail && (
        <div className="drawer" onClick={() => setDetail(null)}>
          <div className="drawer-body" onClick={(e) => e.stopPropagation()}>
            <h2>镜头 #{detail.idx + 1} 的候选</h2>
            <p className="sub">{detail.prompt}</p>
            <div className="cands">
              {detail.candidates.map((c) => (
                <div key={c.id} className={c.is_selected ? 'cand selected' : 'cand'}>
                  <img src={c.url} alt={`候选 ${c.id}`} />
                  <div className="cand-meta">
                    <span>seed {c.seed}</span>
                    <button className="mini" onClick={() => pick(detail.id, c.id)}>
                      {c.is_selected ? '已选用' : '选用'}
                    </button>
                  </div>
                </div>
              ))}
              {detail.candidates.length === 0 && <p className="empty">该镜头还没有候选</p>}
            </div>
            <button className="mini" onClick={() => setDetail(null)}>关闭</button>
          </div>
        </div>
      )}
    </div>
  )
}
