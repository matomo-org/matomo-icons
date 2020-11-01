<?php

require_once "vendor/autoload.php";

$brands = \DeviceDetector\Parser\Device\AbstractDeviceParser::$deviceBrands;
natcasesort($brands);

$data = [
    "os" => \DeviceDetector\Parser\OperatingSystem::getAvailableOperatingSystems(),
    "browsers" => \DeviceDetector\Parser\Client\Browser::getAvailableBrowsers(),
    "brand" => $brands
];

echo json_encode($data);
