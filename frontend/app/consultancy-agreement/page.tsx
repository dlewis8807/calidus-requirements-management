'use client';

import { useState } from 'react';
import Link from 'next/link';
import { LockClosedIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { jsPDF } from 'jspdf';

export default function ConsultancyAgreementPage() {
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === '1234') {
      setIsAuthenticated(true);
      setError('');
    } else {
      setError('Incorrect password. Please try again.');
      setPassword('');
    }
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 15;
    const lineHeight = 7;
    let yPosition = margin;

    // Helper function to add text with word wrap
    const addText = (text: string, fontSize: number = 10, isBold: boolean = false, isCenter: boolean = false) => {
      doc.setFontSize(fontSize);
      doc.setFont('helvetica', isBold ? 'bold' : 'normal');

      const maxWidth = pageWidth - (2 * margin);
      const lines = doc.splitTextToSize(text, maxWidth);

      lines.forEach((line: string) => {
        if (yPosition > pageHeight - margin) {
          doc.addPage();
          yPosition = margin;
        }

        if (isCenter) {
          const textWidth = doc.getTextWidth(line);
          doc.text(line, (pageWidth - textWidth) / 2, yPosition);
        } else {
          doc.text(line, margin, yPosition);
        }
        yPosition += lineHeight;
      });
    };

    const addLine = () => {
      yPosition += 3;
      doc.line(margin, yPosition, pageWidth - margin, yPosition);
      yPosition += 5;
    };

    // Title Page
    yPosition = 80;
    addText('═══════════════════════════════════════', 12, true, true);
    addText('PROFESSIONAL SERVICES AGREEMENT', 16, true, true);
    addText('REQUIREMENTS MANAGEMENT SYSTEM DEVELOPMENT', 12, true, true);
    addText('═══════════════════════════════════════', 12, true, true);
    yPosition += 20;
    addText('Between', 11, false, true);
    yPosition += 5;
    addText('CALIDUS AEROSPACE', 12, true, true);
    addText('and', 11, false, true);
    addText('RUYA AI FZCO', 12, true, true);
    yPosition += 10;
    addText('Effective Date: October 28, 2025', 10, false, true);
    yPosition += 10;
    addText('Total Project Value: AED 2,185,548', 12, true, true);

    // New Page - Parties
    doc.addPage();
    yPosition = margin;
    addText('PARTIES', 14, true);
    addLine();
    addText('CALIDUS AEROSPACE', 11, true);
    addText('("Client" or "CALIDUS")', 10);
    addText('An aerospace engineering company organized under the laws of the United Arab Emirates', 10);
    addText('Principal Address: 8th Floor Al Bustan Office Tower, Airport Road, 29th Rabdan Street, Abu Dhabi, UAE', 10);
    yPosition += 5;
    addText('AND', 10, true, true);
    yPosition += 5;
    addText('RUYA AI FZCO - Trade License DMCC980534', 11, true);
    addText('("Consultant" or "RUYA AI")', 10);
    addText('A technology consulting firm specializing in AI-powered enterprise solutions', 10);
    addText('Principal Address: Unit No: UT-12-CO-190, DMCC Business Centre, Level No 12, Uptown Tower, Dubai, UAE', 10);

    // Project Overview
    yPosition += 10;
    addText('1. PROJECT OVERVIEW', 14, true);
    addLine();
    addText('RUYA AI shall consult on the design, develop, test, deploy, and maintain an AI-Powered Requirements Management & Traceability Assistant system for CALIDUS, including:', 10);
    yPosition += 3;
    addText('a) Backend API Infrastructure (FastAPI, PostgreSQL, Redis, JWT authentication)', 10);
    addText('b) Frontend Web Application (Next.js 14, Real-time dashboards, Interactive graphs)', 10);
    addText('c) AI-Powered Features (Ask Ahmed assistant, K2 Think LLM integration)', 10);
    addText('d) Integration Capabilities (ENOVIA PLM, RESTful APIs)', 10);
    addText('e) Regulatory Compliance Features (FAA, EASA, UAE GCAA)', 10);

    // Timeline
    yPosition += 10;
    addText('2. PROJECT TIMELINE', 14, true);
    addLine();
    addText('Commencement Date: November 1, 2025', 10, true);
    addText('Estimated Completion: January 31, 2026', 10, true);
    addText('Total Duration: 12 weeks (3 months)', 10, true);

    // Financial Terms
    yPosition += 10;
    addText('3. FINANCIAL TERMS', 14, true);
    addLine();
    addText('Software Development Services: AED 1,190,548', 11, true);
    addText('Total Estimated Man-Hours: 2,480 hours', 10);
    yPosition += 5;
    addText('Hardware Procurement (Air-Gapped Deployment): AED 995,000', 11, true);
    addText('NVIDIA DGX B200 System with Blackwell Architecture', 10);
    yPosition += 5;
    addText('TOTAL PROJECT COST: AED 2,185,548', 12, true);

    // Payment Schedule
    yPosition += 10;
    addText('4. PAYMENT SCHEDULE', 14, true);
    addLine();
    addText('Software Services Payments:', 11, true);
    addText('• P1 (25%): AED 297,637 - Contract Signing', 10);
    addText('• P2 (20%): AED 238,109.60 - Core Backend Complete', 10);
    addText('• P3 (20%): AED 238,109.60 - Frontend UI Complete', 10);
    addText('• P4 (15%): AED 178,582.20 - AI Integration Complete', 10);
    addText('• P5 (10%): AED 119,054.80 - Advanced Features Complete', 10);
    addText('• P6 (10%): AED 119,054.80 - Final Delivery & Acceptance', 10);
    yPosition += 5;
    addText('Hardware Payments:', 11, true);
    addText('• H1 (50%): AED 497,500 - Hardware Order Placement', 10);
    addText('• H2 (30%): AED 298,500 - Equipment Delivery', 10);
    addText('• H3 (15%): AED 149,250 - Installation Complete', 10);
    addText('• H4 (5%): AED 49,750 - Final Acceptance', 10);

    // Key Deliverables
    yPosition += 10;
    addText('5. KEY DELIVERABLES', 14, true);
    addLine();
    addText('Completed (80%):', 11, true);
    addText('✓ Backend API & Authentication', 10);
    addText('✓ Database (16,501 requirements)', 10);
    addText('✓ Frontend Dashboard & UI', 10);
    addText('✓ Traceability Graph', 10);
    addText('✓ Risk Assessment Dashboard', 10);
    addText('✓ AI Assistant Integration (Ask Ahmed)', 10);
    yPosition += 5;
    addText('Pending (20%):', 11, true);
    addText('⏳ Compliance Dashboard', 10);
    addText('⏳ Impact Analysis', 10);
    addText('⏳ Test Coverage Analyzer', 10);
    addText('⏳ Production Deployment & Hardware Installation', 10);

    // Technical Specifications
    yPosition += 10;
    addText('6. TECHNICAL SPECIFICATIONS', 14, true);
    addLine();
    addText('AI/ML Integration:', 11, true);
    addText('• K2 Think pre-trained API for on-premises LLM', 10);
    addText('• Air-gapped, secured engineering-based LLM', 10);
    addText('• 72 PetaFLOPS AI performance (NVIDIA B200)', 10);
    addText('• Real-time inference: <100ms per requirement', 10);
    yPosition += 5;
    addText('Security Features:', 11, true);
    addText('• Air-gapped deployment (no internet connectivity)', 10);
    addText('• Hardware Security Module (FIPS 140-2 Level 3)', 10);
    addText('• Full disk encryption (AES-256)', 10);
    addText('• Role-based access control', 10);

    // Hardware Breakdown
    yPosition += 10;
    addText('7. HARDWARE INFRASTRUCTURE', 14, true);
    addLine();
    addText('NVIDIA DGX B200 System: AED 550,000', 11, true);
    addText('- 8x NVIDIA B200 GPUs (Blackwell)', 10);
    addText('- 1.4TB GPU Memory (HBM3e)', 10);
    addText('- 72 PetaFLOPS FP4 performance', 10);
    addText('- Optimized for LLM inference', 10);
    yPosition += 5;
    addText('Database & Application Servers: AED 128,450', 11, true);
    addText('Storage Infrastructure (184TB): AED 88,080', 11, true);
    addText('Network Infrastructure: AED 99,090', 11, true);
    addText('Power & Environmental: AED 110,100', 11, true);
    addText('Security & Management (HSM): AED 18,350', 11, true);

    // Warranty & Support
    yPosition += 10;
    addText('8. WARRANTY & SUPPORT', 14, true);
    addLine();
    addText('• 90-day software warranty for defect-free operation', 10);
    addText('• 3-year hardware manufacturer warranty', 10);
    addText('• Next Business Day on-site service for hardware', 10);
    addText('• 12 months RUYA AI on-site support post-installation', 10);
    addText('• Quarterly preventive maintenance visits', 10);
    addText('• 99.9% system uptime guarantee', 10);

    // Intellectual Property
    yPosition += 10;
    addText('9. INTELLECTUAL PROPERTY', 14, true);
    addLine();
    addText('Upon receipt of full payment, all intellectual property rights in the System and deliverables shall be assigned to and become the exclusive property of CALIDUS, including source code, documentation, and all related materials.', 10);

    // Confidentiality
    yPosition += 10;
    addText('10. CONFIDENTIALITY', 14, true);
    addLine();
    addText('Both parties agree to maintain strict confidentiality of all proprietary information, technical data, business strategies, and aerospace requirements shared during the project. Confidentiality obligations survive for 5 years post-termination.', 10);

    // Governing Law
    yPosition += 10;
    addText('11. GOVERNING LAW & DISPUTE RESOLUTION', 14, true);
    addLine();
    addText('This Agreement shall be governed by the laws of the Emirate of Dubai and the UAE. Disputes shall be resolved through mediation, and if unsuccessful, binding arbitration administered by Dubai International Arbitration Centre (DIAC).', 10);

    // Signature Page
    doc.addPage();
    yPosition = margin;
    addText('EXECUTION', 14, true, true);
    addLine();
    addText('IN WITNESS WHEREOF, the Parties have executed this Agreement as of October 28, 2025.', 10, false, true);
    yPosition += 20;

    // Signatures
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text('CALIDUS AEROSPACE', margin, yPosition);
    doc.text('RUYA AI FZCO', pageWidth / 2 + 10, yPosition);
    yPosition += 30;
    doc.line(margin, yPosition, (pageWidth / 2) - 10, yPosition);
    doc.line(pageWidth / 2 + 10, yPosition, pageWidth - margin, yPosition);
    yPosition += 7;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.text('Authorized Signatory', margin, yPosition);
    doc.text('Authorized Signatory', pageWidth / 2 + 10, yPosition);
    yPosition += 20;
    doc.text('Date: __________________', margin, yPosition);
    doc.text('Date: __________________', pageWidth / 2 + 10, yPosition);

    // Footer
    yPosition = pageHeight - 20;
    doc.setFontSize(8);
    doc.setFont('helvetica', 'italic');
    addText('This document is a complete and binding Professional Services Agreement between CALIDUS AEROSPACE and RUYA AI FZCO.', 8, false, true);
    addText('For complete terms and conditions, refer to the full 15-section agreement document.', 8, false, true);
    addText('Document ID: RUYA-CALIDUS-2025-001 | Generated: October 28, 2025', 8, false, true);

    // Save the PDF
    doc.save('RUYA_CALIDUS_Professional_Services_Agreement.pdf');
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <Link href="/">
              <img src="/images/CLS-AEROSPACE-LOGO.svg" alt="CALIDUS" className="h-16 mx-auto mb-6" />
            </Link>
            <div className="bg-primary-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <LockClosedIcon className="h-10 w-10 text-primary-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Protected Document</h1>
            <p className="text-gray-600">Please enter the password to view the RUYA Consultancy Agreement</p>
          </div>

          {/* Password Form */}
          <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
                  placeholder="Enter password"
                  autoFocus
                />
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              )}

              <button
                type="submit"
                className="w-full px-6 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-semibold shadow-card hover:shadow-card-hover"
              >
                Access Document
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">
                ← Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <Link href="/">
            <img src="/images/CLS-AEROSPACE-LOGO.svg" alt="CALIDUS" className="h-12" />
          </Link>
          <div className="flex items-center space-x-4">
            <button
              onClick={generatePDF}
              className="px-4 py-2 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors font-semibold text-sm flex items-center space-x-2"
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
              <span>Download PDF</span>
            </button>
            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-semibold text-sm"
            >
              Print Document
            </button>
            <Link
              href="/"
              className="px-4 py-2 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-semibold text-sm"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-xl shadow-lg p-12 border border-gray-200">
          <div className="prose max-w-none">
            <div className="text-center mb-12 pb-8 border-b-2 border-gray-300">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                PROFESSIONAL SERVICES AGREEMENT
              </h1>
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                Requirements Management System Development
              </h2>
              <p className="text-sm text-gray-600">
                Between CALIDUS AEROSPACE and RUYA AI FZCO
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Effective Date: October 28, 2025
              </p>
            </div>

            <div className="space-y-8 text-gray-800 leading-relaxed" style={{ fontFamily: 'monospace', fontSize: '13px', lineHeight: '1.6' }}>
              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">PARTIES</h3>
                <div className="space-y-4">
                  <div>
                    <p className="font-semibold">CALIDUS AEROSPACE</p>
                    <p>(&quot;Client&quot; or &quot;CALIDUS&quot;)</p>
                    <p>An aerospace engineering company organized under the laws of the United Arab Emirates</p>
                    <p>Principal Address: 8th Floor Al Bustan Office Tower, Airport Road, 29th Rabdan Street, Abu Dhabi, UAE</p>
                  </div>
                  <p className="text-center font-bold">AND</p>
                  <div>
                    <p className="font-semibold">RUYA AI FZCO - Trade License DMCC980534</p>
                    <p>(&quot;Consultant&quot; or &quot;RUYA AI&quot;)</p>
                    <p>A technology consulting firm specializing in AI-powered enterprise solutions</p>
                    <p>Principal Address:</p>
                    <p>Unit No: UT-12-CO-190</p>
                    <p>DMCC Business Centre, Level No 12</p>
                    <p>Uptown Tower, Dubai, United Arab Emirates</p>
                  </div>
                </div>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">PROJECT OVERVIEW</h3>
                <p className="mb-4">
                  RUYA AI shall consult on the design, develop, test, deploy, and maintain an AI-Powered
                  Requirements Management & Traceability Assistant system for CALIDUS, including:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Backend API Infrastructure (FastAPI, PostgreSQL, Redis)</li>
                  <li>Frontend Web Application (Next.js 14, Real-time dashboards)</li>
                  <li>AI-Powered Features (Ask Ahmed assistant, K2 Think LLM integration)</li>
                  <li>Integration Capabilities (ENOVIA PLM, RESTful APIs)</li>
                  <li>Regulatory Compliance (FAA, EASA, UAE GCAA)</li>
                </ul>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">PROJECT TIMELINE</h3>
                <div className="space-y-2">
                  <p><strong>Commencement Date:</strong> November 1, 2025</p>
                  <p><strong>Estimated Completion:</strong> January 31, 2026</p>
                  <p><strong>Total Duration:</strong> 12 weeks (3 months)</p>
                </div>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">FINANCIAL TERMS</h3>

                <div className="mb-6">
                  <h4 className="font-bold text-lg mb-3">Software Development Services</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-2xl font-bold text-primary-600 mb-2">AED 1,190,548</p>
                    <p className="text-sm text-gray-600">Total Estimated Man-Hours: 2,480 hours</p>
                  </div>
                </div>

                <div className="mb-6">
                  <h4 className="font-bold text-lg mb-3">Hardware Procurement (Air-Gapped Deployment)</h4>
                  <div className="bg-gray-50 p-4 rounded-lg mb-4">
                    <p className="text-2xl font-bold text-primary-600 mb-2">AED 995,000</p>
                    <p className="text-sm text-gray-600">NVIDIA Blackwell Architecture</p>
                  </div>
                  <div className="space-y-2 text-sm">
                    <p><strong>• NVIDIA DGX B200 System:</strong> AED 550,000</p>
                    <p className="ml-4">8x B200 GPUs, 1.4TB GPU Memory, 72 PetaFLOPS AI Performance</p>
                    <p><strong>• Database & Application Servers:</strong> AED 128,450</p>
                    <p><strong>• Storage Infrastructure (184TB):</strong> AED 88,080</p>
                    <p><strong>• Network Infrastructure:</strong> AED 99,090</p>
                    <p><strong>• Power & Environmental:</strong> AED 110,100</p>
                    <p><strong>• Security & Management (HSM):</strong> AED 18,350</p>
                  </div>
                </div>

                <div className="bg-primary-50 p-6 rounded-lg border-2 border-primary-200">
                  <h4 className="font-bold text-xl mb-2 text-primary-900">TOTAL PROJECT COST</h4>
                  <p className="text-3xl font-bold text-primary-600">AED 2,185,548</p>
                  <p className="text-sm text-gray-600 mt-2">Services + Hardware Infrastructure</p>
                </div>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">PAYMENT SCHEDULE</h3>
                <div className="space-y-3">
                  <h4 className="font-semibold">Software Services Payments:</h4>
                  <div className="space-y-2 text-sm">
                    <p>• P1 (25%): AED 297,637 - Contract Signing</p>
                    <p>• P2 (20%): AED 238,109.60 - Core Backend Complete</p>
                    <p>• P3 (20%): AED 238,109.60 - Frontend UI Complete</p>
                    <p>• P4 (15%): AED 178,582.20 - AI Integration Complete</p>
                    <p>• P5 (10%): AED 119,054.80 - Advanced Features Complete</p>
                    <p>• P6 (10%): AED 119,054.80 - Final Delivery & Acceptance</p>
                  </div>

                  <h4 className="font-semibold mt-4">Hardware Payments:</h4>
                  <div className="space-y-2 text-sm">
                    <p>• H1 (50%): AED 497,500 - Hardware Order Placement</p>
                    <p>• H2 (30%): AED 298,500 - Equipment Delivery</p>
                    <p>• H3 (15%): AED 149,250 - Installation Complete</p>
                    <p>• H4 (5%): AED 49,750 - Final Acceptance</p>
                  </div>
                </div>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">KEY DELIVERABLES</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <p className="font-semibold mb-2">✓ Completed (80%)</p>
                    <ul className="space-y-1">
                      <li>• Backend API & Authentication</li>
                      <li>• Database (16,501 requirements)</li>
                      <li>• Frontend Dashboard & UI</li>
                      <li>• Traceability Graph</li>
                      <li>• Risk Assessment</li>
                      <li>• AI Assistant Integration</li>
                    </ul>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                    <p className="font-semibold mb-2">⏳ Pending (20%)</p>
                    <ul className="space-y-1">
                      <li>• Compliance Dashboard</li>
                      <li>• Impact Analysis</li>
                      <li>• Test Coverage Analyzer</li>
                      <li>• Production Deployment</li>
                      <li>• Hardware Installation</li>
                      <li>• UAT & Training</li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">TECHNICAL SPECIFICATIONS</h3>
                <div className="space-y-4 text-sm">
                  <div>
                    <p className="font-semibold mb-2">AI/ML Integration:</p>
                    <ul className="list-disc list-inside space-y-1 ml-4">
                      <li>K2 Think pre-trained API for on-premises LLM</li>
                      <li>Air-gapped, secured engineering-based LLM</li>
                      <li>72 PetaFLOPS AI performance (NVIDIA B200)</li>
                      <li>Real-time inference: &lt;100ms per requirement</li>
                    </ul>
                  </div>
                  <div>
                    <p className="font-semibold mb-2">Security Features:</p>
                    <ul className="list-disc list-inside space-y-1 ml-4">
                      <li>Air-gapped deployment (no internet connectivity)</li>
                      <li>Hardware Security Module (FIPS 140-2 Level 3)</li>
                      <li>Full disk encryption (AES-256)</li>
                      <li>Role-based access control</li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">WARRANTY & SUPPORT</h3>
                <ul className="list-disc list-inside space-y-2 ml-4 text-sm">
                  <li>90-day software warranty for defect-free operation</li>
                  <li>3-year hardware manufacturer warranty</li>
                  <li>Next Business Day on-site service for hardware</li>
                  <li>12 months RUYA AI on-site support post-installation</li>
                  <li>Quarterly preventive maintenance visits</li>
                  <li>99.9% system uptime guarantee</li>
                </ul>
              </section>

              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">INTELLECTUAL PROPERTY</h3>
                <p className="text-sm">
                  Upon receipt of full payment, all intellectual property rights in the System and
                  deliverables shall be assigned to and become the exclusive property of CALIDUS,
                  including source code, documentation, and all related materials.
                </p>
              </section>

              <section className="bg-gray-100 p-6 rounded-lg border border-gray-300">
                <p className="text-xs text-gray-600 text-center mb-4">
                  This is a summary document. For complete terms, conditions, warranties, liability limitations,
                  and legal provisions, please refer to the full Professional Services Agreement document.
                </p>
                <div className="border-t-2 border-gray-400 pt-6 mt-6">
                  <div className="grid grid-cols-2 gap-8 text-sm">
                    <div>
                      <p className="font-bold mb-2">CALIDUS AEROSPACE</p>
                      <div className="border-t border-gray-400 mt-8 pt-2">
                        <p>Authorized Signatory</p>
                        <p className="text-xs text-gray-500 mt-4">Date: ______________</p>
                      </div>
                    </div>
                    <div>
                      <p className="font-bold mb-2">RUYA AI FZCO</p>
                      <div className="border-t border-gray-400 mt-8 pt-2">
                        <p>Authorized Signatory</p>
                        <p className="text-xs text-gray-500 mt-4">Date: ______________</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>For full agreement details, contact RUYA AI FZCO or CALIDUS Aerospace legal department.</p>
          <p className="mt-2">Document ID: RUYA-CALIDUS-2025-001 | Generated: October 28, 2025</p>
        </div>
      </main>
    </div>
  );
}
