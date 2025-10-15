"use client";

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, Eye, TrendingUp, Users, Shield, Zap, ArrowRight, Sparkles, BarChart3 } from "lucide-react";
import { motion } from "framer-motion";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20 max-w-6xl">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Sparkles className="h-4 w-4" />
            AI-Powered Customer Intelligence
          </motion.div>

          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 bg-clip-text text-transparent">
            Turn Customer Data Into
            <br />
            Actionable Insights
          </h1>

          <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-8">
            Upload any CSV and instantly get AI-powered churn predictions, expansion opportunities,
            and customer health scores. No integrations needed.
          </p>

          <div className="flex gap-4 justify-center">
            <Link href="/upload">
              <Button size="lg" className="bg-purple-600 hover:bg-purple-700 text-white">
                <UploadCloud className="h-5 w-5 mr-2" />
                Get Started Free
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
            </Link>
            <Link href="/wireframe">
              <Button size="lg" variant="outline">
                <Eye className="h-5 w-5 mr-2" />
                View Demo
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Feature Cards */}
        <motion.div
          className="grid md:grid-cols-3 gap-6 mb-20"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          <Card className="border-2 hover:border-purple-200 transition-all hover:shadow-lg">
            <CardHeader>
              <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <CardTitle>Churn Prediction</CardTitle>
              <CardDescription>
                AI identifies at-risk customers before they leave, with confidence scores and recommended actions
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-2 hover:border-blue-200 transition-all hover:shadow-lg">
            <CardHeader>
              <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <CardTitle>Customer Profiles</CardTitle>
              <CardDescription>
                Automatically generate rich profiles with engagement scores, purchase patterns, and growth opportunities
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-2 hover:border-green-200 transition-all hover:shadow-lg">
            <CardHeader>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle>Smart Analytics</CardTitle>
              <CardDescription>
                Visual dashboards show revenue trends, engagement distribution, and key metrics at a glance
              </CardDescription>
            </CardHeader>
          </Card>
        </motion.div>

        {/* How It Works */}
        <motion.div
          className="mb-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <h2 className="text-3xl font-bold text-center mb-12 text-slate-900">How It Works</h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="h-16 w-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2 text-slate-900">Upload Your CSV</h3>
              <p className="text-slate-700 font-medium">
                Export customer data from your CRM, Stripe, or any system. We handle messy data automatically.
              </p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2 text-slate-900">AI Analyzes Everything</h3>
              <p className="text-slate-700 font-medium">
                Our AI profiles each customer, calculates health scores, and identifies patterns in seconds.
              </p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2 text-slate-900">Get Actionable Insights</h3>
              <p className="text-slate-700 font-medium">
                See which customers to prioritize, who's at risk, and where to expand revenue.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-12 text-white"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">60s</div>
              <div className="text-purple-100">Time to First Insights</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">85%+</div>
              <div className="text-purple-100">Churn Prediction Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">$0</div>
              <div className="text-purple-100">Setup & Integration Costs</div>
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          className="text-center mt-20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <h2 className="text-3xl font-bold mb-4 text-slate-900">Ready to understand your customers?</h2>
          <p className="text-xl text-slate-700 mb-8 font-medium">
            Start analyzing customer data in under 60 seconds. No credit card required.
          </p>
          <Link href="/upload">
            <Button size="lg" className="bg-purple-600 hover:bg-purple-700 text-white">
              <UploadCloud className="h-5 w-5 mr-2" />
              Upload Your First File
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
