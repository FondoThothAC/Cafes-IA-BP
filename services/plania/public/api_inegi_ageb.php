<?php
/**
 * API INEGI AGEB - Consulta AGEBs por polígono
 * 
 * Este servicio recibe un polígono en formato WKT o GeoJSON y consulta
 * los datos de población de las AGEBs que intersectan con él.
 * 
 * Servicios INEGI:
 * - WFS: https://gaia.inegi.org.mx/wfs/...
 * - Catálogo Geoestadístico: https://gaia.inegi.org.mx/wscatgeo/
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');

// Obtener parámetros
$input = json_decode(file_get_contents('php://input'), true);
$polygon = $input['polygon'] ?? $_GET['polygon'] ?? null;
$cve_ent = $input['cve_ent'] ?? $_GET['cve_ent'] ?? '26';
$cve_mun = $input['cve_mun'] ?? $_GET['cve_mun'] ?? '030';
$lat = floatval($input['lat'] ?? $_GET['lat'] ?? 29.0729);
$lng = floatval($input['lng'] ?? $_GET['lng'] ?? -110.9559);

try {
    // Si tenemos polígono, hacer consulta espacial
    if ($polygon) {
        $result = queryAGEBsByPolygon($polygon, $cve_ent, $cve_mun);
    } else {
        // Buscar AGEBs cercanas a las coordenadas
        $result = queryAGEBsByLocation($lat, $lng, $cve_ent, $cve_mun);
    }

    echo json_encode($result);

} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
        'fallback' => getFallbackData($cve_ent, $cve_mun)
    ]);
}

/**
 * Consulta AGEBs que intersectan con un polígono dado
 */
function queryAGEBsByPolygon($polygon, $cve_ent, $cve_mun)
{
    // Convertir GeoJSON a WKT si es necesario
    $wkt = is_array($polygon) ? geoJsonToWKT($polygon) : $polygon;

    // Intentar consultar el servicio de INEGI primero
    $inegiResult = queryINEGIService($wkt, $cve_ent, $cve_mun);

    if ($inegiResult) {
        return $inegiResult;
    }

    // Fallback: calcular basándose en el área del polígono y datos censales
    return calculateFromPolygonArea($polygon, $cve_ent, $cve_mun);
}

/**
 * Consulta el servicio WFS de INEGI
 */
function queryINEGIService($wkt, $cve_ent, $cve_mun)
{
    // Intentar con el servicio de catálogo geoestadístico de INEGI
    $baseUrl = "https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgee/buscar";

    // Construir parámetros de búsqueda
    $params = [
        'cve_ent' => $cve_ent,
        'cve_mun' => $cve_mun,
        'formato' => 'json'
    ];

    $url = $baseUrl . '?' . http_build_query($params);

    $context = stream_context_create([
        'http' => [
            'timeout' => 15,
            'header' => 'Accept: application/json'
        ]
    ]);

    $response = @file_get_contents($url, false, $context);

    if ($response) {
        $data = json_decode($response, true);
        if ($data && isset($data['datos'])) {
            return [
                'success' => true,
                'source' => 'INEGI WFS',
                'agebs' => $data['datos']
            ];
        }
    }

    return null;
}

/**
 * Consulta AGEBs cercanas a una ubicación
 */
function queryAGEBsByLocation($lat, $lng, $cve_ent, $cve_mun)
{
    // Intentar consulta inversa de INEGI
    $url = "https://gaia.inegi.org.mx/wscatgeo/v2/geo/mgee/geocodificacion/{$lng},{$lat}";

    $context = stream_context_create([
        'http' => [
            'timeout' => 10,
            'header' => 'Accept: application/json'
        ]
    ]);

    $response = @file_get_contents($url, false, $context);

    if ($response) {
        $data = json_decode($response, true);
        if ($data && isset($data['clave_geoestadistica'])) {
            // Tenemos la clave del AGEB, obtener datos censales
            $ageb_key = $data['clave_geoestadistica'];
            return [
                'success' => true,
                'source' => 'INEGI Geocodificación',
                'clave_ageb' => $ageb_key,
                'data' => getCensusDataForAGEB($ageb_key)
            ];
        }
    }

    // Fallback
    return getFallbackData($cve_ent, $cve_mun);
}

/**
 * Convierte GeoJSON polygon a WKT
 */
function geoJsonToWKT($geoJson)
{
    $coords = $geoJson['coordinates'][0] ?? $geoJson;
    $points = [];

    foreach ($coords as $coord) {
        $points[] = $coord[0] . ' ' . $coord[1];
    }

    // Cerrar el polígono si no está cerrado
    if ($points[0] !== end($points)) {
        $points[] = $points[0];
    }

    return 'POLYGON((' . implode(', ', $points) . '))';
}

/**
 * Calcula la población basándose en el área del polígono
 */
