"use client";
import React, { useState } from "react";
import Workflow from "./Workflow";
import { motion, AnimatePresence } from "framer-motion";
import { FaPlay, FaMusic, FaInfoCircle, FaBars } from "react-icons/fa";

export default function HomePage() {
  const [executing, setExecuting] = useState(false);
  const [executionFunc, setExecutionFunc] = useState<(() => void) | null>(null);
  const [showScore, setShowScore] = useState(false);
  const [showMessages, setShowMessages] = useState(false);
  const [selectedNodeType, setSelectedNodeType] = useState<string>("aiAgent");

  // 新增節點類型選項
  const nodeTypes = [
    { value: "aiAgent", label: "AI Agent", icon: "🤖" },
    { value: "action", label: "Action", icon: "⚡" },
    { value: "state", label: "State", icon: "📊" },
    { value: "input", label: "Input", icon: "📥" },
    { value: "output", label: "Output", icon: "📤" },
    { value: "reflect", label: "Reflect", icon: "💭" },
  ];

  const handleStartExecution = () => {
    if (executionFunc && !executing) {
      setExecuting(true);
      executionFunc();
      setTimeout(() => setExecuting(false), 3000);
    }
  };

  const handleExecutionCallback = (startExecution: () => void) => {
    setExecutionFunc(() => startExecution);
  };

  const toggleScore = () => setShowScore(!showScore);
  const toggleMessages = () => setShowMessages(!showMessages);

  const buttonVariants = {
    hover: {
      scale: 1.05,
      background: "linear-gradient(135deg, #6366f1 0%, #a855f7 100%)",
      transition: { duration: 0.2 },
    },
    tap: { scale: 0.97 },
    initial: {
      background: "linear-gradient(135deg, #4f46e5 0%, #9333ea 100%)",
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
      {/* 導航列 */}
      <nav className="fixed w-full p-4 backdrop-blur-lg bg-white/80 dark:bg-gray-800/80 shadow-sm z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <motion.div
              whileHover={{ rotate: 90 }}
              className="p-2 rounded-lg bg-white dark:bg-gray-700 shadow-md"
            >
              <FaBars className="text-xl text-indigo-600 dark:text-indigo-400" />
            </motion.div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent dark:from-indigo-400 dark:to-purple-400">
              SynthFlow
            </h1>
          </div>

          <div className="flex space-x-3">
            <motion.button
              variants={buttonVariants}
              initial="initial"
              whileHover="hover"
              whileTap="tap"
              onClick={handleStartExecution}
              disabled={executing || !executionFunc}
              className="px-6 py-3 rounded-xl text-white font-medium flex items-center space-x-2 shadow-lg relative overflow-hidden"
            >
              <FaPlay className="text-sm" />
              <span>{executing ? "Processing..." : "Start Execution"}</span>
              {executing && (
                <motion.div
                  className="absolute inset-0 bg-white/10 backdrop-blur-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                />
              )}
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleScore}
              className="p-3 rounded-lg bg-white dark:bg-gray-700 shadow-md text-indigo-600 dark:text-indigo-400"
            >
              <FaMusic className="text-xl" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleMessages}
              className="p-3 rounded-lg bg-white dark:bg-gray-700 shadow-md text-indigo-600 dark:text-indigo-400"
            >
              <FaInfoCircle className="text-xl" />
            </motion.button>
          </div>
        </div>
      </nav>

      {/* 主內容 */}
      <div className="pt-24 pb-8 px-4 w-full h-full">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* 控制面板 */}
          <div className="w-full lg:w-1/6 space-y-6">
            <AnimatePresence>
              {showScore && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="p-6 bg-white dark:bg-gray-700 rounded-2xl shadow-xl backdrop-blur-sm"
                >
                  <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
                    Score Preview
                  </h3>
                  <div className="p-4 bg-gray-50 dark:bg-gray-600 rounded-xl">
                    <pre className="text-sm font-mono text-gray-600 dark:text-gray-300">
                      {`C4 - D4 - E4 - G4
A3 - B3 - C4 - E4
F4 - E4 - D4 - C4`}
                    </pre>
                  </div>
                </motion.div>
              )}

              {showMessages && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="p-6 bg-white dark:bg-gray-700 rounded-2xl shadow-xl"
                >
                  <h3 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">
                    Execution Logs
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        Status:
                      </span>
                      <span
                        className={`font-medium ${
                          executing ? "text-green-600" : "text-gray-600"
                        }`}
                      >
                        {executing ? "Running" : "Idle"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        Last Updated:
                      </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        {new Date().toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* 新增節點創建面板 */}
            <div className="p-6 bg-white dark:bg-gray-700 rounded-2xl shadow-xl">
              <h2 className="text-xl font-bold mb-6 text-gray-800 dark:text-gray-200">
                Create Node
              </h2>
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Node Type
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {nodeTypes.map((type) => (
                      <motion.button
                        key={type.value}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setSelectedNodeType(type.value)}
                        className={`p-2 rounded-lg flex items-center justify-center space-x-2 text-sm
                          ${
                            selectedNodeType === type.value
                              ? "bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300"
                              : "bg-gray-50 dark:bg-gray-600 text-gray-600 dark:text-gray-300"
                          }`}
                      >
                        <span>{type.icon}</span>
                        <span>{type.label}</span>
                      </motion.button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Node Label
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-600 
                             bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200"
                    placeholder="Enter node label..."
                  />
                </div>

                <motion.button
                  variants={buttonVariants}
                  initial="initial"
                  whileHover="hover"
                  whileTap="tap"
                  className="w-full px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 
                           text-white hover:bg-indigo-700 transition-colors"
                >
                  Add Node
                </motion.button>
              </div>
            </div>

            <div className="p-6 bg-white dark:bg-gray-700 rounded-2xl shadow-xl">
              <h2 className="text-xl font-bold mb-6 text-gray-800 dark:text-gray-200">
                Control Panel
              </h2>
              <div className="space-y-4">
                {" "}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    BPM Control
                  </label>
                  <input
                    type="range"
                    min="40"
                    max="200"
                    className="w-full accent-indigo-600 dark:accent-indigo-400"
                  />
                </div>
                <button className="w-full px-4 py-2 text-sm font-medium rounded-lg bg-indigo-100 dark:bg-gray-600 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-200 dark:hover:bg-gray-500 transition-colors">
                  Advanced Settings
                </button>
              </div>
            </div>
          </div>

          {/* Workflow 區域 */}
          <div className="flex-1 lg:w-5/6">
            <div className="h-[750px] bg-white dark:bg-gray-700 rounded-2xl shadow-xl p-4">
              <Workflow
                onStartExecution={handleExecutionCallback}
                executing={executing}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
