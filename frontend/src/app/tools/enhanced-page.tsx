"use client";

import { useState, useMemo } from "react";
import {
  Search,
  Grid3x3,
  List,
  Calendar,
  User,
  Package,
  TrendingUp,
  CheckCircle2,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TypingText } from "@/components/typing-text";

// Tool data type
interface Tool {
  name: string;
  description: string;
  category: string;
  version: string;
  author: string;
  registered_at: string;
  usage_count: number;
  is_enabled: boolean;
  metadata: Record<string, unknown>;
}

// Mock tools data
const TOOLS: Tool[] = [
  {
    name: "custom_calculator",
    description:
      "Safe calculator for mathematical expressions. Supports basic arithmetic operations.",
    category: "utility",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:45.077900",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "gemini_image_editor",
    description:
      "Edit existing images using Google Gemini AI. Modify images with text prompts.",
    category: "ai_image",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:45.078895",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "gemini_image_generator",
    description:
      "Advanced image generation and editing using Google Gemini AI. Supports text-to-image, image editing, restoration, colorization, and iterative editing.",
    category: "ai_image",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:45.078582",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "gemini_text_to_image",
    description:
      "Simple text-to-image generation using Google Gemini AI. Generate images from text descriptions.",
    category: "ai_image",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:45.078747",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "google_search",
    description:
      "Google ADK built-in Google Search tool. Search the web using Google Search grounding.",
    category: "search",
    version: "1.0.0",
    author: "google_adk",
    registered_at: "2025-10-23T10:52:44.623921",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "load_memory",
    description: "Search and load relevant information from memory",
    category: "memory",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:44.623739",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "product_hunt_search",
    description:
      "Search Product Hunt for products, posts, and collections. Supports query types: search, posts, collections.",
    category: "api",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:45.078245",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "text_analyzer",
    description: "Analyze text for word count, sentiment, and other metrics.",
    category: "analysis",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:45.078077",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
  {
    name: "yahoo_finance_data",
    description:
      "Get real-time and historical financial data from Yahoo Finance. Supports stocks, crypto, and other symbols.",
    category: "finance",
    version: "1.0.0",
    author: "system",
    registered_at: "2025-10-23T10:52:45.078410",
    usage_count: 0,
    is_enabled: true,
    metadata: {},
  },
];

// Category configuration with icons and colors
const CATEGORY_CONFIG: Record<
  string,
  { label: string; icon: string; color: string }
> = {
  utility: { label: "Utility", icon: "🔧", color: "text-blue-600" },
  ai_image: { label: "AI Image", icon: "🎨", color: "text-purple-600" },
  search: { label: "Search", icon: "🔍", color: "text-green-600" },
  memory: { label: "Memory", icon: "🧠", color: "text-pink-600" },
  api: { label: "API", icon: "🔌", color: "text-orange-600" },
  analysis: { label: "Analysis", icon: "📊", color: "text-cyan-600" },
  finance: { label: "Finance", icon: "💰", color: "text-emerald-600" },
};

export default function ToolMarketplace() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);
  const [processingTools, setProcessingTools] = useState<Set<string>>(
    new Set()
  );

  // Get unique categories
  const categories = useMemo(() => {
    const cats = Array.from(new Set(TOOLS.map((tool) => tool.category)));
    return ["all", ...cats];
  }, []);

  // Filter tools
  const filteredTools = useMemo(() => {
    return TOOLS.filter((tool) => {
      const matchesSearch =
        tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory =
        selectedCategory === "all" || tool.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory]);

  // Handle attach tool (commented for now)
  const handleAttachTool = async (agentId: string, toolName: string) => {
    // setProcessingTools((prev) => new Set([...prev, `${agentId}-${toolName}`]));
    // try {
    //   await AgentService.attachTools(agentId, [toolName]);
    //   await loadData();
    // } catch (error) {
    //   console.error("Failed to attach tool:", error);
    //   setError("Failed to attach tool. Please try again.");
    // } finally {
    //   setProcessingTools((prev) => {
    //     const newSet = new Set(prev);
    //     newSet.delete(`${agentId}-${toolName}`);
    //     return newSet;
    //   });
    // }
    console.log("Attach tool:", toolName);
  };

  // Handle detach tool (commented for now)
  const handleDetachTool = async (agentId: string, toolName: string) => {
    // setProcessingTools((prev) => new Set([...prev, `${agentId}-${toolName}`]));
    // try {
    //   await AgentService.detachTools(agentId, [toolName]);
    //   await loadData();
    // } catch (error) {
    //   console.error("Failed to detach tool:", error);
    //   setError("Failed to detach tool. Please try again.");
    // } finally {
    //   setProcessingTools((prev) => {
    //     const newSet = new Set(prev);
    //     newSet.delete(`${agentId}-${toolName}`);
    //     return newSet;
    //   });
    // }
    console.log("Detach tool:", toolName);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <section className="relative border-b border-border overflow-hidden">
        {/* Animated background grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
        <div className="absolute inset-0 bg-gradient-to-b from-background/0 via-background/50 to-background" />

        {/* Floating elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse delay-1000" />

        <div className="container relative mx-auto px-4 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">
                Discover powerful integrations
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-balance mb-6">
              Tool Marketplace
            </h1>

            <div className="text-xl md:text-2xl text-muted-foreground text-balance mb-4 min-h-[4rem] flex items-center justify-center">
              <TypingText
                texts={[
                  "Enhance your agents with AI-powered tools",
                  "Integrate search and analysis capabilities",
                  "Connect to financial data and APIs",
                  "Generate and edit images with AI",
                ]}
                typingSpeed={80}
                deletingSpeed={40}
                pauseDuration={2500}
                className="font-medium"
              />
            </div>

            <p className="text-base text-muted-foreground/80 max-w-2xl mx-auto">
              Browse our curated collection of utilities, AI services, and
              integrations to supercharge your workflow
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col lg:flex-row gap-8">
          <aside className="lg:w-72 flex-shrink-0">
            <div className="sticky top-8 space-y-6">
              {/* Search */}
              <div className="bg-card border border-border rounded-lg p-5 shadow-sm">
                <label className="text-sm font-semibold mb-3 block">
                  Search Tools
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search by name or description..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 h-10"
                  />
                </div>
              </div>

              {/* Categories */}
              <div className="bg-card border border-border rounded-lg p-5 shadow-sm">
                <label className="text-sm font-semibold mb-3 block">
                  Categories
                </label>
                <div className="space-y-1">
                  {categories.map((category) => {
                    const config = CATEGORY_CONFIG[category];
                    const count =
                      category === "all"
                        ? TOOLS.length
                        : TOOLS.filter((t) => t.category === category).length;

                    return (
                      <button
                        key={category}
                        onClick={() => setSelectedCategory(category)}
                        className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all ${
                          selectedCategory === category
                            ? "bg-primary text-primary-foreground font-medium shadow-sm"
                            : "hover:bg-secondary/80 text-foreground"
                        }`}
                      >
                        <span className="flex items-center gap-2.5">
                          {config ? (
                            <span className="text-lg">{config.icon}</span>
                          ) : (
                            <span className="text-lg">📦</span>
                          )}
                          <span className="capitalize">
                            {config?.label || category}
                          </span>
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            selectedCategory === category
                              ? "bg-primary-foreground/20"
                              : "bg-secondary"
                          }`}
                        >
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* View Mode */}
              <div className="bg-card border border-border rounded-lg p-5 shadow-sm">
                <label className="text-sm font-semibold mb-3 block">
                  View Mode
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant={viewMode === "grid" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setViewMode("grid")}
                    className="h-10"
                  >
                    <Grid3x3 className="h-4 w-4 mr-2" />
                    Grid
                  </Button>
                  <Button
                    variant={viewMode === "list" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setViewMode("list")}
                    className="h-10"
                  >
                    <List className="h-4 w-4 mr-2" />
                    List
                  </Button>
                </div>
              </div>
            </div>
          </aside>

          {/* Tools Grid/List */}
          <main className="flex-1">
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-1">
                  {selectedCategory === "all"
                    ? "All Tools"
                    : CATEGORY_CONFIG[selectedCategory]?.label}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {filteredTools.length}{" "}
                  {filteredTools.length === 1 ? "tool" : "tools"} available
                </p>
              </div>
            </div>

            {filteredTools.length === 0 ? (
              <div className="text-center py-20 bg-card border border-border rounded-lg">
                <Package className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
                <h3 className="text-xl font-semibold mb-2">No tools found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search or filters
                </p>
              </div>
            ) : viewMode === "grid" ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {filteredTools.map((tool) => {
                  const config = CATEGORY_CONFIG[tool.category];
                  return (
                    <Card
                      key={tool.name}
                      className="hover:shadow-xl hover:border-primary/50 transition-all duration-300 cursor-pointer group bg-card border-border"
                      onClick={() => setSelectedTool(tool)}
                    >
                      <CardHeader className="space-y-4">
                        <div className="flex items-start justify-between gap-3">
                          <div
                            className={`text-4xl transition-transform group-hover:scale-110 ${
                              config?.color || "text-foreground"
                            }`}
                          >
                            {config?.icon || "📦"}
                          </div>
                          <Badge
                            variant="secondary"
                            className="text-xs font-medium"
                          >
                            {config?.label || tool.category}
                          </Badge>
                        </div>
                        <div>
                          <CardTitle className="text-lg mb-2 group-hover:text-primary transition-colors leading-tight">
                            {tool.name.replace(/_/g, " ")}
                          </CardTitle>
                          <CardDescription className="line-clamp-2 text-sm leading-relaxed">
                            {tool.description}
                          </CardDescription>
                        </div>
                      </CardHeader>
                      <CardFooter className="flex items-center justify-between text-xs text-muted-foreground border-t border-border pt-4">
                        <span className="flex items-center gap-1.5">
                          <User className="h-3.5 w-3.5" />
                          {tool.author}
                        </span>
                        <span className="font-mono">v{tool.version}</span>
                      </CardFooter>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredTools.map((tool) => {
                  const config = CATEGORY_CONFIG[tool.category];
                  return (
                    <Card
                      key={tool.name}
                      className="hover:shadow-lg hover:border-primary/50 transition-all duration-300 cursor-pointer group bg-card border-border"
                      onClick={() => setSelectedTool(tool)}
                    >
                      <CardHeader className="p-6">
                        <div className="flex items-start gap-5">
                          <div
                            className={`text-5xl flex-shrink-0 transition-transform group-hover:scale-110 ${
                              config?.color || "text-foreground"
                            }`}
                          >
                            {config?.icon || "📦"}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-2 flex-wrap">
                              <CardTitle className="text-xl group-hover:text-primary transition-colors">
                                {tool.name.replace(/_/g, " ")}
                              </CardTitle>
                              <Badge
                                variant="secondary"
                                className="font-medium"
                              >
                                {config?.label || tool.category}
                              </Badge>
                            </div>
                            <CardDescription className="mb-4 leading-relaxed">
                              {tool.description}
                            </CardDescription>
                            <div className="flex items-center gap-6 text-xs text-muted-foreground">
                              <span className="flex items-center gap-1.5">
                                <User className="h-3.5 w-3.5" />
                                {tool.author}
                              </span>
                              <span className="flex items-center gap-1.5">
                                <Package className="h-3.5 w-3.5" />v
                                {tool.version}
                              </span>
                              <span className="flex items-center gap-1.5">
                                <TrendingUp className="h-3.5 w-3.5" />
                                {tool.usage_count} uses
                              </span>
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                    </Card>
                  );
                })}
              </div>
            )}
          </main>
        </div>
      </div>

      {/* Tool Detail Modal */}
      <Dialog open={!!selectedTool} onOpenChange={() => setSelectedTool(null)}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          {selectedTool && (
            <>
              <DialogHeader>
                <div className="flex items-start gap-4 mb-4">
                  <div
                    className={`text-5xl ${
                      CATEGORY_CONFIG[selectedTool.category]?.color ||
                      "text-foreground"
                    }`}
                  >
                    {CATEGORY_CONFIG[selectedTool.category]?.icon || "📦"}
                  </div>
                  <div className="flex-1">
                    <DialogTitle className="text-2xl mb-2">
                      {selectedTool.name.replace(/_/g, " ")}
                    </DialogTitle>
                    <div className="flex items-center gap-2 mb-3">
                      <Badge variant="secondary">
                        {CATEGORY_CONFIG[selectedTool.category]?.label ||
                          selectedTool.category}
                      </Badge>
                      <Badge variant="outline">v{selectedTool.version}</Badge>
                      {selectedTool.is_enabled && (
                        <Badge variant="default" className="bg-green-600">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Enabled
                        </Badge>
                      )}
                    </div>
                    <DialogDescription className="text-base">
                      {selectedTool.description}
                    </DialogDescription>
                  </div>
                </div>
              </DialogHeader>

              <Tabs defaultValue="overview" className="mt-6">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="documentation">Documentation</TabsTrigger>
                  <TabsTrigger value="details">Details</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-6 mt-6">
                  <div>
                    <h3 className="font-semibold mb-3">About this tool</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {selectedTool.description}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">Author</p>
                      <p className="font-medium flex items-center gap-2">
                        <User className="h-4 w-4" />
                        {selectedTool.author}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">Version</p>
                      <p className="font-medium flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        {selectedTool.version}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">
                        Registered
                      </p>
                      <p className="font-medium flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        {formatDate(selectedTool.registered_at)}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-muted-foreground">
                        Usage Count
                      </p>
                      <p className="font-medium flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        {selectedTool.usage_count} times
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button
                      className="flex-1"
                      onClick={() =>
                        handleAttachTool("agent-id", selectedTool.name)
                      }
                    >
                      Attach to Agent
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() =>
                        handleDetachTool("agent-id", selectedTool.name)
                      }
                    >
                      Detach
                    </Button>
                  </div>
                </TabsContent>

                <TabsContent value="documentation" className="space-y-4 mt-6">
                  <div className="prose prose-sm max-w-none">
                    <h3>Documentation</h3>
                    <p className="text-muted-foreground">
                      Detailed documentation for{" "}
                      <strong>{selectedTool.name}</strong> will be available
                      here.
                    </p>

                    <h4>Installation</h4>
                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                      <code>{`// Attach this tool to your agent
await AgentService.attachTools(agentId, ['${selectedTool.name}']);`}</code>
                    </pre>

                    <h4>Usage</h4>
                    <p className="text-muted-foreground">
                      Once attached, your agent will have access to this tool's
                      capabilities. The tool will be automatically available in
                      the agent's context.
                    </p>

                    <h4>Parameters</h4>
                    <p className="text-muted-foreground">
                      Tool-specific parameters and configuration options will be
                      documented here.
                    </p>

                    <h4>Examples</h4>
                    <p className="text-muted-foreground">
                      Code examples and use cases will be provided to help you
                      get started quickly.
                    </p>
                  </div>
                </TabsContent>

                <TabsContent value="details" className="space-y-4 mt-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Technical Details</h4>
                      <div className="bg-muted rounded-lg p-4 space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Tool Name:
                          </span>
                          <span className="font-mono">{selectedTool.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Category:
                          </span>
                          <span className="font-mono">
                            {selectedTool.category}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">
                            Version:
                          </span>
                          <span className="font-mono">
                            {selectedTool.version}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Author:</span>
                          <span className="font-mono">
                            {selectedTool.author}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Status:</span>
                          <span
                            className={
                              selectedTool.is_enabled
                                ? "text-green-600"
                                : "text-red-600"
                            }
                          >
                            {selectedTool.is_enabled ? "Enabled" : "Disabled"}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-2">Metadata</h4>
                      <div className="bg-muted rounded-lg p-4">
                        <pre className="text-xs overflow-x-auto">
                          <code>
                            {JSON.stringify(selectedTool.metadata, null, 2)}
                          </code>
                        </pre>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold mb-2">Registration Info</h4>
                      <p className="text-sm text-muted-foreground">
                        This tool was registered on{" "}
                        {formatDate(selectedTool.registered_at)} and has been
                        used {selectedTool.usage_count} times.
                      </p>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
