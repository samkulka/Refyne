"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */

import React, { useMemo, useState } from "react";
import { 
  Card, CardHeader, CardTitle, CardContent, CardDescription 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { 
  UploadCloud, Plus, Search, Settings, Download, Wand2, Sparkles, 
  Link2, TrendingUp, FileText, ShieldCheck, ArrowRight, X, ListFilter, 
  ExternalLink, Map, Share2
} from "lucide-react";

// ------------------------------------------------------------
// REFYNE – High‑Fidelity UI Wireframe
// Single‑file React mock using Tailwind + shadcn/ui
// Focus: "See your customers clearly" MVP flow
// Views: Upload → Data Health → Profiles → Profile Detail → Relationships → Export
// ------------------------------------------------------------

const MOCK_FILES = [
  { id: "f1", name: "customers_2024.csv", status: "needs-cleaning", score: 68 },
  { id: "f2", name: "transactions_q3.avro", status: "processing", score: null },
  { id: "f3", name: "my_sales_data.csv", status: "cleaned", score: 92 },
];

const MOCK_CUSTOMERS = [
  {
    id: "c1",
    name: "Sarah Martinez",
    city: "Austin, TX",
    value: 15340,
    active: "2024-10-03",
    accounts: 2,
    growth: 12,
    gaps: false,
  },
  {
    id: "c2",
    name: "Julian Park",
    city: "Denver, CO",
    value: 8020,
    active: "2024-09-29",
    accounts: 3,
    growth: 4,
    gaps: true,
  },
  {
    id: "c3",
    name: "Ava Chen",
    city: "San Jose, CA",
    value: 21980,
    active: "2024-10-01",
    accounts: 1,
    growth: 18,
    gaps: false,
  },
  {
    id: "c4",
    name: "Hector Ruiz",
    city: "Phoenix, AZ",
    value: 4420,
    active: "2024-09-17",
    accounts: 1,
    growth: -2,
    gaps: false,
  },
];

function formatCurrency(n: number) {
  return n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function FileRow({ file, onOpenHealth }: { file: any; onOpenHealth: (file: any) => void }) {
  const statusChip = {
    "cleaned": <Badge className="bg-emerald-600 hover:bg-emerald-600">Cleaned ({file.score}%)</Badge>,
    "needs-cleaning": <Badge variant="secondary" className="bg-amber-100 text-amber-900">Needs Cleaning ({file.score}%)</Badge>,
    "processing": <Badge variant="outline" className="border-dashed">Processing…</Badge>,
  }[file.status as "cleaned" | "needs-cleaning" | "processing"];

  return (
    <Card className="border rounded-xl">
      <CardContent className="flex items-center justify-between py-4">
        <div className="flex items-center gap-3">
          <FileText className="h-5 w-5" />
          <div>
            <div className="font-medium">{file.name}</div>
            <div className="text-xs text-muted-foreground">Detected: 12 cols · 10,248 rows</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {statusChip}
          {file.status !== "processing" && (
            <Button size="sm" variant="outline" onClick={() => onOpenHealth(file)}>
              View Health
            </Button>
          )}
          <Button size="sm" variant="ghost">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function DataHealthDialog({ open, onOpenChange, file }: { open: boolean; onOpenChange: (open: boolean) => void; file: any }) {
  const score = file?.score ?? 0;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Data Health – {file?.name}</DialogTitle>
          <DialogDescription>
            Automatic profile with completeness, duplicates, type consistency and suggestions.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-6">
          <div>
            <div className="mb-2 text-sm font-medium">Overall Readiness</div>
            <Progress value={score} className="h-2" />
            <div className="mt-1 text-xs text-muted-foreground">{score}% AI‑ready</div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Metric label="Completeness" value="82%" />
            <Metric label="Duplicate Rows" value="5%" />
            <Metric label="Missing Values" value="12%" />
            <Metric label="Type Consistency" value="98%" />
          </div>
          <div className="space-y-3">
            <Suggestion text="Standardize phone number formats (US E.164)." />
            <Suggestion text="Normalize state / region codes (TX → Texas)." />
            <Suggestion text="Fill missing emails via lookup or mark as null-safes." />
          </div>
          <div className="flex items-center justify-between gap-3">
            <Button variant="secondary"><Wand2 className="mr-2 h-4 w-4" /> Apply Fixes Automatically</Button>
            <div className="flex gap-2">
              <Button variant="outline">Download Report</Button>
              <Button>Generate Profiles <ArrowRight className="ml-2 h-4 w-4" /></Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Card className="border rounded-xl">
      <CardContent className="py-4">
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className="text-lg font-semibold">{value}</div>
      </CardContent>
    </Card>
  );
}

function Suggestion({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border p-3">
      <Sparkles className="mt-0.5 h-4 w-4" />
      <div className="text-sm">{text}</div>
    </div>
  );
}

function ProfilesGrid({ data, onOpenProfile }: { data: any[]; onOpenProfile: (customer: any) => void }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {data.map((c) => (
        <Card key={c.id} className="rounded-2xl hover:shadow-md transition">
          <CardContent className="pt-5">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10"><AvatarFallback>{c.name.split(" ").map((x: string)=>x[0]).join("")}</AvatarFallback></Avatar>
                <div>
                  <div className="font-semibold leading-tight">{c.name}</div>
                  <div className="text-xs text-muted-foreground">{c.city}</div>
                </div>
              </div>
              <Badge variant={c.gaps ? "destructive" : "secondary"}>
                {c.gaps ? "Data gaps" : "Healthy"}
              </Badge>
            </div>
            <Separator className="my-3" />
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg bg-muted p-3">
                <div className="text-xs text-muted-foreground">Total Value</div>
                <div className="font-medium">{formatCurrency(c.value)}</div>
              </div>
              <div className="rounded-lg bg-muted p-3">
                <div className="text-xs text-muted-foreground">Accounts</div>
                <div className="font-medium">{c.accounts}</div>
              </div>
              <div className="rounded-lg bg-muted p-3">
                <div className="text-xs text-muted-foreground">Active</div>
                <div className="font-medium">{c.active}</div>
              </div>
              <div className="rounded-lg bg-muted p-3">
                <div className="text-xs text-muted-foreground">QoQ</div>
                <div className="font-medium flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" /> {c.growth}%
                </div>
              </div>
            </div>
            <div className="mt-4 flex justify-end">
              <Button onClick={() => onOpenProfile(c)} size="sm">View Profile</Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function ProfileDrawer({ customer, onClose }: { customer: any; onClose: () => void }) {
  if (!customer) return null;
  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div className="flex-1 bg-black/40" onClick={onClose} />
      {/* Panel */}
      <div className="w-full max-w-xl bg-background shadow-2xl animate-in slide-in-from-right rounded-l-2xl">
        <div className="p-5 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10"><AvatarFallback>{customer.name.split(" ").map((x: string)=>x[0]).join("")}</AvatarFallback></Avatar>
            <div>
              <div className="font-semibold text-lg">{customer.name}</div>
              <div className="text-xs text-muted-foreground">{customer.city}</div>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}><X className="h-5 w-5" /></Button>
        </div>
        <Separator />
        <ScrollArea className="h-[calc(100vh-5rem)] p-5">
          <div className="grid gap-5">
            <Card className="rounded-xl">
              <CardHeader>
                <CardTitle className="text-base">Overview</CardTitle>
                <CardDescription>Key metrics and activity summary</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-lg bg-muted p-3">
                  <div className="text-xs text-muted-foreground">Total Value</div>
                  <div className="font-medium">{formatCurrency(customer.value)}</div>
                </div>
                <div className="rounded-lg bg-muted p-3">
                  <div className="text-xs text-muted-foreground">Transactions</div>
                  <div className="font-medium">23</div>
                </div>
                <div className="rounded-lg bg-muted p-3">
                  <div className="text-xs text-muted-foreground">Customer Since</div>
                  <div className="font-medium">2022</div>
                </div>
                <div className="rounded-lg bg-muted p-3">
                  <div className="text-xs text-muted-foreground">QoQ Growth</div>
                  <div className="font-medium flex items-center gap-1"><TrendingUp className="h-4 w-4" /> {customer.growth}%</div>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-xl">
              <CardHeader>
                <CardTitle className="text-base">Transactions Over Time</CardTitle>
                <CardDescription>Sparkline placeholder (integrate chart lib)</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-24 w-full rounded-lg bg-gradient-to-r from-muted to-muted/50" />
              </CardContent>
            </Card>

            <Card className="rounded-xl">
              <CardHeader>
                <CardTitle className="text-base">Related Entities</CardTitle>
                <CardDescription>Accounts, referrals, vendors</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2 text-sm"><Link2 className="h-4 w-4" /> Connected Account: <span className="font-medium">Martinez Holdings LLC</span></div>
                <div className="flex items-center gap-2 text-sm"><Link2 className="h-4 w-4" /> Referred Customer: <span className="font-medium">Erin M.</span></div>
                <div className="flex items-center gap-2 text-sm"><Link2 className="h-4 w-4" /> Preferred Vendor: <span className="font-medium">Vendor Co.</span></div>
              </CardContent>
            </Card>

            <Card className="rounded-xl">
              <CardHeader>
                <CardTitle className="text-base">Notes & AI Insights</CardTitle>
                <CardDescription>Summaries and prompts</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="rounded-lg bg-muted p-3 text-sm">
                  “Spending increased 12% QoQ; predicted lifetime value $22,400. Consider upsell to Premium.”
                </div>
                <Textarea placeholder="Add internal note or ask: ‘Why did spend spike in Q3?’" />
                <div className="flex justify-end">
                  <Button><Sparkles className="mr-2 h-4 w-4" /> Generate Insight</Button>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-xl">
              <CardHeader>
                <CardTitle className="text-base">Export / Integrations</CardTitle>
                <CardDescription>Choose formats and destinations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <Select defaultValue="json"><SelectTrigger><SelectValue placeholder="Format" /></SelectTrigger><SelectContent><SelectItem value="csv">CSV</SelectItem><SelectItem value="json">JSON</SelectItem><SelectItem value="parquet">Parquet</SelectItem><SelectItem value="api">API</SelectItem></SelectContent></Select>
                  <Select defaultValue="salesforce"><SelectTrigger><SelectValue placeholder="Destination" /></SelectTrigger><SelectContent><SelectItem value="salesforce">Salesforce</SelectItem><SelectItem value="hubspot">HubSpot</SelectItem><SelectItem value="snowflake">Snowflake</SelectItem><SelectItem value="s3">Amazon S3</SelectItem></SelectContent></Select>
                </div>
                <div className="flex justify-between items-center">
                  <div className="text-xs text-muted-foreground">Mask PII on export</div>
                  <Slider defaultValue={[80]} className="max-w-[200px]" />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline"><ShieldCheck className="mr-2 h-4 w-4" /> Validate</Button>
                  <Button>Run Export <ArrowRight className="ml-2 h-4 w-4" /></Button>
                </div>
              </CardContent>
            </Card>

          </div>
        </ScrollArea>
      </div>
    </div>
  );
}

function RelationshipCanvas({ customers }: { customers: any[] }) {
  // Simple SVG mock of a relationship graph (static layout for wireframe)
  const nodes = useMemo(() => customers.slice(0, 4).map((c, i) => ({
    id: c.id, label: c.name.split(" ")[0], x: 120 + i * 160, y: 80 + (i % 2) * 70
  })), [customers]);
  const edges = [
    { from: nodes[0]?.id, to: nodes[1]?.id },
    { from: nodes[1]?.id, to: nodes[2]?.id },
    { from: nodes[0]?.id, to: nodes[3]?.id },
  ];
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]));

  return (
    <Card className="rounded-2xl">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2"><Map className="h-4 w-4" /> Relationship Map</CardTitle>
        <CardDescription>Visualize linked customers, accounts, referrals</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative h-72 rounded-xl bg-muted">
          <svg className="absolute inset-0 w-full h-full">
            {edges.map((e, idx) => (
              <line key={idx}
                x1={byId[e.from]?.x} y1={byId[e.from]?.y}
                x2={byId[e.to]?.x} y2={byId[e.to]?.y}
                stroke="#999" strokeWidth={2} strokeDasharray="4 3" />
            ))}
            {nodes.map(n => (
              <g key={n.id}>
                <circle cx={n.x} cy={n.y} r={22} fill="white" stroke="#ddd" />
                <text x={n.x} y={n.y+4} textAnchor="middle" className="text-[10px] fill-black">{n.label}</text>
              </g>
            ))}
          </svg>
        </div>
      </CardContent>
    </Card>
  );
}

export default function RefyneWireframe() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [files, setFiles] = useState(MOCK_FILES);
  const [openHealth, setOpenHealth] = useState(false);
  const [healthFile, setHealthFile] = useState(null);
  const [tab, setTab] = useState("overview");
  const [q, setQ] = useState("");
  const [profile, setProfile] = useState(null);
  const filtered = useMemo(() => MOCK_CUSTOMERS.filter(c => c.name.toLowerCase().includes(q.toLowerCase())), [q]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/30">
      {/* Top Bar */}
      <div className="sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-background/80 border-b">
        <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-emerald-600 grid place-items-center text-white font-bold">R</div>
            <div className="font-semibold tracking-tight">Refyne</div>
            <Badge variant="secondary" className="ml-2">See your customers clearly</Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm"><ShieldCheck className="mr-2 h-4 w-4" /> Privacy‑Safe</Button>
            <Button variant="ghost" size="sm"><Share2 className="mr-2 h-4 w-4" /> Invite</Button>
            <Button variant="outline" size="sm"><Settings className="mr-2 h-4 w-4" /> Settings</Button>
          </div>
        </div>
      </div>

      {/* Main */}
      <div className="mx-auto max-w-7xl px-4 py-6 grid gap-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload & Files */}
          <Card className="lg:col-span-2 rounded-2xl">
            <CardHeader className="pb-2">
              <CardTitle className="text-xl flex items-center gap-2"><UploadCloud className="h-5 w-5" /> Upload & Sources</CardTitle>
              <CardDescription>Drop files or connect a source. Generate instant health reports.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-2xl border border-dashed p-6 text-center">
                <div className="text-sm text-muted-foreground">Drag & drop CSV / JSON / Parquet / Avro here</div>
                <div className="mt-3 flex justify-center gap-2">
                  <Button variant="secondary"><Plus className="mr-2 h-4 w-4" /> Upload Data</Button>
                  <Button variant="outline">Connect Source</Button>
                </div>
              </div>
              <div className="space-y-3">
                {files.map(f => (
                  <FileRow key={f.id} file={f} onOpenHealth={(ff) => { setHealthFile(ff); setOpenHealth(true); }} />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="rounded-2xl">
            <CardHeader className="pb-2">
              <CardTitle className="text-xl">Quick Actions</CardTitle>
              <CardDescription>Jumpstart your flow</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full" variant="secondary"><Wand2 className="mr-2 h-4 w-4" /> Apply Auto‑Fixes</Button>
              <Button className="w-full">Generate Profiles <ArrowRight className="ml-2 h-4 w-4" /></Button>
              <Button className="w-full" variant="outline"><ExternalLink className="mr-2 h-4 w-4" /> Download Health Report</Button>
              <Separator />
              <div className="text-xs text-muted-foreground">PII safeguards enabled</div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs: Overview / Profiles / Relationships / Settings */}
        <Tabs value={tab} onValueChange={setTab} className="grid gap-4">
          <TabsList className="w-full justify-start">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="profiles">Profiles</TabsTrigger>
            <TabsTrigger value="relationships">Relationships</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="grid gap-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Metric label="Datasets Processed" value="3" />
              <Metric label="Average Readiness" value="84%" />
              <Metric label="Entities Detected" value="10,248" />
            </div>
            <RelationshipCanvas customers={MOCK_CUSTOMERS} />
          </TabsContent>

          <TabsContent value="profiles" className="grid gap-4">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 w-full max-w-md">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search customers…" />
              </div>
              <Button variant="outline"><ListFilter className="mr-2 h-4 w-4" /> Filter</Button>
            </div>
            <ProfilesGrid data={filtered} onOpenProfile={(c) => setProfile(c)} />
          </TabsContent>

          <TabsContent value="relationships" className="grid gap-4">
            <RelationshipCanvas customers={MOCK_CUSTOMERS} />
            <Card className="rounded-2xl">
              <CardHeader>
                <CardTitle className="text-base">Linking Rules</CardTitle>
                <CardDescription>How Refyne resolves entities</CardDescription>
              </CardHeader>
              <CardContent className="grid md:grid-cols-3 gap-3 text-sm">
                <div className="rounded-lg bg-muted p-3">Exact: customer_id, email</div>
                <div className="rounded-lg bg-muted p-3">Fuzzy: name + phone</div>
                <div className="rounded-lg bg-muted p-3">Heuristics: address proximity</div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="grid gap-4">
            <Card className="rounded-2xl">
              <CardHeader>
                <CardTitle className="text-base">Privacy & PII</CardTitle>
                <CardDescription>Masking, retention, and on‑prem mode</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm">PII Masking Level</div>
                  <Slider defaultValue={[70]} className="max-w-[240px]" />
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-lg bg-muted p-3">Retention: Ephemeral</div>
                  <div className="rounded-lg bg-muted p-3">Deployment: Local‑first</div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <DataHealthDialog open={openHealth} onOpenChange={setOpenHealth} file={healthFile} />
      <ProfileDrawer customer={profile} onClose={() => setProfile(null)} />
    </div>
  );
}
