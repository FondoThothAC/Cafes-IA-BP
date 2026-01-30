<?php
/**
 * API DENUE Proxy - Búsqueda de establecimientos económicos
 * 
 * DENUE: Directorio Estadístico Nacional de Unidades Económicas
 * Fuente: https://www.inegi.org.mx/servicios/api_denue.html
 * 
 * IMPORTANTE: Para datos REALES necesitas tu propio token de INEGI
 * Obtenerlo gratis en: https://www.inegi.org.mx/app/api/denue/v1/tokenVerify.aspx
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');

// ============================================
// CONFIGURACIÓN - Token de DENUE INEGI
// ============================================
// CAMBIA ESTE TOKEN por el tuyo propio de INEGI
// Obtenerlo en: https://www.inegi.org.mx/app/api/denue/v1/tokenVerify.aspx
$DENUE_TOKEN = getenv('DENUE_TOKEN') ?: '1b9e230f-2ae0-48db-bd20-8810b1db575e';

// Parámetros
$lat = floatval($_GET['lat'] ?? $_POST['lat'] ?? 29.0729);
$lng = floatval($_GET['lng'] ?? $_POST['lng'] ?? -110.9559);
$radius = min(intval($_GET['radius'] ?? $_POST['radius'] ?? 2000), 5000);
$keywords = $_GET['keywords'] ?? $_POST['keywords'] ?? 'todos';
$keywords = trim($keywords);
if (empty($keywords))
    $keywords = 'todos';

// Si hay token, intentar API real
if (!empty($DENUE_TOKEN)) {
    $result = searchDENUE_Real($lat, $lng, $radius, $keywords, $DENUE_TOKEN);
    if ($result['success']) {
        echo json_encode($result, JSON_UNESCAPED_UNICODE);
        exit;
    }
}

// Fallback: Mensaje informativo con link a DENUE
echo json_encode([
    'success' => true,
    'source' => 'Configurar Token DENUE',
    'total' => 0,
    'by_size' => ['micro' => 0, 'pequeña' => 0, 'mediana' => 0, 'grande' => 0],
    'top_activities' => [],
    'businesses' => [],
    'message' => 'Para ver datos reales del DENUE, configura tu token de INEGI',
    'instructions' => [
        '1. Visita https://www.inegi.org.mx/app/api/denue/v1/tokenVerify.aspx',
        '2. Ingresa tu correo electrónico',
        '3. Recibirás tu token por email',
        '4. Agrega la variable DENUE_TOKEN en tu servidor'
    ],
    'denue_web_url' => "https://www.inegi.org.mx/app/mapa/denue/?lg=es&ll=$lat,$lng&z=15",
    'search_term' => $keywords
], JSON_UNESCAPED_UNICODE);

/**
 * Consulta la API real de DENUE
 */
function searchDENUE_Real($lat, $lng, $radius, $keywords, $token)
{
    $url = "https://www.inegi.org.mx/app/api/denue/v1/consulta/Buscar/"
        . urlencode($keywords) . "/"
        . number_format($lat, 8, '.', '') . "," . number_format($lng, 8, '.', '') . "/"
        . $radius . "/" . $token;

    $context = stream_context_create([
        'http' => [
            'timeout' => 30,
            'method' => 'GET',
            'header' => "Accept: application/json\r\nUser-Agent: PlanIA/1.0",
            'ignore_errors' => true
        ],
        'ssl' => ['verify_peer' => false, 'verify_peer_name' => false]
    ]);

    $response = @file_get_contents($url, false, $context);

    if ($response === false || empty($response)) {
        return ['success' => false, 'error' => 'No response'];
    }

    $data = json_decode($response, true);

    if (!is_array($data) || count($data) === 0) {
        return ['success' => false, 'error' => 'No data'];
    }

    // Procesar resultados
    $businesses = [];
    $bySize = ['micro' => 0, 'pequeña' => 0, 'mediana' => 0, 'grande' => 0];
    $byActivity = [];

    foreach ($data as $item) {
        $nombre = $item['Nombre'] ?? 'Sin nombre';
        $razonSocial = $item['Razon_social'] ?? '';
        // Campo correcto: Clase_actividad
        $actividad = $item['Clase_actividad'] ?? $item['Nombre_Actividad'] ?? '';

        // Dirección: Tipo_vialidad, Calle, Num_Exterior
        $tipoVial = $item['Tipo_vialidad'] ?? '';
        $calle = $item['Calle'] ?? '';
        $numExt = $item['Num_Exterior'] ?? '';
        $numInt = $item['Num_Interior'] ?? '';
        $direccion = trim("$tipoVial $calle $numExt" . ($numInt ? " Int. $numInt" : ""));

        // Colonia y CP directos
        $colonia = $item['Colonia'] ?? '';
        $cp = $item['CP'] ?? '';
        $telefono = $item['Telefono'] ?? '';
        $email = $item['Correo_e'] ?? '';
        $web = $item['Sitio_internet'] ?? '';

        // Tamaño: Estrato
        $tamano = $item['Estrato'] ?? '0 a 5 personas';

        $bizLat = floatval($item['Latitud'] ?? 0);
        $bizLng = floatval($item['Longitud'] ?? 0);

        $businesses[] = [
            'id' => $item['Id'] ?? '',
            'nombre' => $nombre ?: $razonSocial,
            'actividad' => $actividad,
            'direccion' => $direccion,
            'colonia' => $colonia,
            'cp' => $cp,
            'telefono' => $telefono,
            'email' => $email,
            'web' => $web,
            'tamaño' => $tamano,
            'lat' => $bizLat,
            'lng' => $bizLng
        ];

        // Clasificar tamaño basado en Estrato
        $s = strtolower($tamano);
        if (strpos($s, '0 a 5') !== false || strpos($s, '1 a 5') !== false)
            $bySize['micro']++;
        elseif (strpos($s, '6 a 10') !== false || strpos($s, '11 a 30') !== false)
            $bySize['pequeña']++;
        elseif (strpos($s, '31 a') !== false || strpos($s, '51 a') !== false)
            $bySize['mediana']++;
        elseif (strpos($s, '101') !== false || strpos($s, '251') !== false)
            $bySize['grande']++;
        else
            $bySize['micro']++;

        // Actividades
        if ($actividad) {
            $actShort = strlen($actividad) > 50 ? substr($actividad, 0, 50) . '...' : $actividad;
            $byActivity[$actShort] = ($byActivity[$actShort] ?? 0) + 1;
        }
    }

    arsort($byActivity);

    return [
        'success' => true,
        'source' => 'DENUE INEGI 2024',
        'total' => count($businesses),
        'by_size' => $bySize,
        'top_activities' => array_slice($byActivity, 0, 5, true),
        'businesses' => $businesses,
        'search_term' => $keywords
    ];
}
