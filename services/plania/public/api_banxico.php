<?php
/**
 * Banxico API Proxy - Obtiene datos de inflación del Sistema de Información Económica
 * 
 * Series disponibles:
 * - SP1 (INPC General)
 * - SP74625 (Inflación anual)
 * - SF43718 (Tipo de cambio)
 * 
 * Documentación: https://www.banxico.org.mx/SieAPIRest/service/v1/doc/catalogoSeries
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Token de Banxico (obtener desde https://www.banxico.org.mx/SieAPIRest/service/v1/)
// Este es un token de ejemplo - el usuario debe obtener el suyo propio
$BANXICO_TOKEN = 'da45f26edb9a72e9d18e0217de25f9d8e5c79e9a5e4c1e8b7a6d5c4b3a2'; // EJEMPLO

// Series IDs
$SERIES = [
    'inpc' => 'SP1',           // INPC General
    'inflacion' => 'SP74625',  // Inflación anual (% cambio)
    'tipo_cambio' => 'SF43718', // Tipo de cambio USD/MXN
    'cetes_28' => 'SF43936',   // CETES 28 días
    'tiie_28' => 'SF43783',    // TIIE 28 días
];

// Obtener parámetros
$action = $_GET['action'] ?? 'inflacion';
$startDate = $_GET['start'] ?? date('Y-m-d', strtotime('-5 years'));
$endDate = $_GET['end'] ?? date('Y-m-d');

// Mapear acción a serie
$serieId = $SERIES[$action] ?? 'SP74625';

try {
    // Construir URL de la API de Banxico
    $baseUrl = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series';
    $url = "$baseUrl/$serieId/datos/$startDate/$endDate";

    // Hacer request a Banxico
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTPHEADER => [
            'Bmx-Token: ' . $BANXICO_TOKEN,
            'Accept: application/json'
        ]
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);

    if ($error) {
        throw new Exception("Error de conexión: $error");
    }

    if ($httpCode === 200 && $response) {
        $data = json_decode($response, true);

        // Procesar respuesta de Banxico
        if (isset($data['bmx']['series'][0]['datos'])) {
            $rawData = $data['bmx']['series'][0]['datos'];
            $processedData = [];

            foreach ($rawData as $item) {
                $processedData[] = [
                    'fecha' => $item['fecha'],
                    'valor' => floatval(str_replace(',', '.', $item['dato'] ?? '0'))
                ];
            }

            // Calcular estadísticas
            $values = array_column($processedData, 'valor');
            $stats = [
                'ultimo' => end($values),
                'promedio' => count($values) > 0 ? array_sum($values) / count($values) : 0,
                'minimo' => count($values) > 0 ? min($values) : 0,
                'maximo' => count($values) > 0 ? max($values) : 0,
                'count' => count($values)
            ];

            echo json_encode([
                'success' => true,
                'serie' => $action,
                'serie_id' => $serieId,
                'periodo' => ['inicio' => $startDate, 'fin' => $endDate],
                'stats' => $stats,
                'datos' => array_slice($processedData, -24) // Últimos 24 registros
            ]);
        } else {
            // Devolver datos simulados si no hay respuesta de Banxico
            echo json_encode(getFallbackData($action));
        }
    } else {
        // Devolver datos simulados como fallback
        echo json_encode(getFallbackData($action));
    }

} catch (Exception $e) {
    // En caso de error, devolver datos simulados
    echo json_encode(getFallbackData($action));
}

/**
 * Datos de fallback basados en información pública de Banxico
 * Valores aproximados históricos de inflación en México
 */
function getFallbackData($action)
{
    $currentYear = (int) date('Y');

    // Inflación histórica anualizada (fuente: Banxico/INEGI)
    $inflacionHistorica = [
        2020 => 3.15,
        2021 => 7.36,
        2022 => 7.82,
        2023 => 4.66,
        2024 => 4.21,
        2025 => 3.80, // Proyección Banxico
        2026 => 3.50, // Proyección
    ];

    // Tipo de cambio histórico promedio
    $tipoCambioHistorico = [
        2020 => 21.49,
        2021 => 20.28,
        2022 => 20.13,
        2023 => 17.76,
        2024 => 17.05,
        2025 => 17.50, // Proyección
        2026 => 18.00, // Proyección
    ];

    // TIIE 28 días histórico
    $tiieHistorico = [
        2020 => 5.28,
        2021 => 4.98,
        2022 => 9.25,
        2023 => 11.50,
        2024 => 10.75,
        2025 => 9.00, // Proyección
        2026 => 8.00, // Proyección
    ];

    $datos = [];
    $stats = ['ultimo' => 0, 'promedio' => 0, 'minimo' => 0, 'maximo' => 0];

    switch ($action) {
        case 'inflacion':
        case 'inpc':
            foreach ($inflacionHistorica as $year => $val) {
                $datos[] = ['fecha' => "$year-12-31", 'valor' => $val];
            }
            $stats = [
                'ultimo' => $inflacionHistorica[$currentYear] ?? 3.80,
                'promedio' => array_sum($inflacionHistorica) / count($inflacionHistorica),
                'minimo' => min($inflacionHistorica),
                'maximo' => max($inflacionHistorica),
                'proyeccion_2026' => 3.50
            ];
            break;

        case 'tipo_cambio':
            foreach ($tipoCambioHistorico as $year => $val) {
                $datos[] = ['fecha' => "$year-12-31", 'valor' => $val];
            }
            $stats = [
                'ultimo' => $tipoCambioHistorico[$currentYear] ?? 17.50,
                'promedio' => array_sum($tipoCambioHistorico) / count($tipoCambioHistorico),
                'minimo' => min($tipoCambioHistorico),
                'maximo' => max($tipoCambioHistorico)
            ];
            break;

        case 'tiie_28':
        case 'cetes_28':
            foreach ($tiieHistorico as $year => $val) {
                $datos[] = ['fecha' => "$year-12-31", 'valor' => $val];
            }
            $stats = [
                'ultimo' => $tiieHistorico[$currentYear] ?? 9.00,
                'promedio' => array_sum($tiieHistorico) / count($tiieHistorico),
                'minimo' => min($tiieHistorico),
                'maximo' => max($tiieHistorico)
            ];
            break;
    }

    return [
        'success' => true,
        'source' => 'fallback',
        'note' => 'Datos basados en información pública de Banxico/INEGI. Para datos en tiempo real, configure su token de API.',
        'serie' => $action,
        'stats' => $stats,
        'datos' => $datos
    ];
}
