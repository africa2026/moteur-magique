import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Search, 
  BookOpen, 
  Sparkles, 
  MessageSquare, 
  FileText, 
  Library, 
  History, 
  Settings, 
  Globe, 
  Wifi, 
  WifiOff,
  TrendingUp,
  Zap,
  Cpu,
  Database,
  Trophy,
  Target,
  Share2,
  Maximize2,
  Upload,
  Cloud,
  HardDrive
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "";

export default function Home() {
  const [query, setQuery] = useState("");
  const [isOnline, setIsOnline] = useState(true);
  const [activeTab, setActiveTab] = useState("search");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [systemLoad, setSystemLoad] = useState(34);
  const [knowledgeScore, setKnowledgeScore] = useState(1250);
  const [error, setError] = useState<string | null>(null);
  const [isDriveConnected, setIsDriveConnected] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  // Simulate system activity
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemLoad(prev => Math.min(98, Math.max(20, prev + (Math.random() * 10 - 5))));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    setError(null);
    setResults([]);

    try {
      // REAL API CALL
      const response = await fetch(`${API_URL}/api/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          query: query,
          mode: "deep_research", // Enable deep research mode
          sources: ["corpus_salesiano", "semantic_scholar", "wikipedia", "uploaded_docs", "google_drive"] 
        }),
      });

      if (!response.ok) {
        throw new Error(`Errore server: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform API response to UI format
      // NO MOCK DATA - ONLY REAL RESULTS
      const transformedResults = data.results.map((item: any, index: number) => ({
        title: item.title || "Documento senza titolo",
        source: item.source || "Fonte sconosciuta",
        type: item.type || "DOCUMENTO",
        relevance: Math.round((item.confidence || item.score || 0) * 1), // Use confidence directly if available
        snippet: item.snippet || item.content?.substring(0, 300) + "...",
        citations: item.citations || 0,
        url: item.url
      }));

      setResults(transformedResults);
      setKnowledgeScore(prev => prev + (transformedResults.length * 50));
      
    } catch (err) {
      console.error("Search error:", err);
      setError("Errore di connessione al cervello centrale. Riprovare.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleFileUpload = () => {
    // Simulate file upload for UI demo
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.docx,.txt';
    input.onchange = (e: any) => {
      const file = e.target.files[0];
      if (file) {
        setUploadedFiles(prev => [...prev, file.name]);
        // In real implementation, this would upload to backend
      }
    };
    input.click();
  };

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans text-foreground overflow-hidden selection:bg-primary selection:text-primary-foreground">
      
      {/* Top HUD Bar */}
      <header className="h-14 border-b border-border bg-background/90 backdrop-blur-md flex items-center justify-between px-4 sticky top-0 z-50 shadow-lg shadow-primary/5">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-primary animate-pulse">
            <Cpu className="w-5 h-5" />
            <span className="font-tech font-bold tracking-widest text-lg">MOTEUR v4.0</span>
          </div>
          <div className="h-6 w-px bg-border mx-2"></div>
          <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
            <span className={isOnline ? "text-green-500" : "text-amber-500"}>●</span>
            {isOnline ? "SYSTEM ONLINE" : "OFFLINE MODE"}
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="hidden md:flex items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider">System Load</div>
              <div className="font-mono text-accent font-bold">{Math.round(systemLoad)}%</div>
            </div>
            <div className="w-24 h-1.5 bg-secondary rounded-full overflow-hidden">
              <div 
                className="h-full bg-accent transition-all duration-500 ease-out"
                style={{ width: `${systemLoad}%` }}
              ></div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary hover:bg-primary/10">
              <Settings className="w-5 h-5" />
            </Button>
            <div className="w-8 h-8 rounded bg-primary/20 border border-primary flex items-center justify-center text-primary font-bold font-tech">
              AO
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Command Panel */}
        <aside className="w-20 md:w-64 bg-sidebar border-r border-border flex flex-col z-40 hidden md:flex">
          <div className="p-4 space-y-2">
            <Button 
              variant={activeTab === "search" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "search" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("search")}
            >
              <Search className="w-5 h-5" />
              <span className="hidden md:inline">RICERCA</span>
            </Button>
            <Button 
              variant={activeTab === "chat" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "chat" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("chat")}
            >
              <MessageSquare className="w-5 h-5" />
              <span className="hidden md:inline">CHAT PDF</span>
            </Button>
            <Button 
              variant={activeTab === "write" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "write" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("write")}
            >
              <FileText className="w-5 h-5" />
              <span className="hidden md:inline">REDAZIONE</span>
            </Button>
            <Button 
              variant={activeTab === "library" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "library" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("library")}
            >
              <Library className="w-5 h-5" />
              <span className="hidden md:inline">ARCHIVIO</span>
            </Button>
          </div>

          <div className="mt-auto p-4 border-t border-border">
            <Card className="bg-card border-primary/20 shadow-[0_0_15px_rgba(251,191,36,0.1)]">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-tech text-muted-foreground uppercase">Knowledge Score</span>
                  <Trophy className="w-4 h-4 text-primary" />
                </div>
                <div className="text-2xl font-mono font-bold text-primary mb-1">{knowledgeScore}</div>
                <div className="text-[10px] text-muted-foreground">Livello: <span className="text-accent">MASTER</span></div>
              </CardContent>
            </Card>
          </div>
        </aside>

        {/* Main Arena */}
        <main className="flex-1 relative overflow-hidden flex flex-col">
          {/* Background Grid Effect */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:40px_40px] opacity-20 pointer-events-none"></div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#0f172a_100%)] pointer-events-none"></div>

          <ScrollArea className="flex-1 p-6 md:p-10 z-10">
            <div className="max-w-5xl mx-auto space-y-10 pb-20">
              
              {/* Hero Section */}
              <div className="text-center space-y-6 py-10 relative">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px] pointer-events-none"></div>
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 px-4 py-1 font-mono tracking-widest">
                  KNOWLEDGE ARENA ONLINE
                </Badge>
                <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight drop-shadow-[0_0_15px_rgba(251,191,36,0.3)]">
                  COMANDI <span className="text-primary">ATTIVI</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light font-tech tracking-wide">
                  Accesso a 12 motori accademici e corpus salesiano. In attesa di input.
                </p>
              </div>

              {/* Central Command Input */}
              <div className="relative max-w-3xl mx-auto group">
                <div className="absolute -inset-1 bg-gradient-to-r from-primary via-accent to-primary rounded-lg opacity-30 group-hover:opacity-70 blur transition duration-500 animate-pulse"></div>
                <form onSubmit={handleSearch} className="relative bg-background border border-primary/30 rounded-lg flex items-center p-2 shadow-2xl">
                  <div className="pl-4 pr-2 text-primary">
                    <Target className="w-6 h-6" />
                  </div>
                  <Input 
                    className="border-none shadow-none focus-visible:ring-0 text-xl h-14 bg-transparent placeholder:text-muted-foreground/30 font-tech tracking-wide text-white" 
                    placeholder="INSERIRE PARAMETRI DI RICERCA..." 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                  <Button 
                    type="submit" 
                    size="lg" 
                    className="h-12 px-8 bg-primary text-primary-foreground hover:bg-primary/90 font-bold tracking-wider font-tech rounded-md shadow-[0_0_20px_rgba(251,191,36,0.4)] transition-all hover:scale-105" 
                    disabled={isSearching}
                  >
                    {isSearching ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></span>
                        SCANNING...
                      </span>
                    ) : (
                      "ESEGUI"
                    )}
                  </Button>
                </form>
                
                {/* Search Stats & Personal Sources */}
                <div className="flex justify-between mt-4 px-2 font-mono text-xs text-muted-foreground">
                  <div className="flex gap-4 items-center">
                    <span className="flex items-center gap-1 text-accent"><Database className="w-3 h-3" /> 12 FONTI CONNESSE</span>
                    
                    {/* Uploaded Files Indicator */}
                    {uploadedFiles.length > 0 && (
                      <span className="flex items-center gap-1 text-green-400 animate-pulse">
                        <FileText className="w-3 h-3" /> {uploadedFiles.length} DOCS PERSONALI
                      </span>
                    )}

                    {/* Drive Indicator */}
                    {isDriveConnected && (
                      <span className="flex items-center gap-1 text-blue-400 animate-pulse">
                        <Cloud className="w-3 h-3" /> DRIVE CONNESSO
                      </span>
                    )}
                  </div>
                  <span className="text-muted-foreground/50">LATENCY: 12ms</span>
                </div>
              </div>

              {/* Personal Sources Control Panel */}
              <div className="max-w-3xl mx-auto grid grid-cols-2 gap-4">
                <Button 
                  variant="outline" 
                  className="h-12 border-primary/20 hover:bg-primary/10 hover:border-primary/50 text-muted-foreground hover:text-primary transition-all group"
                  onClick={handleFileUpload}
                >
                  <Upload className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                  <span className="font-tech tracking-wide">UPLOAD DOCUMENTI</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className={`h-12 border-primary/20 hover:bg-primary/10 hover:border-primary/50 transition-all group ${isDriveConnected ? "text-blue-400 border-blue-500/30 bg-blue-500/5" : "text-muted-foreground hover:text-primary"}`}
                  onClick={() => setIsDriveConnected(!isDriveConnected)}
                >
                  <Cloud className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                  <span className="font-tech tracking-wide">{isDriveConnected ? "DRIVE CONNESSO" : "CONNETTI DRIVE"}</span>
                </Button>
              </div>

              {/* Error Message */}
              {error && (
                <div className="max-w-3xl mx-auto bg-destructive/10 border border-destructive/50 text-destructive p-4 rounded-lg flex items-center gap-3 animate-in fade-in slide-in-from-top-4">
                  <WifiOff className="w-5 h-5" />
                  <span className="font-mono">{error}</span>
                </div>
              )}

              {/* Results Grid */}
              {results.length > 0 && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
                  <div className="flex items-center justify-between border-b border-border pb-4">
                    <h3 className="font-tech text-2xl font-bold text-white flex items-center gap-2">
                      <span className="w-2 h-8 bg-primary rounded-sm"></span>
                      RISULTATI ANALISI
                    </h3>
                    <Badge variant="outline" className="font-mono border-accent text-accent bg-accent/10">
                      {results.length} MATCH TROVATI
                    </Badge>
                  </div>
                  
                  <div className="grid gap-4">
                    {results.map((result, index) => (
                      <Card key={index} className="group bg-card border-l-4 border-l-primary border-y border-r border-border hover:border-primary/50 transition-all duration-300 overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button size="sm" variant="outline" className="border-primary text-primary hover:bg-primary hover:text-primary-foreground font-mono text-xs" onClick={() => window.open(result.url, '_blank')}>
                            <Maximize2 className="w-3 h-3 mr-1" /> ESPANDI
                          </Button>
                        </div>
                        
                        <CardHeader className="pb-2">
                          <div className="flex justify-between items-start">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="secondary" className="bg-primary/20 text-primary border-none font-mono text-[10px] tracking-wider">
                                  {result.type}
                                </Badge>
                                <span className="text-xs font-mono text-muted-foreground">RILEVANZA: <span className="text-accent">{result.relevance}%</span></span>
                                <Progress value={result.relevance} className="w-20 h-1.5 bg-secondary [&>div]:bg-accent" />
                              </div>
                              <CardTitle className="font-tech text-xl text-white group-hover:text-primary transition-colors">
                                {result.title}
                              </CardTitle>
                              <CardDescription className="flex items-center gap-2 text-sm font-mono">
                                <span className="text-accent">{result.source}</span>
                                <span className="text-muted-foreground/50">|</span>
                                <span>ID: REF-{1000 + index}</span>
                              </CardDescription>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="bg-secondary/50 p-3 rounded border border-white/5 font-mono text-sm text-muted-foreground leading-relaxed">
                            <span className="text-primary mr-2">{">"}</span>
                            {result.snippet}
                          </div>
                          <div className="mt-4 flex gap-2">
                            <Button variant="ghost" size="sm" className="h-8 text-xs font-mono text-muted-foreground hover:text-white">
                              <Share2 className="w-3 h-3 mr-1" /> CONDIVIDI
                            </Button>
                            <Button variant="ghost" size="sm" className="h-8 text-xs font-mono text-muted-foreground hover:text-white">
                              <BookOpen className="w-3 h-3 mr-1" /> CITA ({result.citations})
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty State / Quick Actions */}
              {results.length === 0 && !isSearching && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
                  <Card className="bg-card border border-white/5 hover:border-primary/50 transition-all cursor-pointer group relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <CardContent className="p-6 flex flex-col items-center text-center gap-4 relative z-10">
                      <div className="w-16 h-16 rounded-full bg-secondary border border-white/10 flex items-center justify-center text-primary group-hover:scale-110 group-hover:border-primary transition-all duration-300 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                        <Sparkles className="w-8 h-8" />
                      </div>
                      <div>
                        <h3 className="font-tech font-bold text-lg text-white mb-1">SUGGESTIONS</h3>
                        <p className="text-xs font-mono text-muted-foreground">ANALISI CONTESTUALE ATTIVA</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-card border border-white/5 hover:border-accent/50 transition-all cursor-pointer group relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <CardContent className="p-6 flex flex-col items-center text-center gap-4 relative z-10">
                      <div className="w-16 h-16 rounded-full bg-secondary border border-white/10 flex items-center justify-center text-accent group-hover:scale-110 group-hover:border-accent transition-all duration-300 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                        <MessageSquare className="w-8 h-8" />
                      </div>
                      <div>
                        <h3 className="font-tech font-bold text-lg text-white mb-1">CHAT PDF</h3>
                        <p className="text-xs font-mono text-muted-foreground">INTERROGAZIONE DOCUMENTALE</p>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-card border border-white/5 hover:border-white/30 transition-all cursor-pointer group relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <CardContent className="p-6 flex flex-col items-center text-center gap-4 relative z-10">
                      <div className="w-16 h-16 rounded-full bg-secondary border border-white/10 flex items-center justify-center text-white group-hover:scale-110 group-hover:border-white transition-all duration-300 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                        <Library className="w-8 h-8" />
                      </div>
                      <div>
                        <h3 className="font-tech font-bold text-lg text-white mb-1">BIBLIOGRAFIA</h3>
                        <p className="text-xs font-mono text-muted-foreground">GESTIONE FONTI AVANZATA</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          </ScrollArea>
        </main>
      </div>
    </div>
  );
}
