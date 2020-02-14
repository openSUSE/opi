<?php

# Test it with `php -S localhost:8000 index.php`

require __DIR__ . '/config.php';

# TODO add API rate limits.

$obs_api_link = $_GET['obs_api_link'];
$obs_instance = $_GET['obs_instance']; # OBS / Packman

if ($obs_instance === 'openSUSE') {
    $username = $obs_username;
    $password = $obs_password;
} elseif ($obs_instance === 'Packman') {
    $username = $pmbs_username;
    $password = $pmbs_password;
}

$obs_api_link = str_replace('://', "://$username:$password@", $obs_api_link);

echo file_get_contents($obs_api_link);
