"use client";

import React, { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  BookOpen,
  Sparkles,
  Download,
  Radio,
  Layers,
  Cpu,
  Zap,
  Copy,
  CheckCircle2,
  Search,
} from "lucide-react";

// Type definitions
type MacroCommand = {
  command: string;
  category: string;
  layer: "macro" | "micro";
  description: string;
  agents: string[];
  latency: string;
  channel?: string;
};

type BluetoothChannel = {
  name: string;
  status: "active" | "broadcast" | "idle";
  frequency: string;
  protocol: string;
  throughput: string;
  agents: string[];
};

type AutonomousWorkflow = {
  name: string;
  trigger: string;
  flow: string;
  agents: string[];
};

// Placeholder data – replace/expand with real sources
const macroCommands: MacroCommand[] = [
  {
    command: "scan → simulate → deploy",
    category: "deployment",
    layer: "macro",
    description: "Complete deployment pipeline with validation",
    agents: ["Route Sage", "Policy Oracle"],
    latency: "~120ms",
    channel: "deployment.prime",
  },
  {
    command: "audit → lock → route",
    category: "security",
    layer: "macro",
    description: "Security-first routing with compliance checks",
    agents: ["Vault Sentinel", "Compliance Herald"],
    latency: "~95ms",
    channel: "security.shield",
  },
  // Add micro-layer examples...
  {
    command: "verify → sign",
    category: "attestation",
    layer: "micro",
    description: "Atomic signature verification",
    agents: ["Trust Anchor"],
    latency: "~15ms",
  },
];

const bluetoothChannels: BluetoothChannel[] = [
  {
    name: "prime.mesh",
    status: "active",
    frequency: "2.4GHz",
    protocol: "x402-BLE",
    throughput: "1.2Mbps",
    agents: ["Route Sage", "Vault Sentinel"],
  },
  {
    name: "shield.broadcast",
    status: "broadcast",
    frequency: "5GHz",
    protocol: "x402-Consensus",
    throughput: "800Kbps",
    agents: ["Policy Oracle", "Compliance Herald"],
  },
  // Add more...
];

const autonomousWorkflows: AutonomousWorkflow[] = [
  {
    name: "Auto-Hedge Settlement",
    trigger: "Price Deviation > 2%",
    flow: "scan → prefetch → hedge → settle → attest",
    agents: ["Market Sentinel", "Risk Oracle"],
  },
  {
    name: "Compliance Sweep",
    trigger: "New Block Finalized",
    flow: "audit → lock → verify → seal",
    agents: ["Vault Sentinel"],
  },
];

const categories = ["all", "deployment", "security", "attestation", "settlement"];

