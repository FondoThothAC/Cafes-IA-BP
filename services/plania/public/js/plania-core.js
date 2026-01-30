/**
 * =================================================================================
 * PROYECTO: PlanIA (Frontend)
 * ARCHIVO: public/js/plania-core.js
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: MIT
 * DESCRIPCIÓN: Core JavaScript - Navegación global, temas, guardado y proyectos
 * =================================================================================
 */

const PlanIA = {
    // Configuration
    API_URL: 'save_row.php',
    autoSaveInterval: null,
    unsavedChanges: false,

    // Theme definitions
    themes: {
        // Dark Themes
        'blue-dark': { name: 'Azul Oscuro', primary: '#2563eb', bg: '#0f172a', surface: '#1e293b', text: '#f1f5f9' },
        'green-dark': { name: 'Verde Esmeralda', primary: '#10b981', bg: '#022c22', surface: '#064e3b', text: '#ecfdf5' },
        'purple-dark': { name: 'Púrpura', primary: '#8b5cf6', bg: '#1e1033', surface: '#2e1065', text: '#f5f3ff' },
        'orange-dark': { name: 'Naranja', primary: '#f59e0b', bg: '#1a1207', surface: '#451a03', text: '#fffbeb' },
        'pink-dark': { name: 'Rosa', primary: '#ec4899', bg: '#2d0a1e', surface: '#500724', text: '#fdf2f8' },
        'cyan-dark': { name: 'Cian', primary: '#06b6d4', bg: '#0c1a1e', surface: '#083344', text: '#ecfeff' },
        'red-dark': { name: 'Rojo', primary: '#ef4444', bg: '#1a0505', surface: '#450a0a', text: '#fef2f2' },

        // Light Themes
        'blue-light': { name: 'Azul Claro', primary: '#2563eb', bg: '#f8fafc', surface: '#ffffff', text: '#0f172a' },
        'green-light': { name: 'Verde Claro', primary: '#059669', bg: '#f0fdf4', surface: '#ffffff', text: '#064e3b' },
        'purple-light': { name: 'Púrpura Claro', primary: '#7c3aed', bg: '#f5f3ff', surface: '#ffffff', text: '#2e1065' },
        'orange-light': { name: 'Naranja Claro', primary: '#d97706', bg: '#fffbeb', surface: '#ffffff', text: '#451a03' },
        'pink-light': { name: 'Rosa Claro', primary: '#db2777', bg: '#fdf2f8', surface: '#ffffff', text: '#500724' },
        'cyan-light': { name: 'Cian Claro', primary: '#0891b2', bg: '#ecfeff', surface: '#ffffff', text: '#083344' },
        'red-light': { name: 'Rojo Claro', primary: '#dc2626', bg: '#fef2f2', surface: '#ffffff', text: '#450a0a' },
        'slate-light': { name: 'Gris Profesional', primary: '#475569', bg: '#f8fafc', surface: '#ffffff', text: '#0f172a' },
    },

    // State
    state: {
        currentProject: null,
        projects: [],
        theme: 'blue-dark',
        uuid: null,
    },

    // Initialize
    init() {
        // Auth Check
        const publicPages = ['login.html'];
        const currentPage = window.location.pathname.split('/').pop();
        this.state.uuid = localStorage.getItem('uuid_usuario');

        if (!this.state.uuid && !publicPages.includes(currentPage)) {
            window.location.href = 'login.html';
            return;
        }

        this.state.theme = localStorage.getItem('plania_theme') || 'blue-dark';
        this.state.currentProject = localStorage.getItem('plania_current_project') || null;

        this.applyTheme(this.state.theme);

        // Only load projects if authenticated
        if (this.state.uuid) {
            this.loadProjects().then(() => {
                this.renderNavbar();
                this.setupEventListeners();
                this.startAutoSave();
            });
        }
    },

    // Apply theme
    applyTheme(themeId) {
        const theme = this.themes[themeId];
        if (!theme) return;

        document.documentElement.style.setProperty('--primary', theme.primary);
        document.documentElement.style.setProperty('--bg', theme.bg);
        document.documentElement.style.setProperty('--surface', theme.surface);
        document.documentElement.style.setProperty('--text', theme.text);

        document.body.style.backgroundColor = theme.bg;
        document.body.style.color = theme.text;

        localStorage.setItem('plania_theme', themeId);
        this.state.theme = themeId;
    },

    // Logout
    logout() {
        localStorage.removeItem('uuid_usuario');
        localStorage.removeItem('user_role');
        window.location.href = 'login.html';
    },

    // Load projects from API
    async loadProjects() {
        try {
            const role = localStorage.getItem('user_role') || 'emprendedor';
            const res = await fetch(this.API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'list', uuid_usuario: this.state.uuid, role: role })
            });
            const data = await res.json();
            this.state.projects = data.projects || [];

            if (!this.state.currentProject && this.state.projects.length > 0) {
                this.setCurrentProject(this.state.projects[0].id_proyecto);
            }
        } catch (err) {
            console.error('Error loading projects:', err);
            this.state.projects = [];
        }
    },

    // Set current project
    setCurrentProject(projectId) {
        this.state.currentProject = projectId;
        localStorage.setItem('plania_current_project', projectId);

        window.dispatchEvent(new CustomEvent('plania:projectChanged', {
            detail: { projectId, project: this.getCurrentProject() }
        }));

        const selector = document.getElementById('plania-project-selector');
        if (selector) selector.value = projectId;

        // Update edit link
        this.updateEditLink();
    },

    // Update edit link href
    updateEditLink() {
        const editLink = document.querySelector('a[href*="wizard.html"]');
        if (editLink && this.state.currentProject) {
            editLink.href = `wizard.html?edit=${this.state.currentProject}`;
        }
    },

    // Get current project data
    getCurrentProject() {
        return this.state.projects.find(p => p.id_proyecto == this.state.currentProject) || null;
    },

    // Render navbar
    renderNavbar() {
        const container = document.getElementById('plania-navbar');
        if (!container) return;

        const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
        const project = this.getCurrentProject();
        const userRole = localStorage.getItem('user_role') || 'usuario';

        const navItems = [
            { id: 'index', icon: '🏠', label: 'Inicio', href: 'index.html' },
            {
                id: 'strategy', icon: '♟️', label: 'Estrategia', items: [
                    { id: 'wizard', icon: '✏️', label: 'Plan de Negocios', href: project ? `wizard.html?edit=${project.id_proyecto}` : 'wizard.html' },
                    { id: 'problem_definition', icon: '🎯', label: 'Definición Problema', href: 'problem_definition.html' },
                    { id: 'delta', icon: '🔺', label: 'Modelo Delta', href: 'delta_dashboard.html' },
                    { id: 'canvas', icon: '🎨', label: 'Modelo Canvas', href: 'canvas.html' },
                    { id: 'foda', icon: '⚡', label: 'Análisis FODA', href: 'foda.html' },
                    { id: 'brand_identity', icon: '🏷️', label: 'Identidad de Marca', href: 'brand_identity.html' },
                    { id: 'flywheel', icon: '🔄', label: 'Flywheel (Ciclo)', href: 'flywheel.html' },
                ]
            },
            {
                id: 'market', icon: '🛍️', label: 'Mercado', items: [
                    { id: 'industry_analysis', icon: '🏭', label: 'Análisis Industria', href: 'industry_analysis.html' },
                    { id: 'market_study', icon: '📊', label: 'Estudio de Mercado', href: 'market_study.html' },
                    { id: 'customer_research', icon: '🔬', label: 'Investigación Cliente', href: 'customer_research.html' },
                    { id: 'marketing_plan', icon: '📣', label: 'Plan de Marketing', href: 'marketing_plan.html' },
                    { id: 'surveys', icon: '📝', label: 'Encuestas', href: 'surveys.html' },
                ]
            },
            {
                id: 'operations', icon: '⚙️', label: 'Operación', items: [
                    { id: 'organization', icon: '👔', label: 'Organización', href: 'organization.html' },
                    { id: 'operations', icon: '🏭', label: 'Plan Operativo', href: 'operations.html' },
                    { id: 'payroll', icon: '👥', label: 'Nómina (Payroll)', href: 'payroll.html' },
                    { id: 'customers', icon: '📇', label: 'CRM Clientes', href: 'customers.html' },
                    { id: 'risk_analysis', icon: '⚠️', label: 'Análisis de Riesgos', href: 'risk_analysis.html' },
                ]
            },
            {
                id: 'finance', icon: '💰', label: 'Finanzas', items: [
                    { id: 'investment_budget', icon: '🏦', label: '1. Inversión Inicial', href: 'investment_budget.html' },
                    { id: 'cost_projection', icon: '📉', label: '2. Costos y Gastos', href: 'cost_projection.html' },
                    { id: 'revenue_projection', icon: '📈', label: '3. Ingresos (Ventas)', href: 'revenue_projection.html' },
                    { id: 'estado_resultados', icon: '📊', label: '4. Estado de Resultados', href: 'estado_resultados.html' },
                    { id: 'balance_general', icon: '⚖️', label: '5. Balance General', href: 'balance_general.html' },
                    { id: 'income_statement', icon: '💵', label: '6. Valuación (VAN/TIR)', href: 'income_statement.html' },
                    { id: 'exit_strategy', icon: '🚪', label: '7. Estrategia Salida', href: 'exit_strategy.html' },
                ]
            },
            {
                id: 'control', icon: '🎛️', label: 'Control', items: [
                    { id: 'flywheel', icon: '🔄', label: 'Flywheel (Ciclo)', href: 'flywheel.html' },
                    { id: 'kpis', icon: '🎯', label: 'Dashboard KPIs', href: 'kpis.html' },
                    { id: 'esg_sustainability', icon: '🌱', label: 'ESG Sostenibilidad', href: 'esg_sustainability.html' },
                    { id: 'projects_list', icon: '📋', label: 'Mis Proyectos', href: 'projects_list.html' },
                    { id: 'export_pdf', icon: '📄', label: 'Exportar PDF', href: 'export_pdf.html' },
                    { id: 'admin_grid', icon: '🔐', label: 'Admin Global', href: 'admin_grid.html' },
                ]
            }
        ];

        // Helper to render items
        const renderItem = (item) => {
            if (item.items) {
                // Dropdown
                const isActive = item.items.some(sub => sub.id === currentPage);
                // Note: Added onclick to toggle 'active' class on the dropdown parent for mobile/click support
                return `
                    <div class="nav-item-dropdown" onclick="this.classList.toggle('force-show')">
                        <div class="nav-link nav-dropdown-trigger ${isActive ? 'active' : ''}">
                            <span class="nav-icon">${item.icon}</span>
                            <span class="nav-label">${item.label}</span>
                        </div>
                        <div class="nav-dropdown-menu">
                            ${item.items.map(sub => `
                                <a href="${sub.href}" class="nav-dropdown-item ${currentPage === sub.id ? 'active' : ''}">
                                    <span class="nav-icon">${sub.icon}</span>
                                    <span>${sub.label}</span>
                                </a>
                            `).join('')}
                        </div>
                    </div>
                `;
            } else {
                // Single Link
                return `
                    <a href="${item.href}" class="nav-link ${currentPage === item.id ? 'active' : ''}" title="${item.label}">
                        <span class="nav-icon">${item.icon}</span>
                        <span class="nav-label">${item.label}</span>
                    </a>
                `;
            }
        };

        container.innerHTML = `
            <style>
                /* Inject logic for force-show click handling */
                .nav-item-dropdown.force-show .nav-dropdown-menu { display: block; }
                .user-widget { display: flex; align-items: center; gap: 8px; padding: 0 10px; border-left: 1px solid var(--surface-light); margin-left: 10px; font-size: 0.85rem; cursor: pointer; position: relative;}
                .user-widget .user-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--surface-light); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
                .user-dropdown { display: none; position: absolute; top: 100%; right: 0; background: var(--surface); border: 1px solid var(--surface-light); border-radius: 8px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); min-width: 150px; padding: 0.5rem; z-index: 1000; }
                .user-dropdown.show { display: block; }
                .user-item { display: block; padding: 0.5rem 1rem; color: var(--text); padding: 8px; border-radius: 6px; cursor: pointer; transition: background 0.1s; text-align: left; width: 100%; border: none; background: transparent; }
                .user-item:hover { background: var(--surface-light); }
            </style>
            <nav class="plania-nav">
                <div class="nav-brand">
                    <a href="index.html">🚀 <span>PlanIA</span></a>
                </div>
                
                <div class="nav-project-selector">
                    <label>Proyecto:</label>
                    <select id="plania-project-selector">
                        <option value="">-- Seleccionar --</option>
                        ${this.state.projects.map(p => `
                            <option value="${p.id_proyecto}" ${p.id_proyecto == this.state.currentProject ? 'selected' : ''}>
                                ${p.a1_nombre_negocio || 'Sin nombre'}
                            </option>
                        `).join('')}
                    </select>
                </div>
                
                <div class="nav-links-container">
                    <div class="nav-links" id="nav-links-scroll" style="overflow: visible;">
                        ${navItems.map(renderItem).join('')}
                    </div>
                </div>
                
                <div class="nav-actions">
                    <!-- Save/Export Actions -->
                    <div class="nav-save-group">
                        <button id="btn-save" class="nav-btn save-btn" title="Guardar (Ctrl+S)">
                            💾 <span class="save-label">Guardar</span>
                        </button>
                        <button id="btn-export-menu" class="nav-btn" title="Exportar">
                            📤
                        </button>
                        <div class="export-dropdown" id="export-dropdown">
                            <button class="export-option" data-export="pdf">📄 Exportar PDF</button>
                            <button class="export-option" data-export="csv">📊 Exportar CSV</button>
                        </div>
                    </div>
                    
                    <!-- Save Indicator -->
                    <span id="save-indicator" class="save-indicator"></span>
                    
                    <!-- Theme Toggle -->
                    <button id="theme-toggle" class="nav-btn" title="Cambiar tema">
                        ${this.state.theme.includes('light') ? '🌙' : '☀️'}
                    </button>
                    <div class="theme-dropdown" id="theme-dropdown">
                        ${Object.entries(this.themes).map(([id, theme]) => `
                            <button class="theme-option ${this.state.theme === id ? 'active' : ''}" data-theme="${id}">
                                <span class="theme-color" style="background: ${theme.primary}"></span>
                                ${theme.name}
                            </button>
                        `).join('')}
                    </div>

                    <!-- User Widget -->
                    <div class="user-widget" id="user-widget-toggle" title="${this.state.uuid}">
                        <div class="user-avatar">👤</div>
                        <div style="display: flex; flex-direction: column; line-height: 1.2;">
                            <span style="font-weight: 600;">${this.state.uuid.split('.')[0]}</span>
                            <span style="font-size: 0.7rem; color: var(--text-muted);">${userRole}</span>
                        </div>
                        <div class="user-dropdown" id="user-dropdown">
                            <button class="user-item" onclick="PlanIA.logout()">🚪 Cerrar Sesión</button>
                        </div>
                    </div>
                </div>
            </nav>
        `;

        // Init User Dropdown
        document.getElementById('user-widget-toggle')?.addEventListener('click', () => {
            document.getElementById('user-dropdown').classList.toggle('show');
        });

        this.initNavbarScroll();
    },

    // Initialize navbar scroll
    initNavbarScroll() {
        // ... (existing scroll code) ...
    },

    // Initialize Currency Helpers
    setupCurrencyHelpers() {
        // Attach to all number inputs inside form groups
        const inputs = document.querySelectorAll('.form-group input[type="number"], .form-group input.currency-input');

        inputs.forEach(input => {
            // Check if helper already exists
            const parent = input.parentElement;
            if (parent.querySelector('.currency-helper')) return;

            // Create helper
            const helper = document.createElement('span');
            helper.className = 'currency-helper';
            parent.appendChild(helper);

            // Function to update helper
            const updateHelper = () => {
                const val = parseFloat(input.value);
                if (!isNaN(val) && val !== 0) {
                    helper.textContent = this.formatCurrency(val);
                    helper.style.display = 'block';
                } else {
                    helper.style.display = 'none';
                }
            };

            // Listeners
            input.addEventListener('input', updateHelper);
            input.addEventListener('focus', updateHelper);
            input.addEventListener('blur', () => { setTimeout(() => helper.style.display = 'none', 200); });

            // Initial check
            updateHelper();
        });
    },

    // Setup event listeners
    setupEventListeners() {
        // Call currency helper setup periodically to catch dynamic inputs
        this.setupCurrencyHelpers();
        setInterval(() => this.setupCurrencyHelpers(), 2000);

        // Project selector
        document.addEventListener('change', (e) => {
            if (e.target.id === 'plania-project-selector') {
                this.setCurrentProject(e.target.value);
            }
        });

        // Theme toggle
        document.addEventListener('click', (e) => {
            if (e.target.id === 'theme-toggle' || e.target.closest('#theme-toggle')) {
                const dropdown = document.getElementById('theme-dropdown');
                if (dropdown) dropdown.classList.toggle('show');
                document.getElementById('export-dropdown')?.classList.remove('show');
            }

            if (e.target.classList.contains('theme-option')) {
                const themeId = e.target.dataset.theme;
                this.applyTheme(themeId);
                this.renderNavbar();
                document.getElementById('theme-dropdown')?.classList.remove('show');
            }
        });

        // Export menu
        document.addEventListener('click', (e) => {
            if (e.target.id === 'btn-export-menu' || e.target.closest('#btn-export-menu')) {
                const dropdown = document.getElementById('export-dropdown');
                if (dropdown) dropdown.classList.toggle('show');
                document.getElementById('theme-dropdown')?.classList.remove('show');
            }

            if (e.target.classList.contains('export-option')) {
                const exportType = e.target.dataset.export;
                this.handleExport(exportType);
                document.getElementById('export-dropdown')?.classList.remove('show');
            }
        });

        // Save button
        document.addEventListener('click', (e) => {
            if (e.target.id === 'btn-save' || e.target.closest('#btn-save')) {
                this.triggerSave();
            }
        });

        // Keyboard shortcut Ctrl+S
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.triggerSave();
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav-actions')) {
                document.getElementById('theme-dropdown')?.classList.remove('show');
                document.getElementById('export-dropdown')?.classList.remove('show');
            }
            if (!e.target.closest('.user-widget')) {
                document.getElementById('user-dropdown')?.classList.remove('show');
            }
        });

        // Track changes for autosave
        document.addEventListener('input', () => {
            this.unsavedChanges = true;
            this.updateSaveIndicator('unsaved');
        });
    },

    // Trigger save
    triggerSave() {
        window.dispatchEvent(new CustomEvent('plania:save'));
        this.updateSaveIndicator('saving');
    },

    // Handle export
    handleExport(type) {
        const project = this.getCurrentProject();
        if (!project) {
            alert('Selecciona un proyecto primero');
            return;
        }

        if (type === 'pdf') {
            this.showExportModal(project);
        } else if (type === 'csv') {
            this.exportCSV(project);
        }
    },

    // Available modules for PDF export
    exportModules: [
        { id: 'portada', label: '📋 Portada y Presentación', checked: true },
        { id: 'resumen', label: '💡 Resumen Ejecutivo', checked: true },
        { id: 'perfil', label: '👤 Perfil del Emprendedor', checked: true },
        { id: 'mercado', label: '📊 Estudio de Mercado', checked: true },
        { id: 'produccion', label: '🏭 Producción y Productos', checked: true },
        { id: 'marketing', label: '📣 Marketing y Ventas', checked: true },
        { id: 'financiero', label: '💰 Plan Financiero', checked: true },
        { id: 'impacto', label: '🌟 Impacto Social/Económico', checked: true },
        { id: 'canvas', label: '🎨 Business Model Canvas', checked: false },
        { id: 'identidad', label: '🏷️ Identidad de Marca', checked: false },
        { id: 'clientes', label: '👥 Clientes', checked: false },
        { id: 'encuestas', label: '📝 Encuestas', checked: false },
        { id: 'operaciones', label: '⚙️ Operaciones', checked: false },
        { id: 'kpis', label: '🎯 KPIs', checked: false },
    ],

    // Show export modal
    showExportModal(project) {
        // Remove existing modal if any
        document.getElementById('export-modal')?.remove();

        const modal = document.createElement('div');
        modal.id = 'export-modal';
        modal.innerHTML = `
            <div class="export-modal-overlay"></div>
            <div class="export-modal-content">
                <h2>📤 Exportar PDF</h2>
                <p style="color: var(--text); opacity: 0.7;">Selecciona los módulos a incluir:</p>
                
                <div class="export-modal-actions-top">
                    <button type="button" class="btn-select-all">✅ Seleccionar Todo</button>
                    <button type="button" class="btn-deselect-all">❌ Deseleccionar Todo</button>
                </div>
                
                <div class="export-modules-list">
                    ${this.exportModules.map(m => `
                        <label class="export-module-item">
                            <input type="checkbox" name="module" value="${m.id}" ${m.checked ? 'checked' : ''}>
                            <span>${m.label}</span>
                        </label>
                    `).join('')}
                </div>
                
                <div class="export-modal-actions">
                    <button type="button" class="btn-cancel">Cancelar</button>
                    <button type="button" class="btn-export-confirm">📄 Generar PDF</button>
                </div>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .export-modal-overlay {
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.6); z-index: 9998;
            }
            .export-modal-content {
                position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                background: var(--surface); border-radius: 12px; padding: 24px;
                min-width: 400px; max-width: 90vw; max-height: 80vh; overflow-y: auto;
                z-index: 9999; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            .export-modal-content h2 { margin: 0 0 10px; color: var(--text); }
            .export-modal-actions-top { display: flex; gap: 10px; margin: 15px 0; }
            .export-modal-actions-top button {
                padding: 6px 12px; border: 1px solid var(--primary); border-radius: 6px;
                background: transparent; color: var(--primary); cursor: pointer; font-size: 12px;
            }
            .export-modules-list {
                display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
                max-height: 300px; overflow-y: auto; padding: 10px 0;
            }
            .export-module-item {
                display: flex; align-items: center; gap: 8px; padding: 8px 12px;
                background: var(--bg); border-radius: 8px; cursor: pointer;
                transition: background 0.2s;
            }
            .export-module-item:hover { background: var(--primary); color: white; }
            .export-module-item input { width: 18px; height: 18px; cursor: pointer; }
            .export-modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
            .export-modal-actions button { padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
            .btn-cancel { background: transparent; border: 1px solid var(--text); color: var(--text); }
            .btn-export-confirm { background: var(--primary); border: none; color: white; }
        `;
        modal.appendChild(style);
        document.body.appendChild(modal);

        // Event handlers
        modal.querySelector('.export-modal-overlay').onclick = () => modal.remove();
        modal.querySelector('.btn-cancel').onclick = () => modal.remove();
        modal.querySelector('.btn-select-all').onclick = () => {
            modal.querySelectorAll('input[name="module"]').forEach(cb => cb.checked = true);
        };
        modal.querySelector('.btn-deselect-all').onclick = () => {
            modal.querySelectorAll('input[name="module"]').forEach(cb => cb.checked = false);
        };
        modal.querySelector('.btn-export-confirm').onclick = () => {
            const selected = Array.from(modal.querySelectorAll('input[name="module"]:checked'))
                .map(cb => cb.value);
            if (selected.length === 0) {
                alert('Selecciona al menos un módulo');
                return;
            }
            window.open(`export_pdf.html?id=${project.id_proyecto}&modules=${selected.join(',')}`, '_blank');
            modal.remove();
        };
    },

    // Export to CSV
    exportCSV(project) {
        // Financial data CSV
        const headers = ['Campo', 'Valor'];
        const rows = [
            ['Nombre del Negocio', project.a1_nombre_negocio || ''],
            ['Emprendedor', project.a2_nombre_emprendedor || ''],
            ['Monto Solicitado', project.b5_monto_solicitado || 0],
            ['Costos Fijos Mensuales', project.g5_costos_fijos_mensuales || 0],
            ['Inversión Inicial', project.g8_inversion_inicial || 0],
        ];

        // Try to parse financial JSON if exists
        try {
            const finData = JSON.parse(project.g9_flujo_efectivo_json || '{}');
            if (finData.monthlyUnits) {
                const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
                finData.monthlyUnits.forEach((units, i) => {
                    rows.push([`Unidades ${months[i]}`, units]);
                });
            }
        } catch (e) { }

        const csv = [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${project.a1_nombre_negocio || 'proyecto'}_financiero.csv`;
        a.click();
        URL.revokeObjectURL(url);
    },

    // Update save indicator
    updateSaveIndicator(status) {
        const indicator = document.getElementById('save-indicator');
        if (!indicator) return;

        switch (status) {
            case 'saving':
                indicator.innerHTML = '⏳ Guardando...';
                indicator.className = 'save-indicator saving';
                break;
            case 'saved':
                indicator.innerHTML = '✅ Guardado';
                indicator.className = 'save-indicator saved';
                this.unsavedChanges = false;
                setTimeout(() => {
                    indicator.innerHTML = '';
                    indicator.className = 'save-indicator';
                }, 3000);
                break;
            case 'unsaved':
                indicator.innerHTML = '●';
                indicator.className = 'save-indicator unsaved';
                break;
            case 'error':
                indicator.innerHTML = '❌ Error';
                indicator.className = 'save-indicator error';
                break;
        }
    },

    // Start autosave
    startAutoSave() {
        if (this.autoSaveInterval) clearInterval(this.autoSaveInterval);

        this.autoSaveInterval = setInterval(() => {
            if (this.unsavedChanges) {
                this.triggerSave();
            }
        }, 30000); // Every 30 seconds
    },

    // Called by modules after successful save
    notifySaved() {
        this.updateSaveIndicator('saved');
    },

    // Called by modules on save error
    notifySaveError() {
        this.updateSaveIndicator('error');
    },

    // Utility: Format currency
    formatCurrency(value) {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN',
            minimumFractionDigits: 0,
        }).format(value || 0);
    },

    // Utility: Format date
    formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        return new Date(dateStr).toLocaleDateString('es-MX', {
            day: '2-digit', month: 'short', year: 'numeric'
        });
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => PlanIA.init());
