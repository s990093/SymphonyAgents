import React from "react";
import { Node } from "@xyflow/react";
import { initialNodes } from "./flowData";

// 假設節點總數量為固定值，可以從 initialNodes.length 取得
const TOTAL_STEPS = initialNodes.length; // 根據你的 initialNodes 數量調整

export function useExecutionFlow(
  nodes: Node[],
  setNodes: React.Dispatch<React.SetStateAction<Node[]>>
) {
  const [currentStep, setCurrentStep] = React.useState(0);
  const [executing, setExecuting] = React.useState(false);

  // 開始執行流程
  const startExecution = React.useCallback(() => {
    setCurrentStep(0);
    setExecuting(true);
    // 重置所有節點狀態為 pending
    setNodes((prevNodes) =>
      prevNodes.map((node) => ({
        ...node,
        data: { ...node.data, status: "pending" },
      }))
    );
  }, [setNodes]);

  React.useEffect(() => {
    if (!executing) return;

    if (currentStep < TOTAL_STEPS) {
      // 將當前步驟節點狀態設定為 inProgress
      setNodes((prevNodes) =>
        prevNodes.map((node, idx) => {
          if (idx === currentStep) {
            return {
              ...node,
              data: { ...node.data, status: "inProgress" },
            };
          }
          return node;
        })
      );

      const timer = setTimeout(() => {
        // 將當前節點狀態更新為 completed
        setNodes((prevNodes) =>
          prevNodes.map((node, idx) => {
            if (idx === currentStep) {
              return {
                ...node,
                data: { ...node.data, status: "completed" },
              };
            }
            return node;
          })
        );
        setCurrentStep((prev) => prev + 1);
      }, 500);

      return () => clearTimeout(timer);
    } else {
      // 所有步驟完成，結束執行
      setExecuting(false);
    }
  }, [executing, currentStep, setNodes]);

  return { startExecution, executing };
}