export default function BazaarCodexAtlasPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [layerFilter, setLayerFilter] = useState<"all" | "macro" | "micro">("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [selectedChannel, setSelectedChannel] = useState<BluetoothChannel | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const filteredCommands = macroCommands.filter((cmd) => {
    const matchesSearch =
      cmd.command.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cmd.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cmd.category.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesLayer = layerFilter === "all" || cmd.layer === layerFilter;
    const matchesCategory = categoryFilter === "all" || cmd.category === categoryFilter;

    return matchesSearch && matchesLayer && matchesCategory;
  });

  return (
    <div className="container mx-auto py-8 px-4">
      <Card className="mb-8 shadow-xl border-slate-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-3 text-3xl">
            <Cpu className="h-8 w-8 text-primary" />
            Bazaar Codex Atlas
          </CardTitle>
          <CardDescription>
            Explore macro/micro commands, bluetooth-like channels, autonomous flows, and compose custom workflows in the Sei-x402 ecosystem.
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs defaultValue="commands" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="commands">Command Library</TabsTrigger>
          <TabsTrigger value="channels">Bluetooth Channels</TabsTrigger>
          <TabsTrigger value="autonomous">Autonomous Flows</TabsTrigger>
          <TabsTrigger value="composer">Flow Composer</TabsTrigger>
        </TabsList>

        <TabsContent value="commands">
          <Card className="shadow-xl border-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-indigo-600" />
                Complete Command Reference
              </CardTitle>
              <CardDescription>E2E coverage of all macro and micro layer operations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row gap-3 mb-6 flex-wrap">
                <div className="flex-1 relative min-w-[200px]">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <Input
                    placeholder="Search commands..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <div className="flex gap-2 flex-wrap">
                  <Button
                    variant={layerFilter === "all" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setLayerFilter("all")}
                  >
                    All
                  </Button>
                  <Button
                    variant={layerFilter === "macro" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setLayerFilter("macro")}
                  >
                    <Layers className="w-3 h-3 mr-1" />
                    Macro
                  </Button>
                  <Button
                    variant={layerFilter === "micro" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setLayerFilter("micro")}
                  >
                    <Cpu className="w-3 h-3 mr-1" />
                    Micro
                  </Button>
                </div>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="px-3 py-2 border border-slate-200 rounded-lg text-sm bg-white"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat === "all" ? "All Categories" : cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <ScrollArea className="h-[600px] pr-4">
                <div className="space-y-3">
                  {filteredCommands.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      No commands match your filters.
                    </div>
                  ) : (
                    filteredCommands.map((cmd, idx) => (
                      <Card
                        key={`${cmd.command}-${idx}`}
                        className={`border-2 transition-all ${
                          cmd.layer === "macro"
                            ? "border-purple-200 bg-purple-50/50"
                            : "border-blue-200 bg-blue-50/50"
                        }`}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between mb-3 flex-wrap gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2 flex-wrap">
                                <Badge
                                  className={
                                    cmd.layer === "macro" ? "bg-purple-600" : "bg-blue-600"
                                  }
                                >
                                  {cmd.layer}
                                </Badge>
                                <Badge variant="outline" className="capitalize">
                                  {cmd.category}
                                </Badge>
                                {cmd.channel && (
                                  <Badge variant="secondary" className="text-xs">
                                    <Radio className="w-3 h-3 mr-1" />
                                    {cmd.channel}
                                  </Badge>
                                )}
                              </div>
                              <p className="font-mono text-lg font-bold text-slate-900 mb-2">
                                {cmd.command}
                              </p>
                              <p className="text-sm text-slate-600 mb-2">{cmd.description}</p>
                              {cmd.agents.length > 0 && (
                                <div className="flex gap-2 flex-wrap">
                                  {cmd.agents.map((agent) => (
                                    <span
                                      key={agent}
                                      className="text-xs text-indigo-600"
                                    >
                                      @{agent.replace(" ", "")}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                            <div className="text-right shrink-0">
                              <p className="text-xs text-slate-500 mb-1">Latency</p>
                              <p className="text-sm font-semibold text-slate-900">
                                {cmd.latency}
                              </p>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="mt-2"
                                onClick={() => copyToClipboard(cmd.command, `cmd-${idx}`)}
                              >
                                {copied === `cmd-${idx}` ? (
                                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                                ) : (
                                  <Copy className="w-4 h-4" />
                                )}
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </div>
              </ScrollArea>

              <div className="mt-4 text-center text-sm text-slate-500">
                Showing {filteredCommands.length} of {macroCommands.length} commands
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Bluetooth Channels Tab */}
        <TabsContent value="channels">
          <Card className="shadow-xl border-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Radio className="w-5 h-5 text-indigo-600" />
                Bluetooth-like Agent Channels
              </CardTitle>
              <CardDescription>
                Low-latency broadcast channels for autonomous agent coordination
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {bluetoothChannels.map((channel) => (
                  <Card
                    key={channel.name}
                    className={`border-2 cursor-pointer transition-all ${
                      selectedChannel?.name === channel.name
                        ? "border-indigo-500 bg-indigo-50"
                        : "border-slate-200 hover:border-slate-300"
                    }`}
                    onClick={() => setSelectedChannel(channel)}
                  >
                    <CardContent className="p-4">
                      {/* Channel card content as in your snippet */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Radio className="w-4 h-4 text-indigo-600" />
                            <p className="font-mono font-bold text-slate-900">
                              {channel.name}
                            </p>
                          </div>
                          <div className="flex gap-2 mb-3 flex-wrap">
                            <Badge
                              className={
                                channel.status === "active"
                                  ? "bg-emerald-600"
                                  : channel.status === "broadcast"
                                  ? "bg-blue-600"
                                  : "bg-amber-600"
                              }
                            >
                              {channel.status}
                            </Badge>
                            <Badge variant="outline">{channel.frequency}</Badge>
                            <Badge variant="secondary">{channel.protocol}</Badge>
                          </div>
                          <div className="space-y-1">
                            <p className="text-sm text-slate-600">
                              <span className="font-semibold">Throughput:</span> {channel.throughput}
                            </p>
                            <div className="flex flex-wrap gap-1">
                              <span className="text-xs text-slate-500">Agents:</span>
                              {channel.agents.map((agent, idx) => (
                                <span
                                  key={`${channel.name}-${idx}`}
                                  className="text-xs text-indigo-600"
                                >
                                  {agent}
                                  {idx < channel.agents.length - 1 ? ", " : ""}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center">
                            <div className="w-3 h-3 rounded-full bg-indigo-600 animate-pulse" />
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {selectedChannel && (
                <div className="mt-6 bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                  <h4 className="font-semibold text-indigo-900 mb-2">
                    Channel Details: {selectedChannel.name}
                  </h4>
                  <div className="grid md:grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-indigo-700">
                        <span className="font-semibold">Frequency:</span> {selectedChannel.frequency}
                      </p>
                      <p className="text-indigo-700">
                        <span className="font-semibold">Protocol:</span> {selectedChannel.protocol}
                      </p>
                    </div>
                    <div>
                      <p className="text-indigo-700">
                        <span className="font-semibold">Status:</span> {selectedChannel.status}
                      </p>
                      <p className="text-indigo-700">
                        <span className="font-semibold">Throughput:</span> {selectedChannel.throughput}
                      </p>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-3"
                    onClick={() =>
                      copyToClipboard(`bazaar://${selectedChannel.name}`, "channel")
                    }
                  >
                    {copied === "channel" ? (
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                    ) : (
                      <Copy className="w-3 h-3 mr-1" />
                    )}
                    Copy Channel URI
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Autonomous Flows Tab – similar structure, implement as needed */}
        <TabsContent value="autonomous">
          <Card className="shadow-xl border-slate-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-600" />
                Autonomous Workflows
              </CardTitle>
              <CardDescription>
                Self-executing command flows triggered by system events
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {autonomousWorkflows.map((workflow) => (
                <Card
                  key={workflow.name}
                  className="border-2 border-amber-200 bg-amber-50/50"
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3 flex-wrap gap-4">
                      <div>
                        <p className="font-bold text-slate-900 mb-1">{workflow.name}</p>
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          <Badge className="bg-amber-600">Auto-Execute</Badge>
                          <Badge variant="outline" className="text-xs">
                            Trigger: {workflow.trigger}
                          </Badge>
                        </div>
                      </div>
                      <Zap className="w-6 h-6 text-amber-500 shrink-0" />
                    </div>
                    <div className="bg-white rounded-lg p-3 mb-3">
                      <p className="font-mono text-sm text-slate-900 mb-2">{workflow.flow}</p>
                      <div className="flex gap-2 flex-wrap">
                        {workflow.agents.map((agent) => (
                          <Badge key={agent} variant="secondary" className="text-xs">
                            @{agent.replace(" ", "")}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                      <Button size="sm" variant="outline" className="flex-1">
                        View Logs
                      </Button>
                      <Button size="sm" className="flex-1">
                        Test Run
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          copyToClipboard(workflow.flow, `flow-${workflow.name}`)
                        }
                      >
                        {copied === `flow-${workflow.name}` ? (
                          <CheckCircle2 className="w-4 h-4 text-green-600" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}

              <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg p-4 mt-4">
                <h4 className="font-semibold text-amber-900 mb-2">Autonomous Execution Engine</h4>
                <p className="text-sm text-amber-800 mb-3">
                  Workflows execute automatically when triggers fire. No manual intervention required. All actions logged and attested via ConvergenceLedger.
                </p>
                <div className="grid md:grid-cols-3 gap-3 text-center">
                  <div className="bg-white rounded p-2">
                    <p className="text-xs text-amber-700">Executions today</p>
                    <p className="text-lg font-bold text-amber-900">1,284</p>
                  </div>
                  <div className="bg-white rounded p-2">
                    <p className="text-xs text-amber-700">Success rate</p>
                    <p className="text-lg font-bold text-emerald-600">99.2%</p>
                  </div>
                  <div className="bg-white rounded p-2">
                    <p className="text-xs text-amber-700">Avg latency</p>
                    <p className="text-lg font-bold text-blue-600">84ms</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Flow Composer Tab */}
        <TabsContent value="composer">
          <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <Card className="shadow-xl border-slate-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                  Visual Flow Composer
                </CardTitle>
                <CardDescription>Compose custom workflows by chaining commands</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-slate-900 rounded-lg p-6 mb-4 text-green-400 font-mono text-sm">
                  <p># Example: Custom Settlement Flow</p>
                  <p className="text-blue-300">
                    scan → verify → prefetch → parallelize → hedge → settle → sign → attest → seal
                  </p>
                  <p className="text-slate-400 text-xs mt-3">
                    # Mixed macro + micro for optimal performance
                  </p>
                </div>
                <div className="space-y-3">
                  <h4 className="font-semibold text-slate-900">Composition Templates</h4>
                  <Card className="border-indigo-200">
                    <CardContent className="p-3">
                      <p className="font-semibold text-sm text-slate-900 mb-1">Fast Settlement</p>
                      <p className="font-mono text-xs text-indigo-600 mb-2">
                        prefetch → hedge → settle → commit
                      </p>
                      <Button size="sm" variant="outline">Load Template</Button>
                    </CardContent>
                  </Card>
                  {/* Add other templates similarly */}
                </div>
              </CardContent>
            </Card>

            <Card className="shadow-xl border-slate-200">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button className="w-full justify-start" variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Export All Commands
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Radio className="w-4 h-4 mr-2" />
                  Export Channels Config
                </Button>
                <Button className="w-full justify-start" variant="outline">
                  <Zap className="w-4 h-4 mr-2" />
                  Export Workflows
                </Button>
                <Button className="w-full justify-start bg-indigo-600 text-white hover:bg-indigo-700">
                  <Download className="w-4 h-4 mr-2" />
                  Export Complete Atlas
                </Button>
                <div className="bg-purple-50 rounded-lg p-3 mt-4 text-xs text-purple-800">
                  <p className="font-semibold mb-1">💾 Export Formats</p>
                  <p>JSON, YAML, Markdown, or executable scripts for agent deployment</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      <Card className="mt-8 shadow-xl border-slate-200 bg-gradient-to-r from-slate-900 to-indigo-900 text-white">
        <CardContent className="p-6">
          <div className="flex items-center gap-3 mb-3">
            <Sparkles className="w-6 h-6 text-amber-400" />
            <p className="text-lg font-bold">Bazaar Codex Philosophy</p>
          </div>
          <p className="text-sm opacity-90 mb-4">
            "Speak once, mesh forever. The market hears and routes obey. Every command is a sovereign signal, every channel a trustless highway, every workflow an autonomous sentinel."
          </p>
          <div className="grid md:grid-cols-3 gap-4 text-xs opacity-75">
            <div>
              <p className="font-semibold mb-1">Macro Principles</p>
              <p>Chain operations, orchestrate systems, compose strategies</p>
            </div>
            <div>
              <p className="font-semibold mb-1">Micro Principles</p>
              <p>Atomic actions, instant execution, minimal latency</p>
            </div>
            <div>
              <p className="font-semibold mb-1">Channel Principles</p>
              <p>Bluetooth-like discovery, auto-pairing, broadcast consensus</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
