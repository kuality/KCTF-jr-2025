<?php

if(!isset($_GET['url'])){
    die("empty url querystring");
}

if(!isset($_GET['option'])){
    $_GET['option'] = NULL;
}

require __DIR__ . '/vendor/autoload.php';

use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

$process = new Process(['curl', $_GET['url'], $_GET['option']]);
$process->run();

if (!$process->isSuccessful()) {
    throw new ProcessFailedException($process);
}

echo "<pre>" . $process->getOutput() . "</pre>";