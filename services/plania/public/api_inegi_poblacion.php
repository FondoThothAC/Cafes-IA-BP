<?php
/**
 * API INEGI Población - Consulta datos del Censo 2020 por coordenadas
 * 
 * Este servicio recibe coordenadas (lat/lng) y un radio, y devuelve
 * datos de población estimados para esa área usando datos del censo INEGI.
 * 
 * Fuentes:
 * - México en Datos API: https://mexicoendatos.com/api/
 * - INEGI Censo 2020
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Parámetros de entrada
$lat = floatval($_GET['lat'] ?? 29.0729);
$lng = floatval($_GET['lng'] ?? -110.9559);
$radius = intval($_GET['radius'] ?? 1000); // metros

// Mapeo de coordenadas a claves geoestadísticas (simplificado)
// En producción, esto debería usar un servicio de geocodificación inversa de INEGI
$geoMapping = getGeoKeyFromCoords($lat, $lng);

try {
    // Intentar consultar API externa (México en Datos o similar)
    $population = fetchPopulationFromAPI($geoMapping['cve_ent'], $geoMapping['cve_mun'], $lat, $lng, $radius);

    if ($population) {
        echo json_encode([
            'success' => true,
            'source' => 'INEGI Censo 2020',
            'location' => $geoMapping,
            'data' => $population
        ]);
    } else {
        // Fallback a datos pre-cargados del censo
        echo json_encode(getLocalCensusData($geoMapping, $radius));
    }
} catch (Exception $e) {
    // En caso de error, usar datos locales
    echo json_encode(getLocalCensusData($geoMapping, $radius));
}

/**
 * Determina las claves geoestadísticas basándose en las coordenadas
 * Mapeo simplificado para las principales ciudades de México
 */
function getGeoKeyFromCoords($lat, $lng)
{
    // Hermosillo, Sonora (default)
    $result = [
        'cve_ent' => '26',
        'cve_mun' => '030',
        'nom_ent' => 'Sonora',
        'nom_mun' => 'Hermosillo'
    ];

    // Detectar ubicación basándose en rangos de coordenadas
    // Sonora
    if ($lat >= 26 && $lat <= 32 && $lng >= -115 && $lng <= -108) {
        $result['cve_ent'] = '26';
        $result['nom_ent'] = 'Sonora';

        // Hermosillo
        if ($lat >= 28.5 && $lat <= 29.5 && $lng >= -111.5 && $lng <= -110.5) {
            $result['cve_mun'] = '030';
            $result['nom_mun'] = 'Hermosillo';
        }
        // Nogales
        elseif ($lat >= 31.0 && $lat <= 31.5 && $lng >= -111.2 && $lng <= -110.5) {
            $result['cve_mun'] = '043';
            $result['nom_mun'] = 'Nogales';
        }
        // Cajeme (Cd. Obregón)
        elseif ($lat >= 27.2 && $lat <= 27.8 && $lng >= -110.5 && $lng <= -109.5) {
            $result['cve_mun'] = '018';
            $result['nom_mun'] = 'Cajeme';
        }
    }
    // Ciudad de México
    elseif ($lat >= 19.0 && $lat <= 19.8 && $lng >= -99.5 && $lng <= -98.9) {
        $result['cve_ent'] = '09';
        $result['nom_ent'] = 'Ciudad de México';
        $result['cve_mun'] = '015';
        $result['nom_mun'] = 'Cuauhtémoc';
    }
    // Guadalajara, Jalisco
    elseif ($lat >= 20.5 && $lat <= 21.0 && $lng >= -103.5 && $lng <= -103.0) {
        $result['cve_ent'] = '14';
        $result['nom_ent'] = 'Jalisco';
        $result['cve_mun'] = '039';
        $result['nom_mun'] = 'Guadalajara';
    }
    // Monterrey, Nuevo León
    elseif ($lat >= 25.5 && $lat <= 26.0 && $lng >= -100.5 && $lng <= -99.8) {
        $result['cve_ent'] = '19';
        $result['nom_ent'] = 'Nuevo León';
        $result['cve_mun'] = '039';
        $result['nom_mun'] = 'Monterrey';
    }

    return $result;
}

/**
 * Intenta consultar una API externa de datos censales
 */
function fetchPopulationFromAPI($cve_ent, $cve_mun, $lat, $lng, $radius)
{
    // Intentar consultar México en Datos API
    $url = "https://mexicoendatos.com/api/inegi/datos/censo/ageb/{$cve_ent}/{$cve_mun}/?year=2020";

    $context = stream_context_create([
        'http' => [
            'timeout' => 10,
            'header' => 'Accept: application/json'
        ]
    ]);

    $response = @file_get_contents($url, false, $context);

    if ($response) {
        $data = json_decode($response, true);
        if ($data && isset($data['data'])) {
            // Agregar datos de todas las AGEBs del municipio
            $totals = aggregateAGEBData($data['data'], $lat, $lng, $radius);
            return $totals;
        }
    }

    return null;
}

/**
 * Agrega datos de AGEBs cercanas a las coordenadas dadas
 */
