/**
 * CALIDUS Design & Functionality Audit Agent
 *
 * This agent audits the entire application for:
 * - Design consistency (fonts, colors, spacing, buttons)
 * - Broken links
 * - Non-functional features
 * - Missing pages
 * - UI inconsistencies
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
};

class AuditAgent {
  constructor() {
    this.issues = {
      critical: [],
      warning: [],
      info: [],
    };
    this.stats = {
      pagesChecked: 0,
      linksChecked: 0,
      designElementsChecked: 0,
      issuesFound: 0,
    };
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
    const prefix = {
      critical: `${colors.red}${colors.bold}[CRITICAL]${colors.reset}`,
      warning: `${colors.yellow}[WARNING]${colors.reset}`,
      info: `${colors.cyan}[INFO]${colors.reset}`,
      success: `${colors.green}[SUCCESS]${colors.reset}`,
    }[type] || '[INFO]';

    console.log(`${colors.blue}[${timestamp}]${colors.reset} ${prefix} ${message}`);
  }

  addIssue(severity, category, page, description, recommendation) {
    this.issues[severity].push({
      category,
      page,
      description,
      recommendation,
      timestamp: new Date().toISOString(),
    });
    this.stats.issuesFound++;
  }

  // ========================================
  // DESIGN CONSISTENCY CHECKS
  // ========================================

  async checkDesignConsistency() {
    this.log('Checking design consistency...', 'info');

    const frontendDir = path.join(__dirname, 'frontend');
    const appDir = path.join(frontendDir, 'app');
    const componentDir = path.join(frontendDir, 'components');

    // Check Tailwind configuration
    await this.checkTailwindConfig(frontendDir);

    // Check for inconsistent color usage
    await this.checkColorConsistency(appDir, componentDir);

    // Check font usage
    await this.checkFontConsistency(appDir, componentDir);

    // Check button styles
    await this.checkButtonConsistency(appDir, componentDir);

    // Check spacing consistency
    await this.checkSpacingConsistency(appDir, componentDir);

    this.log('Design consistency check complete', 'success');
  }

  async checkTailwindConfig(frontendDir) {
    const tailwindConfigPath = path.join(frontendDir, 'tailwind.config.ts');

    if (!fs.existsSync(tailwindConfigPath)) {
      this.addIssue(
        'critical',
        'Design',
        'tailwind.config.ts',
        'Tailwind configuration file not found',
        'Create tailwind.config.ts with design tokens'
      );
      return;
    }

    const config = fs.readFileSync(tailwindConfigPath, 'utf-8');

    // Check for custom colors
    if (!config.includes('colors:') && !config.includes('extend:')) {
      this.addIssue(
        'warning',
        'Design',
        'tailwind.config.ts',
        'No custom colors defined in Tailwind config',
        'Define brand colors in extend.colors for consistency'
      );
    }

    this.log('Tailwind configuration checked', 'success');
  }

  async checkColorConsistency(appDir, componentDir) {
    const files = this.getAllFiles([appDir, componentDir], ['.tsx', '.jsx']);
    const colorPatterns = new Map();
    const hardcodedColors = [];

    files.forEach(file => {
      const content = fs.readFileSync(file, 'utf-8');

      // Check for hardcoded hex colors
      const hexMatches = content.match(/#[0-9A-Fa-f]{6}/g) || [];
      if (hexMatches.length > 0) {
        hardcodedColors.push({
          file: path.relative(process.cwd(), file),
          colors: hexMatches,
        });
      }

      // Track color class usage
      const colorClasses = content.match(/(?:bg|text|border)-\w+-\d{3}/g) || [];
      colorClasses.forEach(cls => {
        colorPatterns.set(cls, (colorPatterns.get(cls) || 0) + 1);
      });
    });

    if (hardcodedColors.length > 0) {
      hardcodedColors.forEach(({ file, colors }) => {
        this.addIssue(
          'warning',
          'Design',
          file,
          `Hardcoded colors found: ${[...new Set(colors)].join(', ')}`,
          'Use Tailwind color classes (e.g., bg-primary-500) instead of hex colors'
        );
      });
    }

    this.log(`Color consistency checked: ${colorPatterns.size} unique color classes found`, 'success');
  }

  async checkFontConsistency(appDir, componentDir) {
    const files = this.getAllFiles([appDir, componentDir], ['.tsx', '.jsx']);
    const fontSizes = new Map();
    const fontWeights = new Map();

    files.forEach(file => {
      const content = fs.readFileSync(file, 'utf-8');

      // Track font sizes
      const sizeClasses = content.match(/text-(?:xs|sm|base|lg|xl|\dxl)/g) || [];
      sizeClasses.forEach(cls => {
        fontSizes.set(cls, (fontSizes.get(cls) || 0) + 1);
      });

      // Track font weights
      const weightClasses = content.match(/font-(?:thin|light|normal|medium|semibold|bold|extrabold)/g) || [];
      weightClasses.forEach(cls => {
        fontWeights.set(cls, (fontWeights.get(cls) || 0) + 1);
      });

      // Check for inline font sizes
      if (content.includes('fontSize:') || content.includes('fontWeight:')) {
        this.addIssue(
          'warning',
          'Design',
          path.relative(process.cwd(), file),
          'Inline font styles detected',
          'Use Tailwind font classes for consistency'
        );
      }
    });

    this.log(`Font consistency checked: ${fontSizes.size} font sizes, ${fontWeights.size} font weights`, 'success');
  }

  async checkButtonConsistency(appDir, componentDir) {
    const files = this.getAllFiles([appDir, componentDir], ['.tsx', '.jsx']);
    const buttonPatterns = {
      primary: [],
      secondary: [],
      danger: [],
      inconsistent: [],
    };

    files.forEach(file => {
      const content = fs.readFileSync(file, 'utf-8');
      const buttonMatches = content.match(/<button[^>]*className="([^"]*)"[^>]*>/g) || [];

      buttonMatches.forEach(button => {
        const classMatch = button.match(/className="([^"]*)"/);
        if (classMatch) {
          const classes = classMatch[1];

          // Check for consistent button patterns
          if (classes.includes('bg-primary') || classes.includes('bg-blue')) {
            buttonPatterns.primary.push({ file: path.relative(process.cwd(), file), classes });
          } else if (classes.includes('bg-gray') || classes.includes('bg-white')) {
            buttonPatterns.secondary.push({ file: path.relative(process.cwd(), file), classes });
          } else if (classes.includes('bg-red')) {
            buttonPatterns.danger.push({ file: path.relative(process.cwd(), file), classes });
          } else {
            buttonPatterns.inconsistent.push({ file: path.relative(process.cwd(), file), classes });
          }
        }
      });
    });

    if (buttonPatterns.inconsistent.length > 0) {
      buttonPatterns.inconsistent.slice(0, 5).forEach(({ file, classes }) => {
        this.addIssue(
          'info',
          'Design',
          file,
          `Button with unusual styling: ${classes.substring(0, 80)}...`,
          'Consider using standard button patterns (primary, secondary, danger)'
        );
      });
    }

    this.log(`Button consistency checked: ${buttonPatterns.primary.length} primary, ${buttonPatterns.secondary.length} secondary buttons`, 'success');
  }

  async checkSpacingConsistency(appDir, componentDir) {
    const files = this.getAllFiles([appDir, componentDir], ['.tsx', '.jsx']);
    const spacingPatterns = new Map();

    files.forEach(file => {
      const content = fs.readFileSync(file, 'utf-8');

      // Track spacing classes
      const spacingClasses = content.match(/(?:p|m|gap|space)-(?:x|y|t|b|l|r)?-\d+/g) || [];
      spacingClasses.forEach(cls => {
        spacingPatterns.set(cls, (spacingPatterns.get(cls) || 0) + 1);
      });
    });

    this.log(`Spacing consistency checked: ${spacingPatterns.size} unique spacing patterns`, 'success');
  }

  // ========================================
  // LINK VALIDATION
  // ========================================

  async checkLinks() {
    this.log('Checking all internal links...', 'info');

    const frontendDir = path.join(__dirname, 'frontend');
    const appDir = path.join(frontendDir, 'app');
    const componentDir = path.join(frontendDir, 'components');

    const files = this.getAllFiles([appDir, componentDir], ['.tsx', '.jsx']);
    const linkPatterns = {
      internal: [],
      external: [],
      broken: [],
    };

    files.forEach(file => {
      const content = fs.readFileSync(file, 'utf-8');
      const relativePath = path.relative(process.cwd(), file);

      // Find Link components
      const linkMatches = content.match(/<Link[^>]*href=["']([^"']*)["'][^>]*>/g) || [];
      linkMatches.forEach(link => {
        const hrefMatch = link.match(/href=["']([^"']*)["']/);
        if (hrefMatch) {
          const href = hrefMatch[1];
          this.stats.linksChecked++;

          if (href.startsWith('http')) {
            linkPatterns.external.push({ file: relativePath, href });
          } else {
            linkPatterns.internal.push({ file: relativePath, href });
            this.validateInternalLink(relativePath, href);
          }
        }
      });

      // Find router.push calls
      const routerPushMatches = content.match(/router\.push\(['"`]([^'"`]*)['"`]\)/g) || [];
      routerPushMatches.forEach(push => {
        const pathMatch = push.match(/router\.push\(['"`]([^'"`]*)['"`]\)/);
        if (pathMatch) {
          const href = pathMatch[1];
          this.stats.linksChecked++;
          linkPatterns.internal.push({ file: relativePath, href });
          this.validateInternalLink(relativePath, href);
        }
      });
    });

    this.log(`Links checked: ${linkPatterns.internal.length} internal, ${linkPatterns.external.length} external`, 'success');
  }

  validateInternalLink(file, href) {
    // Remove query params and hash
    const cleanHref = href.split('?')[0].split('#')[0];

    // Skip dynamic routes with params
    if (cleanHref.includes('[') || cleanHref === '/') {
      return;
    }

    const frontendDir = path.join(__dirname, 'frontend');
    const appDir = path.join(frontendDir, 'app');

    // Convert route to file path
    const routePath = cleanHref.replace(/^\//, '');
    const possiblePaths = [
      path.join(appDir, routePath, 'page.tsx'),
      path.join(appDir, routePath, 'page.jsx'),
      path.join(appDir, routePath + '.tsx'),
      path.join(appDir, routePath + '.jsx'),
    ];

    const exists = possiblePaths.some(p => fs.existsSync(p));

    if (!exists) {
      this.addIssue(
        'critical',
        'Navigation',
        file,
        `Broken link detected: ${href}`,
        `Create page at ${routePath}/page.tsx or update link`
      );
    }
  }

  // ========================================
  // FUNCTIONALITY CHECKS
  // ========================================

  async checkFunctionality() {
    this.log('Checking application functionality...', 'info');

    // Check API routes
    await this.checkAPIRoutes();

    // Check authentication flow
    await this.checkAuthFlow();

    // Check key features
    await this.checkKeyFeatures();

    this.log('Functionality check complete', 'success');
  }

  async checkAPIRoutes() {
    const backendDir = path.join(__dirname, 'backend', 'app', 'api');

    if (!fs.existsSync(backendDir)) {
      this.addIssue(
        'critical',
        'Backend',
        'backend/app/api',
        'Backend API directory not found',
        'Ensure backend is properly set up'
      );
      return;
    }

    const apiFiles = this.getAllFiles([backendDir], ['.py']);
    const endpoints = new Set();

    apiFiles.forEach(file => {
      const content = fs.readFileSync(file, 'utf-8');
      const routeMatches = content.match(/@router\.(get|post|put|delete|patch)\(['"]([^'"]*)['"]\)/g) || [];

      routeMatches.forEach(route => {
        const pathMatch = route.match(/@router\.\w+\(['"]([^'"]*)['"]\)/);
        if (pathMatch) {
          endpoints.add(pathMatch[1]);
        }
      });
    });

    this.log(`API routes checked: ${endpoints.size} endpoints found`, 'success');
  }

  async checkAuthFlow() {
    const authFilePath = path.join(__dirname, 'backend', 'app', 'api', 'auth.py');

    if (!fs.existsSync(authFilePath)) {
      this.addIssue(
        'critical',
        'Authentication',
        'backend/app/api/auth.py',
        'Authentication module not found',
        'Implement authentication endpoints'
      );
      return;
    }

    const content = fs.readFileSync(authFilePath, 'utf-8');
    const requiredEndpoints = ['/login', '/register', '/refresh', '/me'];

    requiredEndpoints.forEach(endpoint => {
      if (!content.includes(`"${endpoint}"`) && !content.includes(`'${endpoint}'`)) {
        this.addIssue(
          'warning',
          'Authentication',
          'backend/app/api/auth.py',
          `Missing or incomplete endpoint: ${endpoint}`,
          `Ensure ${endpoint} endpoint is implemented`
        );
      }
    });

    // Check for token refresh in frontend
    const authUtilsPath = path.join(__dirname, 'frontend', 'lib', 'auth-utils.ts');
    if (fs.existsSync(authUtilsPath)) {
      const utilsContent = fs.readFileSync(authUtilsPath, 'utf-8');
      if (utilsContent.includes('refreshAuthToken')) {
        this.log('Token refresh functionality verified', 'success');
      } else {
        this.addIssue(
          'warning',
          'Authentication',
          'frontend/lib/auth-utils.ts',
          'Token refresh function not found',
          'Implement automatic token refresh'
        );
      }
    }
  }

  async checkKeyFeatures() {
    const features = [
      { name: 'Requirements Management', path: 'frontend/app/dashboard/requirements/page.tsx' },
      { name: 'Test Cases', path: 'frontend/app/dashboard/test-cases/page.tsx' },
      { name: 'Traceability', path: 'frontend/app/dashboard/traceability/page.tsx' },
      { name: 'Risk Assessment', path: 'frontend/app/dashboard/risk/page.tsx' },
      { name: 'Ask Ahmed Chat', path: 'frontend/components/chat/AskAhmedModal.tsx' },
      { name: 'Settings', path: 'frontend/app/dashboard/settings/page.tsx' },
    ];

    features.forEach(({ name, path: featurePath }) => {
      const fullPath = path.join(__dirname, featurePath);
      if (!fs.existsSync(fullPath)) {
        this.addIssue(
          'critical',
          'Features',
          featurePath,
          `${name} feature not found`,
          `Create ${name} feature at ${featurePath}`
        );
      } else {
        this.stats.pagesChecked++;
      }
    });

    this.log(`Key features checked: ${features.length} features`, 'success');
  }

  // ========================================
  // UTILITY METHODS
  // ========================================

  getAllFiles(directories, extensions) {
    const files = [];

    const walk = (dir) => {
      if (!fs.existsSync(dir)) return;

      const items = fs.readdirSync(dir);
      items.forEach(item => {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
          walk(fullPath);
        } else if (stat.isFile() && extensions.some(ext => item.endsWith(ext))) {
          files.push(fullPath);
        }
      });
    };

    directories.forEach(dir => walk(dir));
    return files;
  }

  // ========================================
  // REPORT GENERATION
  // ========================================

  generateReport() {
    console.log('\n' + '='.repeat(80));
    console.log(`${colors.bold}${colors.cyan}CALIDUS DESIGN & FUNCTIONALITY AUDIT REPORT${colors.reset}`);
    console.log('='.repeat(80) + '\n');

    // Statistics
    console.log(`${colors.bold}Statistics:${colors.reset}`);
    console.log(`  Pages Checked: ${colors.green}${this.stats.pagesChecked}${colors.reset}`);
    console.log(`  Links Checked: ${colors.green}${this.stats.linksChecked}${colors.reset}`);
    console.log(`  Issues Found: ${this.stats.issuesFound > 0 ? colors.red : colors.green}${this.stats.issuesFound}${colors.reset}\n`);

    // Critical Issues
    if (this.issues.critical.length > 0) {
      console.log(`${colors.bold}${colors.red}CRITICAL ISSUES (${this.issues.critical.length}):${colors.reset}`);
      this.issues.critical.forEach((issue, i) => {
        console.log(`\n  ${i + 1}. ${colors.red}[${issue.category}]${colors.reset} ${issue.page}`);
        console.log(`     ${colors.bold}Issue:${colors.reset} ${issue.description}`);
        console.log(`     ${colors.bold}Fix:${colors.reset} ${issue.recommendation}`);
      });
      console.log();
    }

    // Warnings
    if (this.issues.warning.length > 0) {
      console.log(`${colors.bold}${colors.yellow}WARNINGS (${this.issues.warning.length}):${colors.reset}`);
      this.issues.warning.slice(0, 10).forEach((issue, i) => {
        console.log(`\n  ${i + 1}. ${colors.yellow}[${issue.category}]${colors.reset} ${issue.page}`);
        console.log(`     ${colors.bold}Issue:${colors.reset} ${issue.description}`);
        console.log(`     ${colors.bold}Fix:${colors.reset} ${issue.recommendation}`);
      });
      if (this.issues.warning.length > 10) {
        console.log(`\n  ... and ${this.issues.warning.length - 10} more warnings`);
      }
      console.log();
    }

    // Info
    if (this.issues.info.length > 0) {
      console.log(`${colors.bold}${colors.cyan}INFO (${this.issues.info.length}):${colors.reset}`);
      console.log(`  ${this.issues.info.length} minor issues or suggestions found`);
      console.log();
    }

    // Summary
    console.log('='.repeat(80));
    if (this.issues.critical.length === 0 && this.issues.warning.length === 0) {
      console.log(`${colors.green}${colors.bold}✓ ALL CHECKS PASSED!${colors.reset} Your application is consistent and functional.`);
    } else if (this.issues.critical.length === 0) {
      console.log(`${colors.yellow}${colors.bold}⚠ WARNINGS FOUND${colors.reset} - Address these issues to improve consistency.`);
    } else {
      console.log(`${colors.red}${colors.bold}✗ CRITICAL ISSUES FOUND${colors.reset} - These must be fixed immediately.`);
    }
    console.log('='.repeat(80) + '\n');

    // Save detailed report to file
    this.saveReportToFile();
  }

  saveReportToFile() {
    const reportPath = path.join(__dirname, 'audit-report.json');
    const report = {
      timestamp: new Date().toISOString(),
      stats: this.stats,
      issues: this.issues,
    };

    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    this.log(`Detailed report saved to: ${reportPath}`, 'success');
  }

  // ========================================
  // MAIN AUDIT EXECUTION
  // ========================================

  async run() {
    console.log(`\n${colors.bold}${colors.magenta}╔════════════════════════════════════════════════════════════╗${colors.reset}`);
    console.log(`${colors.bold}${colors.magenta}║  CALIDUS Design & Functionality Audit Agent               ║${colors.reset}`);
    console.log(`${colors.bold}${colors.magenta}╚════════════════════════════════════════════════════════════╝${colors.reset}\n`);

    this.log('Starting comprehensive audit...', 'info');

    try {
      await this.checkDesignConsistency();
      await this.checkLinks();
      await this.checkFunctionality();

      this.log('Audit complete! Generating report...', 'success');
      this.generateReport();

    } catch (error) {
      this.log(`Audit failed: ${error.message}`, 'critical');
      console.error(error);
      process.exit(1);
    }
  }
}

// Run the audit
if (require.main === module) {
  const agent = new AuditAgent();
  agent.run();
}

module.exports = AuditAgent;
