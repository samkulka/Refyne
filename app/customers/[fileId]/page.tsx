"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, User, TrendingUp, AlertTriangle, Award, Mail, Phone, Building, MapPin, DollarSign, Target, Users } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { motion } from "framer-motion";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CustomerInsight {
  category: string;
  title: string;
  description: string;
  severity: "positive" | "neutral" | "negative";
  confidence: number;
}

interface CustomerProfile {
  customer_id: string;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
  industry?: string;
  job_title?: string;
  location?: string;
  account_value?: number;
  lifetime_purchases?: number;
  total_orders?: number;
  average_order_value?: number;
  engagement_score?: number;
  engagement_level?: "champion" | "active" | "moderate" | "at_risk" | "dormant";
  nps_score?: number;
  customer_since?: string;
  last_purchase_date?: string;
  days_since_last_purchase?: number;
  churn_risk?: "low" | "medium" | "high";
  insights: CustomerInsight[];
}

interface CustomerListResponse {
  total: number;
  customers: CustomerProfile[];
  summary?: {
    total_account_value: number;
    average_engagement_score: number;
    high_risk_customers: number;
    champion_customers: number;
    engagement_distribution: {
      champion: number;
      active: number;
      moderate: number;
      at_risk: number;
      dormant: number;
    };
  };
}

const ENGAGEMENT_COLORS = {
  champion: "#9333ea",
  active: "#22c55e",
  moderate: "#3b82f6",
  at_risk: "#f97316",
  dormant: "#6b7280"
};

