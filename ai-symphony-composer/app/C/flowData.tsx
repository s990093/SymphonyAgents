import { Node, Edge } from "@xyflow/react";

// 常量定義
const CUSTOM_NODE_TYPE = "customNode";
const STATUS_PENDING = "pending";

// 創建基礎節點的輔助函數
const createNode = (
  id: string,
  label: string,
  category: string,
  x: number,
  y: number,
  additionalData = {}
) => ({
  id,
  type: CUSTOM_NODE_TYPE,
  position: { x, y },
  data: {
    label,
    category,
    status: STATUS_PENDING,
    ...additionalData,
  },
});

// 創建樂器相關節點
const createInstrumentNodes = (
  instrument: string,
  baseX: number,
  baseY: number,
  role: string
) => {
  const stateNode = createNode(
    instrument.toLowerCase(),
    instrument.toUpperCase(),
    "state",
    baseX,
    baseY,
    {
      params: [
        { key: "instrument", value: instrument },
        { key: "role", value: role },
      ],
      tools: [
        { name: "OpenAI" },
        { name: "RAG", icon: "🔍" },
        { name: "VectorDB", icon: "📚" },
      ],
    }
  );

  const generateNode = createNode(
    `${instrument.toLowerCase()}Generate`,
    "GENERATE_SCORES",
    "action",
    baseX + 150,
    baseY,
    {
      params: [
        { key: "target", value: `${instrument} Score` },
        { key: "role", value: role },
      ],
    }
  );

  return [stateNode, generateNode];
};

// 定義樂器及其位置和角色
const instruments = [
  { name: "Violin", y: 0, role: "melody" }, // 小提琴：主旋律
  { name: "Viola", y: 70, role: "harmony" }, // 中提琴：和聲
  { name: "Cello", y: 140, role: "bass" }, // 大提琴：低音
  { name: "Flute", y: 210, role: "melody" }, // 長笛：主旋律
  { name: "Clarinet", y: 280, role: "harmony" }, // 單簧管：和聲
  { name: "Trumpet", y: 350, role: "highlight" }, // 小號：重點段落
  { name: "Timpani", y: 420, role: "rhythm" }, // 定音鼓：節奏
];

// 生成所有節點
export const initialNodes: Node[] = [
  // 輸入節點
  {
    ...createNode("input", "輸入", "input", 50, 100),
    data: {
      label: "音樂創作輸入",
      category: "input",
      status: "completed",
      timestamp: "2024-03-01T09:00:00",
      params: [
        { key: "format", value: "MIDI", type: "file" },
        { key: "style", value: "古典交響樂" },
        { key: "duration", value: "15分鐘", type: "duration" },
      ],
      tools: [
        { name: "OpenAI", version: "4.0" },
        { name: "音樂理論庫", version: "2.1" },
      ],
      execution: {
        attempts: 1,
        lastAttempt: "2024-03-01T09:00:05",
        duration: "5s",
      },
    },
  },
  createNode("conductor", "指揮家", "aiAgent", 200, 100, {
    params: [{ key: "role", value: "Conductor" }],
    tools: [
      { name: "OpenAI" },
      { name: "SerpAPI" },
      { name: "RAG", icon: "🔍" },
      { name: "VectorDB", icon: "📚" },
    ],
  }),
  createNode("designFramework", "DESIGN_FRAMEWORK", "action", 400, 50, {
    params: [{ key: "framework", value: "F1" }],
  }),
  createNode("planComposition", "PLAN_COMPOSITION", "action", 400, 150, {
    params: [{ key: "composition", value: "Symphony" }],
  }),
  ...instruments.flatMap((inst) =>
    createInstrumentNodes(inst.name, 650, inst.y, inst.role)
  ),
  createNode("reviewer", "鑑定師", "aiAgent", 1000, 100, {
    params: [
      { key: "model", value: "GPT-4" },
      { key: "role", value: "Music Reviewer" },
    ],
    tools: [
      { name: "OpenAI" },
      { name: "SerpAPI" },
      { name: "VectorDB", icon: "📚" },
    ],
  }),
  createNode("evaluate", "EVALUATE_AND_REVISE", "action", 1150, 100, {
    params: [{ key: "review", value: "Check all" }],
  }),
  createNode("reflect", "反思", "reflect", 1000, 200, {
    params: [{ key: "feedback", value: "Refine next time" }],
  }),
  createNode("output", "輸出", "output", 1300, 100, {
    status: "inProgress",
    params: [{ key: "output", value: "Final Score" }],
  }),
];

// 創建邊緣連接的輔助函數
const createEdge = (source: string, target: string) => ({
  id: `e-${source}-${target}`,
  source,
  target,
});

// 生成所有邊緣連接
export const initialEdges: Edge[] = [
  // 基礎流程連接
  createEdge("input", "conductor"),
  createEdge("conductor", "designFramework"),
  createEdge("designFramework", "planComposition"),

  // 樂器連接
  ...instruments.flatMap((inst) => {
    const instLower = inst.name.toLowerCase();
    return [
      createEdge("planComposition", instLower),
      createEdge(instLower, `${instLower}Generate`),
      createEdge(`${instLower}Generate`, "reviewer"),
    ];
  }),

  // 最終評估連接
  createEdge("reviewer", "evaluate"),
  createEdge("evaluate", "output"),
  createEdge("evaluate", "reflect"),
  createEdge("reflect", "reviewer"),
];
