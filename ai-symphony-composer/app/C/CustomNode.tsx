"use client";
import React, { JSX } from "react";
import { Handle, Position } from "@xyflow/react";
import { motion } from "framer-motion";
import {
  FaRobot,
  FaCogs,
  FaInfoCircle,
  FaArrowRight,
  FaArrowLeft,
  FaLightbulb,
} from "react-icons/fa";

// 節點資料結構定義
export type NodeStatus = "pending" | "inProgress" | "completed";
export type NodeCategory =
  | "aiAgent"
  | "action"
  | "state"
  | "input"
  | "output"
  | "reflect";

export interface NodeParam {
  key: string;
  value: string;
}

export interface NodeTool {
  name: string;
  icon?: string;
}

export interface CustomNodeData {
  label: string;
  category: NodeCategory;
  status: NodeStatus;
  params: NodeParam[];
  tools?: NodeTool[];
}

export default function CustomNode({ data }: { data: CustomNodeData }) {
  const [isExpanded, setIsExpanded] = React.useState(true);
  const { label, category, status, params, tools = [] } = data;

  // 各類別對應的顏色
  const categoryColors: Record<NodeCategory, string> = {
    aiAgent: "#3498db", // 藍色
    action: "#2ecc71", // 綠色
    state: "#e67e22", // 橙色
    input: "#f1c40f", // 黃色
    output: "#9b59b6", // 紫色
    reflect: "#e91e63", // 粉紅色
  };

  // 各類別對應的圖標
  const categoryIcons: Record<NodeCategory, JSX.Element> = {
    aiAgent: <FaRobot />,
    action: <FaCogs />,
    state: <FaInfoCircle />,
    input: <FaArrowRight />,
    output: <FaArrowLeft />,
    reflect: <FaLightbulb />,
  };

  // 狀態對應的圖示
  const statusIcons: Record<NodeStatus, string> = {
    pending: "⏳",
    inProgress: "🌀",
    completed: "✅",
  };

  // 工具圖示預設
  const defaultToolIcons: Record<string, string> = {
    openai: "🔮",
    serpapi: "🔍",
    memory: "💾",
    vectordb: "📚",
  };

  return (
    <motion.div
      className="border border-gray-200 rounded-lg shadow-lg overflow-hidden"
      style={{
        background: `linear-gradient(to bottom right, white, ${categoryColors[category]}10)`,
      }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{
        y: -4,
        boxShadow: "0 10px 20px rgba(0,0,0,0.1)",
        transition: { duration: 0.2 },
      }}
    >
      {/* 标题栏 */}
      <motion.div
        className="flex items-center p-2 cursor-pointer"
        style={{
          background: `linear-gradient(45deg, ${categoryColors[category]}, ${categoryColors[category]}dd)`,
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="mr-2">{categoryIcons[category]}</span>
        <motion.span
          className="mr-2"
          animate={{
            rotate: status === "inProgress" ? 360 : 0,
          }}
          transition={{
            repeat: status === "inProgress" ? Infinity : 0,
            duration: 2,
          }}
        >
          {statusIcons[status]}
        </motion.span>
        <strong className="text-sm font-bold text-white">{label}</strong>
      </motion.div>

      {/* 展开的内容区域 */}
      <motion.div
        initial={false}
        animate={{
          height: isExpanded ? "auto" : 0,
          opacity: isExpanded ? 1 : 0,
        }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        {/* 工具区 */}
        {tools.length > 0 && (
          <div className="grid grid-cols-2 gap-2 p-2 bg-gray-50">
            {tools.map((tool, idx) => {
              const icon =
                tool.icon || defaultToolIcons[tool.name.toLowerCase()] || "🔧";
              return (
                <motion.div
                  className="flex items-center p-1 rounded hover:bg-white"
                  key={idx}
                  whileHover={{ scale: 1.05 }}
                  title={`Tool: ${tool.name}`}
                >
                  <span className="mr-1">{icon}</span>
                  <span className="text-xs truncate">{tool.name}</span>
                </motion.div>
              );
            })}
          </div>
        )}

        {/* 参数网格 */}
        <div className="grid grid-cols-1 gap-1 p-2">
          {params?.map((p, idx) => (
            <motion.div
              key={idx}
              className="text-xs p-1 rounded hover:bg-gray-50"
              whileHover={{ x: 5 }}
            >
              <span className="font-bold">{p.key}:</span>
              <span className="ml-1 text-gray-600 truncate">{p.value}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Handles */}
      <Handle
        type="target"
        position={Position.Left}
        className="w-2 h-2 rounded-full transition-all duration-300 hover:scale-150"
        style={{ backgroundColor: categoryColors[category] }}
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-2 h-2 rounded-full transition-all duration-300 hover:scale-150"
        style={{ backgroundColor: categoryColors[category] }}
      />
    </motion.div>
  );
}