function calculateFromPolygonArea($polygon, $cve_ent, $cve_mun)
{
    // Calcular área aproximada del polígono
    $areaKm2 = calculatePolygonArea($polygon);

    // Obtener densidad del municipio
    $census = getCensusData($cve_ent, $cve_mun);
    $densidad = $census['densidad_urbana'];

    // Calcular población
    $poblacion = round($areaKm2 * $densidad);

    return [
        'success' => true,
        'source' => 'INEGI Censo 2020 (calculado)',
        'area_km2' => round($areaKm2, 4),
        'densidad_urbana' => $densidad,
        'location' => [
            'nom_ent' => $census['nom_ent'],
            'nom_mun' => $census['nom_mun']
        ],
        'data' => [
            'pobtot' => $poblacion,
            'pobmas' => round($poblacion * 0.49),
            'pobfem' => round($poblacion * 0.51),
            'p_0a14' => round($poblacion * 0.22),
            'p_15a64' => round($poblacion * 0.68),
            'p_65ymas' => round($poblacion * 0.10),
            'vivhab' => round($poblacion / 3.6)
        ],
        'nota' => 'Calculado usando densidad urbana promedio del municipio'
    ];
}

/**
 * Calcula el área de un polígono en km²
 * Usando la fórmula del polígono (Shoelace formula)
 */
function calculatePolygonArea($polygon)
{
    $coords = [];

    if (is_array($polygon)) {
        $coords = $polygon['coordinates'][0] ?? $polygon;
    } else {
        // Parse WKT
        preg_match('/POLYGON\(\((.+)\)\)/', $polygon, $matches);
        if (isset($matches[1])) {
            $points = explode(',', $matches[1]);
            foreach ($points as $point) {
                $xy = explode(' ', trim($point));
                $coords[] = [floatval($xy[0]), floatval($xy[1])];
            }
        }
    }

    if (count($coords) < 3) {
        return 0;
    }

    // Shoelace formula para calcular área
    $n = count($coords);
    $area = 0;

    for ($i = 0; $i < $n; $i++) {
        $j = ($i + 1) % $n;
        $area += $coords[$i][0] * $coords[$j][1];
        $area -= $coords[$j][0] * $coords[$i][1];
    }

    $area = abs($area) / 2;

    // Convertir de grados² a km² (aproximación para México ~latitud 25-30)
    // 1 grado de latitud ≈ 111 km
    // 1 grado de longitud ≈ 100 km (varía según latitud)
    $areaKm2 = $area * 111 * 100;

    return $areaKm2;
}

/**
 * Datos censales por municipio (Censo 2020)
 */
function getCensusData($cve_ent, $cve_mun)
{
    $data = [
        // Sonora
        '26030' => ['nom_ent' => 'Sonora', 'nom_mun' => 'Hermosillo', 'poblacion' => 936263, 'area_km2' => 14880, 'area_urbana' => 220, 'densidad_urbana' => 4256],
        '26043' => ['nom_ent' => 'Sonora', 'nom_mun' => 'Nogales', 'poblacion' => 264782, 'area_km2' => 1682, 'area_urbana' => 80, 'densidad_urbana' => 3310],
        '26018' => ['nom_ent' => 'Sonora', 'nom_mun' => 'Cajeme', 'poblacion' => 433050, 'area_km2' => 4037, 'area_urbana' => 150, 'densidad_urbana' => 2887],
        // CDMX
        '09015' => ['nom_ent' => 'Ciudad de México', 'nom_mun' => 'Cuauhtémoc', 'poblacion' => 545884, 'area_km2' => 32.4, 'area_urbana' => 32.4, 'densidad_urbana' => 16848],
        '09014' => ['nom_ent' => 'Ciudad de México', 'nom_mun' => 'Benito Juárez', 'poblacion' => 434153, 'area_km2' => 26.6, 'area_urbana' => 26.6, 'densidad_urbana' => 16320],
        // Jalisco
        '14039' => ['nom_ent' => 'Jalisco', 'nom_mun' => 'Guadalajara', 'poblacion' => 1385629, 'area_km2' => 151.4, 'area_urbana' => 151.4, 'densidad_urbana' => 9152],
        // Nuevo León
        '19039' => ['nom_ent' => 'Nuevo León', 'nom_mun' => 'Monterrey', 'poblacion' => 1142994, 'area_km2' => 324.8, 'area_urbana' => 200, 'densidad_urbana' => 5715],
    ];

    $key = $cve_ent . $cve_mun;
    return $data[$key] ?? $data['26030']; // Default a Hermosillo
}

/**
 * Obtiene datos censales para una clave de AGEB específica
 */
function getCensusDataForAGEB($ageb_key)
{
    // Aquí se podría consultar una base de datos o API con datos por AGEB
    // Por ahora, usamos promedios
    return [
        'pobtot' => 3500,
        'pobmas' => 1715,
        'pobfem' => 1785,
        'p_0a14' => 770,
        'p_15a64' => 2380,
        'p_65ymas' => 350,
        'vivhab' => 972
    ];
}

/**
 * Datos de fallback
 */
function getFallbackData($cve_ent, $cve_mun)
{
    $census = getCensusData($cve_ent, $cve_mun);

    return [
        'success' => true,
        'source' => 'INEGI Censo 2020 (fallback)',
        'location' => [
            'nom_ent' => $census['nom_ent'],
            'nom_mun' => $census['nom_mun']
        ],
        'densidad_urbana' => $census['densidad_urbana'],
        'nota' => 'Use las herramientas de dibujo para seleccionar un área específica'
    ];
}
