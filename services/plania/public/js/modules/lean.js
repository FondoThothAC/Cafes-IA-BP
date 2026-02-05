/**
 * PlanIA - Lean Startup Module
 * Manejo del Tablero de Experimentos y Lógica Lean
 */

const LeanExperiments = {
    // State
    experiments: [],

    init: async function () {
        console.log('🧪 Initializing Lean Experiments...');

        // Cargar datos del proyecto actual
        await this.loadData();
        this.renderBoard();

        // Listeners globales si fuera necesario
    },

    loadData: async function () {
        // En un caso real, esto vendría de la DB del proyecto en 'PlanIA.state'
        // Simularemos una estructura dentro del proyecto para 'lean_data'

        const project = PlanIA.getCurrentProject();
        if (!project) return;

        // Intentar cargar de alguna propiedad custom o simulada
        // Por simplicidad, usaremos localStorage temporalmente asociado al ID del proyecto
        // O idealmente extenderemos el modelo de datos.

        const stored = localStorage.getItem(`plania_lean_${project.id_proyecto}`);
        if (stored) {
            this.experiments = JSON.parse(stored);
        } else {
            // Datos demo si está vacío
            this.experiments = [
                {
                    id: 'exp_' + Date.now(),
                    hypothesis: 'Los usuarios prefieren pagar suscripción mensual',
                    type: 'interview',
                    metric: '> 5 de 10 entrevistados',
                    status: 'backlog',
                    description: 'Entrevistar a 10 dueños de pymes para validar modelo de precios.'
                }
            ];
        }
    },

    saveData: function () {
        const project = PlanIA.getCurrentProject();
        if (!project) {
            alert('No hay proyecto seleccionado');
            return;
        }

        localStorage.setItem(`plania_lean_${project.id_proyecto}`, JSON.stringify(this.experiments));
        // Aquí podríamos llamar a una API real de backend para guardar en MySQL
    },

    renderBoard: function () {
        // Limpiar columnas
        document.querySelectorAll('.kanban-items').forEach(el => el.innerHTML = '');

        const counts = { backlog: 0, progress: 0, analysis: 0, validated: 0, invalidated: 0 };

        this.experiments.forEach(exp => {
            const col = document.getElementById(`col-${exp.status}`);
            if (col) {
                col.appendChild(this.createCardElement(exp));
                counts[exp.status]++;
            }
        });

        // Actualizar contadores
        Object.keys(counts).forEach(key => {
            const el = document.getElementById(`count-${key}`);
            if (el) el.textContent = counts[key];
        });
    },

    createCardElement: function (exp) {
        const div = document.createElement('div');
        div.className = 'experiment-card';
        div.draggable = true;
        div.ondragstart = (e) => this.drag(e);
        div.id = exp.id;

        // Set info for parsing on drop
        div.dataset.id = exp.id;

        const typeLabels = {
            interview: 'Entrevista',
            landing: 'Landing Page',
            concierge: 'Concierge',
            prototype: 'Prototipo',
            ads: 'Anuncios',
            pricing: 'Precio'
        };

        div.innerHTML = `
            <span class="tag tag-${exp.type}">${typeLabels[exp.type] || exp.type}</span>
            <div class="card-title">${exp.hypothesis}</div>
            <div class="card-meta">
               <span>🎯 ${exp.metric || 'Sin métrica'}</span>
            </div>
            <div style="margin-top:0.5rem; text-align:right;">
                <button class="btn-icon" onclick="LeanExperiments.editExperiment('${exp.id}')">✏️</button>
            </div>
        `;
        return div;
    },

    // Modal Actions
    openModal: function (status = 'backlog') {
        document.getElementById('experiment-form').reset();
        document.getElementById('exp-id').value = '';
        document.getElementById('exp-status').value = status;
        document.getElementById('modal-title').textContent = 'Definir Experimento';

        document.getElementById('experiment-modal').classList.add('active');
    },

    editExperiment: function (id) {
        const exp = this.experiments.find(e => e.id === id);
        if (!exp) return;

        document.getElementById('exp-id').value = exp.id;
        document.getElementById('exp-hypothesis').value = exp.hypothesis;
        document.getElementById('exp-type').value = exp.type;
        document.getElementById('exp-metric').value = exp.metric || '';
        document.getElementById('exp-description').value = exp.description || '';
        document.getElementById('exp-learning').value = exp.learning || '';
        document.getElementById('exp-status').value = exp.status;

        document.getElementById('modal-title').textContent = 'Editar Experimento';
        document.getElementById('experiment-modal').classList.add('active');
    },

    closeModal: function () {
        document.getElementById('experiment-modal').classList.remove('active');
    },

    saveExperiment: function (e) {
        e.preventDefault();

        const id = document.getElementById('exp-id').value;
        const hypothesis = document.getElementById('exp-hypothesis').value;
        const type = document.getElementById('exp-type').value;
        const metric = document.getElementById('exp-metric').value;
        const description = document.getElementById('exp-description').value;
        const learning = document.getElementById('exp-learning').value;
        const status = document.getElementById('exp-status').value;

        if (id) {
            // Update
            const index = this.experiments.findIndex(e => e.id === id);
            if (index !== -1) {
                this.experiments[index] = { ...this.experiments[index], hypothesis, type, metric, description, learning };
            }
        } else {
            // Create
            const newExp = {
                id: 'exp_' + Date.now(),
                hypothesis,
                type,
                metric,
                description,
                learning,
                status: status || 'backlog',
                created_at: new Date().toISOString()
            };
            this.experiments.push(newExp);
        }

        this.saveData();
        this.renderBoard();
        this.closeModal();
    },

    // Drag and Drop Logic
    allowDrop: function (ev) {
        ev.preventDefault();
    },

    drag: function (ev) {
        ev.dataTransfer.setData("text", ev.target.id);
    },

    drop: function (ev) {
        ev.preventDefault();
        const data = ev.dataTransfer.getData("text");
        const draggedElement = document.getElementById(data);

        // Find drop target column
        let targetCol = ev.target;
        while (targetCol && !targetCol.classList.contains('kanban-column')) {
            targetCol = targetCol.parentElement;
        }

        if (targetCol && draggedElement) {
            const newStatus = targetCol.dataset.status;
            const expId = draggedElement.dataset.id;

            // Update model
            const exp = this.experiments.find(e => e.id === expId);
            if (exp && exp.status !== newStatus) {
                exp.status = newStatus;
                this.saveData();
                this.renderBoard(); // Re-render to sort/update counts
            }
        }
    }
};

// Auto-init when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Esperar a que el core cargue (pequeño delay o evento)
    setTimeout(() => {
        LeanExperiments.init();
    }, 500);
});
