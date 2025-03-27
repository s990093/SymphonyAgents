"use client";
import React, { useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  NodeTypes,
  MiniMap,
  useNodesState,
  useEdgesState,
} from "@xyflow/react";
import CustomNode from "./C/CustomNode";
import { useExecutionFlow } from "./C/useExecutionFlow";
import "@xyflow/react/dist/style.css";
import "./globals.css";
import { initialEdges, initialNodes } from "./C/flowData";
import { getLayoutedElements } from "./C/layoutHelper";

interface WorkflowProps {
  onStartExecution: (startExecution: () => void) => void;
  executing: boolean;
}

export default function Workflow({
  onStartExecution,
  executing,
}: WorkflowProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const { startExecution } = useExecutionFlow(nodes, setNodes);

  const nodeTypes: NodeTypes = {
    customNode: CustomNode,
  };

  React.useEffect(() => {
    onStartExecution(startExecution);
  }, [startExecution, onStartExecution]);
  useEffect(() => {
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      nodes,
      edges,
      "LR"
    );
    setNodes([...layoutedNodes]);
    setEdges([...layoutedEdges]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes.length, edges.length]);

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodeTypes={nodeTypes}
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        panOnScroll
      >
        <Background />
        <MiniMap />
        <Controls showInteractive={!executing} />
      </ReactFlow>
    </div>
  );
}