export default function CustomersPage() {
  const params = useParams();
  const fileId = params.fileId as string;
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<CustomerListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerProfile | null>(null);

  useEffect(() => {
    fetchCustomers();
  }, [fileId]);

  const fetchCustomers = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/${fileId}`);
      if (!response.ok) throw new Error("Failed to fetch customers");
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getEngagementColor = (level?: string) => {
    switch (level) {
      case "champion": return "bg-purple-500 text-white";
      case "active": return "bg-green-500 text-white";
      case "moderate": return "bg-blue-500 text-white";
      case "at_risk": return "bg-orange-500 text-white";
      case "dormant": return "bg-gray-500 text-white";
      default: return "bg-gray-400 text-white";
    }
  };

  const getRiskColor = (risk?: string) => {
    switch (risk) {
      case "low": return "text-green-700 bg-green-100 border-green-300";
      case "medium": return "text-orange-700 bg-orange-100 border-orange-300";
      case "high": return "text-red-700 bg-red-100 border-red-300";
      default: return "text-gray-700 bg-gray-100 border-gray-300";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "positive": return <Award className="h-4 w-4 text-green-600" />;
      case "negative": return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default: return <TrendingUp className="h-4 w-4 text-blue-600" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-800 font-medium">Loading customer profiles...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <p className="text-red-600">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data) return null;

  // Prepare chart data
  const engagementData = data.summary ? [
    { name: "Champions", value: data.summary.engagement_distribution.champion, color: ENGAGEMENT_COLORS.champion },
    { name: "Active", value: data.summary.engagement_distribution.active, color: ENGAGEMENT_COLORS.active },
    { name: "Moderate", value: data.summary.engagement_distribution.moderate, color: ENGAGEMENT_COLORS.moderate },
    { name: "At Risk", value: data.summary.engagement_distribution.at_risk, color: ENGAGEMENT_COLORS.at_risk },
    { name: "Dormant", value: data.summary.engagement_distribution.dormant, color: ENGAGEMENT_COLORS.dormant },
  ].filter(d => d.value > 0) : [];

  if (selectedCustomer) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
        <div className="container mx-auto py-8 px-4 max-w-6xl">
          <Button
            variant="ghost"
            onClick={() => setSelectedCustomer(null)}
            className="mb-6"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>

          <motion.div
            className="grid gap-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Header Card */}
            <Card className="border-2">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-3xl mb-2 text-slate-900">{selectedCustomer.name}</CardTitle>
                    <CardDescription className="text-base text-slate-700 font-medium">
                      {selectedCustomer.job_title && `${selectedCustomer.job_title} · `}
                      {selectedCustomer.company}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Badge className={getEngagementColor(selectedCustomer.engagement_level)}>
                      {selectedCustomer.engagement_level}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {selectedCustomer.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-slate-600" />
                      <span className="text-sm text-slate-800 font-medium">{selectedCustomer.email}</span>
                    </div>
                  )}
                  {selectedCustomer.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-slate-600" />
                      <span className="text-sm text-slate-800 font-medium">{selectedCustomer.phone}</span>
                    </div>
                  )}
                  {selectedCustomer.industry && (
                    <div className="flex items-center gap-2">
                      <Building className="h-4 w-4 text-slate-600" />
                      <span className="text-sm text-slate-800 font-medium">{selectedCustomer.industry}</span>
                    </div>
                  )}
                  {selectedCustomer.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-slate-600" />
                      <span className="text-sm text-slate-800 font-medium">{selectedCustomer.location}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Metrics Grid */}
            <div className="grid md:grid-cols-4 gap-4">
              {selectedCustomer.account_value !== undefined && (
                <Card className="border-2 hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-2">
                    <CardDescription className="flex items-center gap-2 text-slate-700 font-semibold">
                      <DollarSign className="h-5 w-5" />
                      Account Value
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold text-purple-600">
                      ${selectedCustomer.account_value.toLocaleString()}
                    </p>
                  </CardContent>
                </Card>
              )}
              {selectedCustomer.engagement_score !== undefined && (
                <Card className="border-2 hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-2">
                    <CardDescription className="flex items-center gap-2 text-slate-700 font-semibold">
                      <Target className="h-5 w-5" />
                      Engagement Score
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold text-green-600">{selectedCustomer.engagement_score}</p>
                    <p className="text-xs text-slate-600 mt-1 font-medium">out of 100</p>
                  </CardContent>
                </Card>
              )}
              {selectedCustomer.total_orders !== undefined && (
                <Card className="border-2 hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-2">
                    <CardDescription className="text-slate-700 font-semibold">Total Orders</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold text-blue-600">{selectedCustomer.total_orders}</p>
                  </CardContent>
                </Card>
              )}
              {selectedCustomer.churn_risk && (
                <Card className="border-2 hover:shadow-lg transition-shadow">
                  <CardHeader className="pb-2">
                    <CardDescription className="text-slate-700 font-semibold">Churn Risk</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Badge className={`${getRiskColor(selectedCustomer.churn_risk)} border text-base px-3 py-1`}>
                      {selectedCustomer.churn_risk.toUpperCase()}
                    </Badge>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Insights */}
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-900">
                  <TrendingUp className="h-5 w-5" />
                  AI-Generated Insights
                </CardTitle>
                <CardDescription className="text-slate-700 font-medium">
                  Auto-detected patterns and recommendations based on customer data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {selectedCustomer.insights.map((insight, idx) => (
                    <motion.div
                      key={idx}
                      className="flex gap-3 p-4 border-2 rounded-lg hover:shadow-md transition-shadow"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                    >
                      {getSeverityIcon(insight.severity)}
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-900 text-base">{insight.title}</h4>
                        <p className="text-sm text-slate-700 mt-1 leading-relaxed">
                          {insight.description}
                        </p>
                        <div className="flex gap-2 mt-2">
                          <Badge variant="outline" className="text-xs font-medium">
                            {insight.category}
                          </Badge>
                          <Badge variant="outline" className="text-xs font-medium">
                            {Math.round(insight.confidence * 100)}% confidence
                          </Badge>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto py-8 px-4 max-w-7xl">
        <div className="mb-6">
          <Link href="/upload">
            <Button variant="ghost">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Upload
            </Button>
          </Link>
        </div>

        <motion.div
          className="mb-12 text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-5xl md:text-6xl font-bold mb-6 text-slate-900">
            Customer Insights
          </h1>
          <p className="text-2xl text-slate-700 font-medium">
            {data.total} customers analyzed
          </p>
        </motion.div>

        {/* Summary Stats */}
        {data.summary && (
          <motion.div
            className="grid md:grid-cols-4 gap-6 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="border-2 border-slate-200 shadow-lg">
              <CardContent className="pt-8 pb-8 text-center">
                <p className="text-lg text-slate-700 mb-3 font-semibold">Total Value</p>
                <p className="text-5xl font-bold text-purple-600">
                  ${data.summary.total_account_value.toLocaleString()}
                </p>
              </CardContent>
            </Card>
            <Card className="border-2 border-slate-200 shadow-lg">
              <CardContent className="pt-8 pb-8 text-center">
                <p className="text-lg text-slate-700 mb-3 font-semibold">Engagement</p>
                <p className="text-5xl font-bold text-green-600">
                  {data.summary.average_engagement_score}
                </p>
                <p className="text-base text-slate-700 mt-2">out of 100</p>
              </CardContent>
            </Card>
            <Card className="border-2 border-slate-200 shadow-lg">
              <CardContent className="pt-8 pb-8 text-center">
                <p className="text-lg text-slate-700 mb-3 font-semibold">Champions</p>
                <p className="text-5xl font-bold text-blue-600">
                  {data.summary.champion_customers}
                </p>
                <p className="text-base text-slate-700 mt-2">highly engaged</p>
              </CardContent>
            </Card>
            <Card className="border-2 border-slate-200 shadow-lg">
              <CardContent className="pt-8 pb-8 text-center">
                <p className="text-lg text-slate-700 mb-3 font-semibold">At Risk</p>
                <p className="text-5xl font-bold text-red-600">
                  {data.summary.high_risk_customers}
                </p>
                <p className="text-base text-slate-700 mt-2">need attention</p>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Charts Row */}
        {data.summary && engagementData.length > 0 && (
          <motion.div
            className="grid md:grid-cols-2 gap-6 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="border-2 border-slate-200 shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl text-slate-900 font-bold">Engagement Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={engagementData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }: any) => `${name} ${((percent as number) * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {engagementData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="border-2 border-slate-200 shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl text-slate-900 font-bold">Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {engagementData.map((item, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="h-6 w-6 rounded" style={{ backgroundColor: item.color }}></div>
                        <span className="text-lg font-bold text-slate-900">{item.name}</span>
                      </div>
                      <span className="text-4xl font-bold" style={{ color: item.color }}>
                        {item.value}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Customer List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-3xl font-bold text-slate-900 mb-6">All Customers</h2>
          <div className="grid gap-4">
            {data.customers.map((customer, idx) => (
              <motion.div
                key={customer.customer_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Card
                  className="cursor-pointer hover:shadow-xl transition-all border-2 hover:border-purple-200"
                  onClick={() => setSelectedCustomer(customer)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="flex items-center gap-2 text-xl">
                          <User className="h-5 w-5 text-purple-600" />
                          {customer.name}
                        </CardTitle>
                        <CardDescription className="mt-2 text-base text-slate-700 font-medium">
                          {customer.company} {customer.industry && `· ${customer.industry}`}
                        </CardDescription>
                      </div>
                      <div className="flex gap-2 flex-wrap justify-end">
                        <Badge className={getEngagementColor(customer.engagement_level)}>
                          {customer.engagement_level}
                        </Badge>
                        {customer.churn_risk && (
                          <Badge className={`${getRiskColor(customer.churn_risk)} border`}>
                            {customer.churn_risk} risk
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-4">
                      {customer.account_value !== undefined && (
                        <div>
                          <p className="text-sm text-slate-700 mb-2 font-semibold">Value</p>
                          <p className="font-bold text-purple-600 text-2xl">
                            ${customer.account_value.toLocaleString()}
                          </p>
                        </div>
                      )}
                      {customer.engagement_score !== undefined && (
                        <div>
                          <p className="text-sm text-slate-700 mb-2 font-semibold">Engagement</p>
                          <p className="font-bold text-green-600 text-2xl">{customer.engagement_score}/100</p>
                        </div>
                      )}
                      {customer.total_orders !== undefined && (
                        <div>
                          <p className="text-sm text-slate-700 mb-2 font-semibold">Orders</p>
                          <p className="font-bold text-blue-600 text-2xl">{customer.total_orders}</p>
                        </div>
                      )}
                      {customer.insights.length > 0 && (
                        <div>
                          <p className="text-sm text-slate-700 mb-2 font-semibold">Insights</p>
                          <p className="font-bold text-slate-900 text-2xl">{customer.insights.length}</p>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-base text-slate-700 font-semibold">
                      <TrendingUp className="h-5 w-5" />
                      Click for details
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