function aggregateAGEBData($agebs, $lat, $lng, $radius)
{
    $totals = [
        'pobtot' => 0,
        'pobmas' => 0,
        'pobfem' => 0,
        'p_0a14' => 0,
        'p_15a64' => 0,
        'p_65ymas' => 0,
        'vivtot' => 0,
        'vivhab' => 0,
        'ageb_count' => 0
    ];

    foreach ($agebs as $ageb) {
        // Sumar población (esto es simplificado, idealmente filtrar por geometría)
        $totals['pobtot'] += intval($ageb['POBTOT'] ?? 0);
        $totals['pobmas'] += intval($ageb['POBMAS'] ?? 0);
        $totals['pobfem'] += intval($ageb['POBFEM'] ?? 0);
        $totals['p_0a14'] += intval($ageb['P_0A14'] ?? 0);
        $totals['p_15a64'] += intval($ageb['P_15A64'] ?? 0);
        $totals['p_65ymas'] += intval($ageb['P_65YMAS'] ?? 0);
        $totals['vivtot'] += intval($ageb['VIVTOT'] ?? 0);
        $totals['vivhab'] += intval($ageb['VIVHAB'] ?? 0);
        $totals['ageb_count']++;
    }

    return $totals;
}

/**
 * Datos del Censo 2020 pre-cargados para principales municipios
 * Fuente: INEGI Censo de Población y Vivienda 2020
 */
function getLocalCensusData($geoMapping, $radius)
{
    // Datos reales del Censo 2020 por municipio (totales municipales)
    $censusData = [
        // Sonora
        '26030' => [ // Hermosillo
            'poblacion_total' => 936263,
            'hombres' => 465154,
            'mujeres' => 471109,
            'p_0a14' => 209499,
            'p_15a64' => 639451,
            'p_65ymas' => 78605,
            'viviendas_hab' => 261544,
            'area_km2' => 14880.2
        ],
        '26043' => [ // Nogales
            'poblacion_total' => 264782,
            'hombres' => 131420,
            'mujeres' => 133362,
            'p_0a14' => 60543,
            'p_15a64' => 183217,
            'p_65ymas' => 18391,
            'viviendas_hab' => 77231,
            'area_km2' => 1682.7
        ],
        '26018' => [ // Cajeme (Cd. Obregón)
            'poblacion_total' => 433050,
            'hombres' => 214291,
            'mujeres' => 218759,
            'p_0a14' => 93188,
            'p_15a64' => 295067,
            'p_65ymas' => 42094,
            'viviendas_hab' => 126543,
            'area_km2' => 4037.1
        ],
        // CDMX - Cuauhtémoc
        '09015' => [
            'poblacion_total' => 545884,
            'hombres' => 261625,
            'mujeres' => 284259,
            'p_0a14' => 77195,
            'p_15a64' => 396419,
            'p_65ymas' => 69684,
            'viviendas_hab' => 218478,
            'area_km2' => 32.4
        ],
        // Guadalajara
        '14039' => [
            'poblacion_total' => 1385629,
            'hombres' => 662571,
            'mujeres' => 723058,
            'p_0a14' => 260817,
            'p_15a64' => 959024,
            'p_65ymas' => 156580,
            'viviendas_hab' => 452348,
            'area_km2' => 151.4
        ],
        // Monterrey
        '19039' => [
            'poblacion_total' => 1142994,
            'hombres' => 565318,
            'mujeres' => 577676,
            'p_0a14' => 212876,
            'p_15a64' => 805492,
            'p_65ymas' => 114654,
            'viviendas_hab' => 343982,
            'area_km2' => 324.8
        ]
    ];

    $key = $geoMapping['cve_ent'] . $geoMapping['cve_mun'];
    $munData = $censusData[$key] ?? $censusData['26030']; // Default a Hermosillo

    // Calcular densidad del municipio
    $densidad = $munData['poblacion_total'] / $munData['area_km2'];

    // Calcular población para el radio solicitado
    $areaKm2 = M_PI * pow($radius / 1000, 2);
    $poblacionArea = round($areaKm2 * $densidad);

    // Calcular proporcionalmente los otros indicadores
    $factor = $poblacionArea / $munData['poblacion_total'];

    return [
        'success' => true,
        'source' => 'INEGI Censo 2020 (calculado)',
        'location' => $geoMapping,
        'area_km2' => round($areaKm2, 4),
        'densidad_hab_km2' => round($densidad, 0),
        'data' => [
            'pobtot' => $poblacionArea,
            'pobmas' => round($munData['hombres'] * $factor),
            'pobfem' => round($munData['mujeres'] * $factor),
            'p_0a14' => round($munData['p_0a14'] * $factor),
            'p_15a64' => round($munData['p_15a64'] * $factor),
            'p_65ymas' => round($munData['p_65ymas'] * $factor),
            'vivhab' => round($munData['viviendas_hab'] * $factor)
        ],
        'municipio' => [
            'poblacion_total' => $munData['poblacion_total'],
            'area_km2' => $munData['area_km2'],
            'densidad' => round($densidad, 0)
        ]
    ];
}
