<?php
/**
 * ================================================================================
 * PROYECTO: CAFES - Sistema de Planes de Negocio
 * ARCHIVO:  public/export_pdf.php
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: GPL-2.0-or-later
 * ================================================================================
 */

/**
 * =================================================================================
 * PROYECTO: PlanIA (Backend)
 * ARCHIVO: public/export_pdf.php
 * COPYRIGHT: © 2026 Fondo Thoth AC.
 * LICENCIA: GPLv2
 * DESCRIPCIÓN: Exportador de Plan de Negocios a PDF usando HTML template
 *              Con selección de módulos
 * =================================================================================
 */

// Set UTF-8 encoding
header('Content-Type: text/html; charset=utf-8');
mb_internal_encoding('UTF-8');

// Load database configuration
$config = require_once __DIR__ . '/../config/database.php';

// Get project ID and modules
$projectId = $_GET['id'] ?? null;
$modulesParam = $_GET['modules'] ?? 'portada,resumen,mercado,produccion,financiero,impacto';
$selectedModules = array_map('trim', explode(',', $modulesParam));

if (!$projectId) {
    die('Error: ID de proyecto requerido');
}

// Helper function to check if module is selected
function showModule($id)
{
    global $selectedModules;
    return in_array($id, $selectedModules);
}

// Connect to database
try {
    $dsn = "mysql:host={$config['host']};dbname={$config['database']};charset=utf8mb4";
    $pdo = new PDO($dsn, $config['user'], $config['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
    ]);
} catch (PDOException $e) {
    die('Error de conexión a base de datos');
}

// Fetch project
$stmt = $pdo->prepare("SELECT * FROM proyectos_negocio WHERE id_proyecto = :id");
$stmt->execute(['id' => $projectId]);
$project = $stmt->fetch();

if (!$project) {
    die('Proyecto no encontrado');
}

// Parse JSON fields safely
function safeJsonDecode($json)
{
    if (empty($json))
        return [];
    $decoded = json_decode($json, true);
    return is_array($decoded) ? $decoded : [];
}

$bom = safeJsonDecode($project['e3_productos_bom_json'] ?? '');
$competitors = safeJsonDecode($project['d3_competidores_json'] ?? '');
$canalesVenta = safeJsonDecode($project['f3_canales_venta'] ?? '');
$identidad = safeJsonDecode($project['i7_identidad_json'] ?? '');
$clientes = safeJsonDecode($project['i1_clientes_json'] ?? '');
$encuestas = safeJsonDecode($project['i2_encuestas_json'] ?? '');
$marketingData = safeJsonDecode($project['i3_marketing_json'] ?? '');
$operaciones = safeJsonDecode($project['i4_operaciones_json'] ?? '');

// Format numbers
$montoSolicitado = number_format($project['b5_monto_solicitado'] ?? 0, 2);
$inversionInicial = number_format($project['g8_inversion_inicial'] ?? 0, 2);
$costosFijos = number_format($project['g5_costos_fijos_mensuales'] ?? 0, 2);
$date = date('d/m/Y H:i');

// Escape function that handles UTF-8 properly
function e($str)
{
    return htmlspecialchars($str ?? '', ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

// Build products table
$productsHtml = '';
if (!empty($bom)) {
    $productsHtml = '<h4>Productos (BOM):</h4><table><tr><th>#</th><th>Producto</th><th>Precio Venta</th></tr>';
    foreach ($bom as $i => $product) {
        $precio = number_format($product['precio_venta'] ?? 0, 2);
        $nombre = e($product['producto'] ?? '');
        $productsHtml .= "<tr><td>" . ($i + 1) . "</td><td>{$nombre}</td><td>\${$precio}</td></tr>";
    }
    $productsHtml .= '</table>';
}

// Build competitors table
$competitorsHtml = '';
if (!empty($competitors)) {
    $competitorsHtml = '<h4>Competidores Identificados:</h4><table><tr><th>Nombre</th><th>Actividad</th><th>Colonia</th></tr>';
    foreach (array_slice($competitors, 0, 5) as $comp) {
        $competitorsHtml .= "<tr><td>" . e($comp['nombre'] ?? '') . "</td><td>" . e($comp['actividad'] ?? '') . "</td><td>" . e($comp['colonia'] ?? '') . "</td></tr>";
    }
    $competitorsHtml .= '</table>';
}

// Prepare all text fields
$nombreNegocio = e($project['a1_nombre_negocio'] ?? '');
$nombreEmprendedor = e($project['a2_nombre_emprendedor'] ?? '');
$cartaPresentacion = nl2br(e($project['a4_carta_presentacion'] ?? ''));
$descripcionNegocio = nl2br(e($project['b1_descripcion_negocio'] ?? ''));
$problemaOportunidad = nl2br(e($project['b2_problema_oportunidad'] ?? ''));
$propuestaValor = nl2br(e($project['b3_propuesta_valor'] ?? ''));
$clienteObjetivo = nl2br(e($project['b4_cliente_objetivo_resumen'] ?? ''));
$experienciaPrevia = nl2br(e($project['c1_experiencia_previa'] ?? ''));
$motivacion = nl2br(e($project['c2_motivacion'] ?? ''));
$disponibilidad = e($project['c3_disponibilidad_tiempo'] ?? '');
$segmentoCliente = nl2br(e($project['d1_segmento_cliente'] ?? ''));
$necesidadesGustos = nl2br(e($project['d2_necesidades_gustos'] ?? ''));
$ventajaCompetitiva = nl2br(e($project['d5_ventaja_competitiva'] ?? ''));
$direccion = e($project['d8_direccion_formateada'] ?? '');
$procesoProduccion = nl2br(e($project['e1_proceso_produccion'] ?? ''));
$capacidadProduccion = e($project['e2_capacidad_produccion'] ?? '');
$identidadMarca = nl2br(e($project['f1_identidad_marca'] ?? ''));
$estrategiaPrecios = nl2br(e($project['f2_estrategia_precios'] ?? ''));
$estrategiaPromocion = nl2br(e($project['f4_estrategia_promocion'] ?? ''));
$impactoSocial = nl2br(e($project['h1_impacto_social'] ?? ''));
$impactoEconomico = nl2br(e($project['h2_impacto_economico'] ?? ''));

?>
<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <title>Plan de Negocios - <?= $nombreNegocio ?></title>
    <style>
        body {
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.6;
            color: #333;
            margin: 20px;
        }

        .header {
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #2563eb;
            font-size: 28px;
            margin: 0;
        }

        .header p {
            color: #666;
            margin: 5px 0;
        }

        .section {
            margin-bottom: 25px;
            page-break-inside: avoid;
        }

        .section-title {
            background: #2563eb;
            color: white;
            padding: 8px 15px;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .section-content {
            padding: 10px 15px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
        }

        .row {
            display: flex;
            margin-bottom: 10px;
        }

        .label {
            font-weight: bold;
            width: 200px;
            color: #475569;
        }

        .value {
            flex: 1;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th,
        td {
            border: 1px solid #e2e8f0;
            padding: 8px;
            text-align: left;
        }

        th {
            background: #e2e8f0;
            font-weight: bold;
        }

        .highlight {
            background: #dbeafe;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }

        .highlight-value {
            font-size: 24px;
            font-weight: bold;
            color: #2563eb;
        }

        .footer {
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 10px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
        }

        .canvas-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-top: 10px;
        }

        .canvas-box {
            border: 1px solid #e2e8f0;
            padding: 10px;
            background: #f8fafc;
            min-height: 80px;
        }

        .canvas-box h5 {
            margin: 0 0 5px;
            color: #2563eb;
            font-size: 11px;
        }

        .tag {
            display: inline-block;
            background: #2563eb;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            margin: 2px;
        }
    </style>
</head>

<body>

    <div class="header">
        <h1><?= $nombreNegocio ?></h1>
        <p><strong>Emprendedor:</strong> <?= $nombreEmprendedor ?></p>
        <p>Generado: <?= $date ?></p>
    </div>

    <?php if (showModule('portada')): ?>
        <div class="section">
            <div class="section-title">📋 A. PORTADA</div>
            <div class="section-content">
                <div class="row"><span class="label">Nombre del Negocio:</span><span
                        class="value"><?= $nombreNegocio ?></span></div>
                <div class="row"><span class="label">Emprendedor:</span><span class="value"><?= $nombreEmprendedor ?></span>
                </div>
                <div class="row"><span class="label">Carta de Presentación:</span></div>
                <p><?= $cartaPresentacion ?></p>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('resumen')): ?>
        <div class="section">
            <div class="section-title">💡 B. RESUMEN EJECUTIVO</div>
            <div class="section-content">
                <div class="row"><span class="label">Descripción del Negocio:</span></div>
                <p><?= $descripcionNegocio ?></p>
                <div class="row"><span class="label">Problema/Oportunidad:</span></div>
                <p><?= $problemaOportunidad ?></p>
                <div class="row"><span class="label">Propuesta de Valor:</span></div>
                <p><?= $propuestaValor ?></p>
                <div class="row"><span class="label">Cliente Objetivo:</span></div>
                <p><?= $clienteObjetivo ?></p>
                <div class="row">
                    <span class="label">Monto Solicitado:</span>
                    <span class="value"><strong>$<?= $montoSolicitado ?> MXN</strong></span>
                </div>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('perfil')): ?>
        <div class="section">
            <div class="section-title">👤 C. PERFIL DEL EMPRENDEDOR</div>
            <div class="section-content">
                <div class="row"><span class="label">Experiencia Previa:</span></div>
                <p><?= $experienciaPrevia ?></p>
                <div class="row"><span class="label">Motivación:</span></div>
                <p><?= $motivacion ?></p>
                <div class="row"><span class="label">Disponibilidad de Tiempo:</span><span
                        class="value"><?= $disponibilidad ?></span></div>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('mercado')): ?>
        <div class="section">
            <div class="section-title">📊 D. ESTUDIO DE MERCADO</div>
            <div class="section-content">
                <div class="row"><span class="label">Segmento de Cliente:</span></div>
                <p><?= $segmentoCliente ?></p>
                <div class="row"><span class="label">Necesidades y Gustos:</span></div>
                <p><?= $necesidadesGustos ?></p>
                <div class="row"><span class="label">Ventaja Competitiva:</span></div>
                <p><?= $ventajaCompetitiva ?></p>
                <div class="row"><span class="label">Ubicación:</span><span class="value"><?= $direccion ?></span></div>
                <?= $competitorsHtml ?>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('produccion')): ?>
        <div class="section">
            <div class="section-title">🏭 E. PRODUCCIÓN Y PRODUCTOS</div>
            <div class="section-content">
                <div class="row"><span class="label">Proceso de Producción:</span></div>
                <p><?= $procesoProduccion ?></p>
                <div class="row"><span class="label">Capacidad:</span><span class="value"><?= $capacidadProduccion ?></span>
                </div>
                <?= $productsHtml ?>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('marketing')): ?>
        <div class="section">
            <div class="section-title">📣 F. MARKETING Y VENTAS</div>
            <div class="section-content">
                <div class="row"><span class="label">Identidad de Marca:</span></div>
                <p><?= $identidadMarca ?></p>
                <div class="row"><span class="label">Estrategia de Precios:</span></div>
                <p><?= $estrategiaPrecios ?></p>
                <div class="row"><span class="label">Canales de Venta:</span></div>
                <p>
                    <?php
                    if (is_array($canalesVenta)) {
                        foreach ($canalesVenta as $canal) {
                            echo "<span class='tag'>" . e($canal) . "</span> ";
                        }
                    } else {
                        echo e($canalesVenta);
                    }
                    ?>
                </p>
                <div class="row"><span class="label">Estrategia de Promoción:</span></div>
                <p><?= $estrategiaPromocion ?></p>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('financiero')): ?>
        <div class="section">
            <div class="section-title">💰 G. PLAN FINANCIERO</div>
            <div class="section-content">
                <div class="highlight">
                    <p>Inversión Inicial</p>
                    <div class="highlight-value">$<?= $inversionInicial ?> MXN</div>
                </div>
                <br>
                <div class="row">
                    <span class="label">Costos Fijos Mensuales:</span>
                    <span class="value">$<?= $costosFijos ?> MXN</span>
                </div>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('impacto')): ?>
        <div class="section">
            <div class="section-title">🌟 H. IMPACTO</div>
            <div class="section-content">
                <div class="row"><span class="label">Impacto Social:</span></div>
                <p><?= $impactoSocial ?></p>
                <div class="row"><span class="label">Impacto Económico:</span></div>
                <p><?= $impactoEconomico ?></p>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('canvas')): ?>
        <div class="section" style="page-break-before: always;">
            <div class="section-title">🎨 BUSINESS MODEL CANVAS</div>
            <div class="section-content">
                <p><em>El Business Model Canvas completo se genera desde el módulo Canvas de la aplicación.</em></p>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('identidad')): ?>
        <div class="section">
            <div class="section-title">🏷️ IDENTIDAD DE MARCA</div>
            <div class="section-content">
                <?php if (!empty($identidad)): ?>
                    <?php foreach ($identidad as $key => $value): ?>
                        <div class="row"><span class="label"><?= e(ucfirst($key)) ?>:</span><span
                                class="value"><?= e($value) ?></span></div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <p><em>Sin información de identidad registrada.</em></p>
                <?php endif; ?>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('clientes')): ?>
        <div class="section">
            <div class="section-title">👥 CLIENTES</div>
            <div class="section-content">
                <?php if (!empty($clientes)): ?>
                    <table>
                        <tr>
                            <th>Nombre</th>
                            <th>Contacto</th>
                            <th>Notas</th>
                        </tr>
                        <?php foreach (array_slice($clientes, 0, 10) as $cliente): ?>
                            <tr>
                                <td><?= e($cliente['nombre'] ?? '') ?></td>
                                <td><?= e($cliente['contacto'] ?? '') ?></td>
                                <td><?= e($cliente['notas'] ?? '') ?></td>
                            </tr>
                        <?php endforeach; ?>
                    </table>
                <?php else: ?>
                    <p><em>Sin clientes registrados.</em></p>
                <?php endif; ?>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('encuestas')): ?>
        <div class="section">
            <div class="section-title">📝 ENCUESTAS</div>
            <div class="section-content">
                <?php if (!empty($encuestas)): ?>
                    <p>Total de respuestas: <?= count($encuestas) ?></p>
                <?php else: ?>
                    <p><em>Sin encuestas registradas.</em></p>
                <?php endif; ?>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('operaciones')): ?>
        <div class="section">
            <div class="section-title">⚙️ OPERACIONES</div>
            <div class="section-content">
                <?php if (!empty($operaciones)): ?>
                    <?php foreach ($operaciones as $key => $value): ?>
                        <div class="row"><span class="label"><?= e(ucfirst($key)) ?>:</span><span
                                class="value"><?= e($value) ?></span></div>
                    <?php endforeach; ?>
                <?php else: ?>
                    <p><em>Sin información de operaciones registrada.</em></p>
                <?php endif; ?>
            </div>
        </div>
    <?php endif; ?>

    <?php if (showModule('kpis')): ?>
        <div class="section">
            <div class="section-title">🎯 KPIs</div>
            <div class="section-content">
                <p><em>Los KPIs se calculan automáticamente desde el dashboard de KPIs.</em></p>
            </div>
        </div>
    <?php endif; ?>

    <div class="footer">
        <p>Documento generado por PlanIA © 2026 Fondo Thoth AC</p>
        <p>Este documento es confidencial y para uso exclusivo del destinatario.</p>
    </div>

    <script>window.print();</script>
</body>

</html>